from pathlib import Path
import sys

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
TESTS_DIR = ROOT_DIR / "tests"
ENV_TEST_PATH = ROOT_DIR / ".env.test"

sys.path = [
    str(SRC_DIR),
    str(TESTS_DIR),
    *sys.path,
]

load_dotenv(ENV_TEST_PATH, override=True)
