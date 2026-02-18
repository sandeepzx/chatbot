import os
import psycopg2
from datetime import datetime
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# Get credentials from env file
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
database_url = os.getenv("DATABASE_URL")

# Make connection to database
def get_db_connection():
    return psycopg2.connect(database_url)

# Save to database
def save_to_db(user_id, role, message):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        insert_query = """
        INSERT INTO chat (user_id, role, message, timestamp) 
        VALUES (%s, %s, %s, %s)
        """
        cur.execute(insert_query, (user_id, role, message, datetime.now()))
        conn.commit()
        cur.close()
        conn.close()

    except Exception as e:
        print(f"Error saving to database: {e}")

# Prompt
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "you are a diet specialist, give me the output accordingly"),
        ("placeholder", "{history}"),
        ("user", "{question}")
    ]
)  
llm = ChatGroq(api_key=groq_api_key, model="openai/gpt-oss-20b")
chain = prompt | llm

user_id = "User123"

# Get previous chats
def get_history(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT role, message FROM chat WHERE user_id = %s ORDER BY timestamp", (user_id,))
    chats = cur.fetchall() 

    history = []
    for chat in chats:
        history.append((chat[0],chat[1]))
    
    cur.close()
    conn.close()

    return history

# Enter the chat
while True:
    question = input("Enter a question: ")

    if question.lower() in ["exit","quit"]:
        break

    history = get_history(user_id)
    response = chain.invoke({"history": history,"question": question})

    save_to_db(user_id, "user", question)
    save_to_db(user_id, "assistant", response.content)

    print(response.content)