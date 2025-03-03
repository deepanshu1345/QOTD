# import datetime
# import os
# from typing import Optional, List
# from fastapi import FastAPI, HTTPException, status, Form
# from fastapi.params import Depends
# from fastapi.responses import RedirectResponse
# from fastapi.security import OAuth2PasswordRequestForm
# from jose import jwt, exceptions
# from passlib.context import CryptContext
# from motor import motor_asyncio
# from dotenv import load_dotenv
# from pydantic import BaseModel, constr, EmailStr, field_validator, Field
# from bson import ObjectId
#
#
# app = FastAPI()
# load_dotenv()
#
# # --- Database Connection ---
# client = motor_asyncio.AsyncIOMotorClient(os.getenv("DB_URL"))
# db = client.get_database(os.getenv("DB_NAME"))
# user_collection = db.user
# quote_collection = db.quote
#
# #password Hashing
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#
# #--JWT CONFIG
# SECRET_KEY = os.getenv("SECRET_KEY")
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30
#
# #---User Model---
# class User(BaseModel):
#     username: constr(min_length=1)
#     password: str = ""  # Add a password field for input.
#     password_hash: str = ""
#     email: Optional[EmailStr] = None
#     is_admin: bool = False
#
#     @field_validator("password", mode='after')  # Validate password not password_hash.
#     def password_not_empty(cls, value):
#         if not value.strip():
#             raise ValueError("Password cannot be empty.")
#         return value
#
#     @field_validator("username", mode='after')
#     def username_not_empty(cls, value):
#         if not value.strip():
#             raise ValueError("Username cannot be empty.")
#         return value
#
# # --- Quote Model ---
# class Quote(BaseModel):
#     """Represents a quote - data expected in the request body (e.g., JSON)."""
#     text: constr(min_length=1, max_length=500)
#     author: constr(min_length=1, max_length=100)
#     email: Optional[EmailStr] = None
#     approved : bool = False
#     date_added: datetime.datetime = Field(default_factory=datetime.datetime.now)
#     added_by: Optional[str] = None
#
#
#     @field_validator("text", mode='after')
#     @staticmethod
#     def text_not_empty(value):
#         if not value.strip():
#             raise ValueError("Quote text cannot be empty.")
#         return value
#
#     @field_validator("author", mode='after')
#     @staticmethod
#     def author_not_empty(value):
#         if not value.strip():
#             raise ValueError("Author cannot be empty.")
#         return value
#
#     @field_validator("email", mode='after')
#     @staticmethod
#     def author_not_empty(value):
#         if not value.strip():
#             raise ValueError("Email cannot be empty.")
#         return value
#
# #--Authorization code
# def create_authentication_code(data: dict):
#     to_encode = data.copy()
#     expire = datetime.datetime.now() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     to_encode.update({'exp': expire})
#     code_jwt = jwt.encode(to_encode,SECRET_KEY, algorithm=ALGORITHM)
#     return code_jwt
#
#
# async def get_current_user(token:str = Depends(OAuth2PasswordRequestForm)):
#     try:
#         payload  = jwt.decode(token.username,SECRET_KEY, algorithms=[ALGORITHM])
#         username : str = payload.get("sub")
#         if username is None:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
#         user = await user_collection.find_one({"username": username})
#         if user is None:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
#
#         return User(**user)
#     except exceptions.JWTError:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
#
# async def get_current_active_user(current_user : User = Depends(get_current_user)):
#     return current_user
#
# async def get_current_admin(current_user : User = Depends(get_current_user)):
#     if not current_user.is_admin:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not an admin")
#     return current_user
#
#
# #-----Authentaction end-points
# # @app.post('/login')
# # async def login_for_access_code(form_data: OAuth2PasswordRequestForm = Depends()):
# #     user = await user_collection.find_one({"username": form_data.username})
# #     print(user)
# #     if not user or not pwd_context.verify(form_data.password, user["password_hash"]):
# #         raise HTTPException(
# #             status_code=status.HTTP_401_UNAUTHORIZED,
# #             detail="Incorrect username or password",
# #         )
# #     access_token = create_authentication_code(data={"sub": user["username"]})
# #     print('!!!!!!!!!!!')
# #     print(access_token)
# #     print('!!!!!!!!!!!')
# #     return {"access_token": access_token, "token_type": "bearer"}
#
#
#
#
# @app.post('/login')
# async def login_for_access_code(form_data: OAuth2PasswordRequestForm = Depends()):
#     try:
#         print(f"Attempting login for username: {form_data.username}")  # Debugging
#         user = await user_collection.find_one({"username": form_data.username})
#         print(f"User found: {user}")  # Debugging
#
#         if user is None:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Incorrect username or password",
#             )
#
#         try:
#             password_verified = pwd_context.verify(form_data.password, user["password_hash"])
#             print(f"Password verification result: {password_verified}")  # Debugging
#         except KeyError:
#             print("Error: 'password_hash' key not found in user data")
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail="Internal server error: Missing password hash",
#             ) from None
#
#         if not password_verified:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Incorrect username or password",
#             )
#
#         try:
#             # Ensure SECRET_KEY is properly formatted in create_authentication_code
#             access_token = create_authentication_code(data={"sub": user["username"]})
#             print('!!!!!!!!!!!')
#             print(access_token)
#             print('!!!!!!!!!!!')
#         except KeyError:
#             print("Error: 'username' key not found in user data")
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail="Internal server error: Missing username",
#             ) from None
#         except Exception as e:
#             print(f"Error creating authentication code: {e}")
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail=f"Internal server error: Could not create token: {e}",
#             ) from e
#
#         return {"access_token": access_token, "token_type": "bearer"}
#
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Internal server error: {e}",
#         ) from e
#
#
#
# @app.post("/register", status_code=status.HTTP_201_CREATED)
# async def register_user(user: User):
#     existing_user = await user_collection.find_one({"username": user.username})
#     if existing_user:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
#
#     try:
#         user_dict = user.model_dump()
#         hashed_password = pwd_context.hash(user_dict["password"])
#         user_dict["password_hash"] = hashed_password
#         del user_dict["password"]
#         await user_collection.insert_one(user_dict)
#         return {"message": "User registered successfully"}
#     except Exception as e:
#         print(f"Error during user registration: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Internal server error during registration: {e}"
#         )
#
#
#
# # protected path
# @app.post("/quote", status_code=status.HTTP_201_CREATED)
# async def submit_quote(
#         text: str = Form(...),
#         author: str = Form(...),
#         email: Optional[EmailStr] = Form(None),
#         current_user: User = Depends(get_current_active_user)
# ):
#     """
#     Submits a quote. Expects quote data in the JSON request body.
#
#     - Receives data as a JSON body, automatically validated against the Quote model.
#     - Inserts the quote into the MongoDB collection.
#     """
#     quote = Quote(text=text, author=author, added_by=current_user.username)
#     try:
#         await quote_collection.insert_one(quote.model_dump())
#         return {"message": "Quote is submitted for approval."}
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to submit quote to database: {e}"
#         )
#
# @app.get('/get_quote')
# async def get_quote():
#     quote = await(quote_collection.aggregate([{"$match": {"approved": True}}, {"$sample": {"size": 1}}]).to_list(length=1))
#     if quote:
#         try:
#             quote_object = Quote(**quote[0])
#             return quote_object.model_dump()
#         except ValueError as e:
#             print(f"Validation Error: {e}")
#             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Invalid quote data: {e}")
#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No quotes found.")
#
# #admin routes
#
# @app.get('/admin/quote', response_model=List[Quote])
# async def pending_quote():
#     """
#     Retrieves a list of pending quotes from the database.
#     """
#     quotes = await quote_collection.find({"approved": False}).to_list(length=None)
#
#     if quotes:
#         quote_objects = []
#         for quote_data in quotes:
#             try:
#                 quote_data["id"] = str(quote_data.pop("_id"))  #Important
#                 quote_object = Quote(**quote_data) # Create the Pydantic object
#                 quote_objects.append(quote_object)
#             except ValueError as e:
#                 print(f"Validation Error: {e}, Data: {quote_data}")
#                 raise HTTPException(
#                     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                     detail=f"Invalid quote data: {e}"
#                 ) from e # raise from to preserve traceback
#
#         return quote_objects
#     else:
#         return []
#
# @app.put("/admin/quotes/{quote_id}")
# async def approve_quote(quote_id: str):
#     result = await quote_collection.update_one({"_id": ObjectId(quote_id)}, {"$set": {"approved": True}})
#     if result.modified_count == 0:
#       raise HTTPException(status_code=404, detail="Quote not found")
#     return {"message": "Quote approved"}
#
# @app.delete("/admin/quotes/{quote_id}")
# async def delete_quote(quote_id: str):
#     result = await quote_collection.delete_one({"_id": ObjectId(quote_id)})
#     if result.deleted_count == 0:
#         raise HTTPException(status_code=404, detail="Quote not found")
#     return {"message": "Quote deleted"}
#


