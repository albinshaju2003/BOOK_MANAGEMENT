from bson import ObjectId
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from typing import List
from fastapi.encoders import jsonable_encoder
from fastapi import Body
from bson import ObjectId


app = FastAPI()

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
books_collection = db["books"]

class Book(BaseModel):
    title: str
    author: str
    description: str
    email: str

@app.post("/register")
async def register(request: Request):
    data = await request.json()
    email = data.get("email")
    password = data.get("password")
    if await users_collection.find_one({"email": email}):
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
        return {"message": "Login successful!", "email": email}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/books")
async def add_book(request: Request):
    book = await request.json()
    await books_collection.insert_one(book)
    return {"message": "Book added successfully"}

@app.get("/books/{email}")
async def get_books(email: str):
    books = await books_collection.find({"email": email}).to_list(1000)
    for book in books:
        book["_id"] = str(book["_id"])  
    return books

@app.delete("/books/{book_id}")
async def delete_book(book_id: str):
    result = await books_collection.delete_one({"_id": ObjectId(book_id)})
    if result.deleted_count == 1:
        return {"message": "Book deleted successfully"}
    raise HTTPException(status_code=404, detail="Book not found")

@app.put("/books/{book_id}")
async def update_book(book_id: str, request: Request):
    data = await request.json()
    result = await books_collection.update_one(
        {"_id": ObjectId(book_id), "email": data["email"]},
        {"$set": {
            "title": data["title"],
            "author": data["author"],
            "description": data["description"]
        }}
    )
    if result.modified_count == 1:
        return {"message": "Book updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Book not found or not updated")