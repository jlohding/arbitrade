from ibapi.order import Order

def market_order_factory():
    orderid = [0]
    def create_market_order(size):
        order = Order()
        order.orderId = orderid[0]
        orderid[0] += 1
        order.action = "BUY" if size > 0 else "SELL"
        order.orderType = "MKT"
        order.totalQuantity = abs(size)
        return order
    return create_market_order