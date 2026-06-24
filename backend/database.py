import os
import sqlite3
import pandas as pd
import shutil
from fastapi import UploadFile, HTTPException

UPLOAD_DIR = "uploads"
MAX_STORAGE_MB = 100 # Reduced to 100MB to insulate Render instance from high traffic disk consumption

os.makedirs(UPLOAD_DIR, exist_ok=True)

def check_disk_space():
    """Checks if the backend has enough space to accept new files."""
    total, used, free = shutil.disk_usage("/")
    free_mb = free / (1024 * 1024)
    if free_mb < 50: # If total server space drops below 50MB
        raise HTTPException(
            status_code=503, 
            detail="Service temporarily unavailable: Storage capacity reached. Please try again later."
        )

def save_uploaded_file(file: UploadFile, session_id: str):
    check_disk_space()
    
    # Isolate user files in their own session folder
    session_dir = os.path.join(UPLOAD_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)
    
    file_path = os.path.join(session_dir, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return file_path

def create_sqlite_database(file_path: str, session_id: str):
    session_dir = os.path.join(UPLOAD_DIR, session_id)
    db_path = os.path.join(session_dir, f"{session_id}.db")

    try:
        conn = sqlite3.connect(db_path)
        
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
            df.to_sql("data", conn, if_exists="replace", index=False)
            
        elif file_path.endswith(".xlsx"):
            dfs = pd.read_excel(file_path, sheet_name=None)
            for sheet_name, df in dfs.items():
                safe_name = "".join(e for e in sheet_name if e.isalnum() or e == "_")
                df.to_sql(safe_name, conn, if_exists="replace", index=False)
        
        conn.close()
        return db_path
    except Exception as e:
        return None

def extract_schema(db_path: str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    schema = []
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        for column in columns:
            schema.append({
                "table": table_name,
                "name": column[1],
                "type": column[2]
            })
            
    conn.close()
    return schema

def execute_query(db_path: str, query: str):
    try:
        # Enforce read-only state at runtime level via URI configuration
        uri = f"file:{db_path}?mode=ro"
        conn = sqlite3.connect(uri, uri=True, check_same_thread=False)
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df.to_dict(orient="records")
    except Exception as e:
        return str(e)