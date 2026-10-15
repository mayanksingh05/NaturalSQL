import os
import requests
import streamlit as st

class NaturalSQLAPI:
    # Resolve backend URL from environment, Streamlit secrets, or local default
    BASE_URL = (
        os.getenv("BACKEND_URL")
        or (st.secrets.get("BACKEND_URL") if hasattr(st, "secrets") and "BACKEND_URL" in st.secrets else None)
        or "http://127.0.0.1:8000"
    ).rstrip("/")

    TIMEOUT = 90  # 90 seconds timeout for free-tier cloud cold starts

    @classmethod
    def _handle_request_error(cls, exc: Exception) -> str:
        if isinstance(exc, requests.exceptions.ConnectionError):
            return (
                f"Cannot connect to NaturalSQL backend at {cls.BASE_URL}. "
                "If hosted on Render (free tier), the server may be waking up from sleep (takes ~45-60s). "
                "Please wait a moment and try again."
            )
        if isinstance(exc, requests.exceptions.Timeout):
            return "Request timed out waiting for backend response. Please try again."
        return str(exc)

    @classmethod
    def check_health(cls) -> bool:
        """Pings backend health endpoint."""
        try:
            resp = requests.get(f"{cls.BASE_URL}/health", timeout=5)
            return resp.status_code == 200
        except Exception:
            return False

    @classmethod
    def ask_question(cls, question: str, api_key: str, session_id: str, schema_data: list):
        try:
            response = requests.post(
                f"{cls.BASE_URL}/ask",
                json={
                    "question": question,
                    "api_key": api_key,
                    "session_id": session_id,
                    "schema_data": schema_data
                },
                timeout=cls.TIMEOUT
            )
            if response.status_code != 200:
                try:
                    error_detail = response.json().get("detail", response.text)
                except Exception:
                    error_detail = response.text
                raise Exception(error_detail)
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(cls._handle_request_error(e))

    @classmethod
    def upload_file(cls, uploaded_file, session_id: str):
        try:
            response = requests.post(
                f"{cls.BASE_URL}/upload",
                files={
                    "file": (uploaded_file.name, uploaded_file, uploaded_file.type)
                },
                data={
                    "session_id": session_id
                },
                timeout=cls.TIMEOUT
            )
            if response.status_code != 200:
                try:
                    error_detail = response.json().get("detail", response.text)
                except Exception:
                    error_detail = response.text
                raise Exception(error_detail)
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(cls._handle_request_error(e))

    @classmethod
    def execute_sql(cls, query: str, session_id: str):
        try:
            response = requests.post(
                f"{cls.BASE_URL}/execute",
                json={
                    "query": query,
                    "session_id": session_id
                },
                timeout=cls.TIMEOUT
            )
            if response.status_code != 200:
                try:
                    error_detail = response.json().get("detail", response.text)
                except Exception:
                    error_detail = response.text
                raise Exception(error_detail)
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(cls._handle_request_error(e))