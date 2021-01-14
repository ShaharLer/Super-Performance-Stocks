import requests
from bs4 import BeautifulSoup

MARKETWATCH_URL_Q = 'https://www.marketwatch.com/investing/stock/{}/financials/income/quarter'
MARKETWATCH_URL_Y = 'https://www.marketwatch.com/investing/stock/{}/financials/income'

EPS_GROWTH_TEXTS = 'EPS (Basic) Growth'
NET_INCOME_GROWTH_TEXTS = 'Net Income Growth'
SALES_GROWTH_TEXTS = 'Sales Growth'
QUARTERS_NUMBER = 4
NO_DATA = '-'
ZERO_VALUE = '0%'


class MarketwatchFinancialStock:

    def __init__(self, stock_name,duration):
        self.duration = duration
        self.stock_name = stock_name
        self.soup = self.get_html_financial_data()
        self.__eps_growth_array = []
        self.__net_income_growth_array = []
        self.__sales_growth_array = []
        self.fill_values()

    def get_html_financial_data(self):
        if (self.duration == 'q'):
            url = MARKETWATCH_URL_Q.format(self.stock_name)
        else:
            url = MARKETWATCH_URL_Y.format(self.stock_name)
        page = requests.get(url)
        return BeautifulSoup(page.content, 'html.parser')

    @staticmethod
    def get_growth_array(row):
        array_of_values = []
        next_tag = row
        for _ in range(QUARTERS_NUMBER + 1):
            new_tag = next_tag.find_next('td')
            array_of_values.append(ZERO_VALUE if new_tag.text == NO_DATA else new_tag.text)
            next_tag = new_tag
        return array_of_values

    def fill_values(self):
        soup_results_array = self.soup.findAll('tr', {'class': 'table__row'})
        for soup_result in soup_results_array:
            for row in soup_result.findAll('td'):
                if row.text.find(EPS_GROWTH_TEXTS) >= 0:
                    self.__eps_growth_array = MarketwatchFinancialStock.get_growth_array(row)
                elif row.text.find(NET_INCOME_GROWTH_TEXTS) >= 0:
                    self.__net_income_growth_array = MarketwatchFinancialStock.get_growth_array(row)
                elif row.text.find(SALES_GROWTH_TEXTS) >= 0:
                    self.__sales_growth_array = MarketwatchFinancialStock.get_growth_array(row)

    def get_eps_growth_array(self):
        return self.__eps_growth_array

    def get_net_income_growth_array(self):
        return self.__net_income_growth_array

    def get_sales_growth_array(self):
        return self.__sales_growth_array
