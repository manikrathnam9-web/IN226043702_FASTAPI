from fastapi import FastAPI, HTTPException, Query, Path, status
from pydantic import BaseModel, Field
from typing import Optional, List
import math

app = FastAPI(title="City Public Library API")

# ==========================================
# DAY 1: DATA SETUP
# ==========================================
books = [
    {"id": 1, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "genre": "Fiction", "is_available": True},
    {"id": 2, "title": "A Brief History of Time", "author": "Stephen Hawking", "genre": "Science", "is_available": True},
    {"id": 3, "title": "Sapiens", "author": "Yuval Noah Harari", "genre": "History", "is_available": False},
    {"id": 4, "title": "Clean Code", "author": "Robert C. Martin", "genre": "Tech", "is_available": True},
    {"id": 5, "title": "1984", "author": "George Orwell", "genre": "Fiction", "is_available": True},
    {"id": 6, "title": "The Pragmatic Programmer", "author": "Andrew Hunt", "genre": "Tech", "is_available": True}
]

borrow_records = []
record_counter = 1

queue = []

# ==========================================
# DAY 2: PYDANTIC MODELS 
# ==========================================
class BorrowRequest(BaseModel):
    member_name: str = Field(..., min_length=2)
    book_id: int = Field(..., gt=0)
    # Using le=60 to accommodate premium members (Q9) while enforcing standard limits in logic
    borrow_days: int = Field(..., gt=0, le=60)
    member_id: str = Field(..., min_length=4)
    member_type: str = "regular"

class NewBook(BaseModel):
    title: str = Field(..., min_length=2)
    author: str = Field(..., min_length=2)
    genre: str = Field(..., min_length=2)
    is_available: bool = True

# ==========================================
# DAY 3: HELPER FUNCTIONS 
# ==========================================
# (These are plain Python functions, no @app decorators)
def find_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book
    return None

def calculate_due_date(borrow_days: int, member_type: str = "regular"):
    if member_type.lower() == "premium":
        allowed_days = min(borrow_days, 60)
    else:
        allowed_days = min(borrow_days, 30)
    # Using 15 as a generic base day for simplicity as requested
    return f"Return by: Day {15 + allowed_days}"

def filter_books_logic(genre: Optional[str], author: Optional[str], is_available: Optional[bool]):
    filtered = books
    if genre is not None:
        filtered = [b for b in filtered if b["genre"].lower() == genre.lower()]
    if author is not None:
        filtered = [b for b in filtered if author.lower() in b["author"].lower()]
    if is_available is not None:
        filtered = [b for b in filtered if b["is_available"] == is_available]
    return filtered

# ==========================================
# STATIC ROUTES (Must go before variable routes)
# ==========================================

#  Beginner - Home Route
@app.get("/")
def home():
    return {"message": "Welcome to City Public Library"}

#  Beginner - Summary
@app.get("/books/summary")
def get_books_summary():
    available = sum(1 for b in books if b["is_available"])
    borrowed = len(books) - available
    
    genres = {}
    for b in books:
        genres[b["genre"]] = genres.get(b["genre"], 0) + 1
        
    return {
        "total_books": len(books),
        "available_count": available,
        "borrowed_count": borrowed,
        "genre_breakdown": genres
    }

#  Easy - Filter
@app.get("/books/filter")
def filter_books(genre: Optional[str] = None, author: Optional[str] = None, is_available: Optional[bool] = None):
    results = filter_books_logic(genre, author, is_available)
    return {"total_found": len(results), "books": results}

#  Hard - Search
@app.get("/books/search")
def search_books(keyword: str = Query(..., min_length=1)):
    keyword = keyword.lower()
    results = [
        b for b in books 
        if keyword in b["title"].lower() or keyword in b["author"].lower()
    ]
    if not results:
        return {"message": f"No books found matching '{keyword}'."}
    return {"total_found": len(results), "results": results}

#  Hard - Sort
@app.get("/books/sort")
def sort_books(sort_by: str = "title", order: str = "asc"):
    valid_sorts = ["title", "author", "genre"]
    if sort_by not in valid_sorts:
        raise HTTPException(status_code=400, detail=f"sort_by must be one of {valid_sorts}")
    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="order must be 'asc' or 'desc'")
        
    reverse_sort = order == "desc"
    sorted_books = sorted(books, key=lambda x: x[sort_by].lower(), reverse=reverse_sort)
    return {
        "sort_by": sort_by,
        "order": order,
        "books": sorted_books
    }

# Hard - Pagination
@app.get("/books/page")
def paginate_books(page: int = Query(1, ge=1), limit: int = Query(3, ge=1, le=10)):
    total = len(books)
    total_pages = math.ceil(total / limit)
    start = (page - 1) * limit
    sliced_books = books[start : start + limit]
    
    return {
        "total": total,
        "total_pages": total_pages,
        "current_page": page,
        "limit": limit,
        "books": sliced_books
    }

#  Hard - Browse (Combine Filter, Sort, Paginate)
@app.get("/books/browse")
def browse_books(
    keyword: Optional[str] = None,
    sort_by: str = "title",
    order: str = "asc",
    page: int = Query(1, ge=1),
    limit: int = Query(3, ge=1, le=10)
):
    # 1. Filter
    current_list = books
    if keyword:
        kw = keyword.lower()
        current_list = [b for b in current_list if kw in b["title"].lower() or kw in b["author"].lower()]
        
    # 2. Sort
    valid_sorts = ["title", "author", "genre"]
    if sort_by not in valid_sorts:
        raise HTTPException(status_code=400, detail=f"sort_by must be one of {valid_sorts}")
    reverse_sort = order == "desc"
    current_list = sorted(current_list, key=lambda x: str(x[sort_by]).lower(), reverse=reverse_sort)
    
    # 3. Paginate
    total = len(current_list)
    total_pages = math.ceil(total / limit) if total > 0 else 1
    start = (page - 1) * limit
    sliced = current_list[start : start + limit]
    
    return {
        "keyword_used": keyword,
        "sort_settings": {"sort_by": sort_by, "order": order},
        "pagination": {"total_items": total, "total_pages": total_pages, "current_page": page, "limit": limit},
        "results": sliced
    }

