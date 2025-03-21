import streamlit as st
import os
from langchain.agents import AgentExecutor
from langchain_cohere.react_multi_hop.agent import create_cohere_react_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_cohere.chat_models import ChatCohere
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
import psycopg2
from sqlalchemy import create_engine, event, text
from dotenv import load_dotenv
from langsmith import Client

# Load environment variables
load_dotenv()

# Initialize LangSmith client if needed
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "postgres-sql-agent"

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

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize database and agent if not already done
if "agent_executor" not in st.session_state:
    try:
        # Initialize database and agent
        engine = get_postgresql_engine()
        db = SQLDatabase(engine)
        
        MODEL = "command-r-plus"
        llm = ChatCohere(
            model=MODEL, 
            temperature=0.1,
            verbose=True,
            cohere_api_key=os.getenv("COHERE_API_KEY")
        )
        toolkit = SQLDatabaseToolkit(db=db, llm=llm)
        context = toolkit.get_context()
        
        # Store database information in session state
        st.session_state.table_names = context.get('table_names', '')
        st.session_state.table_info = context.get('table_info', '')
        st.session_state.context = context
        
        tools = toolkit.get_tools()
        
        # Create the preamble with context
        preamble = f"""## Task And Context
You use your advanced complex reasoning capabilities to help people by answering their questions and other requests about the cricket academy database. 
You will be asked questions about the database that contains information related to a cricket academy, including tables for players, coaches, programs, 
training sessions, payments, attendance, and more.

## Style Guide
Unless the user asks for a different style of answer, you should answer in full sentences, using proper grammar and spelling.

## Additional Information
You are an expert who answers the user's question by creating SQL queries and executing them.
You are equipped with a number of relevant SQL tools.
IMPORTANT: This application is in READ-ONLY mode. You should ONLY use SELECT queries.
Do not create, modify, or delete any data in the database.

Here is information about the database:
{st.session_state.table_info}

Question: {{input}}"""
        
        # Create the agent with the preamble
        prompt = ChatPromptTemplate.from_template(preamble)
        agent = create_cohere_react_agent(
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
st.title("Cricket Academy SQL Agent (Read-Only)")
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
                st.markdown(response_content)
                
                # Show intermediate steps in an expander
                with st.expander("See agent's thought process"):
                    for step in response["intermediate_steps"]:
                        st.write(f"Tool: {step[0].tool}")
                        st.write(f"Input: {step[0].tool_input}")
                        st.write(f"Output: {step[1]}")
                        st.write("---")
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response_content})
            except Exception as e:
                error_message = f"Error: {str(e)}"
                st.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message}) 