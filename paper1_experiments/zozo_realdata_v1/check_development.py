"""Audit the fixed ZOZO development partition; fit no models.

Run from the project root with Python 3.12 (standard library only).
Only position 1 on 24-25 November 2019 is analysed. Other rows' outcome
strings are read by the CSV parser but never converted or used in statistics.
Weight ESS is a descriptive concentration diagnostic for a constant-item
target policy, not independent sample size, power, or a safety guarantee.
"""

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import statistics
import uuid


ROOT = Path(__file__).resolve().parents[2]
DATES = ("2019-11-24", "2019-11-25")
SOURCES = {
    "random": ("men.csv", "c4b6f65e62bf2c683914703ab6b875cc3e1b4ef0403a5779f548f5578cc34d6d"),
    "bts": ("men_bts.csv", "f116bb11bd0b18f02ca69d313c790c63c006728b3fae28a562d7309e20a0e4b5"),
    "items": ("item_context.csv", "ccdc500e5f96d79f48da43f5fc45c1dc14f07240720a4fd131e94519a16fcba4"),
}


def sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def scan_development(path, item_ids):
    """Filter before accessing click/probability values; reject invalid dev rows."""
    groups = {}
    daily = {day: {"records": 0, "clicks": 0} for day in DATES}
    seen = set()
    previous_time = None
    scanned = 0
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        required = {"timestamp", "position", "item_id", "click", "propensity_score"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError(f"Missing required columns: {path}")
        for row in reader:
            scanned += 1
            day = row["timestamp"][:10]
            if day not in DATES or row["position"] != "1":
                continue
            if None in row or any(row[name] in (None, "") for name in required):
                raise ValueError(f"Malformed development row {scanned}: {path}")
            timestamp = datetime.fromisoformat(row["timestamp"])
            if timestamp.utcoffset() is None or timestamp.utcoffset().total_seconds() != 0:
                raise ValueError("Development timestamps must explicitly use UTC")
            if previous_time is not None and timestamp < previous_time:
                raise ValueError("Development records are not chronological")
            previous_time = timestamp
            if "" in row:
                if row[""] in seen:
                    raise ValueError("Duplicate development source index")
                seen.add(row[""])
            item = int(row["item_id"])
            if item not in item_ids or row["click"] not in ("0", "1"):
                raise ValueError("Unknown item or non-binary development outcome")
            probability = float(row["propensity_score"])
            if not math.isfinite(probability) or not 0 < probability <= 1:
                raise ValueError("Invalid development recommendation probability")
            click = int(row["click"])
            group = groups.setdefault(item, {"clicks": 0, "probabilities": []})
            group["clicks"] += click
            group["probabilities"].append(probability)
            daily[day]["records"] += 1
            daily[day]["clicks"] += click
    if set(groups) != item_ids or any(not values["records"] for values in daily.values()):
        raise ValueError("Development partition lacks expected items or days")
    rows = []
    for item, group in sorted(groups.items()):
        probabilities = group["probabilities"]
        weights = [1.0 / probability for probability in probabilities]
        total = math.fsum(weights)
        rows.append({
            "item_id": item,
            "records": len(weights),
            "clicks": group["clicks"],
            "min_probability": min(probabilities),
            "median_probability": statistics.median(probabilities),
            "weight_ess": total ** 2 / math.fsum(weight ** 2 for weight in weights),
            "largest_weight_percent": 100 * max(weights) / total,
        })
    return rows, daily, scanned


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=ROOT / "data/zozo_open_bandit/raw")
    args = parser.parse_args()
    checkpoint_path = Path(__file__).with_name("feasibility_checkpoint.json")
    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    if (checkpoint["development_dates_UTC"] != list(DATES)
            or checkpoint["position"] != 1 or checkpoint["campaign"] != "men"
            or checkpoint["reserved_click_results_inspected"] is not False
            or checkpoint["revision"] != "90a1283aecd19026caf15a0840af1176a41f6a76"):
        raise ValueError("Checkpoint does not match this fixed development audit")
    provenance = {}
    for source, (name, expected) in SOURCES.items():
        path = args.raw_dir / name
        print(f"Verifying {name}...", flush=True)
        actual = sha256(path)
        if actual != expected:
            raise ValueError(f"SHA-256 mismatch: {name}")
        provenance[source] = {"file": name, "sha256": actual, "bytes": path.stat().st_size}
    with (args.raw_dir / SOURCES["items"][0]).open(newline="", encoding="utf-8-sig") as stream:
        items = list(csv.DictReader(stream))
    item_ids = {int(row["item_id"]) for row in items}
    if len(items) != 34 or len(item_ids) != 34:
        raise ValueError("Expected 34 unique product records")
    all_rows = []
    summaries = {}
    for source in ("random", "bts"):
        print(f"Scanning {source}; analysing only the two development days...", flush=True)
        rows, daily, scanned = scan_development(args.raw_dir / SOURCES[source][0], item_ids)
        count = sum(row["records"] for row in rows)
        clicks = sum(row["clicks"] for row in rows)
        if (count != checkpoint[f"{source}_development_records"]
                or clicks != checkpoint[f"{source}_development_clicks"]):
            raise ValueError(f"Development counts differ from checkpoint: {source}")
        for row in rows:
            row["source"] = source
        all_rows.extend(rows)
        summaries[source] = {"scanned_rows": scanned, "development_rows": count,
                             "development_clicks": clicks, "daily": daily}
        print(f"\n{source}: {count:,} development rows; {clicks:,} clicks")
        print("item   records  clicks   weight_ESS  largest_weight_%")
        for row in rows:
            print(f"{row['item_id']:4d} {row['records']:9d} {row['clicks']:7d} "
                  f"{row['weight_ess']:12.1f} {row['largest_weight_percent']:17.2f}")
    # Create a new result directory only after all input checks pass.
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = ROOT / "data/zozo_open_bandit/checks" / f"development_{stamp}_{uuid.uuid4().hex[:8]}"
    output.mkdir(parents=True, exist_ok=False)
    with (output / "item_support.csv").open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(all_rows[0]))
        writer.writeheader()
        writer.writerows(all_rows)
    summary = {
        "status": "development_audit_complete_no_models_fitted",
        "development_dates_UTC": list(DATES), "position": 1,
        "reserved_outcomes_analysed": False, "source_files": provenance,
        "script_sha256": sha256(Path(__file__)),
        "checkpoint_sha256": sha256(checkpoint_path), "summaries": summaries,
        "limitations": [
            "Only observed-action propensities are available in these files.",
            "Weight ESS describes concentration for each constant-item target policy.",
            "It is not the ESS of a learned policy or a measure of independent observations.",
            "No policy precision, temporal drift, gate safety, or publication novelty established.",
            "BTS propensities are recorded estimates; their accuracy was not reconstructed.",
        ],
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"\nSaved development diagnostics: {output}")
    print("No models fitted. No later click outcomes analysed.")


if __name__ == "__main__":
    main()
