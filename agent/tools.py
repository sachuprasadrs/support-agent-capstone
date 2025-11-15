import time
from typing import Dict, Any

PRODUCTS = {
    "P001": {"name": "RoadRunner Running Shoes", "stock": 12},
    "P002": {"name": "TrailBlaze Boots", "stock": 0}
}

ORDERS = {
    "A123": {"order_id": "A123", "user_id": "u001", "status": "Out for Delivery", "product_id": "P001"},
    "B456": {"order_id": "B456", "user_id": "u002", "status": "Delivered", "product_id": "P002"},
}


def get_order(order_id: str) -> Dict[str, Any]:
    time.sleep(0.1)
    return ORDERS.get(order_id, {"error": "not_found", "order_id": order_id})


def get_product(product_id: str) -> Dict[str, Any]:
    time.sleep(0.1)
    return PRODUCTS.get(product_id, {"error": "not_found", "product_id": product_id})


def create_ticket(user_id: str, summary: str, priority: str = "normal") -> Dict[str, Any]:
    time.sleep(0.1)
    ticket_id = f"T{int(time.time())}"
    return {"ticket_id": ticket_id, "user_id": user_id, "summary": summary, "status": "open"}


def send_email(user_email: str, subject: str, body: str):
    print(f"[MOCK EMAIL] to={user_email}, subject={subject}")
    return {"status": "sent"}
