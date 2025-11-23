import os
import mysql.connector

def get_connection():
    print("DEBUG DB SETTINGS:", {
        "DB_HOST": os.getenv("DB_HOST"),
        "DB_USER": os.getenv("DB_USER"),
        "DB_NAME": os.getenv("DB_NAME"),
        "DB_PORT": os.getenv("DB_PORT"),
    })

    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT", 3306)),
    )
