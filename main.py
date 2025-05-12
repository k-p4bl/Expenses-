import datetime
import calendar
import locale
import os
import sqlite3

from kivy.config import Config

Config.read('myconfig.ini')
locale.setlocale(locale.LC_ALL, 'RU_ru')
from kivy.metrics import dp
from kivy.properties import ObjectProperty
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivy.uix.scrollview import ScrollView

from layouts import AddIncomePage, AddExpensesPage
from screens import MainPage, IncomePage, ExpensesPage, CreditPage, AnalysisPage
from widgets import BtnOfIncomeMoney, BtnOfExpenses, BtnOfCredit, ErrorConnDB, CreditInfo

from kivy.core.window import Window


class ExpensesApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sum_expenses_past_and_future = float()
        self.sum_expenses_past = float()
        self.primary_expenses_float_layout = ObjectProperty()
        self.primary_income_float_layout = ObjectProperty()
        self.float_child_scroll = None
        self.sum_income_past_and_future = float()
        self.sum_expenses_of_current_month = float()
        self.sum_income_past = float()
        self.sum_credit_of_current_month = float()
        self.expenses_of_current_month = list
        self.incomes_of_current_month = list
        self.conn = None

    def build(self):
        main = MainPage(name="main")
        income = IncomePage(name="income")
        expenses = ExpensesPage(name="expenses")
        credit = CreditPage(name="credit")
        self.float_child_scroll = income.ids.ch_scroll
        self.float_child_scroll.bind(children=self.update_height)
        try:
            if os.path.exists("expenses.db"):
                self._get_data_db(main=main, income=income, expenses=expenses, credit=credit)
            else:
                raise
        except:
            main.add_widget(ErrorConnDB())

        Window.clearcolor = (.96, .96, .96, 1)
        scr_manager = ScreenManager(transition=NoTransition())
        scr_manager.add_widget(main)
        scr_manager.add_widget(income)
        scr_manager.add_widget(expenses)
        scr_manager.add_widget(credit)
        scr_manager.add_widget(AnalysisPage(name="analysis"))
        return scr_manager

    def on_stop(self):
        if self.conn:
            self.conn.close()

    def _get_data_db(self, **screens):
        self.conn = sqlite3.connect("expenses.db")
        self.conn.row_factory = sqlite3.Row
        today = datetime.date.today()
        self.update_data_in_screens(today.month, today.year, **screens)

    def get_data_db_in_period(self, table: str, witch_col: str, month: int, year: int, day_start: int,
                              day_finish: int) -> list:

        return self.conn.execute(
            f"""
            SELECT {"*" if witch_col == "all" else witch_col} FROM {table} 
            WHERE date >= date(?) AND date <= date(?)
            """,
            [datetime.date(year=year, month=month, day=day_start).strftime("%Y-%m-%d"),
             datetime.date(year=year, month=month, day=day_finish).strftime("%Y-%m-%d")]).fetchall()

    def update_data_in_screens(self, month: int, year: int, **screens):
        """
        Вызывается в самом начале, при строении приложения, для отображения всех данных из базы данных;
        При смене месяца на экране;
        При вносе изменений в базу данных.
        :param month: number of month
        :param year: number of year
        :param screens: current_screen.name - current_screen
        """
        last_day_in_month = calendar.monthrange(year, month)[1]
        today = datetime.date.today()
        self.sum_income_past = .0
        self.sum_expenses_of_current_month = .0
        self.sum_credit_of_current_month = .0
        self.sum_income_past_and_future = .0
        self.sum_expenses_past = .0
        self.sum_expenses_past_and_future = .0

        if "main" in screens:
            name_and_sum_income = self.get_data_db_in_period("income", "name, sum", month, year,
                                                             1, today.day)
            name_and_sum_expenses = self.get_data_db_in_period("expenses", "name, sum, id_credit", month, year,
                                                               1,
                                                               today.day if month == today.month else last_day_in_month)
            sum_income = sum(row["sum"] for row in name_and_sum_income)
            sum_expenses = sum(row["sum"] for row in name_and_sum_expenses)
            sum_ex_to_credit = sum(row["sum"] if row["id_credit"] else 0 for row in name_and_sum_expenses)

            month_info = screens["main"].ids.month_info
            month_info.sum_income = locale.currency(sum_income,
                                                    grouping=True,
                                                    symbol=False) + " ₽"
            month_info.sum_expenses = locale.currency(sum_expenses,
                                                      grouping=True,
                                                      symbol=False) + " ₽"
            month_info.sum_credit = locale.currency(sum_ex_to_credit,
                                                    grouping=True,
                                                    symbol=False) + " ₽"

        if "income" in screens:
            screens["income"].ids.every_month.clear_widgets()
            screens["income"].ids.onetime.clear_widgets()

            self.incomes_of_current_month = self.get_data_db_in_period("income", "all", month, year,
                                                                       1, last_day_in_month)

            for income in self.incomes_of_current_month:
                if datetime.datetime.strptime(income["date"], "%Y-%m-%d").date() <= today:
                    # For updating data
                    self.sum_income_past += income["sum"]
                    self.sum_income_past_and_future += income["sum"]
                    # Create btn for history past operations of income
                    if income["every_month"]:
                        screens["income"].every_month.add_widget(BtnOfIncomeMoney(
                            BtnOfIncomeMoney.green_canvas,
                            BtnOfIncomeMoney.green_text,
                            income["name"],
                            locale.currency(income["sum"], grouping=True, symbol=False) + " ₽",
                            income["id"]))
                    else:
                        screens["income"].onetime.add_widget(BtnOfIncomeMoney(
                            BtnOfIncomeMoney.green_canvas,
                            BtnOfIncomeMoney.green_text,
                            income["name"],
                            locale.currency(income["sum"], grouping=True, symbol=False) + " ₽",
                            income["id"]))
                else:
                    # This is too updating
                    self.sum_income_past_and_future += income["sum"]
                    # Create for — future
                    if income["every_month"]:
                        screens["income"].every_month.add_widget(BtnOfIncomeMoney(
                            BtnOfIncomeMoney.white_canvas,
                            BtnOfIncomeMoney.white_text,
                            income["name"],
                            locale.currency(income["sum"], grouping=True, symbol=False) + " ₽",
                            income["id"]))
                    else:
                        screens["income"].onetime.add_widget(BtnOfIncomeMoney(
                            BtnOfIncomeMoney.white_canvas,
                            BtnOfIncomeMoney.white_text,
                            income["name"],
                            locale.currency(income["sum"], grouping=True, symbol=False) + " ₽",
                            income["id"]))

            # Update position widgets
            screens["income"].every_month.top = (screens["income"].ids.second_header.top -
                                                 screens["income"].ids.second_header.height - dp(8))
            screens["income"].ids.thrid_header.top = (screens["income"].every_month.top -
                                                      screens["income"].every_month.height - dp(38))
            screens["income"].onetime.top = (screens["income"].ids.thrid_header.top -
                                             screens["income"].ids.thrid_header.height - dp(8))

        if "expenses" in screens:
            screens["expenses"].ids.every_month.clear_widgets()
            screens["expenses"].ids.onetime.clear_widgets()

            self.expenses_of_current_month = self.get_data_db_in_period("expenses", "all", month, year,
                                                                        1, last_day_in_month)

            for expenses in self.expenses_of_current_month:
                if datetime.datetime.strptime(expenses["date"], "%Y-%m-%d").date() <= today:
                    # For updating data
                    self.sum_expenses_past += expenses["sum"]
                    self.sum_expenses_past_and_future += expenses["sum"]
                    # Create btn for history past operations of expenses
                    if expenses["every_month"]:
                        screens["expenses"].every_month.add_widget(BtnOfExpenses(
                            BtnOfExpenses.red_canvas,
                            BtnOfExpenses.red_text,
                            expenses["name"],
                            locale.currency(expenses["sum"], grouping=True, symbol=False) + " ₽",
                            expenses["id"]))
                    else:
                        screens["expenses"].onetime.add_widget(BtnOfExpenses(
                            BtnOfExpenses.red_canvas,
                            BtnOfExpenses.red_text,
                            expenses["name"],
                            locale.currency(expenses["sum"], grouping=True, symbol=False) + " ₽",
                            expenses["id"]))
                else:
                    # This is too updating
                    self.sum_income_past_and_future += expenses["sum"]
                    # Create for — future
                    if expenses["every_month"]:
                        screens["expenses"].every_month.add_widget(BtnOfExpenses(
                            BtnOfExpenses.red_canvas,
                            BtnOfExpenses.red_text,
                            expenses["name"],
                            locale.currency(expenses["sum"], grouping=True, symbol=False) + " ₽",
                            expenses["id"]))
                    else:
                        screens["expenses"].onetime.add_widget(BtnOfExpenses(
                            BtnOfExpenses.red_canvas,
                            BtnOfExpenses.red_text,
                            expenses["name"],
                            locale.currency(expenses["sum"], grouping=True, symbol=False) + " ₽",
                            expenses["id"]))

            # Update position widgets
            screens["expenses"].every_month.top = (screens["expenses"].ids.second_header.top -
                                                   screens["expenses"].ids.second_header.height - dp(8))
            screens["expenses"].ids.thrid_header.top = (screens["expenses"].every_month.top -
                                                        screens["expenses"].every_month.height - dp(38))
            screens["expenses"].onetime.top = (screens["expenses"].ids.thrid_header.top -
                                               screens["expenses"].ids.thrid_header.height - dp(8))

        # self.expenses_of_current_month = self.get_data_db_in_period("expenses", "all", month, year,
        #                                                             1, last_day_in_month)
        # for expenses in self.expenses_of_current_month:
        #     if datetime.datetime.strptime(expenses["date"], "%Y-%m-%d").date() <= today:
        #         if expenses["id_credit"] is not None:
        #             self.sum_credit_of_current_month += expenses["sum"]
        #
        #         self.sum_expenses_of_current_month += expenses["sum"]
        #     else:
        #         continue
        #
        # Update data on main page
        # month_info = screens["main"].ids.month_info
        # month_info.sum_income = locale.currency(self.sum_income_past,
        #                                         grouping=True,
        #                                         symbol=False) + " ₽"
        # month_info.sum_expenses = locale.currency(self.sum_expenses_of_current_month,
        #                                           grouping=True,
        #                                           symbol=False) + " ₽"
        # month_info.sum_credit = locale.currency(self.sum_credit_of_current_month,
        #                                         grouping=True,
        #                                         symbol=False) + " ₽"
        #
        # # Update data on income page
        # displays_sums_income = screens["income"].ids.sum_incomes
        # displays_sums_income.first_sum = locale.currency(self.sum_income_past,
        #                                                  grouping=True,
        #                                                  symbol=False) + " ₽"
        # displays_sums_income.second_sum = " (" + locale.currency(self.sum_income_past_and_future,
        #                                                          grouping=True,
        #                                                          symbol=False) + " ₽)"

    def update_height(self, instance, value):
        self.float_child_scroll.height = sum(child.height for child in self.float_child_scroll.children)

    def switch_to_add_income_page(self, scroll_view: ScrollView):
        self.primary_income_float_layout = scroll_view.children[0]

        header = self.root.current_screen.ids["header"]

        scroll_view.clear_widgets()
        income_page = AddIncomePage()
        scroll_view.add_widget(income_page)

        # Height of a floating widget: the sum of all child elements, the distance between them,
        # and the distance from the top of the root to the bottom of the "Header"
        income_page.height = (sum(child.height for child in income_page.children)
                              + scroll_view.top - header.pos[1] + dp(46))

        x = header.pos[0] + dp(12)
        # position of first widget: sum of heights of widgets below and space between them
        y = sum(child.height for child in income_page.children) - income_page.name_new_income.height + dp(20)
        income_page.name_new_income.pos = (x, y)

    def switch_to_back_income_page(self, scroll_view: ScrollView):
        scroll_view.clear_widgets()
        scroll_view.add_widget(self.primary_income_float_layout)

    def add_new_income(self, btn, name_new_income: str, sum_new_income: str, date_new_income: str, every_month: bool):
        btn.text = ""
        sum_new_income = float(sum_new_income.replace(" ", "").replace(",", "."))
        date_new_income = datetime.datetime.strptime(date_new_income, "%d.%m.%Y").date()

        self.conn.execute("INSERT INTO income (name, sum, date, every_month) VALUES (?, ?, ?, ?)",
                          (name_new_income, sum_new_income, date_new_income, every_month))

        self.conn.commit()

        self.switch_to_back_income_page(self.root.current_screen.ids["scroll"])

    def switch_to_add_expenses_page(self, scroll_view: ScrollView):
        self.primary_expenses_float_layout = scroll_view.children[0]

        header = self.root.current_screen.ids["header"]

        scroll_view.clear_widgets()
        expenses_page = AddExpensesPage()
        scroll_view.add_widget(expenses_page)

        # Height of a floating widget: the sum of all child elements, the distance between them,
        # and the distance from the top of the root to the bottom of the "Header"
        expenses_page.height = (sum(child.height for child in expenses_page.children)
                                + scroll_view.top - header.pos[1] + dp(46))

        x = header.pos[0] + dp(12)
        # position of first widget: sum of heights of widgets below and space between them
        y = sum(child.height for child in expenses_page.children) - expenses_page.name_new_expenses.height + dp(20)
        expenses_page.name_new_expenses.pos = (x, y)

    def add_new_expenses(self, btn, name_new_expenses: str, sum_new_expenses: str,
                         date_new_expenses: str, every_month: bool):
        btn.text = ""
        sum_new_income = float(sum_new_expenses.replace(" ", "").replace(",", "."))
        date_new_income = datetime.datetime.strptime(date_new_expenses, "%d.%m.%Y").date()

        self.conn.execute("INSERT INTO expenses (name, sum, date, every_month) VALUES (?, ?, ?, ?)",
                          (name_new_expenses, sum_new_income, date_new_income, every_month))

        self.conn.commit()

        self.switch_back_to_expenses_page(self.root.current_screen.ids["scroll"])

    def switch_back_to_expenses_page(self, scroll_view: ScrollView):
        scroll_view.clear_widgets()
        scroll_view.add_widget(self.primary_expenses_float_layout)


if __name__ == "__main__":
    ExpensesApp().run()
