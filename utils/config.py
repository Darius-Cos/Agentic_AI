import os
from dotenv import load_dotenv

load_dotenv()

GCP_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "gd-gcp-gridu-genai")
GCP_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-001")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
MCP_FETCH_URL = os.getenv("MCP_FETCH_URL", "http://localhost:8000")
MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "3"))
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "faiss_index")
CORPUS_DIR = os.getenv("CORPUS_DIR", "corpus")
