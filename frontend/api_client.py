import requests

class NaturalSQLAPI:

    BASE_URL = "http://127.0.0.1:8000"

    @classmethod
    def ask_question(cls, question: str, api_key: str, session_id: str, schema_data: list):
        response = requests.post(
            f"{cls.BASE_URL}/ask",
            json={
                "question": question,
                "api_key": api_key,
                "session_id": session_id,
                "schema_data": schema_data
            }
        )
        response.raise_for_status()
        return response.json()

    @classmethod
    def upload_file(cls, uploaded_file, session_id: str):
        response = requests.post(
            f"{cls.BASE_URL}/upload",
            files={
                "file": (uploaded_file.name, uploaded_file, uploaded_file.type)
            },
            data={
                "session_id": session_id
            }
        )
        response.raise_for_status()
        return response.json()

    @classmethod
    def execute_sql(cls, query: str, session_id: str):
        response = requests.post(
            f"{cls.BASE_URL}/execute",
            json={
                "query": query,
                "session_id": session_id
            }
        )
        if response.status_code != 200:
            raise Exception(response.json().get("detail", "Unknown error executing query"))
            
        return response.json()