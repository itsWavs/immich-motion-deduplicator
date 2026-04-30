import csv
import os

import requests

from .config import get_immich_api_url, load_dotenv, require_env


INPUT_CSV = "motion_candidates.csv"
OUTPUT_CSV = "motion_candidates_with_ids.csv"


def get_asset_id(filename, api_url, headers):
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
        return items[0]["id"]
    if len(items) == 0:
        print(f"[NOT FOUND] {filename}")
        return None

    print(f"[MULTIPLE MATCHES] {filename}")
    return None


def run(input_csv=INPUT_CSV, output_csv=OUTPUT_CSV):
    load_dotenv()
    api_url = get_immich_api_url()
    api_key = require_env("IMMICH_API_KEY")
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
    }

    with open(input_csv, newline="", encoding="utf-8") as infile, open(
        output_csv, "w", newline="", encoding="utf-8"
    ) as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ["asset_id"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()

        for row in reader:
            filename = os.path.basename(row["mp4_path"]).upper()
            row["asset_id"] = get_asset_id(filename, api_url, headers)
            writer.writerow(row)

    print("Done.")


def main():
    run()


if __name__ == "__main__":
    main()
