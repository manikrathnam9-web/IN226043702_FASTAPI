# FastAPI Product Management API - Assignment 1

## Overview

This is Assignment 1 from Innomatics Research Labs, implementing a Product Management API using FastAPI. The API provides various endpoints for managing and querying a product catalog for an e-commerce store.

## Features

- **Product Catalog**: Maintains a list of products with details like ID, name, price, category, and stock status
- **Category Filtering**: Filter products by specific categories
- **Stock Management**: View only in-stock products
- **Store Summary**: Get an overview of the store's inventory
- **Product Search**: Search products by name keywords
- **Price Analysis**: Find the cheapest and most expensive products

## Installation

1. **Clone or download** this repository to your local machine.

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   
   Or install manually:
   ```bash
   pip install fastapi uvicorn
   ```

## Usage

### Running the Application

Start the FastAPI server using uvicorn:

```bash
uvicorn main:app --reload
```

The API will be available at: `http://127.0.0.1:8000`

### API Documentation

Once the server is running, you can access the interactive API documentation at:
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

## API Endpoints

### 1. Get All Products
- **Endpoint**: `GET /products`
- **Description**: Returns all products and the total count
- **Response**:
  ```json
  {
    "products": [...],
    "total": 7
  }
  ```

### 2. Get Products by Category
- **Endpoint**: `GET /products/category/{category_name}`
- **Description**: Filters products by category name (case-insensitive)
- **Parameters**: `category_name` (string)
- **Example**: `GET /products/category/electronics`

### 3. Get In-Stock Products
- **Endpoint**: `GET /products/instock`
- **Description**: Returns only products that are currently in stock
- **Response**:
  ```json
  {
    "in_stock_products": [...],
    "count": 5
  }
  ```

### 4. Store Summary
- **Endpoint**: `GET /store/summary`
- **Description**: Provides a high-level overview of the store inventory
- **Response**:
  ```json
  {
    "store_name": "My E-commerce Store",
    "total_products": 7,
    "in_stock": 5,
    "out_of_stock": 2,
    "categories": ["Electronics", "Stationery", "Accessories"]
  }
  ```

### 5. Search Products
- **Endpoint**: `GET /products/search/{keyword}`
- **Description**: Searches for products where the keyword is part of the name (case-insensitive)
- **Parameters**: `keyword` (string)
- **Example**: `GET /products/search/mouse`

### 6. Get Deals
- **Endpoint**: `GET /products/deals`
- **Description**: Finds the cheapest and most expensive products
- **Response**:
  ```json
  {
    "best_deal": {...},
    "premium_pick": {...}
  }
  ```

## Sample Data

The API comes pre-loaded with 7 sample products across different categories:

1. Wireless Mouse - Electronics (₹599)
2. Notebook - Stationery (₹150)
3. Water Bottle - Accessories (₹350)
4. Backpack - Accessories (₹1200)
5. Laptop Stand - Electronics (₹1299)
6. Mechanical Keyboard - Electronics (₹2499)
7. Webcam - Electronics (₹1899)

## Technologies Used

- **FastAPI**: Modern, fast web framework for building APIs with Python
- **Python**: Programming language
- **Uvicorn**: ASGI server for running FastAPI applications

## Learning Objectives

This assignment demonstrates:
- Building REST APIs with FastAPI
- Implementing CRUD operations
- Data filtering and searching
- API documentation with automatic OpenAPI/Swagger generation
- Python list comprehensions and data manipulation

## Author

[Your Name]
Innomatics Research Labs - Assignment 1

## License

This project is for educational purposes as part of Innomatics Research Labs curriculum.