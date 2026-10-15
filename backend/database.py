import os
import re
import shutil
import sqlite3
from pathlib import Path
import pandas as pd
from fastapi import UploadFile, HTTPException

# Canonical uploads directory at workspace root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
MAX_STORAGE_MB = 100

os.makedirs(UPLOAD_DIR, exist_ok=True)

def check_disk_space():
    """Checks if the backend has enough space to accept new files."""
    try:
        total, used, free = shutil.disk_usage(os.path.abspath(UPLOAD_DIR))
        free_mb = free / (1024 * 1024)
        if free_mb < 50:
            raise HTTPException(
                status_code=503, 
                detail="Service temporarily unavailable: Storage capacity reached. Please try again later."
            )
    except HTTPException:
        raise
    except Exception:
        # Pass gracefully if filesystem disk_usage cannot be determined in certain containers
        pass

def sanitize_session_id(session_id: str) -> str:
    """Validates session ID to prevent path traversal."""
    if not session_id or not re.match(r"^[a-zA-Z0-9_\-]+$", session_id):
        raise HTTPException(status_code=400, detail="Invalid session ID.")
    return session_id

def sanitize_table_name(name: str, default: str = "data") -> str:
    """Sanitizes sheet names into valid SQLite table names."""
    clean = re.sub(r"[^a-zA-Z0-9_]", "_", name.strip()).strip("_")
    if not clean:
        clean = default
    if clean[0].isdigit():
        clean = f"t_{clean}"
    return clean

def save_uploaded_file(file: UploadFile, session_id: str) -> str:
    check_disk_space()
    clean_session_id = sanitize_session_id(session_id)
    
    session_dir = os.path.join(UPLOAD_DIR, clean_session_id)
    os.makedirs(session_dir, exist_ok=True)
    
    # Path traversal protection: extract basename only
    clean_filename = os.path.basename(file.filename)
    file_path = os.path.join(session_dir, clean_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return file_path

def create_sqlite_database(file_path: str, session_id: str) -> str:
    clean_session_id = sanitize_session_id(session_id)
    session_dir = os.path.join(UPLOAD_DIR, clean_session_id)
    db_path = os.path.join(session_dir, f"{clean_session_id}.db")

    try:
        lower_path = file_path.lower()

        # 1. CSV File
        if lower_path.endswith(".csv"):
            try:
                df = pd.read_csv(file_path, encoding="utf-8")
            except UnicodeDecodeError:
                df = pd.read_csv(file_path, encoding="latin1")

            conn = sqlite3.connect(db_path)
            df.to_sql("data", conn, if_exists="replace", index=False)
            conn.close()

        # 2. Excel File (.xlsx, .xls)
        elif lower_path.endswith((".xlsx", ".xls")):
            dfs = pd.read_excel(file_path, sheet_name=None)
            if not dfs:
                raise ValueError("Excel file contains no readable sheets.")

            conn = sqlite3.connect(db_path)
            for idx, (sheet_name, df) in enumerate(dfs.items()):
                table_name = sanitize_table_name(sheet_name, default=f"sheet_{idx+1}")
                df.to_sql(table_name, conn, if_exists="replace", index=False)
            conn.close()

        # 3. SQLite Database File (.db, .sqlite, .sqlite3)
        elif lower_path.endswith((".db", ".sqlite", ".sqlite3")):
            if os.path.abspath(file_path) != os.path.abspath(db_path):
                shutil.copyfile(file_path, db_path)

            # Validate that the copied file is indeed a readable SQLite database
            test_conn = sqlite3.connect(db_path)
            test_cursor = test_conn.cursor()
            test_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = test_cursor.fetchall()
            test_conn.close()

            if not tables:
                raise ValueError("Uploaded SQLite database contains no user tables.")

        else:
            raise ValueError("Unsupported file format. Please upload CSV, Excel, or SQLite DB.")

        return db_path

    except Exception as e:
        # Cleanup incomplete database file on failure
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
            except Exception:
                pass
        raise HTTPException(status_code=400, detail=f"Failed to process file: {str(e)}")

def extract_schema(db_path: str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Exclude internal SQLite metadata tables
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name NOT LIKE 'sqlite_%';
    """)
    tables = cursor.fetchall()
    
    schema = []
    for table in tables:
        table_name = table[0]
        # Quote table name in PRAGMA query to handle special characters or names
        cursor.execute(f'PRAGMA table_info("{table_name}")')
        columns = cursor.fetchall()
        for column in columns:
            schema.append({
                "table": table_name,
                "name": column[1],
                "type": column[2] or "TEXT"
            })
            
    conn.close()
    return schema

def execute_query(db_path: str, query: str):
    try:
        # Cross-platform URI formatting: Works seamlessly on Windows, Linux, and macOS
        resolved_uri = Path(db_path).resolve().as_uri() + "?mode=ro"
        conn = sqlite3.connect(resolved_uri, uri=True, check_same_thread=False)

        df = pd.read_sql_query(query, conn)
        conn.close()

        # Guard against memory exhaustion: limit to 5000 rows
        if len(df) > 5000:
            df = df.head(5000)

        return df.to_dict(orient="records")
    except Exception as e:
        return str(e)