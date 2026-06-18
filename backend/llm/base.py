class LLMProvider:

    def generate_sql(
        self,
        question: str,
        schema: str
    ) -> str:
        raise NotImplementedError