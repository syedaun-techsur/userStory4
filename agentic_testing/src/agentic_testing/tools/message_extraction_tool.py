import os
import re
import json

EXCLUDE_DIRS = {'node_modules', 'dist', 'build', '.git'}
SCAN_EXTENSIONS = ('.js', '.jsx', '.ts', '.tsx')
KEYWORD_WHITELIST = None  # or set to {'error', 'required', ...}
MESSAGE_PATTERNS = {
    'react-form': r"newErrors\.\w+\s*=\s*['\"]([^'\"]{5,150})['\"]",
    'setError': r"setError\(\s*['\"]([^'\"]{5,150})['\"]\s*[\),]",
    'toast': r"toast\.(?:error|success|info|warning)\(\s*['\"]([^'\"]{5,150})['\"]\s*[,)]",
    'i18n': r"\bt\(\s*['\"]([^'\"]{5,150})['\"]\s*[\),]",
    'throwError': r"throw\s+new\s+Error\(\s*['\"]([^'\"]{5,150})['\"]\s*\)",
    'toast-desc': r"description\s*:\s*['\"]([^'\"]{5,150})['\"]",
    'toast-title': r"title\s*:\s*['\"]([^'\"]{5,150})['\"]",
    'alert': r"alert\(\s*['\"]([^'\"]{5,150})['\"]\s*\)",
    'console': r"console\.(?:log|warn|error)\(\s*['\"]([^'\"]{5,150})['\"]\s*\)"
}

def is_relevant(msg: str) -> bool:
    low = msg.lower()
    if KEYWORD_WHITELIST:
        if not any(k in low for k in KEYWORD_WHITELIST):
            return False
    return 5 <= len(msg) <= 150 and any(c.isalpha() for c in msg)

def extract_messages_from_file(path):
    messages = []
    try:
        with open(path, encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            full_text = ''.join(lines)
            for msg_type, pattern in MESSAGE_PATTERNS.items():
                for match in re.finditer(pattern, full_text):
                    msg = match.group(1).strip()
                    if is_relevant(msg):
                        start = match.start()
                        line_no = full_text[:start].count('\n') + 1
                        messages.append({
                            'message': msg,
                            'type': msg_type,
                            'file': path,
                            'line': line_no
                        })
    except Exception as e:
        print(f"Error parsing {path}: {e}")
    return messages

def extract_messages():
    # Get the project root directory (4 levels up from this file)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
    
    all_msgs = []
    seen = set()
    # Use absolute path for scanning
    scan_dir = os.path.join(project_root, 'testing_automation')
    if not os.path.exists(scan_dir):
        print(f"Directory not found: {scan_dir}")
        return
        
    for root, dirs, files in os.walk(scan_dir):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for f in files:
            if f.endswith(SCAN_EXTENSIONS):
                path = os.path.join(root, f)
                for msg in extract_messages_from_file(path):
                    key = (msg['message'], msg['type'])
                    if key not in seen:
                        all_msgs.append({'message': msg['message'], 'type': msg['type']})
                        seen.add(key)
    
    # Use absolute path for output
    out_dir = os.path.join(project_root, 'features', 'meta_data')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'extracted_messages.json')
    with open(out_path, 'w') as out:
        json.dump(all_msgs, out, indent=2)
    print(f"Extracted {len(all_msgs)} unique messages from source files. Saved to {out_path}")

if __name__ == "__main__":
    extract_messages() 