import os
import psycopg2
from datetime import datetime
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
database_url = os.getenv("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(database_url)

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

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "you are a diet specialist, give me the output accordingly"),
        ("user", "{question}")
    ]
)  
llm = ChatGroq(api_key=groq_api_key, model="openai/gpt-oss-20b")
chain = prompt | llm

user_id = "User123"

while True:
    question = input("Enter a question: ")

    if question.lower() in ["exit","quit"]:
        break

    response = chain.invoke({"question": question})

    save_to_db(user_id, "user", question)
    save_to_db(user_id, "assistant", response.content)

    print(response.content)