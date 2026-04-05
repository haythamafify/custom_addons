import os
import sys

# ============================================================
# كل حاجة أوتو — مش محتاج تغير أي حاجة
# ============================================================

# المسار هو الفولدر اللي فيه السكريبت نفسه
MODULE_PATH = os.path.dirname(os.path.abspath(__file__))
MODULE_NAME = os.path.basename(MODULE_PATH)
OUTPUT_FILE = os.path.join(os.path.expanduser("~/Desktop"), f"{MODULE_NAME}.txt")

SKIP_DIRS  = {'__pycache__', '.vscode', '.git'}
SKIP_FILES = {'collect_module.py'}
EXTENSIONS = ('.py', '.xml', '.csv', '.md')

# ============================================================

def collect_files(base_path: str) -> None:
    collected = []

    for root, dirs, files in os.walk(base_path):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)

        for file in sorted(files):
            if file in SKIP_FILES:
                continue
            if not file.endswith(EXTENSIONS):
                continue

            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, base_path)

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                collected.append((relative_path, content))
            except Exception as e:
                collected.append((relative_path, f"⚠️ Error reading file: {e}"))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write(f"MODULE: {MODULE_NAME}\n")
        out.write(f"FILES : {len(collected)}\n")
        out.write("=" * 60 + "\n")

        for relative_path, content in collected:
            out.write(f"\n\n{'=' * 60}\n")
            out.write(f"FILE: {relative_path}\n")
            out.write(f"{'=' * 60}\n\n")
            out.write(content)

    print(f"✅ تم! ({len(collected)} ملف) → {OUTPUT_FILE}")


if __name__ == "__main__":
    collect_files(MODULE_PATH)
