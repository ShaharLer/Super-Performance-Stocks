import time
import yfinance as yf
from stocks_tracker.models import Stock
from background_task import background


def update_stock_extra_data():
    start = time.time()
    all_stocks = Stock.objects.all()
    for stock in all_stocks:
        try:
            yf_object = yf.Ticker(stock.symbol)
            stock.sector = yf_object.info['sector']
            stock.industry = yf_object.info['industry']
            print(f'{stock.symbol}, sector: {stock.sector}, industry: {stock.industry}')
            stock.save()
        except Exception as e:
            print(f'Failed to find sector and industry for stock {stock.symbol}: {str(e)}')
    end = time.time()
    print(f'Running all threads took {round(end - start, 2)} seconds')


@background()
def update_sector_and_industry():
    print(f'Started update_sector_and_industry')
    update_stock_extra_data()
    print(f'Finished update_sector_and_industry')
