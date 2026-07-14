import argparse
import os
import re
from typing import Dict, List, Any, Tuple
from search import get_all_files, search_text_in_file

SYNONYMS = {
    'login': ['signin', 'auth', 'authentication'],
    'logout': ['signout'],
    'navbar': ['navigation', 'nav'],
    'button': ['btn'],
    'ui': ['frontend', 'interface'],
    'backend': ['server'],
    'db': ['database'],
    'repo': ['repository'],
    'config': ['configuration'],
    'test': ['spec'],
    'api': ['endpoint'],
    'route': ['routing'],
    'user': ['account'],
    'admin': ['administrator']
}

EVIDENCE_PRIORITY = {
    "EXACT_FILENAME": 90,
    "NORMALIZED_FILENAME": 80,
    "STARTS_WITH_FILENAME": 70,
    "CONTAINS_FILENAME": 60,
    "CLASS_DEFINITION": 50,
    "FUNCTION_DEFINITION": 40,
    "IMPORT_REFERENCE": 30,
    "DIRECTORY_MATCH": 20,
    "TEXT_REFERENCE": 10
}

CONFIDENCE_MAP = {
    "EXACT_FILENAME": "High",
    "NORMALIZED_FILENAME": "High",
    "STARTS_WITH_FILENAME": "Medium",
    "CONTAINS_FILENAME": "Medium",
    "CLASS_DEFINITION": "High",
    "FUNCTION_DEFINITION": "High",
    "IMPORT_REFERENCE": "Medium",
    "DIRECTORY_MATCH": "Medium",
    "TEXT_REFERENCE": "Low"
}

REASON_MAP = {
    "EXACT_FILENAME": "Exact filename match",
    "NORMALIZED_FILENAME": "Normalized filename match",
    "STARTS_WITH_FILENAME": "Filename starts with keyword",
    "CONTAINS_FILENAME": "Filename contains keyword",
    "CLASS_DEFINITION": "Contains class definition",
    "FUNCTION_DEFINITION": "Contains function definition",
    "IMPORT_REFERENCE": "Imports symbol",
    "DIRECTORY_MATCH": "Directory name matches keyword",
    "TEXT_REFERENCE": "Text reference match"
}

def normalize_word(word: str) -> str:
    """Basic plural normalization: strip trailing 's' or 'es' if word is long enough."""
    if len(word) > 4 and word.endswith('es'):
        return word[:-2]
    if len(word) > 3 and word.endswith('s') and not word.endswith('ss'):
        return word[:-1]
    return word

def normalize_filename(name: str) -> str:
    """Lowercases, removes extensions, and strips separators for deterministic matching."""
    if '.' in name:
        name = name.split('.')[0]
    return re.sub(r'[\.\_\-]', '', name.lower())

