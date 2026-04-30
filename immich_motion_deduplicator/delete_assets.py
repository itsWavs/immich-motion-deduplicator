import csv
import time

import requests

from .config import get_immich_api_url, load_dotenv, require_env


INPUT_CSV = "motion_candidates_with_ids.csv"
BATCH_SIZE = 25
DRY_RUN = True
SLEEP_BETWEEN_BATCHES = 3.5


def chunk_list(values, size):
    """Split a list into sublists of size 'size'."""
    for index in range(0, len(values), size):
        yield values[index:index + size]


def delete_batch(ids, api_url, headers):
    """Delete a batch of assets via the DELETE /assets API."""
    response = requests.delete(
        f"{api_url}/assets",
        json={"ids": ids, "force": False},
        headers=headers,
        timeout=30,
    )
    response.raise_for_status()

    try:
        return response.json()
    except ValueError:
        return {"status_code": response.status_code, "message": "No content returned"}


def run(input_csv=INPUT_CSV, batch_size=BATCH_SIZE, dry_run=DRY_RUN):
    load_dotenv()
    api_url = get_immich_api_url()
    api_key = require_env("IMMICH_API_KEY")
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
    }

    asset_ids = []
    with open(input_csv, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            if row.get("asset_id"):
                asset_ids.append(row["asset_id"])

    print(f"{len(asset_ids)} assets to delete.")

    if dry_run:
        print("DRY RUN enabled - no deletion performed.")
        print("Processing complete.")
        return

    for batch_num, batch in enumerate(chunk_list(asset_ids, batch_size), start=1):
        print(f"Deleting batch {batch_num} ({len(batch)} assets)...")
        try:
            result = delete_batch(batch, api_url, headers)
            print(f"Batch {batch_num} OK. API response: {result}")
        except requests.RequestException as exc:
            print(f"[ERROR] Batch {batch_num} failed:", exc)

        time.sleep(SLEEP_BETWEEN_BATCHES)

    print("Processing complete.")


def main():
    run()


if __name__ == "__main__":
    main()
