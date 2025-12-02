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
parser.add_argument("-c", "--contacts", required=True, help="Excel file containing contacts")
args = parser.parse_args()

INPUT_FILE = args.input
OUTPUT_FILE = args.output

contacts_df = pd.read_excel(args.contacts, sheet_name="Contacts Contacts")
contacts_df['Name'] = contacts_df['Name'].apply(lambda x: x.lower() if isinstance(x, str) else x)
contacts_df['Tel'] = contacts_df['Tel'].apply(lambda x: x.replace('+','') if isinstance(x, str) else x)

contact_map = contacts_df.dropna(subset=["Tel"]).drop_duplicates("Tel").set_index("Tel")["Name"].to_dict()
print(contact_map)

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
    if "tel" in name:
        match = re.search(r"tel(\+?\d+)", name)
        if match:
            name = match.group(1)
        name = normalize_phone(name).replace('+','')
        ## entity resolution
        if name in contact_map:
            name = contact_map[name]
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

# Save cleaned output
df.to_csv(OUTPUT_FILE, index=False)
print(f"Cleaned data saved to {OUTPUT_FILE} with {len(df)} rows.")
