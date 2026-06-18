import requests


class NaturalSQLAPI:

    BASE_URL = "http://127.0.0.1:8000"

    @classmethod
    def ask_question(
        cls,
        question: str
    ):
        response = requests.post(
            f"{cls.BASE_URL}/ask",
            json={
                "question": question
            }
        )

        response.raise_for_status()

        return response.json()

    @classmethod
    def upload_file(
        cls,
        uploaded_file
    ):
        response = requests.post(
            f"{cls.BASE_URL}/upload",
            files={
                "file": (
                    uploaded_file.name,
                    uploaded_file,
                    uploaded_file.type
                )
            }
        )

        response.raise_for_status()

        return response.json()