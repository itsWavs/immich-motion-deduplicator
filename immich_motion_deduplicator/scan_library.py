import csv
import os

from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from .config import load_dotenv, require_directory_env, require_env
from .ui import console, print_summary


PROGRESS_EVERY = 500
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".heic")


def find_image_name(stem, files_by_name):
    for extension in IMAGE_EXTENSIONS:
        image_name = files_by_name.get(f"{stem}{extension}")
        if image_name:
            return image_name
    return None


def build_candidate(root, mp4_name, image_name):
    mp4_path = os.path.join(root, mp4_name)
    return {
        "mp4_path": mp4_path,
        "jpg_path": os.path.join(root, image_name),
        "mp4_size_MB": round(os.path.getsize(mp4_path) / (1024 * 1024), 2),
    }


def run(progress_every=PROGRESS_EVERY):
    load_dotenv()
    root_dir = require_directory_env("IMMICH_ROOT_DIR")
    output_csv = require_env("MOTION_CANDIDATES_CSV")

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
            files_by_name = {file_name.lower(): file_name for file_name in files}
            progress.update(task_id, directories=total_dirs)

            for file_name in files:
                stem, extension = os.path.splitext(file_name)
                if extension.lower() != ".mp4":
                    continue

                total_mp4 += 1

                if progress_every > 0 and total_mp4 % progress_every == 0:
                    console.log(
                        f"Scanned {total_mp4} MP4 files and found {len(candidates)} candidates so far."
                    )

                image_name = find_image_name(stem.lower(), files_by_name)
                if image_name is None:
                    progress.update(task_id, mp4=total_mp4, candidates=len(candidates))
                    continue

                candidates.append(build_candidate(root, file_name, image_name))
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
