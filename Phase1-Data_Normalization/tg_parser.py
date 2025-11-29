import os
import re
import csv
from datetime import datetime

# CONFIGURATION
DATA_ROOT = "..\\..\\81663932-telegram\\chats"  # Root Telegram extraction directory
OUTPUT_FILE = "telegram_parsed_output.csv"
USER_NAME = "Forensics11"  # The forensic user's name

# REGEX for Telegram messages
MESSAGE_PATTERN = re.compile(r"\[ID: (\d+)\],\[date:(.*?)\] From: (.*?)\nText: (.*)")



rows = []

for file in os.listdir(DATA_ROOT):
    if not file.endswith(".txt"):
        continue

    chat_name = file.replace(".txt", "")
    chat_id = f"TG_{chat_name}"
    file_path = os.path.join(DATA_ROOT, file)

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        matches = MESSAGE_PATTERN.findall(content)

        senders = {sender for _, _, sender, _ in matches}
        is_group_chat = len(senders) > 2  # More than one sender means group chat
        
        for msg_id, date_str, sender, message in matches:
            try:
                timestamp = datetime.fromisoformat(date_str)
            except ValueError:
                continue  # Skip invalid formats

            if is_group_chat:
                if sender == USER_NAME:
                    direction = "outbound"
                    receiver = chat_name  # Receiver is group name if USER_SELF is sender
                else:
                    direction = "inbound"
                    receiver = chat_name  # Receiver is USER_SELF if someone else is the sender
            else:
                direction = "outbound" if sender == USER_NAME else "inbound"
                receiver = chat_name if direction == "outbound" else USER_NAME

            rows.append([
                chat_id, "Telegram", sender, receiver, timestamp.isoformat(), message.strip(), direction
            ])

# Write output CSV
with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as out:
    writer = csv.writer(out)
    writer.writerow(["chat_id", "source", "sender", "receiver", "timestamp", "message", "direction"])
    writer.writerows(rows)

print(f"Parsed {len(rows)} messages into {OUTPUT_FILE}")
