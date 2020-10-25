class NasdaqComposite:
    def __init__(self, ma_3, ma_3_change, ma_7, ma_7_change, is_a_buy_market):
        self.__ma_3 = ma_3
        self.__ma_3_change = ma_3_change
        self.__ma_7 = ma_7
        self.__ma_7_change = ma_7_change
        self.__is_a_buy_market = is_a_buy_market

    def get_ma_3(self):
        return self.__ma_3

    def get_ma_3_change(self):
        return self.__ma_3_change

    def get_ma_7(self):
        return self.__ma_7

    def get_ma_7_change(self):
        return self.__ma_7_change

    def get_is_a_buy_market(self):
        return self.__is_a_buy_market
