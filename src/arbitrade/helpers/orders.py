from ibapi.order import Order

def create_market_order(size):
    order = Order()
    order.action = "BUY" if size > 0 else "SELL"
    order.orderType = "MKT"
    order.totalQuantity = abs(size)
    return order