from stocks_tracker.models import *
from yahoofinancials import YahooFinancials
import datetime
from django.db.models import Q

def create_new_stock_stat(symbol,pivot_price,date):
    stock_stat_obj = Stock_stat()
    try:
        stock_stat_obj.enter_price = pivot_price * 1.005
        stock_stat_obj.success_rate_20_8 = 0
        stock_stat_obj.success_rate_18_7 = 0
        stock_stat_obj.success_rate_15_6 = 0
        stock_stat_obj.success_rate_10_4 = 0
        stock_stat_obj.yahoo_date_format = date
        stock_stat_obj.symbol = symbol
        stock_stat_obj.save()

    except Exception as e:
        print(e)


def does_target_achived(gain_target, loss_target, price_low, price_high):

    if (price_low <= loss_target):
        return -1

    if (gain_target <= price_high):
        return 1

    return 0

def fill_stats(stock_stat_obj):

    yahoo_stock_obj = YahooFinancials(stock_stat_obj.symbol)
    json = (yahoo_stock_obj.get_historical_price_data(stock_stat_obj.yahoo_date_format, str(datetime.date.today()), 'daily'))
    twenty_percent_gain = stock_stat_obj.enter_price * 1.2
    eigtheen_percent_gain = stock_stat_obj.enter_price * 1.18
    fifteen_percent_gain = stock_stat_obj.enter_price * 1.15
    ten_percent_gain = stock_stat_obj.enter_price * 1.1
    eight_percent_loss = stock_stat_obj.enter_price * 0.92
    seven_percent_loss = stock_stat_obj.enter_price * 0.93
    six_percent_loss = stock_stat_obj.enter_price * 0.94
    four_percent_loss = stock_stat_obj.enter_price * 0.96

    for row in json[stock_stat_obj.symbol]["prices"]:

        price_high = row['high']
        price_low = row['low']
        stock_stat_obj.success_rate_20_8 = stock_stat_obj.success_rate_20_8 if stock_stat_obj.success_rate_20_8 != 0 else does_target_achived(twenty_percent_gain, eight_percent_loss,price_low,price_high)
        stock_stat_obj.success_rate_18_7 = stock_stat_obj.success_rate_18_7 if stock_stat_obj.success_rate_18_7 != 0 else does_target_achived(eigtheen_percent_gain, seven_percent_loss,price_low,price_high)
        stock_stat_obj.success_rate_15_6 = stock_stat_obj.success_rate_15_6 if stock_stat_obj.success_rate_15_6 != 0 else does_target_achived(fifteen_percent_gain, six_percent_loss,price_low,price_high)
        stock_stat_obj.success_rate_10_4 = stock_stat_obj.success_rate_10_4 if stock_stat_obj.success_rate_10_4 != 0 else does_target_achived(ten_percent_gain, four_percent_loss,price_low,price_high)
        stock_stat_obj.save()

def fill_all_stock_stats_objects():
    queryset = Stock_stat.objects.all()
    for stock in queryset:
        print(stock.yahoo_date_format)
        if (stock):
            try:
                fill_stats(stock)
            except Exception as e:
                print(e)


def get_summary_data(date):

    twenty_percent_gain = Stock_stat.objects.filter(Q(yahoo_date_format=date) & (Q(success_rate_20_8 = 1)))
    eigtheen_percent_gain = Stock_stat.objects.filter(Q(yahoo_date_format=date) & (Q(success_rate_18_7 = 1)))
    fifteen_percent_gain = Stock_stat.objects.filter(Q(yahoo_date_format=date) & (Q(success_rate_15_6 = 1)))
    ten_percent_gain = Stock_stat.objects.filter(Q(yahoo_date_format=date) & (Q(success_rate_10_4 = 1)))
    eight_percent_loss = Stock_stat.objects.filter(Q(yahoo_date_format=date) & (Q(success_rate_20_8 = -1)))
    seven_percent_loss = Stock_stat.objects.filter(Q(yahoo_date_format=date) & (Q(success_rate_18_7 = -1)))
    six_percent_loss = Stock_stat.objects.filter(Q(yahoo_date_format=date) & (Q(success_rate_15_6 = -1)))
    four_percent_loss = Stock_stat.objects.filter(Q(yahoo_date_format=date) & (Q(success_rate_10_4 = -1)))

    print(ten_percent_gain)
    for stock in eight_percent_loss:
        print(stock.symbol)

def stock_stats_main():
    queryset = Stock.objects.filter(is_technically_valid=True)
    for stock in queryset :
       if stock.pivot != 0 :
           create_new_stock_stat(stock.symbol,stock.pivot,'2020-12-15')

    get_summary_data('2020-12-15')
    #fill_all_stock_stats_objects()