#  Beginner - Get All Books
@app.get("/books")
def get_all_books():
    available = sum(1 for b in books if b["is_available"])
    return {"total": len(books), "available_count": available, "books": books}

#  Medium - Create New Book
@app.post("/books", status_code=status.HTTP_201_CREATED)
def add_new_book(book: NewBook):
    # Reject duplicate titles (case-insensitive)
    for b in books:
        if b["title"].lower() == book.title.lower():
            raise HTTPException(status_code=400, detail="A book with this title already exists")
            
    new_id = max(b["id"] for b in books) + 1 if books else 1
    new_book_dict = {
        "id": new_id,
        "title": book.title,
        "author": book.author,
        "genre": book.genre,
        "is_available": book.is_available
    }
    books.append(new_book_dict)
    return {"message": "Book added successfully", "book": new_book_dict}

# ==========================================
# BORROW RECORDS & QUEUE STATIC ROUTES
# ==========================================

#  Hard - Borrow Records Search
@app.get("/borrow-records/search")
def search_borrow_records(member_name: str = Query(...)):
    name = member_name.lower()
    results = [r for r in borrow_records if name in r["member_name"].lower()]
    return {"total_found": len(results), "records": results}

#  Hard - Borrow Records Pagination
@app.get("/borrow-records/page")
def paginate_borrow_records(page: int = Query(1, ge=1), limit: int = Query(5, ge=1)):
    total = len(borrow_records)
    total_pages = math.ceil(total / limit)
    start = (page - 1) * limit
    return {
        "total": total,
        "total_pages": total_pages,
        "current_page": page,
        "records": borrow_records[start : start + limit]
    }

# Beginner - Get All Borrow Records
@app.get("/borrow-records")
def get_all_borrow_records():
    return {"total": len(borrow_records), "records": borrow_records}

#  Easy - Post Borrow Record
@app.post("/borrow")
def borrow_book(req: BorrowRequest):
    global record_counter
    book = find_book(req.book_id)
    
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if not book["is_available"]:
        raise HTTPException(status_code=400, detail="Book is currently unavailable")
        
    book["is_available"] = False
    due_date_msg = calculate_due_date(req.borrow_days, req.member_type)
    
    record = {
        "record_id": record_counter,
        "member_id": req.member_id,
        "member_name": req.member_name,
        "member_type": req.member_type,
        "book_id": req.book_id,
        "book_title": book["title"],
        "due_date": due_date_msg
    }
    borrow_records.append(record)
    record_counter += 1
    
    return {"message": "Borrow successful", "record": record}

#  Medium - Get Queue
@app.get("/queue")
def get_queue():
    return {"total_waiting": len(queue), "waitlist": queue}

#  Medium - Add to Queue
@app.post("/queue/add")
def add_to_queue(member_name: str, book_id: int):
    book = find_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if book["is_available"]:
        raise HTTPException(status_code=400, detail="Book is currently available, you can borrow it directly.")
        
    queue_item = {"member_name": member_name, "book_id": book_id}
    queue.append(queue_item)
    return {"message": f"{member_name} added to waitlist for '{book['title']}'", "queue_position": len(queue)}


# ==========================================
# VARIABLE ROUTES (MUST BE AT THE BOTTOM)
# ==========================================

#  Beginner - Get Book by ID
@app.get("/books/{book_id}")
def get_book_by_id(book_id: int):
    book = find_book(book_id)
    if not book:
        return {"error": "Book not found"}  # Returning standard dict as requested in Q3
    return book

#  Medium - Update Book
@app.put("/books/{book_id}")
def update_book(book_id: int, genre: Optional[str] = None, is_available: Optional[bool] = None):
    book = find_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
        
    if genre is not None:
        book["genre"] = genre
    if is_available is not None:
        book["is_available"] = is_available
        
    return {"message": "Book updated successfully", "book": book}

#  Medium - Delete Book
@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    book = find_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
        
    books.remove(book)
    return {"message": f"Successfully deleted '{book['title']}'"}

# Medium - Return Book Workflow
@app.post("/return/{book_id}")
def return_book(book_id: int):
    global record_counter
    book = find_book(book_id)
    
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
        
    book["is_available"] = True
    
    # Check the queue to auto-assign
    for i, q_item in enumerate(queue):
        if q_item["book_id"] == book_id:
            next_member = q_item["member_name"]
            queue.pop(i) # Remove from queue
            
            # Automatically assign book to the person waiting
            book["is_available"] = False 
            auto_record = {
                "record_id": record_counter,
                "member_id": "QUEUE-AUTO",
                "member_name": next_member,
                "member_type": "regular",
                "book_id": book_id,
                "book_title": book["title"],
                "due_date": calculate_due_date(14, "regular") # Generic 14 day assignment
            }
            borrow_records.append(auto_record)
            record_counter += 1
            
            return {
                "message": "returned and re-assigned", 
                "assigned_to": next_member, 
                "record": auto_record
            }

    return {"message": "returned and available", "book": book}