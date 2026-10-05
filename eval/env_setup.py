import sys, os
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parent
REPO_ROOT = EVAL_DIR.parent

# Load keys from AgentLens/.env if python-dotenv is installed (optional in CI)
try:
    from dotenv import load_dotenv
    load_dotenv(REPO_ROOT / ".env")
except ImportError:
    pass


def _find_sentinel() -> str:
    explicit = os.environ.get("SENTINEL_PATH")
    if explicit:
        return explicit
    for candidate in (REPO_ROOT / "Sentinel", REPO_ROOT.parent / "Sentinel"):
        if candidate.is_dir():
            return str(candidate)
    raise RuntimeError(
        "Sentinel not found. Clone it next to AgentLens, or set SENTINEL_PATH."
    )


SENTINEL_PATH = _find_sentinel()
SCENARIOS_DIR = os.path.join(str(EVAL_DIR), "..", "scenarios")

sys.path.insert(0, SENTINEL_PATH)
sys.path.insert(0, str(EVAL_DIR))
sys.path.insert(0, SCENARIOS_DIR)