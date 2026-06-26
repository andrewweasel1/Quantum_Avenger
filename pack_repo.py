import os
from pathlib import Path

# Configuration
OUTPUT_FILE = "codebase_bundle.md"
# Folders and files to completely ignore (add yours here)
IGNORE_DIRS = {".git", "__pycache__", "node_modules", ".venv", "env", "build", "dist"}
IGNORE_FILES = {OUTPUT_FILE, ".DS_Store", "package-lock.json"}
# Supported text file extensions
SUPPORTED_EXTENSIONS = {".py", ".md", ".txt", ".json", ".yaml", ".yml", ".ini", ".conf", ".toml"}

def generate_markdown_bundle(repo_path: Path, output_path: Path):
    with open(output_path, "w", encoding="utf-8") as outfile:
        outfile.write(f"# Codebase Bundle: {repo_path.resolve().name}\n\n")
        
        # 1. Generate a Folder Structure Visual First
        outfile.write("## Project Structure\n```text\n")
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            level = len(Path(root).relative_to(repo_path).parts)
            indent = "  " * level
            outfile.write(f"{indent}📁 {os.path.basename(root)}/\n")
            sub_indent = "  " * (level + 1)
            for f in files:
                if f not in IGNORE_FILES and Path(f).suffix in SUPPORTED_EXTENSIONS:
                    outfile.write(f"{sub_indent}📄 {f}\n")
        outfile.write("```\n\n---\n\n")

        # 2. Pack File Contents
        outfile.write("## File Contents\n\n")
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            
            for file in files:
                if file in IGNORE_FILES:
                    continue
                    
                file_path = Path(root) / file
                relative_path = file_path.relative_to(repo_path)
                
                if file_path.suffix in SUPPORTED_EXTENSIONS:
                    # Determine markdown syntax highlighting language
                    lang = file_path.suffix.lstrip('.')
                    if lang in ["yml", "yaml"]: lang = "yaml"
                    elif lang in ["md", "txt"]: lang = "markdown"

                    outfile.write(f"### File: `{relative_path}`\n\n")
                    outfile.write(f"```{lang}\n")
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="replace") as infile:
                            outfile.write(infile.read())
                    except Exception as e:
                        outfile.write(f"[Error reading file: {e}]")
                    outfile.write("\n```\n\n---\n\n")

    print(f" Successfully packed repository into {output_path}")

if __name__ == "__main__":
    generate_markdown_bundle(Path("."), Path(OUTPUT_FILE))