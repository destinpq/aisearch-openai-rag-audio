"""Simple sqlite helper moved from nested app."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / 'app_data.db'

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    return conn
