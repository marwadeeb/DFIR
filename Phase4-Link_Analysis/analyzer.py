import os
import argparse
from openai import OpenAI

# -----------------------------
# Config
# -----------------------------

# You can set OPENROUTER_API_KEY as an environment variable,
# or hardcode it here (not recommended for real setups).
# API_KEY = os.getenv("OPENROUTER_API_KEY", "<OPENROUTER_API_KEY>")

API_KEY="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"
MODEL_NAME = "openai/gpt-oss-20b:free"


# -----------------------------
# Helper: load GML file
# -----------------------------

def load_gml(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# -----------------------------
# Build contents for chat
# -----------------------------

def build_contents(gml_text: str) -> list:

    # Main instructions to the model
    main_prompt = (
        "You are a forensic link analysis assistant working on a digital investigation.\n\n"
        "You are given a communication graph in GML format. Nodes represent people, phone numbers, "
        "or groups; edges represent communications (messages, calls, SMS) between them.\n\n"
        "Conventions:\n"
        "- The node labeled 'USER_SELF' is the root subject of the investigation.\n"
        "- Some nodes represent groups (e.g., project/work groups); these often appear as nodes "
        "connected to multiple distinct persons.\n"
        "- Edges contain a 'messages' attribute that may include messages, calls, or SMS metadata.\n\n"
        "Your tasks:\n"
        "1. At a zoomed-out level (do NOT go line-by-line through every message), infer the relationship "
        "type between USER_SELF and each other node (e.g., parent/child, sibling, close friend, coworker, manager, "
        "client, unknown, or possibly suspicious/criminal associate).\n"
        "2. Identify which nodes are most likely:\n"
        "   - family members,\n"
        "   - work colleagues or project collaborators,\n"
        "   - purely logistical/utility contacts,\n"
        "   - group nodes and what their purpose likely is.\n"
        "3. Use the content of messages (including those about drives, versions, sanitized files, metadata, etc.) "
        "plus call/SMS patterns to infer context: what kind of work or activity is going on around USER_SELF.\n"
        "4. Identify any communication patterns or content that might be suspicious from a forensic perspective. "
        "Explain *why* they are suspicious.\n"
        "5. Summarize your findings in a structured way, for example:\n"
        "   - A table-like summary (in text) of each node versus USER_SELF with inferred relationship and confidence\n"
        "   - A short narrative describing the overall social/organizational structure\n"
        "   - A short section of hypotheses for investigators (e.g., which relationships or nodes deserve closer review).\n\n"
        "Important:\n"
        "- Work at a coarse-grained, relationship level; do not just repeat raw messages.\n"
        "- It is okay to make reasoned hypotheses as long as you mark them as such.\n"
        "- If something cannot be inferred with reasonable confidence, say so.\n"
    )

    # # Optionally truncate GML if extremely large (safety)
    # max_chars = 20000
    # if len(gml_text) > max_chars:
    #     gml_for_model = gml_text[:max_chars] + "\n... [GML truncated] ..."
    # else:
    #     gml_for_model = gml_text

    # Attach the GML as a separate text part 
    gml_part = (
        "Below is the graph in GML format. Use it as your data source for the analysis:\n\n"
        "----- BEGIN GML -----\n"
        f"{gml_text}\n"
        "----- END GML -----"
    )

    contents = [
        {"type": "text", "text": main_prompt},
        {"type": "text", "text": gml_part},
    ]

    return contents


# -----------------------------
# Main
# -----------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Send graph.gml and a forensic analysis prompt to an LLM via OpenRouter."
    )
    parser.add_argument(
        "-g", "--gml",
        required=True,
        help="Path to the GML file (e.g., graph.gml)"
    )
    parser.add_argument(
        "-m", "--model",
        default=MODEL_NAME,
        help=f"Model name to use (default: {MODEL_NAME})"
    )
    args = parser.parse_args()

    if API_KEY is None or API_KEY == "<OPENROUTER_API_KEY>":
        print("❌ Please set your OPENROUTER_API_KEY environment variable or edit API_KEY in the script.")
        return

    # Load GML content
    if not os.path.isfile(args.gml):
        print(f"❌ GML file not found: {args.gml}")
        return

    gml_text = load_gml(args.gml)

    # Build multi-part content
    contents = build_contents(gml_text)

    # Create OpenRouter client (OpenAI-compatible)
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=API_KEY,
    )

    print("🧠 Sending graph and prompt to model for high-level relationship analysis...")

    try:
        response = client.chat.completions.create(
            model=args.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a digital forensics and link-analysis expert assisting investigators."
                },
                {
                    "role": "user",
                    "content": contents
                }
            ],
            # # optional: enable reasoning if the model supports it
            # extra_body={"reasoning": {"enabled": True}},
        )

        assistant_message = response.choices[0].message
        # For OpenRouter / openai client, content is typically assistant_message.content
        print("\n===== MODEL ANALYSIS =====\n")
        print(assistant_message.content)

    except Exception as e:
        print(f"❌ Error calling model: {e}")


if __name__ == "__main__":
    main()
