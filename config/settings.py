import tomllib
import os
from pathlib import Path
from dotenv import load_dotenv

CONFIG_DIR = Path(__file__).resolve().parent
BASE_DIR = CONFIG_DIR.parent
load_dotenv(BASE_DIR / ".env")

with open("config/config.toml", "rb") as file:
    config = tomllib.load(file)

DATABASE_URL = os.getenv("DATABASE_URL")
EXTRACTORS = config["extractors"]
TRANSFORMERS = config["transformers"]
LOADERS = config["loaders"]