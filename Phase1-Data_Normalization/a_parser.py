import os
import re
import csv
import argparse
from datetime import datetime
import pandas as pd

# --- ARGUMENT PARSING ---
parser = argparse.ArgumentParser(description="Parse call, message, WhatsApp, and Telegram logs into unified format")
parser.add_argument("-wa", "--waInput", required=True, help="Parsed WhatsApp messages CSV file")
parser.add_argument("-tg", "--tgInput", required=True, help="Parsed Telegram messages CSV file")
parser.add_argument("-cm", "--cmInput", required=True, help="Parsed Calls and Messages CSV file")
parser.add_argument("-o", "--output", required=True, help="Name for output file")
args = parser.parse_args()


OUTPUT_FILE = f"{args.output}"

# CONFIGURATION
# CALLS_FILE = ".\\calls_parsed_output.csv"          # Path to parsed calls CSV
# MESSAGES_FILE = ".\\messages_parsed_output.csv"      # Path to parsed SMS messages CSV
# WHATSAPP_FILE = ".\\whatsapp_parsed_output.csv"  # Parsed WhatsApp
# TELEGRAM_FILE = ".\\telegram_parsed_output.csv"  # Parsed Telegram

CALLS_FILE = args.cm         # Path to parsed calls CSV
MESSAGES_FILE = args.cm    # Path to parsed SMS messages CSV
WHATSAPP_FILE = args.wa # Parsed WhatsApp
TELEGRAM_FILE = args.tg  # Parsed Telegram



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
            row.get("sender", ""),
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


# --- WRITE UNIFIED OUTPUT ---
pd.DataFrame(unified_rows, columns=["chat_id", "source", "sender", "receiver", "timestamp", "message", "direction"]).to_csv(OUTPUT_FILE, index=False)
print(f"Parsed {len(unified_rows)} total entries into {OUTPUT_FILE}.")
