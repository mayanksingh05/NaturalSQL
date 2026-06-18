import os
import sqlite3
import pandas as pd
from fastapi import UploadFile

UPLOAD_DIR = "uploads"

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)


def save_uploaded_file(
    file: UploadFile
):
    file_path = os.path.join(
        UPLOAD_DIR,
        file.filename
    )

    with open(file_path, "wb") as buffer:
        buffer.write(
            file.file.read()
        )

    return file_path


def create_sqlite_database(
    file_path: str
):
    db_path = f"{file_path}.db"

    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)

    elif file_path.endswith(".xlsx"):
        df = pd.read_excel(file_path)

    else:
        return None

    conn = sqlite3.connect(db_path)

    df.to_sql(
        "data",
        conn,
        if_exists="replace",
        index=False
    )

    conn.close()

    return db_path