from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Gemini (supports Tool Calling natively)
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash", # or gemini-1.5-pro
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0
)

# Example: Using Gemini in a Node
def parse_input_node(state: TripState):
    # Gemini uses the same .invoke() pattern as other LangChain models
    response = llm.invoke(state['user_prompt'])
    # ... logic to update state ...