import os
import re
from pathlib import Path

def get_all_files(repo_path: str) -> list[str]:
    """Returns a list of all relative file paths in the repo, ignoring common hidden/build dirs."""
    ignore_dirs = {'.git', 'node_modules', '__pycache__', 'dist', 'build', '.claude-plugin', '.venv', 'venv'}
    files = []
    base_path = Path(repo_path)
    for root, dirs, filenames in os.walk(base_path):
        # Modify dirs in-place to skip ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for filename in filenames:
            full_path = Path(root) / filename
            files.append(str(full_path.relative_to(base_path)).replace("\\", "/"))
    return files

def search_text_in_file(repo_path: str, filepath: str, keyword: str) -> str | None:
    """
    Scans a file line by line to detect the strongest evidence type for a keyword.
    Returns one of: CLASS_DEFINITION, FUNCTION_DEFINITION, IMPORT_REFERENCE, TEXT_REFERENCE, or None.
    """
    full_path = Path(repo_path) / filepath
    best_match = None
    
    kw_esc = re.escape(keyword)
    
    # Language-aware (but dumb/regex-based) patterns
    class_pattern = re.compile(rf'\b(?:class|interface|enum|type)\s+{kw_esc}\b', re.IGNORECASE)
    func_pattern = re.compile(rf'\b(?:function|def|func)\s+{kw_esc}\b', re.IGNORECASE)
    import_pattern = re.compile(rf'\b(?:import|from)\b.*?\b{kw_esc}\b', re.IGNORECASE)

    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            for line in f:
                if keyword.lower() in line.lower():
                    if not best_match:
                        best_match = "TEXT_REFERENCE"
                    
                    if class_pattern.search(line):
                        return "CLASS_DEFINITION" # Highest text evidence, return early
                    
                    if func_pattern.search(line):
                        if best_match not in ["CLASS_DEFINITION", "FUNCTION_DEFINITION"]:
                            best_match = "FUNCTION_DEFINITION"
                            
                    elif import_pattern.search(line):
                        if best_match not in ["CLASS_DEFINITION", "FUNCTION_DEFINITION", "IMPORT_REFERENCE"]:
                            best_match = "IMPORT_REFERENCE"
                            
    except (UnicodeDecodeError, FileNotFoundError, IsADirectoryError):
        pass
        
    return best_match
