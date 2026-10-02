import sys, time, sqlite3
import mlflow
import env_setup
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from incident_db import init_db, DB_PATH
from notifiers import build_notifier
from agent.tools import build_tools
from agent.graph import build_graph
from config import NOTIFY_METHOD, WEBHOOK_URL
from seed import seed_history
from scenarios import SCENARIOS


def clear_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM incidents")
    conn.commit()
    conn.close()


def determine_decision(messages) -> str:
    tool_names = set()
    for m in messages:
        for tc in (getattr(m, "tool_calls", None) or []):
            tool_names.add(tc["name"])
    if "escalate_to_security" in tool_names:
        return "escalate"
    if "flag_for_human_review" in tool_names:
        return "human_review"
    return "no_escalate"


def build_prompt(scenario):
    text = (
        f"New detection event: camera {scenario['camera_id']} flagged "
        f"'{scenario['event_type']}' (confidence {scenario['confidence']}, "
        f"{scenario['timestamp']}). "
    )
    if scenario.get("note_in_prompt"):
        text += scenario["note_in_prompt"] + " "
    text += "Decide what to do."
    return text


def run_scenario(scenario, tools):
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
        {"configurable": {"thread_id": f"eval-{scenario['id']}"}},
    )
    actual = determine_decision(result["messages"])
    reasoning = result["messages"][-1].content
    return actual, reasoning


def main():
    init_db()
    

    notifier = build_notifier(NOTIFY_METHOD, WEBHOOK_URL)
    tools = build_tools(notifier)

    passed, failed, ambiguous, errored = 0, 0, 0, 0
    print(f"{'ID':32} {'EXPECTED':10} {'ACTUAL':10} RESULT")
    print("-" * 75)

    for scenario in SCENARIOS:
        try:
            actual, reasoning = run_scenario(scenario, tools)
        except Exception as e:
            errored += 1
            print(f"{scenario['id']:32} {'--':10} {'--':10} ERROR ({type(e).__name__})")
            time.sleep(2)
            continue

        expected = scenario["expected_decision"]
        if expected == "AMBIGUOUS":
            ambiguous += 1
            result = "REVIEW"
        elif actual == expected:
            passed += 1
            result = "PASS"
        else:
            failed += 1
            result = "FAIL"

        print(f"{scenario['id']:32} {expected:10} {actual:10} {result}")
        time.sleep(2)

    scored = passed + failed
    print("-" * 75)
    print(f"Score: {passed}/{scored} correct  ({ambiguous} flagged for review, {errored} errored)")

    with mlflow.start_run():
        mlflow.log_param("model", "openai/gpt-oss-20b")
        mlflow.log_param("num_scenarios", len(SCENARIOS))
        mlflow.log_metric("passed", passed)
        mlflow.log_metric("failed", failed)
        mlflow.log_metric("ambiguous", ambiguous)
        mlflow.log_metric("errored", errored)
        mlflow.log_metric("pass_rate", passed / scored if scored else 0)


if __name__ == "__main__":
    main()