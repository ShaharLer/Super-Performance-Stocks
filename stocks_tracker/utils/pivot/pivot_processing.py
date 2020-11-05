from stocks_tracker.models import Stock


def get_stock(symbol):
    stock = None if len(Stock.objects.filter(symbol=symbol)) == 0 else Stock.objects.get(symbol=symbol)
    return stock


def update_stock_in_db(stock_symbol, stock_pivot):
    stock_to_update = get_stock(stock_symbol)
    if stock_to_update is None:
        return None

    stock_to_update.pivot = stock_pivot
    stock_to_update.save()
    return stock_to_update


def remove_technical_attribute(symbol):
    stock = get_stock(symbol)
    if stock is None:
        return None

    stock.is_technically_valid = False
    stock.pivot = None
    stock.save()
    return stock
