"""Benchmark manual vs voice-assisted task completion time."""

import csv
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import pyautogui
from commands.dispatcher import CommandDispatcher

BENCHMARK_DIR = Path(__file__).resolve().parent
RESULTS_CSV = BENCHMARK_DIR / "results.csv"

TASKS = [
    {
        "task_type": "app_launch",
        "command": "open calculator",
        "manual_seconds": 3.5,
    },
    {
        "task_type": "file_create",
        "command": "create file benchmark_time_test.txt",
        "manual_seconds": 4.5,
    },
    {
        "task_type": "web_search",
        "command": "search for python tutorials",
        "manual_seconds": 4.0,
    },
    {
        "task_type": "screenshot",
        "command": "take screenshot",
        "manual_seconds": 2.5,
    },
    {
        "task_type": "media_control",
        "command": "pause",
        "manual_seconds": 1.5,
    },
]


def ensure_results_csv():
    BENCHMARK_DIR.mkdir(parents=True, exist_ok=True)
    if not RESULTS_CSV.exists():
        with RESULTS_CSV.open("w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                "timestamp",
                "task_type",
                "command",
                "manual_time_s",
                "voice_time_s",
                "reduction_percent",
                "handled",
                "category",
            ])


def simulate_manual(task):
    start = time.perf_counter()
    time.sleep(task["manual_seconds"])
    return time.perf_counter() - start


def run_voice_task(dispatcher, command):
    # silence interactive alerts during benchmark
    pyautogui.alert = lambda *args, **kwargs: None

    start = time.perf_counter()
    handled, category = dispatcher.dispatch(command)
    elapsed = time.perf_counter() - start
    return elapsed, handled, category or "UNKNOWN"


def cleanup_artifacts(task_type):
    if task_type == "file_create":
        path = Path.home() / "Desktop" / "benchmark_time_test.txt"
        if path.exists():
            path.unlink(missing_ok=True)
    elif task_type == "screenshot":
        now = datetime.now()
        for path in Path.cwd().glob("screenshot_*.png"):
            try:
                age_seconds = (now - datetime.fromtimestamp(path.stat().st_mtime)).total_seconds()
                if age_seconds < 300:
                    path.unlink(missing_ok=True)
            except Exception:
                continue


def write_result(row):
    with RESULTS_CSV.open("a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(row)


def compute_average_reduction(rows):
    reductions = []
    for row in rows:
        try:
            reductions.append(float(row[5]))
        except (TypeError, ValueError):
            continue
    return sum(reductions) / len(reductions) if reductions else 0.0


def print_summary(rows):
    print("\nTime Benchmark Results")
    print("=" * 50)
    print(f"Results file: {RESULTS_CSV}")
    print()
    print(f"{'Task':<15} {'Manual(s)':>10} {'Voice(s)':>10} {'Reduction':>12} {'Handled':>8} {'Category':>15}")
    print("-" * 70)
    for row in rows:
        task_type = row[1]
        manual_s = float(row[3])
        voice_s = float(row[4])
        reduction = float(row[5])
        handled = row[6]
        category = row[7]
        print(f"{task_type:<15} {manual_s:>10.3f} {voice_s:>10.3f} {reduction:>11.2f}% {str(handled):>8} {category:>15}")

    avg_reduction = compute_average_reduction(rows)
    print("\nAverage time reduction: {:.2f}%".format(avg_reduction))


def main():
    ensure_results_csv()
    dispatcher = CommandDispatcher()
    rows = []

    for task in TASKS:
        manual_time = simulate_manual(task)
        voice_time, handled, category = run_voice_task(dispatcher, task["command"])
        reduction = (manual_time - voice_time) / manual_time * 100.0 if manual_time else 0.0

        cleanup_artifacts(task["task_type"])

        row = [
            datetime.utcnow().isoformat(),
            task["task_type"],
            task["command"],
            f"{manual_time:.4f}",
            f"{voice_time:.4f}",
            f"{reduction:.2f}",
            handled,
            category,
        ]
        write_result(row)
        rows.append(row)
        time.sleep(0.5)

    print_summary(rows)


if __name__ == "__main__":
    main()
