# Immich Motion deduplicator

If you exported your media using Google Takeout and your phone uses Motion Photos / Live Photos, you probably duplicated your media.

Google Takeout exports:
- A JPG file (the photo with the embedded motion)
- A separate MP4 file (the motion video only)

When importing into Immich, both can appear as standalone assets.

This script helps you safely remove the duplicated motion video files.◊

---

## What This Project Does

1. Scans your library, looks for photos and videos with the same basename, and creates a `.csv`
2. Queries the Immich API (`/search/metadata`) and adds the ID for each asset (matching by filename)
3. Deletes matched video assets in safe batches (`delete` supports dry-run mode)

---

## Requirements

- Python 3.10+

## Configuration

Create a `.env` file in the repo root with:

```env
IMMICH_ROOT_DIR=/path/to/your/immich/library
IMMICH_API_URL=http://your-immich-host:2283/api
IMMICH_API_KEY=your_api_key
MOTION_CANDIDATES_CSV=motion_candidates.csv
MOTION_CANDIDATES_WITH_IDS_CSV=motion_candidates_with_ids.csv
```

`IMMICH_API_URL` may include `/api` or omit it.
Set both CSV variables in `.env`; the commands read them directly.

## Usage

Run the module directly:

```bash
python -m immich_motion_deduplicator scan
python -m immich_motion_deduplicator ids
python -m immich_motion_deduplicator delete
python -m immich_motion_deduplicator all
```

`delete` runs in dry-run mode by default; use `--execute` to perform real deletions.

`all` runs the full flow and deletes by default so it can be used non-interactively in automation.

Use `all --dry-run` to preview the matches without deleting anything.
