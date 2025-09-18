#!/usr/bin/env python3
"""Fetch Azure TTS voices and store them in a local SQLite database.

Usage: python3 backend/save_azure_voices.py

Reads AZURE_TTS_KEY and AZURE_TTS_REGION from the environment or `backend/.env`.
"""
import os
import json
import sqlite3
import requests
from dotenv import load_dotenv

# load backend/.env if present
load_dotenv(dotenv_path='.env')
AZ_KEY = os.environ.get('AZURE_TTS_KEY')
AZ_REGION = os.environ.get('AZURE_TTS_REGION')

if not AZ_KEY or not AZ_REGION:
    raise SystemExit('AZURE_TTS_KEY and AZURE_TTS_REGION must be set in environment or backend/.env')

url = f'https://{AZ_REGION}.tts.speech.microsoft.com/cognitiveservices/voices/list'
headers = {'Ocp-Apim-Subscription-Key': AZ_KEY, 'Content-Type': 'application/json'}
resp = requests.get(url, headers=headers, timeout=30)
resp.raise_for_status()
voices = resp.json()

db_path = 'azure_voices.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute('''
CREATE TABLE IF NOT EXISTS voices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    short_name TEXT,
    name TEXT,
    locale TEXT,
    locale_name TEXT,
    gender TEXT,
    sample_rate_hz INTEGER,
    data JSON
)
''')

# Check if data already exists
cur.execute('SELECT COUNT(*) FROM voices')
count = cur.fetchone()[0]
if count == 0:
    cur.execute('DELETE FROM voices')
    for v in voices:
        short = v.get('ShortName') or v.get('Name')
        name = v.get('Name')
        locale = v.get('Locale')
        locale_name = v.get('LocaleName')
        gender = v.get('Gender')
        sample_rate = v.get('SupportedEngines', [])
        try:
            cur.execute('INSERT INTO voices (short_name,name,locale,locale_name,gender,sample_rate_hz,data) VALUES (?,?,?,?,?,?,?)',
                        (short,name,locale,locale_name,gender,None,json.dumps(v)))
        except Exception as e:
            print('insert failed', e, v.get('ShortName'))

    conn.commit()
    print('Saved', len(voices), 'voices to', db_path)
else:
    print('Data already exists in database, skipping insert')
# show a few rows
for row in cur.execute('SELECT short_name, locale, locale_name FROM voices LIMIT 15'):
    print(row)
conn.close()
