import os
import pandas as pd
from datetime import datetime

# CONFIGURATION
EXCEL_FILE = "./2025-11-17_11.38/2025-11-17_11.38/Excel/2025-11-17_11.38.xlsx"
CALLS_SHEET = "Calls"
SMS_SHEET = "Messages SMS"
CALLS_OUTPUT = "calls_parsed_output.csv"
MESSAGES_OUTPUT = "messages_parsed_output.csv"
USER_NAME = "Forensics11"

# --- CALLS PARSER ---
call_rows = []
try:
    df_calls = pd.read_excel(EXCEL_FILE, sheet_name=CALLS_SHEET)
    for _, row in df_calls.iterrows():
        try:
            raw_time = str(row['Time']).split(' (')[0].strip()
            timestamp = pd.to_datetime(raw_time, errors='raise', utc=False).isoformat()

            direction = str(row.get('Direction', '')).capitalize()
            call_type = str(row.get('Call Type', '')).lower()
            duration = row.get('Duration', '')
            tel = str(row.get('Tel', '')).strip()
            to = str(row.get('To', '')).strip()
            from_ = str(row.get('From', '')).strip()

            # Infer direction if not explicitly present
            if not direction or direction.lower() == 'nan':
                direction = "Outgoing" if call_type == "dialed" else "Incoming"

            sender = USER_NAME if direction == "Outgoing" else from_
            receiver = to if direction == "Outgoing" else USER_NAME

            call_rows.append([
                "CALL_LOG", "PhoneCall", sender, receiver, timestamp, f"Call Duration: {duration}", direction.lower()
            ])
        except Exception as e:
            print(f"Skipping call row due to error: {e}")
except Exception as e:
    print(f"Failed to parse calls: {e}")

# --- MESSAGES PARSER ---
msg_rows = []
try:
    df_msgs = pd.read_excel(EXCEL_FILE, sheet_name=SMS_SHEET)
    for _, row in df_msgs.iterrows():
        try:
            timestamp = pd.to_datetime(row['Time']).isoformat()
            direction = str(row.get('Direction', '')).lower()
            tel = str(row.get('Tel', '')).strip()
            from_ = str(row.get('From', '')).strip()
            to = str(row.get('To', '')).strip()
            text = str(row.get('Text', '') or row.get('Summary', '') or row.get('Subject', '')).strip()

            sender = USER_NAME if direction == "outgoing" else from_
            receiver = to if direction == "outgoing" else USER_NAME

            msg_rows.append([
                "SYS_MSG", "SystemMessage", sender, receiver, timestamp, text, direction
            ])
        except Exception as e:
            print(f"Skipping message row due to error: {e}")
except Exception as e:
    print(f"Failed to parse messages: {e}")

# Write outputs
pd.DataFrame(call_rows, columns=["chat_id", "source", "sender", "receiver", "timestamp", "message", "direction"]).to_csv(CALLS_OUTPUT, index=False)
pd.DataFrame(msg_rows, columns=["chat_id", "source", "sender", "receiver", "timestamp", "message", "direction"]).to_csv(MESSAGES_OUTPUT, index=False)

print(f"Parsed {len(call_rows)} calls and {len(msg_rows)} messages successfully.")
