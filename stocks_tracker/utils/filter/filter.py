from stocks_tracker.models import Stock
from yahoofinancials import YahooFinancials
import concurrent.futures

QUARTERLY = 'quarterly'
YEARLY = 'yearly'
EPS_GROWTH_THRESHOLD_Q = 'eps_growth_threshold_q'
EPS_GROWTH_QUARTERS = 'eps_growth_quarters'
EPS_GROWTH_THRESHOLD_Y = 'eps_growth_threshold_y'
EPS_GROWTH_YEARS = 'eps_growth_years'
SALES_GROWTH_THRESHOLD = 'sales_growth_threshold'
ACCELERATION_QUARTERS = 'acceleration_quarters'
ACCELERATION_YEARS = 'acceleration_years'
STOCK_SYMBOL = 'stock_symbol'
MILLION = 1000000
BILLION = 1000000000
TRILLION = 1000000000000


class FilteredStocks(object):
    def __init__(self, filters):
        self.filters = filters
        self.stocks = Stock.objects.all()
        self.filter_stocks()

    @staticmethod
    def is_growth_potential(target_sales_growth, threshold):
        if not target_sales_growth or target_sales_growth == 'N/A':
            return False

        sales_growth_number = (float(target_sales_growth[:-1].replace(',', '')))
        return sales_growth_number >= threshold

    def calc_sales_growth_stocks(self, threshold):
        filtered_stocks = []
        for stock in self.stocks:
            if FilteredStocks.is_growth_potential(stock.target_sales_growth, threshold):
                filtered_stocks.append(stock)
        self.stocks = filtered_stocks

    def filter_sales_growth(self):
        sales_threshold = self.filters.get(SALES_GROWTH_THRESHOLD, None)
        try:
            if sales_threshold:
                self.calc_sales_growth_stocks(float(sales_threshold))
        except Exception as e:  # check for NAN exception
            raise e

    @staticmethod
    def get_eps_list(stock, period_type):
        if period_type == QUARTERLY:
            return stock.eps_growth_q
        elif period_type == YEARLY:
            return stock.eps_growth_y
        return []

    @staticmethod
    def get_sales_list(stock, period_type):
        if period_type == QUARTERLY:
            return stock.sales_growth_q
        elif period_type == YEARLY:
            return stock.sales_growth_y
        return []

    @staticmethod
    def get_net_income_list(stock, period_type):
        if period_type == QUARTERLY:
            return stock.net_income_growth_q
        elif period_type == YEARLY:
            return stock.net_income_growth_y
        return []

    @staticmethod
    def is_acceleration(data_list, time_periods):
        if not data_list or len(data_list) < time_periods:
            return False

        for period in range(time_periods * (-1), 0):
            if data_list[period] <= 0 or (period < -1 and data_list[period] >= data_list[period + 1]):
                return False

        return True

    @staticmethod
    def is_stock_in_acceleration(eps_list, sales_list, net_income_list, time_periods):
        return FilteredStocks.is_acceleration(eps_list, time_periods) and \
               FilteredStocks.is_acceleration(sales_list, time_periods) and \
               FilteredStocks.is_acceleration(net_income_list, time_periods)

    @staticmethod
    def get_lists_for_acceleration_check(stock, period_type):
        return FilteredStocks.get_eps_list(stock, period_type),\
               FilteredStocks.get_sales_list(stock, period_type),\
               FilteredStocks.get_net_income_list(stock, period_type)

    def calc_acceleration_stocks(self, time_periods, period_type):
        filtered_stocks = []
        for stock in self.stocks:
            eps_list, sales_list, net_income_list = FilteredStocks.get_lists_for_acceleration_check(stock, period_type)
            if FilteredStocks.is_stock_in_acceleration(eps_list, sales_list, net_income_list, time_periods):
                filtered_stocks.append(stock)
        self.stocks = filtered_stocks

    def filter_stocks_in_acceleration(self, time_periods, period_type):
        try:
            if time_periods:
                self.calc_acceleration_stocks(int(time_periods), period_type)
        except Exception as e:  # add check for NAN exception
            raise e

    def filter_acceleration_stocks_yearly(self):
        self.filter_stocks_in_acceleration(self.filters.get(ACCELERATION_YEARS, None), YEARLY)

    def filter_acceleration_stocks_quarterly(self):
        self.filter_stocks_in_acceleration(self.filters.get(ACCELERATION_QUARTERS, None), QUARTERLY)

    @staticmethod
    def is_stock_in_eps_growth(eps_list, threshold, time_periods):
        if not eps_list or len(eps_list) < time_periods:
            return False

        for period in range(time_periods * (-1), 0):
            if eps_list[period] < threshold:
                return False

        return True

    def calc_eps_growth_stocks(self, threshold, time_periods, period_type):
        filtered_stocks = []
        for stock in self.stocks:
            eps_list = FilteredStocks.get_eps_list(stock, period_type)
            if eps_list and FilteredStocks.is_stock_in_eps_growth(eps_list, threshold, time_periods):
                filtered_stocks.append(stock)
        self.stocks = filtered_stocks

    def filter_stocks_in_eps_growth(self, threshold, time_periods, period_type):
        try:
            if threshold and time_periods:
                self.calc_eps_growth_stocks(float(threshold), int(time_periods), period_type)
        except Exception as e:  # add check for NAN exception
            raise e

    def filter_eps_growth_stocks_yearly(self):
        self.filter_stocks_in_eps_growth(self.filters.get(EPS_GROWTH_THRESHOLD_Y, None),
                                         self.filters.get(EPS_GROWTH_YEARS, None),
                                         YEARLY)

    def filter_eps_growth_stocks_quarterly(self):
        self.filter_stocks_in_eps_growth(self.filters.get(EPS_GROWTH_THRESHOLD_Q, None),
                                         self.filters.get(EPS_GROWTH_QUARTERS, None),
                                         QUARTERLY)

    @staticmethod
    def get_multiplier(target_avg_sales_type):
        if target_avg_sales_type == 'B':
            return BILLION
        elif target_avg_sales_type == 'M':
            return MILLION
        else:
            return TRILLION

    @staticmethod
    def calculate_ps_metrics(stock):
        yahoo_stock = YahooFinancials(stock.symbol)
        market_cup = yahoo_stock.get_market_cap()
        if stock.target_avg_sales:
            multiplier = FilteredStocks.get_multiplier(stock.target_avg_sales[-1])
            target_avg_sales = float(stock.target_avg_sales[:-1]) * multiplier
            try:
                stock.price_to_sell_ratio = round(market_cup / target_avg_sales, 2)
                stock.ps_to_growth_ratio = round(stock.price_to_sell_ratio / float(stock.target_sales_growth[:-1]),2)
                ev = (yahoo_stock.get_key_statistics_data()[stock.symbol]["enterpriseValue"])
                stock.ev_to_sell_ratio = round(ev / target_avg_sales, 2)
                stock.gross_margins = round(yahoo_stock.get_gross_profit() / yahoo_stock.get_total_revenue() * 100,2)
                print(stock.gross_margins)
                print(stock.ev_to_sell_ratio)
                print(stock.ps_to_growth_ratio)
                print(stock.target_sales_growth)
            except Exception as e:
                print(str(e))

    def calculate_ps_for_stocks(self):
        maximum_threads = 200
        with concurrent.futures.ThreadPoolExecutor(max_workers=maximum_threads) as executor:
            executor.map(FilteredStocks.calculate_ps_metrics, self.stocks)

    def filter_by_symbol(self):
        stock_symbol = self.filters.get(STOCK_SYMBOL, None)
        self.stocks = Stock.objects.filter(symbol=stock_symbol)

    def filter_stocks(self):
        # add here more parameters to handle
        if STOCK_SYMBOL in self.filters:
            self.filter_by_symbol()
        else:
            for filter_key in self.filters:
                if filter_key == EPS_GROWTH_QUARTERS:
                    self.filter_eps_growth_stocks_quarterly()
                elif filter_key == EPS_GROWTH_YEARS:
                    self.filter_eps_growth_stocks_yearly()
                elif filter_key == ACCELERATION_QUARTERS:
                    self.filter_acceleration_stocks_quarterly()
                elif filter_key == ACCELERATION_YEARS:
                    self.filter_acceleration_stocks_yearly()
                elif filter_key == SALES_GROWTH_THRESHOLD:
                    self.filter_sales_growth()

        self.calculate_ps_for_stocks()

    def get_stocks(self):
        return self.stocks


def get_filtered_stocks(filters):
    filtered_stocks = FilteredStocks(filters)
    return filtered_stocks.get_stocks()
