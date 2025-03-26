# SQL Query Assistant

A natural language interface for PostgreSQL databases powered by AWS Bedrock and Claude 3.5 Sonnet. Ask questions about your database in plain English and get results instantly.

## Features

- Natural language queries to PostgreSQL databases
- Secure authentication with AWS Bedrock
- Interactive Streamlit web interface
- Chat-based interaction with query history
- Predefined sample queries
- Input validation to prevent harmful SQL commands

## Requirements

### Python Libraries
```
streamlit>=1.31.0
langchain>=0.1.0
langchain-aws>=0.0.2
langchain-community>=0.0.13
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
python-dotenv>=1.0.0
```

### External Services
- AWS Bedrock (with Claude 3.5 Sonnet access)
- PostgreSQL database

## Setup

1. Clone the repository:
   ```
   git clone [repository-url]
   cd [repository-directory]
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up your environment variables by copying the example file:
   ```
   cp .env.example .env
   ```

4. Edit the `.env` file with your credentials:
   - `COHERE_API_KEY`: Your Cohere API key
   - `LANGSMITH_API_KEY`: Your LangSmith API key
   - `GOOGLE_API_KEY`: Your Google API key
   - `AWS_ACCESS_KEY_ID`: Your AWS access key
   - `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
   - `AWS_REGION`: AWS region (default: us-east-2)
   - `AWS_BEDROCK_MODEL_ID`: AWS Bedrock model ID
   - Database credentials:
     - `DB_USER`: Database username
     - `DB_PASSWORD`: Database password
     - `DB_HOST`: Database host
     - `DB_PORT`: Database port
     - `DB_NAME`: Database name

## Usage

1. Run the application:
   ```
   streamlit run awsclaude_sql_agent.py
   ```

2. Open your browser and navigate to the URL shown in the terminal (typically http://localhost:8501)

3. Ask natural language questions about your database in the chat interface

4. Use the sample queries in the sidebar to get started

## Security Notes

- The application includes input validation to block potentially harmful SQL commands
- API keys and database credentials are stored in the `.env` file, which should never be committed to version control
- Always follow the principle of least privilege when setting up AWS credentials

## Logging

Application logs are stored in `app.log` and include:
- Database connection attempts
- Query executions
- Errors and warnings
