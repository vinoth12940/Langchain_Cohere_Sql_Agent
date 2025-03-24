# Cricket Academy SQL Agent

This application provides a chat interface to query a PostgreSQL cricket academy database using natural language. The application uses large language models to translate natural language queries into SQL and present the results in a readable format.

## Features

- Natural language to SQL conversion
- Read-only database access (prevents modification queries)
- Interactive chat interface with Streamlit
- Support for multiple LLM providers (Cohere and Google Gemini)
- Query history and thought process visibility
- Database schema visibility in the sidebar

## Prerequisites

- Python 3.8 or higher
- PostgreSQL database (with cricket_academy schema)
- API keys for Cohere and/or Google Gemini

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/cricket-academy-sql-agent.git
cd cricket-academy-sql-agent
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with your API keys:
```
COHERE_API_KEY=your_cohere_api_key
GOOGLE_API_KEY=your_google_api_key
LANGSMITH_API_KEY=your_langsmith_api_key
```

5. Make sure you have a PostgreSQL database named `cricket_academy` running with user `postgres` and password `postgres`. Update the connection string in the code if your configuration is different.

## Usage

### Cohere SQL Agent

Run the Cohere version of the SQL agent:

```bash
streamlit run postgres_sql_agent.py
```

### Gemini SQL Agent

Run the Google Gemini version of the SQL agent:

```bash
streamlit run gemini_sql_agent.py
```

### Interacting with the Application

1. Once the application is running, you'll see a chat interface.
2. Type your questions about the cricket academy database in natural language.
3. The agent will convert your question into SQL, execute it, and return the results.
4. You can view the database schema and available tables in the sidebar.
5. Expand the "See agent's thought process" section to view the step-by-step reasoning.

## Example Queries

- "How many players are registered in the academy?"
- "List all coaches and their specializations."
- "What is the average attendance rate for training sessions in the last month?"
- "Show me the top 5 players with the highest batting average."

## Security Note

This application operates in READ-ONLY mode by design. The database connection is configured to reject any modification queries (INSERT, UPDATE, DELETE, ALTER, DROP, TRUNCATE) as a security measure.

## License

MIT