def extract_keywords(task: str) -> List[str]:
    """Extracts keywords and adds synonyms for broader, yet deterministic matching."""
    task_clean = re.sub(r'[^\w\.\-\/]', ' ', task.lower())
    words = task_clean.split()
    stop_words = {'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'fix', 'add', 'update', 'remove', 'where', 'why', 'how', 'is', 'it'}
    
    keywords = set()
    for w in words:
        if w not in stop_words and len(w) > 2:
            norm = normalize_word(w)
            keywords.add(norm)
            for key, syn_list in SYNONYMS.items():
                if norm == key or norm in syn_list:
                    keywords.add(key)
                    keywords.update(syn_list)
                    
    return list(keywords)

def is_test_file(filepath: str) -> bool:
    name = filepath.lower()
    return '.spec.' in name or '.test.' in name or '_spec.' in name or '_test.' in name

def rank_candidates(task: str, repo_path: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, str]], Dict[str, int]]:
    """Ranks candidates based on multiple signals and tracks skipped files with reasons."""
    keywords = extract_keywords(task)
    all_files = get_all_files(repo_path)
    
    is_test_task = any(w in ['test', 'spec', 'e2e'] for w in keywords)
    
    candidates = {}
    skipped = []
    diagnostics = {
        "scanned": len(all_files),
        "filename": 0,
        "class": 0,
        "import": 0,
        "text": 0
    }
    
    for filepath in all_files:
        path_lower = filepath.lower()
        filename_raw = os.path.basename(path_lower)
        filename_norm = normalize_filename(filename_raw)
        
        best_evidence = None
        best_score = 0
        
        for keyword in keywords:
            kw_norm = normalize_filename(keyword)
            kw_raw = keyword.lower()
            
            evidence = None
            
            # 1. Filename checks
            file_base = filename_raw.split('.')[0]
            if kw_raw == file_base:
                evidence = "EXACT_FILENAME"
                diagnostics["filename"] += 1
            elif kw_norm == filename_norm:
                evidence = "NORMALIZED_FILENAME"
                diagnostics["filename"] += 1
            elif filename_norm.startswith(kw_norm):
                evidence = "STARTS_WITH_FILENAME"
                diagnostics["filename"] += 1
            elif kw_norm in filename_norm:
                evidence = "CONTAINS_FILENAME"
                diagnostics["filename"] += 1
                
            # 2. Directory match
            elif kw_raw in path_lower:
                evidence = "DIRECTORY_MATCH"
                
            # If current evidence is not top-tier, check text for class/func/import which might score higher
            if not evidence or EVIDENCE_PRIORITY[evidence] < EVIDENCE_PRIORITY["CLASS_DEFINITION"]:
                text_evidence = search_text_in_file(repo_path, filepath, keyword)
                if text_evidence:
                    if text_evidence == "CLASS_DEFINITION" or text_evidence == "FUNCTION_DEFINITION":
                        diagnostics["class"] += 1
                    elif text_evidence == "IMPORT_REFERENCE":
                        diagnostics["import"] += 1
                    else:
                        diagnostics["text"] += 1
                        
                    # Override if text evidence is stronger
                    if not evidence or EVIDENCE_PRIORITY[text_evidence] > EVIDENCE_PRIORITY[evidence]:
                        evidence = text_evidence
            
            if evidence and EVIDENCE_PRIORITY[evidence] > best_score:
                best_score = EVIDENCE_PRIORITY[evidence]
                best_evidence = evidence
                
        if best_evidence:
            # Implement "Implementation > Test" priority logic
            if is_test_file(filepath) and not is_test_task:
                # Heavily penalize test files so they rank below weak implementation matches
                best_score -= 50
                if best_score < 1:
                    best_score = 1 # Keep it on the board, but at the very bottom
                    
            candidates[filepath] = {
                "file": filepath,
                "score": best_score,
                "confidence": CONFIDENCE_MAP[best_evidence],
                "reason": REASON_MAP[best_evidence]
            }
        else:
            skipped.append({
                "file": filepath,
                "reason": "No filename similarity. No directory match. No symbol or text match."
            })
            
    # Sort by score descending
    ranked = sorted(candidates.values(), key=lambda x: x['score'], reverse=True)
    return ranked, skipped, diagnostics

def print_execution_plan(task: str, keywords: List[str], candidates: List[Dict], skipped: List[Dict], diagnostics: Dict):
    if not candidates:
        print("\n## Search Diagnostics\n")
        print(f"Task:\n{task}\n")
        print(f"Keywords:\n" + "\n".join(keywords) + "\n")
        print(f"Repository scanned:\n{diagnostics['scanned']} files\n")
        print(f"Filename matches:\n{diagnostics['filename']}")
        print(f"Class matches:\n{diagnostics['class']}")
        print(f"Import matches:\n{diagnostics['import']}")
        print(f"Text matches:\n{diagnostics['text']}\n")
        print("Possible reason:\nNo files matching the extracted concepts exist in the repository.\n")
        
        # Suggest synonyms related to the keywords if any apply
        original_words = set(re.sub(r'[^\w\.\-\/]', ' ', task.lower()).split())
        suggestions = set()
        for kw in original_words:
            norm = normalize_word(kw)
            for key, syns in SYNONYMS.items():
                if norm == key or norm in syns:
                    suggestions.add(key)
                    suggestions.update(syns)
        
        if suggestions:
            print("Suggestions:")
            for s in sorted(suggestions):
                print(s)
            print()
        return

    print("\n## Execution Plan\n")
    
    for i, c in enumerate(candidates, 1):
        round_label = f"Round {i}"
        if i > 1:
            round_label += " (Only if required)"
            
        print(f"{round_label}\n")
        print("Open:\n")
        print(f"{c['file']}\n")
        print("Reason:\n")
        print(c['reason'] + "\n")
        print("Confidence:\n")
        print(c['confidence'] + "\n")
        
        if i == 1:
            print("Stop Condition:\n")
            print("If sufficient understanding is achieved,\nstop immediately.\n")

    if skipped:
        print("## Skipped Files\n")
        # Show only 2 skipped files to keep it clean, as requested "Show only meaningful skipped files"
        for s in skipped[:2]:
            print("Skipped:")
            print(s['file'])
            print("Reason:")
            print(s['reason'] + "\n")

def main():
    parser = argparse.ArgumentParser(description="Forge Context Ranker")
    parser.add_argument("--repo", required=True, help="Path to the repository")
    parser.add_argument("--task", required=True, help="The user's task or request")
    
    args = parser.parse_args()
    
    keywords = extract_keywords(args.task)
    candidates, skipped, diagnostics = rank_candidates(args.task, args.repo)
    print_execution_plan(args.task, keywords, candidates, skipped, diagnostics)

if __name__ == "__main__":
    main()
