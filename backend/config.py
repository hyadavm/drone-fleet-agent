import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    PROJECT_NAME: str = "Autonomous Drone Fleet Inspection"
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    LANGSMITH_TRACING: bool = os.getenv("LANGSMITH_TRACING", "false").lower() == "true"
    LANGSMITH_API_KEY: str = os.getenv("LANGSMITH_API_KEY", "")
    
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    SAMPLE_IMAGES_DIR: str = os.path.join(DATA_DIR, "sample_images")
    KNOWLEDGE_BASE_DIR: str = os.path.join(DATA_DIR, "knowledge_base")
    
    HIGH_CONFIDENCE_THRESHOLD: float = 0.75

settings = Settings()
