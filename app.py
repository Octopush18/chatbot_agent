import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_experimental.agents import create_csv_agent

# Load environment variables from .env file (e.g., for API keys)
load_dotenv()

# Initialize the language model
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# Streamlit UI
st.title("HCP Data Chatbot")
st.write("Upload a data file (Excel or CSV) to start interacting.")

# File uploader for user to upload the data file
uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx", "xls"])

# Once the file is uploaded, read and process it
if uploaded_file is not None:
    # Determine if it's an Excel file, and convert if necessary
    if uploaded_file.name.endswith(('.xlsx', '.xls')):
        # Read Excel file into a DataFrame
        data = pd.read_excel(uploaded_file)
        # Save the DataFrame to a temporary CSV for agent use
        csv_file_path = os.path.join("temp.csv")
        data.to_csv(csv_file_path, index=False)
    else:
        # Load CSV directly
        data = pd.read_csv(uploaded_file)
        csv_file_path = uploaded_file  # Use the uploaded file directly
    
    # Inform the user that the data has been loaded
    st.write("Data file loaded successfully. You may now ask questions about the data.")

    # Create the agent with allow_dangerous_code=True for conversational interaction
    agent_executor = create_csv_agent(
        llm,
        csv_file_path,
        agent_type="openai-tools",
        verbose=True,
        allow_dangerous_code=True  # Enables code execution permissions
    )

    # Chat interface
    st.write("### Chat with your data!")
    user_question = st.text_input("Ask a question about the data:")
    
    if user_question:
        # Construct the prompt for the agent
        prompt = f"""
            Please note:
            - The data is loaded as a DataFrame named `df`.
            - Do not use synthetic or fabricated data.
            - Use the actual values from `df` when calculating counts or creating tables.
            Please examine the data file and provide detailed results for the following request: {user_question}. 
            Ensure the response includes specific data tables, counts, or raw data as requested, 
            and format all outputs as tables for clarity and ease of analysis. All responses should be tabular."""

        # Get the response from the agent
        response = agent_executor.run(prompt)

        # Display the response to the user
        st.write("### Response:")
        st.write(response)

else:
    st.write("Please upload a CSV or Excel file to begin.")
