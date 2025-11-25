import os
import re
import csv
import argparse
from datetime import datetime
import pandas as pd
import phonenumbers

# --- ARGUMENT PARSING ---
parser = argparse.ArgumentParser(description="Clean and normalize unified forensic dataset")
parser.add_argument("-i", "--input", required=True, help="Unified input CSV file")
parser.add_argument("-o", "--output", required=True, help="Output CSV filename")
args = parser.parse_args()

INPUT_FILE = args.input
OUTPUT_FILE = args.output

# --- HELPER FUNCTIONS ---
def normalize_phone(val):
    if not isinstance(val, str): return val
    val = val.strip().replace("Tel:", "").replace(" ", "")
    try:
        number = phonenumbers.parse(val, "LB")  # LB = Lebanon default region
        return phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)
    except:
        return val.lower().strip()

def normalize_name(name):
    if not isinstance(name, str): return name
    name = name.strip().lower()
    name = re.sub(r'[^a-z0-9+@._-]', '', name)
    if name in ["me", "you", "forensics11"]:
        return "USER_SELF"
    return name

def clean_message(msg):
    if not isinstance(msg, str): return ""
    return msg.strip()

# --- CLEANING LOGIC ---
df = pd.read_csv(INPUT_FILE)

required_cols = ["sender", "receiver", "timestamp", "message", "source", "direction"]
for col in required_cols:
    if col not in df.columns:
        raise Exception(f"Missing required column: {col}")

# Clean and normalize columns
df['sender'] = df['sender'].apply(normalize_name)
df['receiver'] = df['receiver'].apply(normalize_name)
df['message'] = df['message'].apply(clean_message)

# Drop empty messages, system notifications, missing timestamps
df.dropna(subset=['timestamp'], inplace=True)
df = df[~df['message'].str.contains("end-to-end encrypted", case=False, na=False)]
df = df[df['message'].str.strip() != ""]

# Parse timestamps
def parse_time(ts):
    try:
        return pd.to_datetime(ts, utc=True, errors='coerce')
    except:
        return pd.NaT

df['timestamp'] = df['timestamp'].apply(parse_time)
df.dropna(subset=['timestamp'], inplace=True)

# Communication type inference
def infer_comm_type(row):
    src = row['source'].lower()
    if 'whatsapp' in src:
        return 'whatsapp'
    if 'telegram' in src:
        return 'telegram'
    if 'call' in src:
        return 'call'
    if 'sms' in src:
        return 'sms'
    if 'system' in src:
        return 'system_message'
    return 'unknown'

df['comm_type'] = df.apply(infer_comm_type, axis=1)

# Save cleaned output
df.to_csv(OUTPUT_FILE, index=False)
print(f"Cleaned data saved to {OUTPUT_FILE} with {len(df)} rows.")