import datetime
import os
from typing import Optional, List
from fastapi import FastAPI, HTTPException, status, Form, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from motor import motor_asyncio
from dotenv import load_dotenv
from pydantic import BaseModel, constr, field_validator, Field, ConfigDict
from bson import ObjectId, errors as bson_errors
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
load_dotenv()



# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=['*'],
#     allow_credentials=True,
#     allow_methods=['*'],
#     allow_headers=['*'],
# )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Allow the React app origin
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Database setup
client = motor_asyncio.AsyncIOMotorClient(os.getenv("DB_URL"))
db = client.get_database(os.getenv("DB_NAME"))
user_collection = db.user
quote_collection = db.quote

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# Models
class UserCreate(BaseModel):
    username: constr(min_length=1)
    password: str

    @field_validator("password")
    def password_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Password cannot be empty.")
        return v

    @field_validator("username")
    def username_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Username cannot be empty.")
        return v


class UserDB(BaseModel):
    username: str
    password_hash: str
    is_admin: bool = False
    model_config = ConfigDict(arbitrary_types_allowed=True)


class QuoteBase(BaseModel):
    text: constr(min_length=1, max_length=500)
    author: constr(min_length=1, max_length=100)
    approved: bool = False

class QuoteCreate(QuoteBase):
    pass


