"""
=========================================================
BHARATAI - Global Configuration
Version : 1.0.0
Author  : Manpreet Singh
=========================================================
"""

from pathlib import Path
from dotenv import load_dotenv
import os

# -------------------------------------------------------
# PROJECT PATHS
# -------------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parent.parent

CONFIG_DIR = ROOT_DIR / "config"
AGENTS_DIR = ROOT_DIR / "agents"
CORE_DIR = ROOT_DIR / "core"
MEMORY_DIR = ROOT_DIR / "memory"
MODELS_DIR = ROOT_DIR / "models"
RAG_DIR = ROOT_DIR / "rag"
SKILLS_DIR = ROOT_DIR / "skills"
TOOLS_DIR = ROOT_DIR / "tools"
PLUGINS_DIR = ROOT_DIR / "plugins"
SERVICES_DIR = ROOT_DIR / "services"
UI_DIR = ROOT_DIR / "ui"
TESTS_DIR = ROOT_DIR / "tests"
DOCS_DIR = ROOT_DIR / "docs"

LOGS_DIR = ROOT_DIR / "logs"
DATA_DIR = ROOT_DIR / "data"
VECTOR_DB_DIR = ROOT_DIR / "data" / "chroma_db"

LOGS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------
# ENVIRONMENT VARIABLES
# -------------------------------------------------------

load_dotenv(ROOT_DIR / ".env")

# Optional Cloud APIs
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# -------------------------------------------------------
# APPLICATION
# -------------------------------------------------------

APP_NAME = "BharatAI"

VERSION = "1.0.0"

DEBUG = True
APP_NAME = "BharatAI"

VERSION = "1.0.0"

DEBUG = True

LOCAL_MODE = True
# -------------------------------------------------------
# OLLAMA
# -------------------------------------------------------
"""
=========================================================
BHARATAI - Global Configuration
Version : 1.0.0
Author  : Manpreet Singh
=========================================================
"""

from pathlib import Path
from dotenv import load_dotenv
import os

# -------------------------------------------------------
# PROJECT PATHS
# -------------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parent.parent

CONFIG_DIR = ROOT_DIR / "config"
AGENTS_DIR = ROOT_DIR / "agents"
CORE_DIR = ROOT_DIR / "core"
MEMORY_DIR = ROOT_DIR / "memory"
MODELS_DIR = ROOT_DIR / "models"
RAG_DIR = ROOT_DIR / "rag"
SKILLS_DIR = ROOT_DIR / "skills"
TOOLS_DIR = ROOT_DIR / "tools"
PLUGINS_DIR = ROOT_DIR / "plugins"
SERVICES_DIR = ROOT_DIR / "services"
UI_DIR = ROOT_DIR / "ui"
TESTS_DIR = ROOT_DIR / "tests"
DOCS_DIR = ROOT_DIR / "docs"

LOGS_DIR = ROOT_DIR / "logs"
DATA_DIR = ROOT_DIR / "data"
VECTOR_DB_DIR = ROOT_DIR / "data" / "chroma_db"

LOGS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------
# ENVIRONMENT VARIABLES
# -------------------------------------------------------

load_dotenv(ROOT_DIR / ".env")

# Optional Cloud APIs
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# -------------------------------------------------------
# APPLICATION
# -------------------------------------------------------

APP_NAME = "BharatAI"

VERSION = "1.0.0"

DEBUG = True
APP_NAME = "BharatAI"

VERSION = "1.0.0"

DEBUG = True

LOCAL_MODE = True
# -------------------------------------------------------
# OLLAMA
# -------------------------------------------------------

OLLAMA_HOST = "http://localhost:11434"

# -------------------------------------------------------
# MODELS
# -------------------------------------------------------

# Default fallback model
DEFAULT_MODEL = "qwen2.5:1.5b"

# General chat
FAST_MODEL = "qwen2.5:1.5b"

# Planning
PLANNING_MODEL = "qwen2.5:1.5b"

# Research
RESEARCH_MODEL = "qwen2.5:1.5b"

# Coding
CODING_MODEL = "qwen2.5:1.5b"

# Classification
SMALL_MODEL = "qwen2.5:1.5b"

# -------------------------------------------------------
# TIMEOUTS
# -------------------------------------------------------

CLASSIFICATION_TIMEOUT = 5.0
FAST_TIMEOUT = 10.0

CODING_TIMEOUT = 20.0
PLANNING_TIMEOUT = 20.0
RESEARCH_TIMEOUT = 20.0
SYNTHESIS_TIMEOUT = 20.0

ENABLE_GEMINI_TIMEOUT_FALLBACK = False

# Only one heavy model at a time
MAX_HEAVY_MODEL_CONCURRENCY = 1

# -------------------------------------------------------
# RAG
# -------------------------------------------------------

EMBEDDING_MODEL = "nomic-embed-text"

CHUNK_SIZE = 1000

CHUNK_OVERLAP = 150

TOP_K = 5

# -------------------------------------------------------
# STREAMLIT
# -------------------------------------------------------

PAGE_TITLE = "BharatAI"

PAGE_ICON = "⚡"

LAYOUT = "wide"

# -------------------------------------------------------
# AGENTS
# -------------------------------------------------------

MAX_AGENTS = 30

MAX_PARALLEL_AGENTS = 6

MAX_RETRY = 3

# -------------------------------------------------------
# MEMORY
# -------------------------------------------------------

ENABLE_MEMORY = True

ENABLE_PROJECT_MEMORY = True

ENABLE_USER_MEMORY = True

ENABLE_SESSION_MEMORY = True

# -------------------------------------------------------
# LOGGING
# -------------------------------------------------------

LOG_LEVEL = "INFO"

LOG_FILE = LOGS_DIR / "bharatai.log"

# -------------------------------------------------------
# SECURITY
# -------------------------------------------------------

ALLOW_CODE_EXECUTION = False

ALLOW_SHELL_COMMANDS = False

ALLOW_FILE_DELETE = False

SAFE_MODE = True

# -------------------------------------------------------
# COLORS
# -------------------------------------------------------

PRIMARY_COLOR = "#4F46E5"

SUCCESS_COLOR = "#10B981"

WARNING_COLOR = "#F59E0B"

ERROR_COLOR = "#EF4444"

# -------------------------------------------------------
# BANNER
# -------------------------------------------------------

BANNER = f"""
==========================================
        {APP_NAME}
        Version {VERSION}
==========================================
"""
