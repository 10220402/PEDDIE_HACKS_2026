# ==========================================
# HEALTHLENS - DATABASE
# ==========================================

import sqlite3
from datetime import datetime


# ==========================================
# DATABASE NAME
# ==========================================

DATABASE_NAME = "healthlens_history.db"


# ==========================================
# CREATE DATABASE TABLE
# ==========================================

def create_database():

    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_message TEXT NOT NULL,

            ai_response TEXT NOT NULL,

            created_at TEXT NOT NULL

        )
    """)

    connection.commit()

    connection.close()


# ==========================================
# SAVE CHAT
# ==========================================

def save_chat(user_message, ai_response):

    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    created_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor.execute("""
        INSERT INTO chat_history
        (user_message, ai_response, created_at)

        VALUES (?, ?, ?)
    """, (
        user_message,
        ai_response,
        created_at
    ))

    connection.commit()

    connection.close()


# ==========================================
# GET CHAT HISTORY
# ==========================================

def get_chat_history():

    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            user_message,
            ai_response,
            created_at

        FROM chat_history

        ORDER BY id ASC
    """)

    history = cursor.fetchall()

    connection.close()

    return history


# ==========================================
# TEST DATABASE
# ==========================================

if __name__ == "__main__":

    create_database()

    print("✅ HealthLens database created successfully!")

    print(
        "Database file:",
        DATABASE_NAME
    )