import os
import re
import csv
import argparse
from datetime import datetime
import pandas as pd

# --- ARGUMENT PARSING ---
parser = argparse.ArgumentParser(description="Phase 3: Entity Resolution")
parser.add_argument("-i", "--input", required=True, help="Input CSV file (cleaned and normalized)")
parser.add_argument("-o", "--output", required=True, help="Output CSV file with entity resolution")
parser.add_argument("--contact_map", help="Optional JSON file with manual contact mappings")
args = parser.parse_args()

INPUT_FILE = args.input
OUTPUT_FILE = args.output
CONTACT_MAP_FILE = args.contact_map

SELF_NAME = "Forensics11"

# --- LOAD CONTACT MAP IF AVAILABLE ---
contact_map = {}
if CONTACT_MAP_FILE and os.path.isfile(CONTACT_MAP_FILE):
    import json
    with open(CONTACT_MAP_FILE, "r", encoding="utf-8") as f:
        contact_map = json.load(f)

# --- LOAD INPUT ---
df = pd.read_csv(INPUT_FILE)

# --- EXTRACT UNIQUE IDENTIFIERS ---
raw_contacts = set(df['sender'].unique().tolist() + df['receiver'].unique().tolist())
raw_contacts.discard(SELF_NAME)

resolved_map = {}

# --- RULE-BASED NORMALIZATION ---
def normalize_identifier(identifier):
    if not isinstance(identifier, str):
        return identifier
    identifier = identifier.strip().lower()
    identifier = re.sub(r"^tel:\s*", "", identifier)
    identifier = re.sub(r"[^\w+]+", "", identifier)  # remove symbols
    return identifier

for raw_id in raw_contacts:
    norm = normalize_identifier(raw_id)
    resolved = contact_map.get(raw_id) or contact_map.get(norm) or norm
    resolved_map[raw_id] = resolved

# --- APPLY MAPPING ---
df['sender_resolved'] = df['sender'].apply(lambda x: SELF_NAME if x == SELF_NAME else resolved_map.get(x, normalize_identifier(x)))
df['receiver_resolved'] = df['receiver'].apply(lambda x: SELF_NAME if x == SELF_NAME else resolved_map.get(x, normalize_identifier(x)))

# --- SAVE OUTPUT ---
df.to_csv(OUTPUT_FILE, index=False)
print(f"Resolved {len(resolved_map)} unique entities and saved to {OUTPUT_FILE}.")
