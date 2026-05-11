import json
import os
import tempfile
from pathlib import Path
from typing import Any

import streamlit as st

from update_jsons import run_revert, run_update, scan_all_paths


st.set_page_config(page_title="JSON Updater Tool", page_icon="🔧", layout="wide")


def parse_uploaded_json(uploaded_file) -> tuple[Any | None, str | None]:
    if uploaded_file is None:
        return None, None

    try:
        raw_content = uploaded_file.getvalue().decode("utf-8")
        return json.loads(raw_content), None
    except UnicodeDecodeError:
        return None, "The uploaded file is not valid UTF-8 text."
    except json.JSONDecodeError as exc:
        return None, f"Invalid JSON: {exc}"


def parse_json_value(value: str) -> Any:
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def edit_dict_content(data: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    rows = [{"key": key, "value": json.dumps(value, ensure_ascii=False)} for key, value in data.items()]
    edited_rows = st.data_editor(
        rows,
        key="dict_editor",
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "key": st.column_config.TextColumn("Key", required=True),
            "value": st.column_config.TextColumn("Value (JSON or plain text)", required=True),
        },
    )

    edited_data: dict[str, Any] = {}
    for row in edited_rows:
        key = str(row.get("key", "")).strip()
        if not key:
            continue
        edited_data[key] = parse_json_value(str(row.get("value", "")))

    if not edited_data:
        return None, "The update JSON must contain at least one key."

    return edited_data, None


def edit_list_of_objects(data: list[Any]) -> list[Any]:
    return st.data_editor(data, key="list_editor", num_rows="dynamic", use_container_width=True)


def edit_raw_json(data: Any) -> tuple[Any | None, str | None]:
    edited_text = st.text_area(
        "Edit JSON",
        value=json.dumps(data, indent=2, ensure_ascii=False),
        height=320,
        key="raw_json_editor",
    )

    try:
        return json.loads(edited_text), None
    except json.JSONDecodeError as exc:
        return None, f"Edited JSON is invalid: {exc}"


def edit_update_content(data: Any) -> tuple[Any | None, str | None]:
    st.subheader("Update JSON Preview And Editor")

    if isinstance(data, dict):
        return edit_dict_content(data)

    if isinstance(data, list) and all(isinstance(item, dict) for item in data):
        return edit_list_of_objects(data), None

    st.info("This JSON is nested or scalar content, so it is shown in a raw JSON editor.")
    return edit_raw_json(data)


def write_temp_update_file(content: Any) -> str:
    temp_file = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
    with temp_file:
        json.dump(content, temp_file, indent=2, ensure_ascii=False)
    return temp_file.name


def validate_directory(path_value: str, label: str) -> Path | None:
    if not path_value.strip():
        st.error(f"{label} is required.")
        return None

    path = Path(path_value).expanduser()
    if not path.exists() or not path.is_dir():
        st.error(f"{label} does not exist or is not a directory: {path}")
        return None

    return path


def render_results(results: dict[str, Any], title: str) -> None:
    st.subheader(title)

    scanned, updated, not_found, exists = st.columns(4)
    scanned.metric("Files Scanned", results.get("scanned", 0))
    updated.metric("Updated", len(results.get("updated", [])))
    not_found.metric("Not Found / Errors", len(results.get("skipped_not_found", [])))
    exists.metric("Already Updated", len(results.get("skipped_exists", [])))

    with st.expander("Successful Updates", expanded=True):
        st.write(results.get("updated", []) or "No files were updated.")

    with st.expander("Skipped: Missing Target Or Errors"):
        st.write(results.get("skipped_not_found", []) or "No missing targets or errors.")

    with st.expander("Skipped: Already Updated Or Same Value"):
        st.write(results.get("skipped_exists", []) or "No already-updated files.")


