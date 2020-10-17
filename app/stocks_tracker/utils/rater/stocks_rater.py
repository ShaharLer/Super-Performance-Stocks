import datetime

from app.stocks_tracker import Stock

QUARTERS_TO_FOLLOW_GROWTH = 3
QUARTERS_TO_FOLLOW_ACCELERATION = 2
EPS_GROWTH_THRESHOLD = 35


def is_stock_in_eps_growth(eps_list):
    if not eps_list or len(eps_list) < QUARTERS_TO_FOLLOW_GROWTH:
        return False

    for quarter in range(QUARTERS_TO_FOLLOW_GROWTH * (-1), 0):
        if eps_list[quarter] < EPS_GROWTH_THRESHOLD:
            return False

    return True


def is_accelerating(data_list):
    if not data_list or len(data_list) < QUARTERS_TO_FOLLOW_ACCELERATION:
        return False

    for quarter in range(QUARTERS_TO_FOLLOW_ACCELERATION * (-1), 0):
        if data_list[quarter] <= 0 or (quarter < -1 and data_list[quarter] >= data_list[quarter + 1]):
            return False

    return True


def is_stock_in_acceleration(stock):
    return is_accelerating(stock.net_income_growth) \
           and is_accelerating(stock.eps_growth) \
           and is_accelerating(stock.sales_growth)


def stocks_rater_main():
    stocks = Stock.objects.all()
    for stock in stocks:
        try:
            stock.is_accelerated = True if is_stock_in_acceleration(stock) else False
            stock.is_eps_growth = True if is_stock_in_eps_growth(stock.eps_growth) else False
            stock.last_rater_update = datetime.date.today()
            stock.save()
        except:
            pass


if __name__ == "__main__":
    stocks_rater_main()
