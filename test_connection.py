import psycopg2
from sqlalchemy import create_engine, text
import sys

def test_psycopg2_connection():
    """Test connection using psycopg2 directly."""
    try:
        print("Testing connection with psycopg2...")
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="cricket_academy",
            user="postgres",
            password="postgres"
        )
        cur = conn.cursor()
        cur.execute("SELECT 1")
        result = cur.fetchone()
        if result and result[0] == 1:
            print("✅ psycopg2 connection successful!")
        else:
            print("❌ psycopg2 connection failed")
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ psycopg2 connection error: {str(e)}")
        return False

def test_sqlalchemy_connection():
    """Test connection using SQLAlchemy."""
    try:
        print("Testing connection with SQLAlchemy...")
        connection_string = "postgresql://postgres:postgres@localhost:5432/cricket_academy"
        engine = create_engine(connection_string)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).fetchone()
            if result and result[0] == 1:
                print("✅ SQLAlchemy connection successful!")
            else:
                print("❌ SQLAlchemy connection failed")
        return True
    except Exception as e:
        print(f"❌ SQLAlchemy connection error: {str(e)}")
        return False

def test_tables():
    """List all tables in the database."""
    try:
        print("\nListing available tables...")
        connection_string = "postgresql://postgres:postgres@localhost:5432/cricket_academy"
        engine = create_engine(connection_string)
        with engine.connect() as conn:
            tables = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)).fetchall()
            
            if tables:
                print("Tables found in database:")
                for idx, table in enumerate(tables, 1):
                    print(f"  {idx}. {table[0]}")
            else:
                print("No tables found in database")
        return True
    except Exception as e:
        print(f"❌ Error listing tables: {str(e)}")
        return False

if __name__ == "__main__":
    print("PostgreSQL Connection Test\n" + "="*30)
    
    psycopg2_result = test_psycopg2_connection()
    print()
    sqlalchemy_result = test_sqlalchemy_connection()
    
    if psycopg2_result and sqlalchemy_result:
        print("\n✅ All connection tests passed!")
        test_tables()
        sys.exit(0)
    else:
        print("\n❌ Some connection tests failed")
        sys.exit(1) 