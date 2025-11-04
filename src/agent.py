import os, time, requests

def llm_chat(messages, tools=None, tool_choice="auto"):
    base  = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    key   = os.getenv("OPENAI_API_KEY", "")
    debug = os.getenv("AI_BASH_DEBUG") == "1"

    if not key or len(key) < 20:
        raise RuntimeError("OPENAI_API_KEY is missing or looks like a placeholder.")

    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    if os.getenv("OPENAI_PROJECT_ID"):
        headers["OpenAI-Project"] = os.getenv("OPENAI_PROJECT_ID")
    if os.getenv("OPENAI_ORG_ID"):
        headers["OpenAI-Organization"] = os.getenv("OPENAI_ORG_ID")

    body = {"model": model, "messages": messages, "max_tokens": int(os.getenv("AI_BASH_MAX_TOKENS","256"))}
    if tools is not None:
        body["tools"] = tools
        if tool_choice:
            body["tool_choice"] = tool_choice

    t0 = time.time()
    if debug:
        print(f"[debug] POST {base}/chat/completions model={model} tool_choice={'auto' if tool_choice else 'none'}")
    r = requests.post(f"{base}/chat/completions", headers=headers, json=body, timeout=15)
    if debug:
        print(f"[debug] LLM call took {int((time.time()-t0)*1000)} ms, status {r.status_code}")
    if r.status_code >= 400:
        raise RuntimeError(f"{r.status_code} error from {base}. Body: {r.text}")
    return r.json()

# -------- Tool dispatcher (restored) --------
def call_tool(name, args):
    from .tools import shell as T_shell, fs as T_fs, net as T_net, sysinfo as T_sys  # local imports to avoid cycles
    if name == "run_cmd":   return T_shell.run_cmd(**args)
    if name == "read_file": return T_fs.read_file(**args)
    if name == "write_file":return T_fs.write_file(**args)
    if name == "append_file": return T_fs.append_file(**args)
    if name == "list_dir":  return T_fs.list_dir(**args)
    if name == "find_text": return T_fs.find_text(**args)
    if name == "http_get":  return T_net.http_get(**args)
    if name == "sys_info":  return T_sys.sys_info()
    if name == "which":     return T_sys.which(**args)
    return {"error": f"unknown tool {name}"}
