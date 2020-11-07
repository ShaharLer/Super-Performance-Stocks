from background_task import background
from stocks_tracker.models import Stock


@background()
def set_pivot(symbol, pivot):
    print(f'Started set_pivot function')
    stock = Stock.objects.get(symbol=symbol)
    if not stock:
        print(f'Finished: did not find stock with symbol {symbol}')
        return

    stock.pivot = pivot
    stock.save()
    print(f'Finished: updated stock {stock.symbol} with pivot {stock.pivot}')
