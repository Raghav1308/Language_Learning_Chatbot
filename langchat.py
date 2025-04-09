import openai
import sqlite3
import os
from dotenv import load_dotenv
from langchain_community.llms import OpenAI
from langchain.memory import ConversationBufferMemory

# Load API Key
load_dotenv()
OPENAI_API_KEY = "OPENAI_API_KEY"

# Initialize SQLite Database
conn = sqlite3.connect("mistakes.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS mistakes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        mistake TEXT,
        correction TEXT
    )
""")
conn.commit()

# Initialize Chatbot
llm = OpenAI(temperature=0.7, openai_api_key=OPENAI_API_KEY)
memory = ConversationBufferMemory()

def ask_user_preferences():
    """Get language learning preferences from the user."""
    learning_language = input("What language do you want to learn? ")
    native_language = input("What is your native language? ")
    level = input("What is your current level (Beginner/Intermediate/Advanced)? ")
    return learning_language, native_language, level

def chat_with_user(language, level):
    """Simulates a conversation in the selected language."""
    print(f"\nLet's start chatting in {language} (Level: {level})!")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        
        response = llm.invoke(f"User said: {user_input} in {language}. "
                               f"Correct any mistakes and provide a response.")
        
        # Detect mistakes (basic approach)
        if "mistake" in response.lower():
            mistake, correction = extract_mistakes(response)
            save_mistake("user", mistake, correction)
        
        print(f"Chatbot: {response}")

def extract_mistakes(response):
    """Extract mistakes and corrections from the AI response."""
    # This is a simplified way; you may improve it with regex or NLP methods.
    if "mistake:" in response.lower():
        parts = response.split("Mistake:")
        mistake = parts[1].split("Correction:")[0].strip()
        correction = parts[1].split("Correction:")[1].strip()
        return mistake, correction
    return "", ""

def save_mistake(user, mistake, correction):
    """Save the mistake in the SQLite database."""
    cursor.execute("INSERT INTO mistakes (user, mistake, correction) VALUES (?, ?, ?)", 
                   (user, mistake, correction))
    conn.commit()

def show_mistake_summary():
    """Display a summary of mistakes at the end."""
    print("\nSummary of your mistakes:")
    cursor.execute("SELECT mistake, correction FROM mistakes")
    for row in cursor.fetchall():
        print(f"❌ {row[0]} → ✅ {row[1]}")
    
# Main Flow
if __name__ == "__main__":
    language, native_language, level = ask_user_preferences()
    chat_with_user(language, level)
    show_mistake_summary()