import os, json
from .utils import ensure_sandbox, redact

def read_file(path, max_kb=128):
    p = ensure_sandbox(path)
    with open(p, "r", encoding="utf-8", errors="replace") as f:
        data = f.read(max_kb*1024)
    return {"path": p, "content": redact(data)}

def write_file(path, content, mode="w"):
    p = ensure_sandbox(path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, mode, encoding="utf-8") as f:
        f.write(content)
    return {"path": p, "bytes": len(content)}

def append_file(path, content):
    return write_file(path, content, mode="a")

def list_dir(path="."):
    p = ensure_sandbox(path or ".")
    entries = []
    for name in sorted(os.listdir(p)):
        full = os.path.join(p, name)
        st = os.stat(full)
        entries.append({"name": name, "bytes": st.st_size, "mode": oct(st.st_mode & 0o777), "is_dir": os.path.isdir(full)})
    return {"path": p, "entries": entries}

def find_text(path, pattern):
    import re
    p = ensure_sandbox(path)
    out = []
    with open(p, "r", encoding="utf-8", errors="ignore") as f:
        for i, line in enumerate(f, start=1):
            if re.search(pattern, line):
                out.append({"line": i, "text": line.strip()[:300]})
    return {"path": p, "matches": out}
