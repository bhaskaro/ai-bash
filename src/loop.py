import json, os, re, time, shlex, shutil
from .agent import llm_chat, call_tool
from .schema import TOOL_SCHEMAS

def load(path):
    with open(path,"r",encoding="utf-8") as f:
        return f.read()

SYSTEM   = load(os.path.join("prompts","system_shell.md"))
TOOLTXT  = load(os.path.join("prompts","tool_instructions.md"))
PLANNER  = load(os.path.join("prompts","planner.md"))
CRITIC   = load(os.path.join("prompts","critic.md"))
NL2CMD   = load(os.path.join("prompts","nl2cmd.md"))

BANNED_SNIPPETS = [
    "rm -rf /", "mkfs", "dd if=", "shutdown", "reboot", "useradd", "usermod",
    ":(){:|:&};:", "chown -R /", "chmod -R 777 /"
]

def _extract_json(text: str):
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r'\{.*\}', text, flags=re.S)
        if not m: raise
        return json.loads(m.group(0))

def _looks_dangerous(cmd: str) -> bool:
    cmd_l = cmd.lower()
    return any(b in cmd_l for b in BANNED_SNIPPETS) or " sudo " in f" {cmd_l} "

def ai_turn(user_text, confirm_callback=input):
    debug = os.getenv("AI_BASH_DEBUG") == "1"
    auto = os.getenv("AI_BASH_AUTO_CONFIRM") == "1"
    nl2cmd_enabled = os.getenv("AI_BASH_NL2CMD", "1") == "1"

    # --- Manual fast path: "use"/"run" (colon optional) runs directly ---
    txt = (user_text or "").strip()
    m = re.match(r'^(use|run)\s*:?\s*(.*)$', txt, flags=re.I)
    if m and m.group(2):
        raw = m.group(2).strip()
        # simple phrase normalization
        normalized = re.sub(r'\b(in\s+)?the\s+current\s+directory\b', '.', raw, flags=re.I)
        normalized = re.sub(r'\bhere\b', '.', normalized, flags=re.I)
        try: parts = shlex.split(normalized)
        except ValueError: parts = normalized.split()
        if parts and shutil.which(parts[0]):
            cmd = ' '.join(parts)
            res = call_tool("run_cmd", {"command": cmd, "timeout_s": 30})
            out = (res.get("stdout") or "").strip()
            err = (res.get("stderr") or "").strip()
            shown = out if out else err
            if len(shown) > 120000:
                shown = shown[:120000] + "\n[...truncated output shown...]"
            return {"final": shown or "(no output)"}
        # fall through to NL2CMD/tool loop if not a valid command

    # --- NL -> CMD -> RUN path (default on) ---
    if nl2cmd_enabled:
        if debug: print("[debug] nl2cmd call...")
        msgs = [
            {"role":"system","content": SYSTEM + "\n\n" + TOOLTXT + "\n\n" + NL2CMD},
            {"role":"user","content": user_text}
        ]
        resp = llm_chat(msgs)
        txt = resp["choices"][0]["message"].get("content","{}").strip() or "{}"
        plan = _extract_json(txt)
        cmd = (plan.get("cmd") or "").strip()
        reason = plan.get("reason","")
        needs = bool(plan.get("needs_confirmation", False))

        if not cmd:
            # fallback to tool loop if model failed to produce a command
            if debug: print("[debug] nl2cmd produced no cmd — falling back to tool loop")

        else:
            # safety gate
            flagged = needs or _looks_dangerous(cmd)
            if flagged and not auto:
                print("\n-------- CONFIRMATION REQUIRED --------")
                print("Reason:", reason or "(n/a)")
                print("Command:", cmd)
                ans = confirm_callback("Type 'yes' to run: ")
                if ans.strip().lower() != "yes":
                    return {"cancelled": True, "cmd": cmd, "reason": reason}

            # execute
            res = call_tool("run_cmd", {"command": cmd, "timeout_s": 30})
            out = (res.get("stdout") or "").strip()
            err = (res.get("stderr") or "").strip()
            shown = out if out else err
            if len(shown) > 120000:
                shown = shown[:120000] + "\n[...truncated output shown...]"
            prefix = f"# {cmd}\n"
            return {"final": prefix + (shown or "(no output)")}

    # --- Tool loop (reason+act) ---
    if debug: print("[debug] executor loop...")
    history = [
        {"role":"system","content": SYSTEM + "\n\n" + TOOLTXT},
        {"role":"user","content": user_text}
    ]
    while True:
        if debug: print("[debug] assistant(step) call...")
        resp = llm_chat(history, tools=TOOL_SCHEMAS, tool_choice="auto")
        msg = resp["choices"][0]["message"]
        if debug: print("[debug] assistant(step) returned")

        if not msg.get("tool_calls"):
            history.append({"role":"assistant","content": msg.get("content","")})
            return {"final": msg.get("content","(no content)")}

        history.append({"role":"assistant","content": msg.get("content",""), "tool_calls": msg["tool_calls"]})
        for tc in msg["tool_calls"]:
            name = tc["function"]["name"]
            args_json = tc["function"].get("arguments") or "{}"
            try: args = json.loads(args_json)
            except Exception: args = {}
            result = call_tool(name, args)
            history.append({"role":"tool","tool_call_id": tc["id"], "name": name, "content": json.dumps(result)})
