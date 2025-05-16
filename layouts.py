import calendar
import datetime
import locale

from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.properties import ColorProperty, StringProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView


class Headers(GridLayout):
    color_header = ColorProperty([1, 1, 1, 1])
    text_header = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.date = datetime.date.today().strftime("%d.%m.%Y")


class MonthChoice(BoxLayout):
    text_with_date = ObjectProperty(None)
    btn_to_next_month = ObjectProperty(None)

    def __init__(self, **kwargs):
        self.date_today = datetime.date.today()
        self.new_date = None
        super().__init__(**kwargs)

    def get_text_from_date(self):
        list_of_month = ["Январь", "Февраль", "Март",
                         "Апрель", "Май", "Июнь",
                         "Июль", "Август", "Сентябрь",
                         "Октябрь", "Ноябрь", "Декабрь"]
        date = self.new_date if self.new_date else self.date_today
        return date.strftime(f"За {list_of_month[int(date.month) - 1]} %Y")

    def get_next_month(self):
        if self.new_date:
            days = calendar.monthrange(self.new_date.year, self.new_date.month)[1]
            self.new_date += datetime.timedelta(days=days)
        else:
            days = calendar.monthrange(self.date_today.year, self.date_today.month)[1]
            self.new_date = self.date_today + datetime.timedelta(days=days)

        self.btn_to_next_month.disabled = True if self.new_date == self.date_today else False
        self.text_with_date.text = self.get_text_from_date()

        app = App.get_running_app()
        app.update_data_in_screens(self.new_date.month, self.new_date.year,
                                   **{app.root.current_screen.name: app.root.current_screen})

    def get_previous_month(self):
        if self.new_date:
            days = calendar.monthrange(self.new_date.year,
                                       12 if self.new_date.month - 1 == 0 else self.new_date.month - 1)[1]
            self.new_date -= datetime.timedelta(days=days)
        else:
            days = calendar.monthrange(self.date_today.year,
                                       12 if self.date_today.month - 1 == 0 else self.date_today.month - 1)[1]
            self.new_date = self.date_today - datetime.timedelta(days=days)

        self.btn_to_next_month.disabled = False
        self.text_with_date.text = self.get_text_from_date()

        app = App.get_running_app()
        app.update_data_in_screens(self.new_date.month, self.new_date.year,
                                   **{app.root.current_screen.name: app.root.current_screen,
                                      "income": app.root.get_screen("income"),
                                      "main": app.root.get_screen("main")})

    def reset_month_choice(self):
        self.new_date = None
        self.text_with_date.text = self.get_text_from_date()
        self.btn_to_next_month.disabled = True

        app = App.get_running_app()
        app.update_data_in_screens(self.date_today.month, self.date_today.year,
                                   **{app.root.current_screen.name: app.root.current_screen,
                                      "main": app.root.get_screen("main")})


class MonthInfo(GridLayout):
    sum_income = StringProperty("0,00 ₽")
    sum_expenses = StringProperty("0,00 ₽")
    sum_credit = StringProperty("0,00 ₽")


class DropDownList(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.children[0].bind(minimum_height=self.children[0].setter("height"))

    def fill_the_table(self, key: str, month: int, year: int):
        app = App.get_running_app()

        current_month = datetime.date.today().month
        last_day_in_month = calendar.monthrange(year, month)[1]
        day_finish = last_day_in_month if month != current_month else datetime.date.today().day

        list_width_info_for_drop_down_list = app.get_data_db_in_period(key, "name, sum", month, year, 1, day_finish)

        layout_for_list: BoxLayout = self.children[0]
        # layout_for_list.bind(minimum_height=layout_for_list.setter('height'))

        def update_row_height(instance):
            # Находим максимальную высоту среди дочерних элементов
            max_height = 0
            for child in instance.children:
                if hasattr(child, 'texture_size'):
                    child_height = child.texture_size[1]
                else:
                    child_height = 0
                if child_height > max_height:
                    max_height = child_height
            instance.height = max_height + dp(10)  # добавляем немного отступа
            update_layout_for_list(instance.parent)

        def update_layout_for_list(instance):
            instance.height = sum([ch.height for ch in instance.children])

        for list_entry in list_width_info_for_drop_down_list:
            # Создаём контейнер для пары лейблов
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(25))
            row.bind(
                minimum_height=lambda instance, value: update_row_height(instance),
                height=lambda instance, value: update_layout_for_list(instance.parent)
            )

            # Первый лейбл — название
            label_with_name = Label(
                text=list_entry[0],
                font_size="14sp",
                color=(0, 0, 0, 1),
                halign='left',
                valign='center',
                size_hint_x=0.7,  # занимает 70% доступной ширины
                size_hint_y=None
            )
            # Установка text_size для переноса текста внутри
            label_with_name.bind(
                texture_size=lambda instance, value: update_row_height(instance.parent),
                size=lambda instance, value: setattr(instance, 'text_size', (instance.width - 10, None))
            )

            row.add_widget(label_with_name)

            # Второй лейбл — сумма
            label_with_amount = Label(
                text=locale.currency(list_entry[1], grouping=True, symbol=False) + " ₽",
                font_size="14sp",
                color=(0, 0, 0, 1),
                halign='right',
                valign='center',
                size_hint_x=0.3,  # занимает оставшиеся 30%
                size_hint_y=None
            )
            label_with_amount.bind(
                texture_size=lambda instance, value: update_row_height(instance.parent),
                size=lambda instance, value: setattr(instance, 'text_size', (instance.width - 10, None))
            )

            row.add_widget(label_with_amount)

            layout_for_list.add_widget(row)
        return


class DisplaysSums(BoxLayout):
    color_text = ColorProperty()
    first_sum = StringProperty("0,00 ₽")
    second_sum = StringProperty("(0,00 ₽)")


class AddIncomePage(FloatLayout):
    pass


class AddExpensesPage(FloatLayout):
    pass


class NavigateButtons(BoxLayout):
    canvas_color_main = ColorProperty([0, 0, 0, 0])
    canvas_color_income = ColorProperty([0, 0, 0, 0])
    canvas_color_expenses = ColorProperty([0, 0, 0, 0])
    canvas_color_credit = ColorProperty([0, 0, 0, 0])
    canvas_color_analysis = ColorProperty([0, 0, 0, 0])
    label_color_main = ColorProperty([.55, .55, .55, 1])
    label_color_income = ColorProperty([.55, .55, .55, 1])
    label_color_expenses = ColorProperty([.55, .55, .55, 1])
    label_color_credit = ColorProperty([.55, .55, .55, 1])
    label_color_analysis = ColorProperty([.55, .55, .55, 1])
    btn_image_main = StringProperty("navigate_image/house.png")
    btn_image_income = StringProperty("navigate_image/money-income.png")
    btn_image_expenses = StringProperty("navigate_image/cheap-stack.png")
    btn_image_credit = StringProperty("navigate_image/bank.png")
    btn_image_analysis = StringProperty("navigate_image/brain.png")
