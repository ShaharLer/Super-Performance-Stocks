import requests
from bs4 import BeautifulSoup


class marketwatch_stock_financials_class:

    def __init__(self, stock_name):
        self.stock_name = stock_name
        self.soup = self.get_html_financial_data()
        number_of_quarters = 4
        self.fill_values(number_of_quarters)

    def get_html_financial_data(self):
        URL = 'https://www.marketwatch.com/investing/stock/' + self.stock_name + '/financials/balance-/quarter'
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, 'html.parser')
        return soup

    def get_growth_array(self, row, number_of_quarters):

        array_of_values = []
        next_tag = row
        x = 0
        for x in range(number_of_quarters + 1):
            new_tag = next_tag.find_next("td")
            value_to_insert_to_array = new_tag.text
            if (value_to_insert_to_array == '-'):
                value_to_insert_to_array = '0%'
            array_of_values.append(value_to_insert_to_array)
            next_tag = new_tag

        return array_of_values

    def fill_values(self, number_of_quarters):

        soup_results_array = self.soup.findAll("tr", {"class": "childRow hidden"})
        for soup_result in soup_results_array:

            for row in soup_result.findAll("td"):

                if (row.text == "EPS (Basic) Growth") or (row.text == "EPS (Basic) - Growth"):
                    self.__q_eps_growth_array = self.get_growth_array(row, number_of_quarters)

                elif (row.text == "Net Income Growth"):
                    self.__q_net_income_growth_array = self.get_growth_array(row, number_of_quarters)

                elif (row.text == "Sales Growth"):
                    self.__q_sales_growth_array = self.get_growth_array(row, number_of_quarters)

    def get_q_eps_growth_array(self):
        return self.__q_eps_growth_array

    def get_q_net_income_growth_array(self):
        return self.__q_net_income_growth_array

    def get_q_sales_growth_array(self):
        return self.__q_sales_growth_array