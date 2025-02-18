import datetime
import os
from typing import Optional, List
from fastapi import FastAPI, HTTPException, status, Form
from motor import motor_asyncio
from dotenv import load_dotenv
from pydantic import BaseModel, constr, EmailStr, field_validator, Field
from bson import ObjectId


app = FastAPI()
load_dotenv()

# --- Database Connection ---
client = motor_asyncio.AsyncIOMotorClient(os.getenv("DB_URL"))
db = client.test_db
collection = db.test_collection

# --- Quote Model ---
class Quote(BaseModel):
    """Represents a quote - data expected in the request body (e.g., JSON)."""
    text: constr(min_length=1, max_length=500)
    author: constr(min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    approved : bool = False
    date_added: datetime.datetime = Field(default_factory=datetime.datetime.now)


    @field_validator("text", mode='after')
    @staticmethod
    def text_not_empty(value):
        if not value.strip():
            raise ValueError("Quote text cannot be empty.")
        return value

    @field_validator("author", mode='after')
    @staticmethod
    def author_not_empty(value):
        if not value.strip():
            raise ValueError("Author cannot be empty.")
        return value


# --- Submit Quote Endpoint - Handling JSON Request Body ---
@app.post("/quote", status_code=status.HTTP_201_CREATED)
async def submit_quote(
        text: str = Form(...),
        author: str = Form(...),
        email: Optional[EmailStr] = Form(None),
): # Expecting a 'Quote' model object from the body
    """
    Submits a quote. Expects quote data in the JSON request body.

    - Receives data as a JSON body, automatically validated against the Quote model.
    - Inserts the quote into the MongoDB collection.
    """
    quote = Quote(text=text, author=author, email=email)
    try:
        await collection.insert_one(quote.model_dump())
        return {"message": "Quote is submitted for approval."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit quote to database: {e}"
        )

@app.get('/get_quote')
async def get_quote():
    quote = await(collection.aggregate([{"$match": {"approved": True}}, {"$sample": {"size": 1}}]).to_list(length=1))
    if quote:
        try:
            quote_object = Quote(**quote[0])
            return quote_object.model_dump()
        except ValueError as e:
            print(f"Validation Error: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Invalid quote data: {e}")
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No quotes found.")

#admin routes

@app.get('/admin/quote', response_model=List[Quote])
async def pending_quote():
    """
    Retrieves a list of pending quotes from the database.
    """
    quotes = await collection.find({"approved": False}).to_list(length=None)

    if quotes:
        quote_objects = []
        for quote_data in quotes:
            try:
                quote_data["id"] = str(quote_data.pop("_id"))  #Important
                quote_object = Quote(**quote_data) # Create the Pydantic object
                quote_objects.append(quote_object)
            except ValueError as e:
                print(f"Validation Error: {e}, Data: {quote_data}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Invalid quote data: {e}"
                ) from e # raise from to preserve traceback

        return quote_objects
    else:
        return []

@app.put("/admin/quotes/{quote_id}")
async def approve_quote(quote_id: str):
    result = await collection.update_one({"_id": ObjectId(quote_id)}, {"$set": {"approved": True}})
    if result.modified_count == 0:
      raise HTTPException(status_code=404, detail="Quote not found")
    return {"message": "Quote approved"}

@app.delete("/admin/quotes/{quote_id}")
async def delete_quote(quote_id: str):
    result = await collection.delete_one({"_id": ObjectId(quote_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Quote not found")
    return {"message": "Quote deleted"}

