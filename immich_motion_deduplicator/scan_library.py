import csv
import os

from .config import load_dotenv, require_env


OUTPUT_CSV = "motion_candidates.csv"
PROGRESS_EVERY = 500


def run(output_csv=OUTPUT_CSV, progress_every=PROGRESS_EVERY):
    load_dotenv()
    root_dir = require_env("IMMICH_ROOT_DIR")

    candidates = []
    total_mp4 = 0

    print(f"Scanning library: {root_dir}")
    if progress_every > 0:
        print(f"Progress updates every {progress_every} MP4 files.")

    for root, _, files in os.walk(root_dir):
        files_lower = {file_name.lower(): file_name for file_name in files}

        for file_name in files:
            if not file_name.lower().endswith(".mp4"):
                continue

            total_mp4 += 1
            base = file_name[:-4]
            jpg_name = base + ".jpg"

            if progress_every > 0 and total_mp4 % progress_every == 0:
                print(
                    f"Scanned {total_mp4} MP4 files, "
                    f"found {len(candidates)} motion candidates so far..."
                )

            if jpg_name.lower() not in files_lower:
                continue

            mp4_path = os.path.join(root, file_name)
            jpg_path = os.path.join(root, files_lower[jpg_name.lower()])
            candidates.append(
                {
                    "mp4_path": mp4_path,
                    "jpg_path": jpg_path,
                    "mp4_size_MB": round(os.path.getsize(mp4_path) / (1024 * 1024), 2),
                }
            )

    if candidates:
        print(f"Writing {len(candidates)} candidates to {output_csv}...")
        with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=candidates[0].keys())
            writer.writeheader()
            writer.writerows(candidates)

        print("\n✅ Analysis complete.")
        print(f"📹 MP4 files scanned: {total_mp4}")
        print(f"🎯 Motion candidates detected: {len(candidates)}")
        print(f"📄 Result exported to: {output_csv}")
        return len(candidates)

    print("\n⚠ No candidates detected.")
    print(f"📹 MP4 files scanned: {total_mp4}")
    return 0


def main():
    run()


if __name__ == "__main__":
    main()
