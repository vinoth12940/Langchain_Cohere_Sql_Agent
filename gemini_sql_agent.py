import streamlit as st
import os
import re
from langchain.agents import AgentExecutor
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import create_react_agent
import psycopg2
from sqlalchemy import create_engine, event, text
from dotenv import load_dotenv
from langsmith import Client

# Load environment variables
load_dotenv()

# Initialize LangSmith client if needed
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "postgres-sql-agent"
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")

# Check if Google API key is set
if os.getenv("GOOGLE_API_KEY") is None:
    st.error("❌ GOOGLE_API_KEY is not set in .env file. Please set it and restart the application.")
    st.stop()

# Function to connect to PostgreSQL database
def get_postgresql_engine():
    """Create connection to PostgreSQL cricket_academy database."""
    try:
        connection_string = "postgresql://postgres:postgres@localhost:5432/cricket_academy"
        engine = create_engine(connection_string)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).fetchone()
            if result and result[0] == 1:
                st.success("✅ Successfully connected to PostgreSQL database!")
            else:
                st.error("❌ Connection test failed")
        
        # Add event listener to prevent modification queries
        @event.listens_for(engine, "before_cursor_execute")
        def prevent_modification_queries(conn, cursor, statement, parameters, context, executemany):
            # Convert statement to lowercase to catch all variations
            statement_lower = statement.lower().strip()
            
            # Check if the statement is a modification query
            if (statement_lower.startswith('update') or 
                statement_lower.startswith('delete') or 
                statement_lower.startswith('insert') or 
                statement_lower.startswith('alter') or 
                statement_lower.startswith('drop') or 
                statement_lower.startswith('truncate')):
                raise Exception("⚠️ This application is set to read-only mode. Modification queries are not allowed.")
        
        return engine
    except Exception as e:
        st.error(f"❌ Database connection error: {str(e)}")
        raise

# Function to fix table formatting in markdown text
def fix_table_formatting(text):
    """Ensures tables in markdown are properly formatted with newlines before and after."""
    # Look for table patterns (lines starting with | and containing |)
    lines = text.split('\n')
    fixed_lines = []
    in_table = False
    
    for i, line in enumerate(lines):
        # Detect start of a table (line with | character)
        if not in_table and line.strip().startswith('|') and '|' in line[1:]:
            # If previous line isn't empty, add blank line
            if i > 0 and lines[i-1].strip() != '':
                fixed_lines.append('')
            in_table = True
            fixed_lines.append(line)
        # Detect end of a table
        elif in_table and (not line.strip().startswith('|') or not '|' in line[1:]):
            # If next line isn't empty, add blank line
            if line.strip() != '':
                fixed_lines.append('')
            in_table = False
            fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize database and agent if not already done
if "agent_executor" not in st.session_state:
    try:
        # Initialize database and agent
        engine = get_postgresql_engine()
        db = SQLDatabase(engine)
        
        # Use Gemini 1.5 Pro model which is more stable and widely available
        MODEL = "gemini-2.0-flash"
        llm = ChatGoogleGenerativeAI(
            model=MODEL, 
            temperature=0.1,
            max_output_tokens=8192,
            verbose=True,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        toolkit = SQLDatabaseToolkit(db=db, llm=llm)
        context = toolkit.get_context()
        
        # Store database information in session state
        st.session_state.table_names = context.get('table_names', '')
        st.session_state.table_info = context.get('table_info', '')
        st.session_state.context = context
        
        tools = toolkit.get_tools()
        
        # Create the proper ReAct prompt template with required variables
        prompt_template = """## Task And Context
You use your advanced complex reasoning capabilities to help people by answering their questions and other requests about the cricket academy database. 
You will be asked questions about the database that contains information related to a cricket academy, including tables for players, coaches, programs, 
training sessions, payments, attendance, and more.

## Style Guide
Unless the user asks for a different style of answer, you should answer in full sentences, using proper grammar and spelling.
When displaying tables in markdown format, always add a blank line before and after the table for proper rendering.

## Additional Information
You are an expert who answers the user's question by creating SQL queries and executing them.
You are equipped with a number of relevant SQL tools.
IMPORTANT: This application is in READ-ONLY mode. You should ONLY use SELECT queries.
Do not create, modify, or delete any data in the database.

Here is information about the database:
{table_info}

## Tools
You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Question: {input}
{agent_scratchpad}
"""
        
        # Create the prompt with the proper format
        prompt = ChatPromptTemplate.from_template(prompt_template)
        
        # Create the React agent using Gemini model
        agent = create_react_agent(
            llm=llm,
            tools=tools,
            prompt=prompt,
        )
        
        st.session_state.agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            return_intermediate_steps=True
        )
    except Exception as e:
        st.error(f"Error initializing the agent: {str(e)}")

# Streamlit UI
st.title("Cricket Academy SQL Agent (Gemini 1.5 Pro) - Read-Only")
st.caption("This application operates in read-only mode and only allows SELECT queries.")

# Add a sidebar with database information
with st.sidebar:
    st.header("Database Information")
    with st.expander("Available Tables"):
        st.write(st.session_state.table_names)
    with st.expander("Database Schema"):
        st.code(st.session_state.table_info)
    
    st.divider()
    st.warning("⚠️ This application operates in READ-ONLY mode. Only SELECT queries are permitted.")

st.write("Ask questions about the Cricket Academy database!")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question about the cricket academy database"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = st.session_state.agent_executor.invoke({
                    "input": prompt,
                    "table_info": st.session_state.context
                })
                response_content = response["output"]
                
                # Fix table formatting in the response
                fixed_response = fix_table_formatting(response_content)
                
                st.markdown(fixed_response)
                
                # Show intermediate steps in an expander
                with st.expander("See agent's thought process"):
                    for step in response["intermediate_steps"]:
                        st.write(f"Tool: {step[0].tool}")
                        st.write(f"Input: {step[0].tool_input}")
                        st.write(f"Output: {step[1]}")
                        st.write("---")
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": fixed_response})
            except Exception as e:
                error_message = f"Error: {str(e)}"
                st.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message}) 