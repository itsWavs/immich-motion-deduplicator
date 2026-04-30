import csv
import os

from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from .config import load_dotenv, require_directory_env
from .ui import console, print_summary


OUTPUT_CSV = "motion_candidates.csv"
PROGRESS_EVERY = 500


def run(output_csv=OUTPUT_CSV, progress_every=PROGRESS_EVERY):
    load_dotenv()
    root_dir = require_directory_env("IMMICH_ROOT_DIR")

    candidates = []
    total_mp4 = 0
    total_dirs = 0

    console.print(f"Scanning library: [bold]{root_dir}[/bold]")
    if progress_every > 0:
        console.print(f"Milestone log every {progress_every} MP4 files.")

    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TextColumn(
            "dirs={task.fields[directories]} mp4={task.fields[mp4]} candidates={task.fields[candidates]}"
        ),
        TimeElapsedColumn(),
        console=console,
    )

    with progress:
        task_id = progress.add_task(
            "Scanning library",
            total=None,
            directories=0,
            mp4=0,
            candidates=0,
        )

        for root, _, files in os.walk(root_dir):
            total_dirs += 1
            files_lower = {file_name.lower(): file_name for file_name in files}
            progress.update(task_id, directories=total_dirs)

            for file_name in files:
                if not file_name.lower().endswith(".mp4"):
                    continue

                total_mp4 += 1
                base = file_name[:-4]
                jpg_name = base + ".jpg"

                if progress_every > 0 and total_mp4 % progress_every == 0:
                    console.log(
                        f"Scanned {total_mp4} MP4 files and found {len(candidates)} candidates so far."
                    )

                if jpg_name.lower() not in files_lower:
                    progress.update(task_id, mp4=total_mp4, candidates=len(candidates))
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
                progress.update(task_id, mp4=total_mp4, candidates=len(candidates))

    if candidates:
        console.print(f"Writing {len(candidates)} candidates to [bold]{output_csv}[/bold]...")
        with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=candidates[0].keys())
            writer.writeheader()
            writer.writerows(candidates)

        print_summary(
            "Scan complete",
            [
                ("Directories scanned", total_dirs),
                ("MP4 files scanned", total_mp4),
                ("Motion candidates detected", len(candidates)),
                ("Output file", output_csv),
            ],
        )
        return len(candidates)

    print_summary(
        "Scan complete",
        [
            ("Directories scanned", total_dirs),
            ("MP4 files scanned", total_mp4),
            ("Motion candidates detected", 0),
        ],
    )
    return 0


def main():
    run()


if __name__ == "__main__":
    main()
