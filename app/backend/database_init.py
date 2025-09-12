#!/usr/bin/env python3
"""
Database initialization script for the service-based user management system
"""

import sqlite3
import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def initialize_database():
    """Initialize the user management database"""
    
    # Database file path
    db_path = backend_dir / "user_management.db"
    
    # Read schema from file
    schema_path = backend_dir / "database_schema.sql"
    
    if not schema_path.exists():
        print(f"Error: Schema file not found at {schema_path}")
        return False
    
    try:
        # Read the schema
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        # Connect to database
        conn = sqlite3.connect(str(db_path))
        
        # Execute schema
        conn.executescript(schema_sql)
        
        # Commit and close
        conn.commit()
        conn.close()
        
        print(f"✅ Database initialized successfully at {db_path}")
        print(f"📊 Tables created:")
        print("   - users")
        print("   - subscription_tiers") 
        print("   - services")
        print("   - user_services")
        print("   - usage_logs")
        print("   - billing_history")
        
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

if __name__ == "__main__":
    success = initialize_database()
    sys.exit(0 if success else 1)
