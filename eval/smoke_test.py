import sys
sys.path.insert(0, r"C:\Users\MSI\Desktop\ahmedaskri\Sentinel")
sys.path.insert(0, r"C:\Users\MSI\Desktop\ahmedaskri\agentlens\eval")

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from incident_db import init_db
from notifiers import build_notifier
from agent.tools import build_tools
from agent.graph import build_graph
from config import NOTIFY_METHOD, WEBHOOK_URL
from seed import seed_history

init_db()

# Seed 2 confirmed-false incidents for cam_02 / smoking_detected
seed_history("cam_02", "smoking_detected", ["confirmed_false", "confirmed_false"])

notifier = build_notifier(NOTIFY_METHOD, WEBHOOK_URL)
tools = build_tools(notifier)
graph = build_graph(tools, checkpointer=MemorySaver())

result = graph.invoke(
    {"messages": [HumanMessage(content="New detection event: camera cam_02 flagged 'smoking_detected' (confidence 0.85). Decide what to do.")]},
    {"configurable": {"thread_id": "smoke-test-2"}},
)

print(result["messages"][-1].content)