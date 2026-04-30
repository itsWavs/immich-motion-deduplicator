import csv
import os

import requests
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

from .config import get_immich_api_url, load_dotenv, require_env
from .ui import print_summary


def get_asset_lookup(filename, api_url, headers):
    payload = {
        "originalFileName": filename,
        "type": "VIDEO",
    }

    response = requests.post(
        f"{api_url}/search/metadata",
        json=payload,
        headers=headers,
        timeout=30,
    )

    response.raise_for_status()
    data = response.json()
    items = data.get("assets", {}).get("items", [])

    if len(items) == 1:
        return items[0]["id"], "matched"
    if len(items) == 0:
        return None, "not_found"

    return None, "multiple_matches"


def run():
    load_dotenv()
    api_url = get_immich_api_url()
    api_key = require_env("IMMICH_API_KEY")
    input_csv = require_env("MOTION_CANDIDATES_CSV")
    output_csv = require_env("MOTION_CANDIDATES_WITH_IDS_CSV")
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
    }

    with open(input_csv, newline="", encoding="utf-8") as infile:
        rows = list(csv.DictReader(infile))

    if not rows:
        print_summary("ID resolution complete", [("Input rows", 0), ("Matched asset IDs", 0)])
        return 0

    fieldnames = list(rows[0].keys()) + ["asset_id"]
    matched = 0
    not_found = 0
    multiple_matches = 0

    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
    )

    with open(output_csv, "w", newline="", encoding="utf-8") as outfile, progress:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        task_id = progress.add_task("Resolving Immich asset IDs", total=len(rows))

        for row in rows:
            filename = os.path.basename(row["mp4_path"]).upper()
            asset_id, status = get_asset_lookup(filename, api_url, headers)
            row["asset_id"] = asset_id
            writer.writerow(row)
            progress.advance(task_id)

            if status == "matched":
                matched += 1
            elif status == "not_found":
                not_found += 1
            else:
                multiple_matches += 1

    print_summary(
        "ID resolution complete",
        [
            ("Input rows", len(rows)),
            ("Matched asset IDs", matched),
            ("Not found", not_found),
            ("Multiple matches", multiple_matches),
            ("Output file", output_csv),
        ],
    )
    return matched


def main():
    run()


if __name__ == "__main__":
    main()
