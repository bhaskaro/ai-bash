import os, re, shlex, subprocess, textwrap, time, signal, resource, pathlib

SANDBOX = os.environ.get("AI_BASH_SANDBOX", os.getcwd())
SECRET_PATTERNS = [r"AKIA[0-9A-Z]{16}", r"ghp_[0-9A-Za-z]{36}", r"(?i)api[_-]?key[:=]\s*[\w-]+"]
MAX_STDIO_BYTES = int(os.environ.get("AI_BASH_MAX_STDIO_BYTES", "131072"))  # 128KB


def ensure_sandbox(path: str) -> str:
    """Return a safe absolute path within AI_BASH_SANDBOX."""
    base = os.getenv("AI_BASH_SANDBOX", os.getcwd())
    full = os.path.abspath(path)
    base_abs = os.path.abspath(base)

    # Allow any subdirectory of the sandbox
    if not full.startswith(base_abs):
        raise PermissionError(f"Access to {full} outside sandbox {base_abs}")
    return full


def redact(text: str) -> str:
    red = text
    for pat in SECRET_PATTERNS:
        red = re.sub(pat, "[REDACTED]", red)
    return red

def clamp_output(data: bytes) -> str:
    if len(data) > MAX_STDIO_BYTES:
        return data[:MAX_STDIO_BYTES].decode(errors="replace") + "\n[...truncated...]"
    return data.decode(errors="replace")

def limit_resources():
    # cpu time (s), address space (bytes), file size (bytes)
    resource.setrlimit(resource.RLIMIT_CPU, (10, 10))
    resource.setrlimit(resource.RLIMIT_AS, (512*1024*1024, 512*1024*1024))
    resource.setrlimit(resource.RLIMIT_FSIZE, (64*1024*1024, 64*1024*1024))
