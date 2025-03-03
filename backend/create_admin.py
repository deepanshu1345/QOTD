import asyncio
import os
import argparse
from getpass import getpass
from dotenv import load_dotenv
from passlib.context import CryptContext
from motor import motor_asyncio

load_dotenv()

# Database setup - configured using environment variables from .env file
DB_URL = os.getenv("DB_URL")
DB_NAME = os.getenv("DB_NAME")

if not DB_URL or not DB_NAME:
    print("Error: DB_URL and DB_NAME environment variables must be set in .env file.")
    exit(1)

client = motor_asyncio.AsyncIOMotorClient(DB_URL)
db = client.get_database(DB_NAME)
user_collection = db.user

# Password hashing context - using bcrypt for security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_admin_user(username, password):
    """
    Creates a new admin user in the database with the provided username and password.

    - Checks if a user with the given username already exists.
    - Hashes the password securely using bcrypt.
    - Inserts the admin user data into the 'user' collection in MongoDB.

    Args:
        username (str): The username for the admin user.
        password (str): The plain text password for the admin user (will be hashed).
    """
    existing_user = await user_collection.find_one({"username": username})
    if existing_user:
        print(f"Error: Username '{username}' already exists. Choose a different username.")
        return

    hashed_password = pwd_context.hash(password)  # Hash the password before storing
    admin_user_data = {
        "username": username,
        "password_hash": hashed_password,
        "is_admin": True  # Set 'is_admin' to True for the admin user role
    }

    try:
        result = await user_collection.insert_one(admin_user_data)
        print(f"Admin user '{username}' created successfully with ObjectId: {result.inserted_id}")
    except Exception as e:
        print(f"Error creating admin user: {e}")
        print(f"Detailed error: {e}")  # Print more detailed error for debugging


async def main():
    """
    Main function to handle script execution, argument parsing, and user interaction.

    - Uses argparse to handle command-line arguments for username.
    - Prioritizes username input from: command-line argument > environment variable > user prompt.
    - Prompts the user securely for password using getpass().
    - Calls create_admin_user() to insert the admin user into the database.
    """
    parser = argparse.ArgumentParser(description="Create an admin user in the database.")
    parser.add_argument(
        "--username",
        help="Username for the admin user (overrides INITIAL_ADMIN_USERNAME env var, prompts if not provided)",
    )
    args = parser.parse_args()

    # Determine username: command-line arg > environment variable > user input prompt
    username = args.username or os.getenv("INITIAL_ADMIN_USERNAME") or input("Enter the username for the admin user: ")

    if not username:
        print("Username cannot be empty. Exiting.")
        return

    password = getpass(f"Enter the password for admin user '{username}': ")  # Secure password prompt
    if not password:
        print("Password cannot be empty. Exiting.")
        return

    password_confirm = getpass("Confirm password: ")
    if password != password_confirm:
        print("Passwords do not match. Exiting.")
        return

    await create_admin_user(username, password)  # Create the admin user in the database
    client.close()  # Close the MongoDB client connection


if __name__ == "__main__":
    asyncio.run(main())