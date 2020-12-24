from stocks_tracker.models import *


def create_new_stock_stat():
    stock_stat_obj = Stock_stat()
    stock_stat_obj.symbol = 'PYPL'
    try:
        stock_stat_obj.save
    except Execption as e:
        print(e)

def stock_stats_main():
    create_new_stock_stat()
