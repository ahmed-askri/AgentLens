import sys, os

SENTINEL_PATH = os.environ.get("SENTINEL_PATH", r"C:\Users\MSI\Desktop\ahmedaskri\Sentinel")
EVAL_DIR = os.path.dirname(os.path.abspath(__file__))
SCENARIOS_DIR = os.path.join(EVAL_DIR, "..", "scenarios")

sys.path.insert(0, SENTINEL_PATH)
sys.path.insert(0, EVAL_DIR)
sys.path.insert(0, SCENARIOS_DIR)