import os
import re
import csv
import argparse
from datetime import datetime
import pandas as pd

# --- ARGUMENT PARSING ---
parser = argparse.ArgumentParser(description="Parse call, message, WhatsApp, and Telegram logs into unified format")
parser.add_argument("-o", "--output", required=True, help="Base name for output file (without extension)")
args = parser.parse_args()

OUTPUT_FILE = f"{args.output}_unified.csv"

# CONFIGURATION
CALLS_FILE = "calls_parsed_output.csv"            # Path to parsed calls CSV
MESSAGES_FILE = "messages_parsed_output.csv"      # Path to parsed SMS messages CSV
WHATSAPP_FILE = "whatsapp_parsed_output.csv"  # Parsed WhatsApp
TELEGRAM_FILE = "telegram_parsed_output.csv"  # Parsed Telegram
USER_NAME = "Forensics11"

unified_rows = []

# --- LOAD FROM FILES IF PRESENT ---
def append_from_file(filepath, source_label):
    if not os.path.isfile(filepath):
        print(f"File not found: {filepath}")
        return
    df = pd.read_csv(filepath)
    for _, row in df.iterrows():
        unified_rows.append([
            row.get("chat_id", source_label),
            row.get("source", source_label),
            row.get("sender", USER_NAME),
            row.get("receiver", ""),
            row.get("timestamp", ""),
            row.get("message", "").strip(),
            row.get("direction", "")
        ])

# Add parsed WhatsApp and Telegram
append_from_file(WHATSAPP_FILE, "WhatsApp")
append_from_file(TELEGRAM_FILE, "Telegram")
append_from_file(CALLS_FILE, "Calls")
append_from_file(MESSAGES_FILE, "SMS")

# # --- CALLS PARSER ---
# if os.path.isfile(CALLS_FILE):
#     df_calls = pd.read_csv(CALLS_FILE)
#     for _, row in df_calls.iterrows():
#         try:
#             raw_time = str(row['timestamp']).split(' (')[0].strip()
#             timestamp = pd.to_datetime(raw_time, errors='raise', utc=False).isoformat()
#             direction = row['Direction'] if 'Direction' in row else ("Outgoing" if row['Call Type'] == "Dialed" else "Incoming")
#             tel = row.get('Tel') or row.get('To') or row.get('From')
#             duration = row.get('Duration', '')
#             other_party = row.get('To') if direction == 'Outgoing' else row.get('From')

#             unified_rows.append([
#                 "CALL_LOG", "PhoneCall", USER_NAME if direction == 'Outgoing' else other_party,
#                 other_party if direction == 'Outgoing' else USER_NAME, timestamp, f"Call Duration: {duration}", direction.lower()
#             ])
#         except Exception as e:
#             print(f"Skipping call row due to error: {e}")

# # --- MESSAGES PARSER ---
# if os.path.isfile(MESSAGES_FILE):
#     df_msgs = pd.read_csv(MESSAGES_FILE)
#     for _, row in df_msgs.iterrows():
#         try:
#             timestamp = pd.to_datetime(row['timestamp']).isoformat()
#             direction = row.get('Direction', '').lower()
#             sender = USER_NAME if direction == 'outgoing' else row.get('From', '')
#             receiver = row.get('To', '') if direction == 'outgoing' else USER_NAME
#             message = row.get('Text', '') or row.get('Summary', '') or row.get('Subject', '')

#             unified_rows.append([
#                 "SYS_MSG", "SystemMessage", sender, receiver, timestamp, message.strip(), direction
#             ])
#         except Exception as e:
#             print(f"Skipping message row due to error: {e}")

# --- WRITE UNIFIED OUTPUT ---
pd.DataFrame(unified_rows, columns=["chat_id", "source", "sender", "receiver", "timestamp", "message", "direction"]).to_csv(OUTPUT_FILE, index=False)
print(f"Parsed {len(unified_rows)} total entries into {OUTPUT_FILE}.")
