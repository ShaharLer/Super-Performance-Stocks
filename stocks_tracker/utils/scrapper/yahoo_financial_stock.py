import requests
from bs4 import BeautifulSoup
import re

YAHOO_URL = 'https://finance.yahoo.com/quote/{}/analysis?p={}'

class YahooFinancialStock:

    def __init__(self, stock_name):
        self.stock_name = stock_name
        self.soup = self.get_html_financial_data()
        self.fill_values()

    def get_html_financial_data(self):
        url = YAHOO_URL.format(self.stock_name,self.stock_name)
        page = requests.get(url)
        return BeautifulSoup(page.content, 'html.parser')

    def fill_values(self):
        # Yahoo doesnt have for all stocks the updated Analysis. current year may be 2020 in some cases.
        current_year_span =  str(self.soup.find('th', attrs={"data-reactid": "103"}).contents[0])
        self.current_year = re.search('\(([^)]+)', current_year_span).group(1)
        print(self.current_year)
        
        if (self.current_year == '2021'):
            self.target_avg_sales = self.soup.find('span', attrs={"data-reactid": "131"}).contents[0]
            self.target_avg_eps = self.soup.find('span', attrs={"data-reactid": "85"}).contents[0]
            self.target_sales_growth = self.soup.find('span', attrs={"data-reactid": "175"}).contents[0]
        else:
            self.target_avg_sales = self.soup.find('span', attrs={"data-reactid": "133"}).contents[0]
            self.target_avg_eps = self.soup.find('span', attrs={"data-reactid": "272"}).contents[0]
            self.target_sales_growth = self.soup.find('span', attrs={"data-reactid": "177"}).contents[0]
        
        print(self.target_sales_growth)
