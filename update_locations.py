#!/usr/bin/env python3
"""Merge a CSV of trip locations into locations.json.

Usage:
    python update_locations.py            # uses CSV_FILE below
    python update_locations.py csv/other.csv

CSV columns: name,latitude,longitude,dates,attenders,sites,pictures
List columns (dates, attenders, sites) are separated by ';'.

Entries are matched by their "pictures" folder: a matching entry in
locations.json is replaced, otherwise the row is appended.
"""

import csv
import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
CSV_DIR = os.path.join(ROOT, "csv")
JSON_PATH = os.path.join(ROOT, "locations.json")
CSV_FILE = "locations_temp10.csv"  # CSV in csv/ to merge; change this for each new file
LIST_FIELDS = ("dates", "attenders", "sites")
MAX_LINE = 80


def split_list(value):
    return [item.strip() for item in value.split(";") if item.strip()]


def read_csv(path):
    rows = []
    with open(path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if not (row.get("name") or "").strip():
                continue
            entry = {
                "name": row["name"].strip(),
                "latitude": float(row["latitude"]),
                "longitude": float(row["longitude"]),
            }
            for field in LIST_FIELDS:
                entry[field] = split_list(row.get(field) or "")
            entry["pictures"] = (row.get("pictures") or "").strip()
            rows.append(entry)
    return rows


def format_entry(entry):
    """Format one location like the existing file: short lists inline, long ones wrapped."""
    lines = []
    for key, value in entry.items():
        prefix = f"    {json.dumps(key)}: "
        if isinstance(value, list):
            inline = prefix + json.dumps(value, ensure_ascii=False)
            if len(inline) + 1 <= MAX_LINE or not value:
                lines.append(inline)
            else:
                items = ",\n".join(f"      {json.dumps(v, ensure_ascii=False)}" for v in value)
                lines.append(f"{prefix}[\n{items}\n    ]")
        else:
            lines.append(prefix + json.dumps(value, ensure_ascii=False))
    return "  {\n" + ",\n".join(lines) + "\n  }"


def read_json():
    """Return (locations, original text of each entry) so untouched entries keep their formatting."""
    with open(JSON_PATH, encoding="utf-8") as f:
        text = f.read()
    decoder = json.JSONDecoder()
    locations, texts = [], []
    pos = text.index("[") + 1
    while True:
        while pos < len(text) and text[pos] in " \t\r\n,":
            pos += 1
        if text[pos] == "]":
            break
        obj, end = decoder.raw_decode(text, pos)
        locations.append(obj)
        texts.append("  " + text[pos:end])
        pos = end
    return locations, texts


def write_json(texts):
    with open(JSON_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write("[\n" + ",\n".join(texts) + "\n]\n")


def main():
    csv_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(CSV_DIR, CSV_FILE)
    new_rows = read_csv(csv_path)

    locations, texts = read_json()

    index = {loc.get("pictures"): i for i, loc in enumerate(locations)}
    added = updated = 0
    for row in new_rows:
        i = index.get(row["pictures"])
        if i is None:
            index[row["pictures"]] = len(locations)
            locations.append(row)
            texts.append(format_entry(row))
            added += 1
        elif locations[i] != row:
            locations[i] = row
            texts[i] = format_entry(row)
            updated += 1

    write_json(texts)
    print(f"{os.path.basename(csv_path)}: {added} added, {updated} updated "
          f"-> {len(locations)} locations in locations.json")


if __name__ == "__main__":
    main()
