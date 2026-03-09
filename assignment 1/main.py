from fastapi import FastAPI

app = FastAPI(title="FastAPI Day 1 Assignment", description="Product Management API")

# Product List
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 599, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 150, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "Water Bottle", "price": 350, "category": "Accessories", "in_stock": False},
    {"id": 4, "name": "Backpack", "price": 1200, "category": "Accessories", "in_stock": True},
    {"id": 5, "name": "Laptop Stand", "price": 1299, "category": "Electronics", "in_stock": True},
    {"id": 6, "name": "Mechanical Keyboard", "price": 2499, "category": "Electronics", "in_stock": True},
    {"id": 7, "name": "Webcam", "price": 1899, "category": "Electronics", "in_stock": False},
]

@app.get("/products")
def get_all_products():
    """Returns all products and the total count."""
    return {"products": products, "total": len(products)}

# Category 
@app.get("/products/category/{category_name}")
def get_by_category(category_name: str):
    """Filters products by category name (exact match)."""
    result = [p for p in products if p["category"].lower() == category_name.lower()]
    if not result:
        return {"error": "No products found in this category"}
    return {"category": category_name, "products": result, "total": len(result)}

# In-Stock
@app.get("/products/instock")
def get_instock():
    """Returns only products that are currently in stock."""
    available = [p for p in products if p["in_stock"]]
    return {"in_stock_products": available, "count": len(available)}

# Store Summary
@app.get("/store/summary")
def store_summary():
    """Provides a high-level overview of the store inventory."""
    in_stock_count = len([p for p in products if p["in_stock"]])
    out_stock_count = len(products) - in_stock_count
    unique_categories = list(set([p["category"] for p in products]))
    
    return {
        "store_name": "My E-commerce Store",
        "total_products": len(products),
        "in_stock": in_stock_count,
        "out_of_stock": out_stock_count,
        "categories": unique_categories,
    }

# Search
@app.get("/products/search/{keyword}")
def search_products(keyword: str):
    """Searches for products where the keyword is part of the name."""
    results = [
        p for p in products 
        if keyword.lower() in p["name"].lower()
    ]
    if not results:
        return {"message": "No products matched your search"}
    return {"keyword": keyword, "results": results, "total_matches": len(results)}

# Cheapest & Most Expensive 
@app.get("/products/deals")
def get_deals():
    """Finds the 'Best Deal' and 'Premium Pick' based on price."""
    if not products:
        return {"error": "No products available"}
        
    cheapest = min(products, key=lambda p: p["price"])
    expensive = max(products, key=lambda p: p["price"])
    
    return {
        "best_deal": cheapest,
        "premium_pick": expensive,
    }