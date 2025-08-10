# pipeline/contracts/checks.py
import os, json
from typing import List, Dict

class ContractError(Exception):
    pass

def require_file(path: str, hint: str = "") -> None:
    if not os.path.exists(path):
        msg = f"[CONTRACT] Missing required file: {path}"
        if hint:
            msg += f"\nHint: {hint}"
        raise ContractError(msg)
    if os.path.isdir(path):
        raise ContractError(f"[CONTRACT] Expected a file but found directory: {path}")

def load_json_array(path: str) -> List[Dict]:
    require_file(path, "Upstream stage may have failed.")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        raise ContractError(f"[CONTRACT] Invalid JSON in {path}: {e}")
    if not isinstance(data, list):
        raise ContractError(f"[CONTRACT] Expected JSON array in {path}.")
    return data

def ensure_article_fields(items: List[Dict], required: List[str]) -> None:
    # All items must have the required keys (allow empty string/None values)
    missing_examples = []
    for i, it in enumerate(items[:20]):  # just sample first 20 for speed
        for k in required:
            if k not in it:
                missing_examples.append((i, k))
    if missing_examples:
        lines = "\n".join([f" - item[{i}] missing '{k}'" for i, k in missing_examples[:10]])
        raise ContractError(f"[CONTRACT] Some items are missing required fields:\n{lines}\n"
                            f"(Showed first {min(10, len(missing_examples))} of {len(missing_examples)})")

def ensure_min_count(items: List[Dict], min_items: int, where: str) -> None:
    if len(items) < min_items:
        raise ContractError(f"[CONTRACT] Too few items in {where}: got {len(items)}, need ≥ {min_items}")

def write_json(path: str, data) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)