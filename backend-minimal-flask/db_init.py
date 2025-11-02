"""
Database initialization script
Creates SQLite database and tables for MFA demo
"""
from auth_core import AuthCore

def init_database():
    """Initialize the database"""
    print("Initializing database...")
    auth = AuthCore()
    print("Database initialization complete!")

if __name__ == '__main__':
    init_database()
