class Embedder:
    def embed(self, texts: list[str]) -> list[list[float]]:
        # Embedding provider abstraction (OpenAI default) lands in later phases.
        return [[0.0] for _ in texts]
