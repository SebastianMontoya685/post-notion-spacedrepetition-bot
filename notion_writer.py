#!/usr/bin/env python3
"""
notion_writer.py
Creates new spaced-rep entries in Notion.
"""
import os, sys, json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_API_KEY")
DB_IDS       = os.getenv("NOTION_DATABASE_IDS", "").split(",")

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

def make_payload(theme, date_str):
    # compute R1–R4 offsets here
    r_offsets = [1, 3, 7, 14]
    payload = {
        "parent": { "database_id": "" },  # fill in per loop
        "properties": {
            "Theme of the Study": {
                "title": [{"text": {"content": theme}}]
            },
            "Date of Studying": {
                "date": {"start": date_str}
            },
        }
    }
    # add R1..R4 dates
    for i, offset in enumerate(r_offsets, start=1):
        key = f"R{i}"
        when = (datetime.fromisoformat(date_str) + timedelta(days=offset)).isoformat()
        payload["properties"][key] = {"date": {"start": when}}
    return payload

def post_to_db(db_id, theme, date_str):
    payload = make_payload(theme, date_str)
    payload["parent"]["database_id"] = db_id
    resp = requests.post("https://api.notion.com/v1/pages",
                         headers=HEADERS, data=json.dumps(payload))
    if resp.ok:
        print(f"→ Created: {resp.json()['url']}")
    else:
        print("⚠️ Error:", resp.status_code, resp.text)

def main():
    if len(sys.argv) < 3:
        print("Usage: python notion_writer.py <theme> <YYYY-MM-DD>")
        sys.exit(1)
    theme, date_str = sys.argv[1], sys.argv[2]
    for db in DB_IDS:
        post_to_db(db, theme, date_str)

if __name__ == "__main__":
    main()
