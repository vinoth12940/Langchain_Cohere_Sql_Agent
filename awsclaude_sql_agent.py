import streamlit as st
from langchain_aws import ChatBedrock
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain.agents.agent_types import AgentType
from sqlalchemy.exc import SQLAlchemyError
import os
import logging
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(filename='app.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Function to securely get database connection using environment variables
@st.cache_resource
def get_db_connection():
    """
    Establishes a connection to the PostgreSQL database using environment variables.
    
    Returns:
        SQLDatabase: The database connection object, or None if connection fails.
    """
    try:
        # Fetch environment variables with defaults
        db_user = os.getenv('DB_USER', 'default_user')
        db_password = os.getenv('DB_PASSWORD', 'default_password')
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '5432')  # Default PostgreSQL port
        db_name = os.getenv('DB_NAME', 'default_db')

        # Construct the database URI
        db_uri = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        
        # Validate port
        if not db_port.isdigit():
            raise ValueError(f"Invalid port number: {db_port}")
        
        logging.info(f"Connecting to database with URI: {db_uri}")
        return SQLDatabase.from_uri(db_uri)
    except ValueError as ve:
        logging.error(f"Database configuration error: {str(ve)}")
        st.error(f"Database configuration error: {str(ve)}")
        return None
    except SQLAlchemyError as e:
        logging.error(f"Database connection failed: {str(e)}")
        st.error("Failed to connect to the database. Please check your configuration.")
        return None

# Function to initialize the Claude 3 Sonnet model via AWS Bedrock
@st.cache_resource
def get_llm():
    """
    Initializes the Claude 3 Sonnet model using AWS Bedrock with credentials from .env.
    
    Returns:
        ChatBedrock: The language model object, or None if initialization fails.
    """
    try:
        # Fetch AWS credentials from environment variables
        aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        aws_region = os.getenv('AWS_REGION', 'us-east-1')

        # Validate AWS credentials
        if not aws_access_key or not aws_secret_key:
            raise ValueError("AWS_ACCESS_KEY_ID or AWS_SECRET_ACCESS_KEY not set in .env")

        llm = ChatBedrock(
            model_id="us.anthropic.claude-3-5-sonnet-20240620-v1:0",
            model_kwargs={
                "temperature": 0.1,
                "max_tokens": 1000
            },
            region_name=aws_region,
            credentials_profile_name=None,  # Explicitly avoid profile-based auth
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )
        logging.info("LLM initialized successfully")
        return llm
    except ValueError as ve:
        logging.error(f"AWS configuration error: {str(ve)}")
        st.error(f"AWS configuration error: {str(ve)}")
        return None
    except Exception as e:
        logging.error(f"Failed to initialize LLM: {str(e)}")
        st.error("Failed to initialize the language model.")
        return None

# Function to create the SQL agent
def create_agent():
    """
    Creates an SQL agent with the database connection and LLM.
    
    Returns:
        AgentExecutor: The SQL agent, or None if creation fails.
    """
    db = get_db_connection()
    llm = get_llm()
    if db is None or llm is None:
        return None
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    agent = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION
    )
    logging.info("SQL agent created successfully")
    return agent

# Basic input validation to prevent harmful SQL commands
def validate_input(query):
    """
    Validates the user input to prevent potentially harmful SQL commands.
    
    Returns:
        bool: True if the input is safe, False otherwise.
    """
    dangerous_commands = ["DROP", "DELETE", "UPDATE", "INSERT"]
    if any(cmd in query.upper() for cmd in dangerous_commands):
        logging.warning(f"Blocked potentially harmful query: {query}")
        return False
    return True

# Asynchronous function to run the agent query
async def run_agent_query(agent, prompt):
    """
    Runs the agent query asynchronously.
    
    Returns:
        str: The result of the query, or an error message.
    """
    try:
        response = await asyncio.to_thread(agent.run, prompt)
        logging.info(f"Query executed successfully: {prompt}")
        return response
    except Exception as e:
        logging.error(f"Query execution failed: {str(e)}")
        return f"Error: {str(e)}"

# Main Streamlit application
def main():
    st.set_page_config(page_title="SQL Query Assistant", page_icon="💬")
    st.title("Chat with Your PostgreSQL Database")
    
    # Initialize session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I can help you query your PostgreSQL database. What would you like to know?"}
        ]
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Create the SQL agent
    agent = create_agent()
    if agent is None:
        st.error("Failed to initialize the SQL agent.")
        return
    
    # Sample queries for user guidance
    sample_queries = [
        "How many users signed up last month?",
        "What is the total revenue for this year?",
        "List the top 5 products by sales.",
        "Show me the average order value."
    ]
    
    # Sidebar with instructions and sample queries
    st.sidebar.title("Instructions")
    st.sidebar.markdown("""
    - Ask natural language questions about your database.
    - Use the sample queries below to get started.
    - Set environment variables in a `.env` file.
    """)
    st.sidebar.subheader("Sample Queries")
    for query in sample_queries:
        if st.sidebar.button(query):
            st.session_state.messages.append({"role": "user", "content": query})
            with st.chat_message("user"):
                st.markdown(query)
            with st.chat_message("assistant"):
                with st.spinner("Querying database..."):
                    if validate_input(query):
                        response = asyncio.run(run_agent_query(agent, query))
                        st.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    else:
                        st.error("This query is not allowed.")
    
    # Chat input for user queries
    if prompt := st.chat_input("Ask a question about your database..."):
        if validate_input(prompt):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner("Querying database..."):
                    response = asyncio.run(run_agent_query(agent, prompt))
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
        else:
            st.error("This query is not allowed.")

# Entry point
if __name__ == "__main__":
    main()