def render_update_tab() -> None:
    st.header("Bulk Update JSON Files")
    st.caption("Mount or expose your JSON directory to the Streamlit runtime, then enter that path here.")

    json_dir = st.text_input("JSON directory", value="/data/json")
    uploaded_file = st.file_uploader("Update JSON file", type="json")
    update_content, upload_error = parse_uploaded_json(uploaded_file)

    if upload_error:
        st.error(upload_error)
        return

    edited_content = None
    edited_error = None
    if update_content is not None:
        edited_content, edited_error = edit_update_content(update_content)
        if edited_error:
            st.error(edited_error)

    mode_label = st.radio(
        "Update mode",
        options=[
            "Mode 1: Add top-level object",
            "Mode 2: Add inside existing object or array",
            "Mode 3: Update string(s) in specific file(s)",
        ],
    )
    mode = {
        "Mode 1: Add top-level object": 1,
        "Mode 2: Add inside existing object or array": 2,
        "Mode 3: Update string(s) in specific file(s)": 3,
    }[mode_label]

    target_path = None
    filename_filter = None

    if mode == 2:
        path_options: list[str] = []
        if Path(json_dir).expanduser().is_dir():
            with st.spinner("Scanning available JSON paths..."):
                path_options = scan_all_paths(json_dir)
        target_path = st.selectbox(
            "Target path (dot notation)",
            options=path_options,
            index=None,
            placeholder="Select a discovered path or type below",
        )
        manual_target_path = st.text_input("Or enter target path manually")
        target_path = manual_target_path.strip() or target_path

    if mode == 3:
        filename_filter = st.text_input("File name filter", placeholder="it-IT.json")
        target_path = st.text_input("Target path to string value", placeholder="errors.messages")

    if st.button("Run Update", type="primary"):
        directory = validate_directory(json_dir, "JSON directory")
        if directory is None or edited_content is None or edited_error:
            if edited_content is None and not edited_error:
                st.error("Upload a valid update JSON file first.")
            return

        if mode == 2 and not target_path:
            st.error("Mode 2 requires a target path.")
            return

        if mode == 3 and (not filename_filter or not target_path):
            st.error("Mode 3 requires both a file name filter and a target path.")
            return

        temp_update_file = write_temp_update_file(edited_content)
        try:
            results = run_update(str(directory), temp_update_file, mode, target_path, filename_filter)
            st.session_state["last_update_results"] = results
        finally:
            os.unlink(temp_update_file)

    if "last_update_results" in st.session_state:
        render_results(st.session_state["last_update_results"], "Update Results")


def render_revert_tab() -> None:
    st.header("Revert JSON Files")
    st.caption("Restore JSON files from a backup directory into a target directory.")

    backup_dir = st.text_input("Backup directory", value="/data/backup")
    target_dir = st.text_input("Target directory", value="/data/json")

    if st.button("Run Revert", type="primary"):
        backup_path = validate_directory(backup_dir, "Backup directory")
        target_path = validate_directory(target_dir, "Target directory")
        if backup_path is None or target_path is None:
            return

        results = run_revert(str(backup_path), str(target_path))
        st.session_state["last_revert_results"] = results

    if "last_revert_results" in st.session_state:
        render_results(st.session_state["last_revert_results"], "Revert Results")


def render_help_tab() -> None:
    st.header("How This Tool Works")
    st.markdown(
        """
        This Streamlit app preserves the original JSON updater behavior:

        - **Mode 1** adds new top-level keys from the update JSON to every JSON file.
        - **Mode 2** adds content inside an existing object or array at a dot-notation path.
        - **Mode 3** updates a string value at a dot-notation path, only in files matching a file name.
        - **Revert** copies JSON files from a backup directory into the selected target directory.

        In containers or Kubernetes, make sure the JSON directories are mounted into the app pod.
        """
    )


def main() -> None:
    st.title("🔧 JSON Updater Tool")

    update_tab, revert_tab, help_tab = st.tabs(["Update", "Revert", "Help"])
    with update_tab:
        render_update_tab()
    with revert_tab:
        render_revert_tab()
    with help_tab:
        render_help_tab()


if __name__ == "__main__":
    main()
