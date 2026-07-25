"""Read logs/accuracy_log.csv and compute recognition accuracy statistics."""

import csv
from collections import Counter
from pathlib import Path

LOG_PATH = Path(__file__).resolve().parent.parent / "logs" / "accuracy_log.csv"

BUCKETS = [
    (0.00, 0.50),
    (0.50, 0.60),
    (0.60, 0.70),
    (0.70, 0.80),
    (0.80, 0.90),
    (0.90, 1.01),
]


def read_accuracy_log(path: Path):
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                "timestamp",
                "raw_transcribed_text",
                "matched_command_category",
                "confidence_score",
                "success",
            ])
        return []

    rows = []
    with path.open("r", encoding="utf-8", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if not row:
                continue
            rows.append({
                "timestamp": row.get("timestamp", ""),
                "raw_transcribed_text": row.get("raw_transcribed_text", ""),
                "matched_command_category": row.get("matched_command_category", ""),
                "confidence_score": float(row.get("confidence_score", 0.0) or 0.0),
                "success": str(row.get("success", "False")).strip().lower() in {"true", "1", "yes"},
            })
    return rows


def bucket_label(low: float, high: float) -> str:
    return f"{low:.2f}-{high:.2f}" if high < 1.0 else f"{low:.2f}-1.00"


def compute_statistics(rows):
    total = len(rows)
    successful = sum(1 for row in rows if row["success"])
    overall_accuracy = (successful / total * 100.0) if total else 0.0

    bucket_totals = Counter()
    bucket_successes = Counter()
    bucket_counts = Counter()

    for row in rows:
        score = row["confidence_score"]
        for low, high in BUCKETS:
            if low <= score < high:
                label = bucket_label(low, high)
                bucket_counts[label] += 1
                if row["success"]:
                    bucket_successes[label] += 1
                break

    bucket_stats = []
    for low, high in BUCKETS:
        label = bucket_label(low, high)
        count = bucket_counts[label]
        succ = bucket_successes[label]
        accuracy = (succ / count * 100.0) if count else 0.0
        bucket_stats.append((label, count, succ, accuracy))

    category_counter = Counter(
        row["matched_command_category"] or "UNKNOWN"
        for row in rows
    )

    return {
        "total_attempts": total,
        "successful_matches": successful,
        "overall_accuracy": overall_accuracy,
        "bucket_stats": bucket_stats,
        "category_counts": category_counter,
    }


def print_summary(stats):
    print("\nRecognition Accuracy Summary")
    print("=" * 40)
    print(f"Total attempts          : {stats['total_attempts']}")
    print(f"Successful matches      : {stats['successful_matches']}")
    print(f"Overall accuracy        : {stats['overall_accuracy']:.2f}%")
    print()
    print("Confidence bucket breakdown:")
    print(f"{'Bucket':<12} {'Count':>6} {'Success':>8} {'Accuracy':>10}")
    print("-" * 40)
    for label, count, succ, accuracy in stats["bucket_stats"]:
        print(f"{label:<12} {count:>6} {succ:>8} {accuracy:>9.2f}%")
    print()
    print("Command category counts:")
    for category, count in stats["category_counts"].most_common():
        print(f"{category:<20} {count:>6}")


def main():
    rows = read_accuracy_log(LOG_PATH)
    if not rows:
        print("No accuracy log entries found. Created placeholder log at:")
        print(f"  {LOG_PATH}")
        return

    stats = compute_statistics(rows)
    print_summary(stats)


if __name__ == "__main__":
    main()
