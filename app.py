import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "you are a diet specialist, give me the output accordingly"),
        ("user", "{question}")
    ]
)  
llm = ChatGroq(api_key=groq_api_key, model="openai/gpt-oss-20b")
chain = prompt | llm

response = chain.invoke({"question": "how to do pullups?"})
print(response.content)