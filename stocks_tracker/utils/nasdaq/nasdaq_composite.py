class NasdaqComposite:
    def __init__(self, date, ma_3, ma_7, ma_3_change=None, ma_7_change=None, market_action=None):
        self.__date = date
        self.__ma_3 = ma_3
        self.__ma_7 = ma_7
        self.__ma_3_change = ma_3_change
        self.__ma_7_change = ma_7_change
        self.__market_action = market_action

    def get_date(self):
        return self.__date

    def set_date(self, date):
        self.__date = date

    def get_ma_3(self):
        return self.__ma_3

    def set_ma_3(self, ma_3):
        self.__ma_3 = ma_3

    def get_ma_7(self):
        return self.__ma_7

    def set_ma_7(self, ma_7):
        self.__ma_7 = ma_7

    def get_ma_3_change(self):
        return self.__ma_3_change

    def set_ma_3_change(self, ma_3_change):
        self.__ma_3_change = ma_3_change

    def get_ma_7_change(self):
        return self.__ma_7_change

    def set_ma_7_change(self, ma_7_change):
        self.__ma_7_change = ma_7_change

    def get_market_action(self):
        return self.__market_action

    def set_market_action(self, market_action):
        self.__market_action = market_action

    def __lt__(self, other):
        return other.get_date() < self.get_date()

    def __gt__(self, other):
        return other.__lt__(self)

    def __eq__(self, other):
        return self.get_date() == other.get_date()

    def __ne__(self, other):
        return not self.__eq__(other)
