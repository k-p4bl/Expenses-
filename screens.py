from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen


class MainPage(Screen):
    pass


class IncomePage(Screen):
    every_month = ObjectProperty(None)
    onetime = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ExpensesPage(Screen):
    pass


class CreditPage(Screen):
    pass


class AnalysisPage(Screen):
    pass
