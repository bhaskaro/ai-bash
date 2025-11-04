from .utils import ensure_sandbox, limit_resources, redact
import subprocess, os, time

MAX_STDIO_BYTES = int(os.environ.get("AI_BASH_MAX_STDIO_BYTES", "131072"))  # 128KB

def _clamp_text(s: str) -> str:
    if s is None:
        return ""
    b = s.encode(errors="replace")
    if len(b) > MAX_STDIO_BYTES:
        return b[:MAX_STDIO_BYTES].decode(errors="replace") + "\n[...truncated...]"
    return s

def run_cmd(command: str, timeout_s: int = 20):
    # inside run_cmd() before spawn
    if any(b in command for b in ["rm -rf /", ":(){:|:&};:", "mkfs", "dd if=", "shutdown", "reboot"]):
        return {"stdout":"", "stderr":"Blocked potentially destructive command.", "exit_code":126, "elapsed_ms":0}

    import shutil
    cmd_name = command.split()[0]
    if not shutil.which(cmd_name):
        return {"stdout": "", "stderr": f"Command '{cmd_name}' not found in PATH.", "exit_code": 127, "elapsed_ms": 0}

    start = time.time()
    try:
        proc = subprocess.Popen(
            command,
            cwd=ensure_sandbox("."),
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env={**os.environ, "LC_ALL":"C", "LANG":"C"},
            preexec_fn=limit_resources
        )
        try:
            out, err = proc.communicate(timeout=timeout_s)
        except subprocess.TimeoutExpired:
            proc.kill()
            out, err = proc.communicate()
            return {
                "stdout": "",
                "stderr": f"Timeout after {timeout_s}s",
                "exit_code": 124,
                "elapsed_ms": int((time.time()-start)*1000)
            }

        out = _clamp_text(out)
        err = _clamp_text(err)
        return {
            "stdout": redact(out),
            "stderr": redact(err),
            "exit_code": proc.returncode or 0,
            "elapsed_ms": int((time.time()-start)*1000)
        }
    except Exception as e:
        return {"stdout": "", "stderr": f"run_cmd error: {e}", "exit_code": 127, "elapsed_ms": int((time.time()-start)*1000)}
