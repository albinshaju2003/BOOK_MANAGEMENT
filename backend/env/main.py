from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

books_db = []

class Book(BaseModel):
    id: int
    title: str
    author: str
    description: str

@app.post("/books")
async def add_book(book: Book):
    books_db.append(book)
    return {"message": "Book added successfully"}

@app.get("/books", response_model=List[Book])
async def get_books():
    return books_db

@app.put("/books/{book_id}")
async def update_book(book_id: int, book: Book):
    for i, b in enumerate(books_db):
        if b.id == book_id:
            books_db[i] = book
            return {"message": "Book updated successfully"}
    raise HTTPException(status_code=404, detail="Book not found")

@app.delete("/books/{book_id}")
async def delete_book(book_id: int):
    for i, b in enumerate(books_db):
        if b.id == book_id:
            del books_db[i]
            return {"message": "Book deleted successfully"}
    raise HTTPException(status_code=404, detail="Book not found")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["book_app"]
users_collection = db["users"]

@app.post("/register")
async def register(request: Request):
    data = await request.json()
    email = data.get("email")
    password = data.get("password")

    
    existing = await users_collection.find_one({"email": email})
    if existing:
        return {"message": "User already exists"}

    await users_collection.insert_one({"email": email, "password": password})
    return {"message": "Registration successful!"}

@app.post("/login")
async def login(request: Request):
    data = await request.json()
    email = data.get("email")
    password = data.get("password")

    user = await users_collection.find_one({"email": email})
    if user and user["password"] == password:
        return {"message": "Login successful!"}
    else:
        return {"message": "Invalid credentials"}
