from pydantic_settings import BaseSettings, SettingsConfigDict
 
 
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
 
    # LLM
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
 
    # Vector store
    chroma_persist_dir: str = "./chroma_db"
    collection_name: str = "documents"
 
    # RAG
    chunk_size: int = 512
    chunk_overlap: int = 64
    top_k_results: int = 4
 
 
settings = Settings()