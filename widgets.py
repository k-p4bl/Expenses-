import locale
import re

from kivy.properties import NumericProperty, ColorProperty, StringProperty
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput


locale.setlocale(locale.LC_ALL, 'RU_ru')


class ErrorConnDB(Label):
    parent_width = NumericProperty()


class BtnOfIncomeMoney(Button):
    green_canvas = (.7, .8156, .6706, 1)
    green_text = (.137, .4941, 0, 1)
    white_canvas = (1, 1, 1, 1)
    white_text = (.4274, .4274, .4274, 1)
    color_canvas = ColorProperty()
    color_text = ColorProperty()
    name_income = StringProperty("")
    sum_income = StringProperty("")

    def __init__(self, c_canvas, c_text, name_income, sum_income, id_income, **kwargs):
        self.id_income = id_income
        self.color_canvas = c_canvas
        self.color_text = c_text
        self.name_income = name_income
        self.sum_income = sum_income
        super().__init__(**kwargs)

    def open_details(self):
        self.canvas.before.children[1].inset = False


class BtnOfExpenses(Button):
    red_canvas = (.882, .627, .627, 1)
    red_text = (.753, .129, .129, 1)
    white_canvas = (1, 1, 1, 1)
    white_text = (.4274, .4274, .4274, 1)
    color_canvas = ColorProperty()
    color_text = ColorProperty()
    name_income = StringProperty("")
    sum_income = StringProperty("")

    def __init__(self, c_canvas, c_text, name_income, sum_income, id_income, **kwargs):
        self.id_income = id_income
        self.color_canvas = c_canvas
        self.color_text = c_text
        self.name_income = name_income
        self.sum_income = sum_income
        super().__init__(**kwargs)

    def open_details(self):
        self.canvas.before.children[1].inset = False


class SumTextInput(TextInput):
    text: str

    def do_backspace(self, from_undo=False, mode='bkspc'):
        super().do_backspace(from_undo=from_undo, mode=mode)

        if "," in self.text:
            cursor = self.cursor
            simbols = len(self.text)
            # reformat number to currency
            if self.text.split(",")[0]:
                self.text = ",".join(['{0:,}'.format(int(self.text.split(",")[0].replace(' ', ''))).replace(',', ' '),
                                      self.text.split(",")[1]])
            else:
                self.text = "0" + self.text
            difference = len(self.text) - simbols
            self.cursor = (cursor[0] + difference, cursor[1])

        else:
            if self.text:
                cursor = self.cursor
                simbols = len(self.text)
                # reformat number to currency
                self.text = '{0:,}'.format(int(self.text.replace(' ', ''))).replace(',', ' ')

                # with adding spaces, move cursor
                difference = len(self.text) - simbols
                self.cursor = (cursor[0] + difference, cursor[1])

    def insert_text(self, substring, from_undo=False):
        pat = re.compile('[^0-9]')

        if substring == ",":
            # blocking input one more "," if it is already in text
            substring = substring if substring not in self.text else ""
            return super().insert_text(substring, from_undo=from_undo)

        if "," in self.text:
            # clearing letters
            s = re.sub(pat, '', substring)
            # blocking input after comma, if after comma already 2 number
            s = s if len(self.text.split(",")[1]) < 2 else s if self.cursor[0] < len(self.text) - 2 else ""
            super().insert_text(s, from_undo=from_undo)

            cursor = self.cursor
            simbols = len(self.text)
            # reformat number to currency
            self.text = ",".join(['{0:,}'.format(int(self.text.split(",")[0].replace(' ', ''))).replace(',', ' '),
                                  self.text.split(",")[1]])
            difference = len(self.text) - simbols
            self.cursor = (cursor[0] + difference, cursor[1])

        else:
            # clearing letters
            s = re.sub(pat, '', substring)

            super().insert_text(s, from_undo=from_undo)

            cursor = self.cursor
            simbols = len(self.text)
            # reformat number to currency
            self.text = '{0:,}'.format(int(self.text.replace(' ', ''))).replace(',', ' ')

            # with adding spaces, move cursor
            difference = len(self.text) - simbols
            self.cursor = (cursor[0] + difference, cursor[1])


class DateTextInput(TextInput):
    def do_backspace(self, from_undo=False, mode='bkspc'):
        super().do_backspace(from_undo=from_undo, mode=mode)
        if self.text:
            if len(self.text) <= 6:
                self.text = self.text[:5]
            if len(self.text) <= 3:
                self.text = self.text[:2]
        return

    def insert_text(self, substring, from_undo=False):
        pat = re.compile('[^0-9]')
        s = re.sub(pat, '', substring)

        if len(self.text) > 9:
            s = ""

        self.text = self.text.replace(".", "")

        super().insert_text(s, from_undo=from_undo)

        if self.text:
            text = self.text
            if len(text) >= 2:
                text = text[:2] + "." + text[2:]
            if len(text) >= 5:
                text = text[:5] + "." + text[5:]
            self.text = text