class Quote(QuoteBase):
    id: Optional[str] = None
    approved: bool = False
    date_added: datetime.datetime = Field(default_factory=datetime.datetime.now)
    added_by: Optional[str] = None
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("text")
    @classmethod
    def validate_text(cls, v):
        if not v.strip():
            raise ValueError("Quote text cannot be empty.")
        return v

    @field_validator("author")
    @classmethod
    def validate_author(cls, v):
        if not v.strip():
            raise ValueError("Author cannot be empty.")
        return v



# Auth functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.datetime.now() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await user_collection.find_one({"username": username})
    if not user:
        raise credentials_exception
    return UserDB(**user)


async def get_current_active_user(current_user: UserDB = Depends(get_current_user)):
    return current_user


async def get_current_admin(current_user: UserDB = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user


# Routes
@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await user_collection.find_one({"username": form_data.username})
    if not user or not pwd_context.verify(form_data.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")
    access_token = create_access_token(data={"sub": user["username"]})
    is_admin = user.get("is_admin", False)
    return {"access_token": access_token, "token_type": "bearer", "is_admin": is_admin}


@app.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    existing_user = await user_collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = pwd_context.hash(user.password)
    new_user = UserDB(
        username=user.username,
        password_hash=hashed_password,
        is_admin=False
    )
    await user_collection.insert_one(new_user.model_dump())
    return {"message": "User registered successfully"}


@app.post("/quote", status_code=status.HTTP_201_CREATED)
async def submit_quote(
        text: str = Form(...),
        author: str = Form(...),
        current_user: UserDB = Depends(get_current_active_user)
):
    quote_data = {
        "text": text,
        "author": author,
        "added_by": current_user.username
    }
    new_quote = QuoteCreate(**quote_data)
    quote_dict = new_quote.model_dump()
    quote_dict["date_added"] = datetime.datetime.now()
    await quote_collection.insert_one(quote_dict)
    return {"message": "Quote submitted for approval"}


@app.get("/quote", response_model=Quote)
async def get_random_quote():
    pipeline = [{"$match": {"approved": True}}, {"$sample": {"size": 1}}]
    quotes = await quote_collection.aggregate(pipeline).to_list(1)
    if not quotes:
        raise HTTPException(status_code=404, detail="No quotes available")
    quote = quotes[0]
    quote["id"] = str(quote.pop("_id"))
    return Quote(**quote)


# Admin routes
@app.get("/admin/quotes", response_model=List[Quote])
async def get_pending_quotes(current_user: UserDB = Depends(get_current_admin)):
    quotes = await quote_collection.find({"approved": False}).to_list(None)
    for quote in quotes:
        quote["id"] = str(quote.pop("_id"))
    return [Quote(**q) for q in quotes]


@app.put("/admin/quotes/{quote_id}")
async def approve_quote(quote_id: str, current_user: UserDB = Depends(get_current_admin)):
    try:
        obj_id = ObjectId(quote_id)
    except bson_errors.InvalidId:
        raise HTTPException(status_code=400, detail="Invalid quote ID")

    result = await quote_collection.update_one({"_id": obj_id}, {"$set": {"approved": True}})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Quote not found")
    return {"message": "Quote approved"}


@app.delete("/admin/quotes/{quote_id}")
async def delete_quote(quote_id: str, current_user: UserDB = Depends(get_current_admin)):
    try:
        obj_id = ObjectId(quote_id)
    except bson_errors.InvalidId:
        raise HTTPException(status_code=400, detail="Invalid quote ID")

    result = await quote_collection.delete_one({"_id": obj_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Quote not found")
    return {"message": "Quote deleted"}

