# PostgreSQL SQL Agent for Cricket Academy

This application connects to a PostgreSQL database containing cricket academy data and provides a chat interface for querying the database using natural language. The application operates in READ-ONLY mode and only allows SELECT queries.

## Prerequisites

- Python 3.9+
- PostgreSQL server running with the cricket_academy database
- Cohere API key

## Setup

1. Clone this repository

2. Create and activate a virtual environment:

   **For Windows:**
   ```
   python -m venv venv
   venv\Scripts\activate
   ```

   **For macOS/Linux:**
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your Cohere API key:
   ```
   COHERE_API_KEY=your_cohere_api_key_here
   ```

5. Update the database connection string in `postgres_sql_agent.py` if your PostgreSQL connection details differ:
   ```python
   connection_string = "postgresql://postgres:postgres@localhost:5432/cricket_academy"
   ```

## Testing Database Connection

Before running the main application, you can test your PostgreSQL connection using the provided test script:

```
python test_connection.py
```

This script will verify:
1. Connection using psycopg2 driver
2. Connection using SQLAlchemy
3. List all tables in the database

## Running the Application

Run the Streamlit application:
```
streamlit run postgres_sql_agent.py
```

## Read-Only Mode

This application is configured to work in READ-ONLY mode:

- The agent is instructed to only generate SELECT queries
- An SQLAlchemy event listener prevents execution of modification queries (UPDATE, DELETE, INSERT, ALTER, DROP, TRUNCATE)
- Visual indicators in the UI remind users of read-only status

## Available Tables

Based on the database schema shown in the screenshot, the following tables are available:
- alembic_version
- attendance
- coach
- communication
- payment
- player
- program
- training_session
- user
- whats_app_group
- whats_app_group_member

## Example Queries

You can ask questions like:
- "How many players are registered in the academy?"
- "List all coaches and their specialties"
- "Show me the training sessions scheduled for next week"
- "What's the total revenue from payments in the last month?"
- "Which players have the best attendance records?" 