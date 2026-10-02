import env_setup
import time, pytest
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from incident_db import init_db
from notifiers import build_notifier
from agent.tools import build_tools
from agent.graph import build_graph
from config import NOTIFY_METHOD, WEBHOOK_URL
from seed import seed_history
from scenarios import SCENARIOS
from runner import clear_db, determine_decision, build_prompt

init_db()
notifier = build_notifier(NOTIFY_METHOD, WEBHOOK_URL)
tools = build_tools(notifier)

SCORED_SCENARIOS = [s for s in SCENARIOS if s["expected_decision"] != "AMBIGUOUS"]


@pytest.mark.parametrize("scenario", SCORED_SCENARIOS, ids=[s["id"] for s in SCORED_SCENARIOS])
def test_sentinel_decision(scenario):
    time.sleep(2)  # stay under Groq's per-minute token limit
    clear_db()

    if scenario.get("history"):
        decisions = [h["decision"] for h in scenario["history"]]
        seed_history(scenario["camera_id"], scenario["event_type"], decisions)
    if scenario.get("seed_other_camera"):
        other = scenario["seed_other_camera"]
        seed_history(other["camera_id"], other["event_type"], other["decisions"])

    graph = build_graph(tools, checkpointer=MemorySaver())
    prompt = build_prompt(scenario)
    result = graph.invoke(
        {"messages": [HumanMessage(content=prompt)]},
        {"configurable": {"thread_id": f"ci-{scenario['id']}"}},
    )
    actual = determine_decision(result["messages"])
    assert actual == scenario["expected_decision"], (
        f"expected {scenario['expected_decision']}, got {actual}"
    )