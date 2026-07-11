"""Main entry point for EdgeAgent."""
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from agent.agent import main

if __name__ == "__main__":
    main()