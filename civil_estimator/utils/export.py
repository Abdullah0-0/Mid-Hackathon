"""
CSV export helpers. No external dependencies beyond the standard library,
so results can always be downloaded even if optional packages are missing.
"""

import csv
import io
from datetime import datetime


def results_to_csv_bytes(title: str, label: str, results: dict) -> bytes:
    """Build a CSV file (as bytes) for a single calculator result."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow([title])
    if label:
        writer.writerow([label])
    writer.writerow(["Generated", datetime.now().strftime("%Y-%m-%d %H:%M")])
    writer.writerow([])
    writer.writerow(["Result", "Value"])
    for k, v in results.items():
        writer.writerow([k, v])
    return buf.getvalue().encode("utf-8")


def project_to_csv_bytes(items: list) -> bytes:
    """Build a single CSV covering every item added to the project/BOQ list."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["Civil QuantEstimate - Project BOQ Summary"])
    writer.writerow(["Generated", datetime.now().strftime("%Y-%m-%d %H:%M")])
    writer.writerow([])
    for i, item in enumerate(items, start=1):
        writer.writerow([f"#{i} {item['module']}", item.get("label", "")])
        writer.writerow(["Result", "Value"])
        for k, v in item["results"].items():
            writer.writerow([k, v])
        writer.writerow([])
    return buf.getvalue().encode("utf-8")
