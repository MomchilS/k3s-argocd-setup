import os
import json

# ===========================================================
# Helper: Gather one-level paths for Mode 2 dropdown
# ===========================================================
def extract_one_level_paths(obj, prefix=""):
    """
    Extract paths one level deep.
    Example:
        obj = { "errors": { "messages": [], "codes": {} }, "status": "ok" }
    extract_one_level_paths(obj) -> ["errors", "status"]
    If prefix='errors', returns ["errors.messages", "errors.codes"]
    """
    paths = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_prefix = f"{prefix}.{k}" if prefix else k
            paths.append(new_prefix)
    elif isinstance(obj, list) and prefix:
        paths.append(prefix)
    return paths

# ===========================================================
# Helper: Recursively gather all possible paths (for scanning)
# ===========================================================
def extract_paths(obj, prefix=""):
    paths = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_prefix = f"{prefix}.{k}" if prefix else k
            paths.append(new_prefix)
            paths.extend(extract_paths(v, new_prefix))
    elif isinstance(obj, list) and prefix:
        paths.append(prefix)
    return paths

# ===========================================================
# Gather all paths from all JSON files in a directory
# ===========================================================
def scan_all_paths(json_dir):
    all_paths = set()
    for root, _, files in os.walk(json_dir):
        for f in files:
            if f.endswith(".json"):
                fpath = os.path.join(root, f)
                try:
                    with open(fpath, "r", encoding="utf-8") as infile:
                        data = json.load(infile)
                        file_paths = extract_paths(data)
                        all_paths.update(file_paths)
                except Exception as e:
                    print(f"[WARN] Skipping {fpath}: {e}")
    return sorted(list(all_paths))

# ===========================================================
# Mode 1: Add top-level object(s)
# ===========================================================
def add_top_level(data, new_content):
    updated = []
    skipped_exists = []

    for key, value in new_content.items():
        if key not in data:
            data[key] = value
            updated.append(key)
        else:
            skipped_exists.append(key)

    return updated, skipped_exists

# ===========================================================
# Mode 2: Add nested content (one level only)
# ===========================================================
def add_nested(data, target_path, new_content):
    keys = target_path.split(".")
    ref = data

    # Traverse path (all but last key)
    for k in keys[:-1]:
        if isinstance(ref, dict) and k in ref:
            ref = ref[k]
        else:
            # parent path missing entirely
            return [], [target_path]

    last_key = keys[-1]

    if isinstance(ref, dict) and last_key in ref:
        target_ref = ref[last_key]

        if isinstance(target_ref, dict):
            updated = []
            skipped = []
            for k, v in new_content.items():
                if k not in target_ref:
                    target_ref[k] = v
                    updated.append(f"{target_path}.{k}")
                else:
                    skipped.append(f"{target_path}.{k}")
            # ✅ skipped returned as "exists"
            return updated, skipped

        elif isinstance(target_ref, list):
            if isinstance(new_content, list):
                target_ref.extend(new_content)
            else:
                target_ref.append(new_content)
            return [f"{target_path}[]"], []

        else:
            # Path exists but not dict/list → treat as "exists"
            return [], [target_path]

    else:
        # last key missing
        return [], [target_path]

# ===========================================================
# Mode 3: Update specific string values
# ===========================================================
def update_strings_in_file(data, target_path, new_content):
    keys = target_path.split(".")
    ref = data
    for k in keys[:-1]:
        if isinstance(ref, dict) and k in ref:
            ref = ref[k]
        else:
            return False  # Path not found
    last_key = keys[-1]
    if isinstance(ref, dict) and last_key in ref:
        if isinstance(ref[last_key], str):
            if isinstance(new_content, dict) and last_key in new_content:
                if ref[last_key] != new_content[last_key]:
                    ref[last_key] = new_content[last_key]
                    return True
                else:
                    return "exists"  # Already same value
    return False

# ===========================================================
# Run update across files
# ===========================================================
def run_update(json_dir, update_file, mode=1, target_path=None, filename_filter=None):
    results = {
        "updated": [],
        "skipped_not_found": [],
        "skipped_exists": [],
        "scanned": 0
    }

    with open(update_file, "r", encoding="utf-8") as f:
        update_content = json.load(f)

    for root, _, files in os.walk(json_dir):
        for file in files:
            if not file.endswith(".json"):
                continue

            # Mode 3: only matching filename
            if mode == 3 and filename_filter and file != filename_filter:
                continue

            filepath = os.path.join(root, file)
            results["scanned"] += 1
            try:
                with open(filepath, "r", encoding="utf-8") as infile:
                    data = json.load(infile)

                updated, skipped_exists, skipped_not_found = [], [], []

                if mode == 1:
                    updated, skipped_exists = add_top_level(data, update_content)

                elif mode == 2:
                    updated, skipped = add_nested(data, target_path, update_content)
                    # now skipped from add_nested means "exists"
                    skipped_exists = skipped

                elif mode == 3:
                    status = update_strings_in_file(data, target_path, update_content)
                    if status is True:
                        updated = [target_path]
                    elif status == "exists":
                        skipped_exists = [target_path]
                    else:
                        skipped_not_found = [target_path]

                # Write updated file
                if updated:
                    with open(filepath, "w", encoding="utf-8") as outfile:
                        json.dump(data, outfile, indent=2, ensure_ascii=False)
                    results["updated"].append(filepath)

                # Record skipped files with absolute paths
                for s in skipped_not_found:
                    results["skipped_not_found"].append(f"{filepath} ({s})")
                for s in skipped_exists:
                    results["skipped_exists"].append(f"{filepath} ({s})")

            except Exception as e:
                results["skipped_not_found"].append(f"{filepath} ({e})")

    return results

# ===========================================================
# Revert
# ===========================================================
def run_revert(backup_dir, target_dir):
    results = {
        "updated": [],
        "skipped_not_found": [],
        "skipped_exists": [],
        "scanned": 0
    }
    for root, _, files in os.walk(backup_dir):
        for file in files:
            if file.endswith(".json"):
                results["scanned"] += 1
                backup_path = os.path.join(root, file)
                rel_path = os.path.relpath(backup_path, backup_dir)
                target_path = os.path.join(target_dir, rel_path)
                try:
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    with open(backup_path, "r", encoding="utf-8") as src:
                        data = src.read()
                    with open(target_path, "w", encoding="utf-8") as dst:
                        dst.write(data)
                    results["updated"].append(target_path)
                except Exception as e:
                    results["skipped_not_found"].append(f"{target_path} ({e})")
    return results