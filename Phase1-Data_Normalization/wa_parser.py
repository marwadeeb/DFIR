import os
import re
import csv
from datetime import datetime

# CONFIGURATION
# DATA_ROOT = "..\\..\\wa 81663932"  # Root WhatsApp extraction directory
parser.add_argument("-i", "--input", required=True, help="Root WhatsApp extraction directory")

DATA_ROOT = args.input
OUTPUT_FILE = "whatsapp_parsed_output.csv"
USER_NAME = "Forensics11"  # The forensic user's name

# REGEX for parsing WhatsApp messages
MESSAGE_PATTERN = re.compile(r"(\d{1,2}/\d{1,2}/\d{4}), (\d{1,2}:\d{2}) - ([^:]+): (.*)")

# Result container
rows = []

for chat_dir in os.listdir(DATA_ROOT):
    chat_path = os.path.join(DATA_ROOT, chat_dir)
    if not os.path.isdir(chat_path):
        continue

    chat_id = "WA_" + chat_dir.replace("WhatsApp Chat with ", "").replace(" ", "_")
    txt_file_path = os.path.join(chat_path, "all_media.txt")

    if not os.path.isfile(txt_file_path):
        continue

    with open(txt_file_path, "r", encoding="utf-8") as f:
        current_message = ""
        current_sender = ""
        current_time = ""
        current_date = ""

        for line in f:
            match = MESSAGE_PATTERN.match(line)
            if match:
                # save previous message if exists
                if current_message:
                    # print(current_message)
                    timestamp = datetime.strptime((line.split(" - ", 1)[0]), "%d/%m/%Y, %H:%M")
                    direction = "outbound" if current_sender == USER_NAME else "inbound"
                    receiver = USER_NAME if direction == "inbound" else chat_id.split("_")[1]
                    rows.append([
                        chat_id, "WhatsApp", current_sender, receiver,
                        timestamp.isoformat(), current_message.strip(), direction
                    ])

                # new message
                current_date, current_time, current_sender, current_message = match.groups()
                print(current_sender)
            else:
                # continuation of the previous message
                current_message += line

        # append last message
        if current_message:
            timestamp = datetime.strptime(f"{current_date} {current_time}", "%d/%m/%Y %H:%M")
            direction = "outbound" if current_sender == USER_NAME else "inbound"
            receiver = USER_NAME if direction == "inbound" else chat_id.split("_")[1]
            rows.append([
                chat_id, "WhatsApp", current_sender, receiver,
                timestamp.isoformat(), current_message.strip(), direction
            ])

# Write output CSV
with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as out:
    writer = csv.writer(out)
    writer.writerow(["chat_id", "source", "sender", "receiver", "timestamp", "message", "direction"])
    writer.writerows(rows)

print(f"Parsed {len(rows)} messages into {OUTPUT_FILE}")
