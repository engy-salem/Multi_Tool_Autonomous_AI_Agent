from pathlib import Path

PROJECT_DIR = Path("/content/multi-tool-autonomous-agent")
WORKSPACE = PROJECT_DIR / "workspace"

notes_file = WORKSPACE / "project_notes.txt"

print("Notes file exists:", notes_file.exists())

if notes_file.exists():
    print(notes_file.read_text(encoding="utf-8"))
