from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="FastAPI Day 5", description="Shopping Cart System")

# --- MOCK DATABASES ---
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
]

cart = []
orders = []

# --- PYDANTIC MODELS ---
class CheckoutRequest(BaseModel):
    customer_name: str
    delivery_address: str

# --- HELPER FUNCTION ---
def find_product(product_id: int):
    return next((p for p in products if p["id"] == product_id), None)

# ---  ADD TO CART ---
@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int):
    product = find_product(product_id)
    
    #  Handle Not Found
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    #  Handle Out of Stock
    if not product["in_stock"]:
        raise HTTPException(status_code=400, detail=f"{product['name']} is out of stock")
        
    #  Handle Existing Item (Update Quantity)
    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            item["subtotal"] = item["quantity"] * product["price"]
            return {"message": "Cart updated", "cart_item": item}
            
    #  Add New Item
    new_item = {
        "product_id": product["id"],
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "subtotal": quantity * product["price"]
    }
    cart.append(new_item)
    return {"message": "Added to cart", "cart_item": new_item}

# --- VIEW CART ---
@app.get("/cart")
def view_cart():
    # Bonus: Empty cart check
    if not cart:
        return {"message": "Cart is empty"}
        
    grand_total = sum(item["subtotal"] for item in cart)
    
    return {
        "items": cart,
        "item_count": len(cart),
        "grand_total": grand_total
    }

# --- REMOVE ITEM FROM CART ---
@app.delete("/cart/{product_id}")
def remove_from_cart(product_id: int):
    global cart
    item_to_remove = next((item for item in cart if item["product_id"] == product_id), None)
    
    if not item_to_remove:
        raise HTTPException(status_code=404, detail="Item not found in cart")
        
    cart.remove(item_to_remove)
    return {"message": f"Product {product_id} removed from cart"}

# --- CHECKOUT ---
@app.post("/cart/checkout")
def checkout(request: CheckoutRequest):
    # Bonus: Prevent checkout on empty cart
    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty — add items first")
        
    grand_total = sum(item["subtotal"] for item in cart)
    new_orders = []
    
    # Create an order for each item in the cart
    for item in cart:
        order = {
            "order_id": len(orders) + 1,
            "customer_name": request.customer_name,
            "delivery_address": request.delivery_address,
            "product": item["product_name"],
            "quantity": item["quantity"],
            "total_price": item["subtotal"]
        }
        orders.append(order)
        new_orders.append(order)
        
    # Clear the cart after successful checkout
    cart.clear()
    
    return {
        "message": "Checkout successful",
        "grand_total": grand_total,
        "orders_placed": new_orders
    }

# --- VIEW ORDERS ---
@app.get("/orders")
def view_orders():
    return {
        "orders": orders,
        "total_orders": len(orders)
    }