import json
import os


def load_checklist(doc_type: str) -> dict:
    """Load the checklist JSON for the given document type."""
    checklist_dir = os.path.join(os.path.dirname(__file__), "checklists")
    checklist_file = os.path.join(checklist_dir, f"{doc_type}.json")

    if not os.path.exists(checklist_file):
        checklist_file = os.path.join(checklist_dir, "general_agreement.json")

    with open(checklist_file, "r") as f:
        return json.load(f)


def detect_missing_clauses(text: str, doc_type: str) -> dict:
    """Check which required clauses are present or missing in the document."""
    text_lower = text.lower()
    checklist = load_checklist(doc_type)

    results = []
    found_count = 0
    missing_critical = 0
    missing_warning = 0

    for item in checklist["required_clauses"]:
        # Check if ANY keyword for this clause appears in text
        found = any(keyword.lower() in text_lower for keyword in item["keywords"])

        if found:
            found_count += 1
        else:
            if item["severity"] == "critical":
                missing_critical += 1
            elif item["severity"] == "warning":
                missing_warning += 1

        results.append({
            "name": item["name"],
            "found": found,
            "severity": item["severity"]
        })

    total = len(results)
    missing_count = total - found_count

    return {
        "doc_type": doc_type,
        "total_checked": total,
        "found_count": found_count,
        "missing_count": missing_count,
        "missing_critical": missing_critical,
        "missing_warning": missing_warning,
        "clauses": results
    }
