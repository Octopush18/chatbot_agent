import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_experimental.agents import create_csv_agent
import os

from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()
# Initialize the language model
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# Ask the user for the file path
file_path = input("Please enter the file path for the data file (Excel or CSV): ")

# Check the file extension to see if it's an Excel file
if file_path.endswith(('.xlsx', '.xls')):
    # Read the Excel file
    excel_data = pd.read_excel(file_path)
    
    # Convert it to a CSV file
    csv_file_path = os.path.splitext(file_path)[0] + ".csv"
    excel_data.to_csv(csv_file_path, index=False)
    
    # Use the CSV file path as the file path for the agent
    file_path = csv_file_path

# Create the agent with allow_dangerous_code=True
agent_executor = create_csv_agent(
    llm,
    file_path,  # Use the user-provided or converted CSV file path
    agent_type="openai-tools",
    verbose=True,
    allow_dangerous_code=True  # Enables code execution permissions
)

# Chatbot loop to interactively take questions from the user
print("Welcome to the HCP Data Bot! Type 'exit' to end the chat.")

while True:
    user_question = input("Ask your question: ")
    
    if user_question.lower() == 'exit':
        print("Goodbye!")
        break

    # Construct the prompt for the agent
    prompt = f"""
        Please note:
        - The data is loaded as a DataFrame named `df`.
        - Do not use synthetic or fabricated data.
        - Use the actual values from `df` when calculating counts or creating tables.
        Please examine the data file and provide detailed results for the following request: {user_question}. 
        Ensure the response includes specific data tables, counts, or raw data as requested, 
        and format all outputs as tables for clarity and ease of analysis. All responses should be tabular."""

    # Run the agent with the prompt
    response = agent_executor.run(prompt)
    
    # Display the response to the user
    print("Response:", response)
