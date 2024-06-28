from dotenv import load_dotenv
import os
load_dotenv()

SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")


