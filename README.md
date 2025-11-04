## ✅ `README.md`

```markdown
# 🧠 AI Bash — Natural-Language Shell with LLM-Powered Command Execution

AI Bash is an **AI-enabled interactive shell** that converts natural language into **safe, auditable shell commands** — then executes them in a **sandboxed** environment.  
It’s built with Python, OpenAI-compatible APIs (e.g., OpenAI GPT-4o or NVIDIA Nemotron), and a modular tool system for command execution, file management, and system queries.

---

## 📑 Table of Contents

1. [Features](#-features)
2. [Project Structure](#-project-structure)
3. [Requirements](#-requirements)
4. [Quickstart](#-quickstart)
5. [Environment Variables](#-environment-variables)
6. [How It Works](#-how-it-works)
7. [Safety & Sandbox](#-safety--sandbox)
8. [Troubleshooting](#-troubleshooting)
9. [Developer Setup](#-developer-setup)
10. [License & Credits](#-license--credits)

---

## ✨ Features

- **Natural Language → Command → Execution**  
  Ask things like “list the top 5 largest files under .” and AI Bash runs the appropriate `find|sort|head` command.
- **Fast Paths**  
  - `use:` or `run:` executes the exact command directly.  
  - Example: `use: tree -sh .` → instant output.
- **AI Reasoning Mode**  
  Uses an LLM to interpret, plan, and confirm tasks before execution.
- **Sandbox Enforcement**  
  All commands execute within a defined directory (`AI_BASH_SANDBOX`).
- **Safety & Confirmation**  
  Risky commands trigger manual confirmation (or auto-approve if you set `AI_BASH_AUTO_CONFIRM=1`).
- **Cross-Provider Support**  
  Works with OpenAI, NVIDIA Nemotron, and other OpenAI-compatible APIs.
- **Debug Mode**  
  Prints detailed `[debug]` logs for troubleshooting API or tool flow.

---

## 🧩 Project Structure

```

ai-bash/
├── README.md
├── .gitignore
├── .env.example
├── requirements.txt
├── bin/
│   └── ai-sh                  # main launcher (bash)
├── prompts/
│   ├── system_shell.md
│   ├── tool_instructions.md
│   ├── planner.md
│   ├── critic.md
│   └── nl2cmd.md
├── src/
│   ├── cli.py                 # REPL loop
│   ├── agent.py               # LLM client + tool dispatcher
│   ├── loop.py                # core logic (fast paths + NL2CMD + tool loop)
│   ├── policy.py              # optional safety policies
│   ├── schema.py              # tool schemas for function-calling
│   └── tools/
│       ├── shell.py
│       ├── fs.py
│       ├── net.py
│       ├── sysinfo.py
│       └── utils.py
└── pyproject.toml             # optional, if packaging

````

---

## ⚙️ Requirements

- Python **3.11+** (tested with 3.12)
- Internet connection for API access
- A valid **OpenAI-compatible API key**
- Optional utilities: `tree`, `find`, `du`, `grep`, etc.  
  ```bash
  sudo apt update && sudo apt install -y tree findutils
````

---

## 🚀 Quickstart

### 1️⃣ Clone and enter the repo

```bash
git clone git@github.com:bhaskaro/ai-bash.git 
cd ai-bash
```

### 2️⃣ Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
# (Windows PowerShell)
# .\.venv\Scripts\Activate.ps1
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Copy and edit environment file

```bash
cp .env.example .env
nano .env   # or vi .env
```

Update your `OPENAI_API_KEY`, `OPENAI_MODEL`, and sandbox path.

---

## 🌍 Loading Environment Variables

### Linux / macOS

```bash
set -a
. ./.env
set +a
```

### Windows (PowerShell)

```powershell
Get-Content .env | ForEach-Object {
    if ($_ -match '^(?<key>[^#=]+)=(?<value>.+)$') {
        [System.Environment]::SetEnvironmentVariable($matches['key'].Trim(), $matches['value'].Trim())
    }
}
```

Your key is loaded when this prints a partial token:

```bash
echo $OPENAI_API_KEY | cut -c1-10
```

---

## 🧠 Running the Shell

```bash
./bin/ai-sh
```

Example session:

```
🤖 AI Bash: type your task. Ctrl+C to exit.

> list the top 5 largest files under .
# find . -type f -printf "%s\t%p\n" | sort -nr | head -n 5
123456 ./bigfile.log
...

> use: tree -sh .
[4.0K] .
├── bin
│   └── ai-sh
...

> exit
👋 Exiting AI Bash — see you next time!
```

---

## 🔐 Environment Variables

| Variable                  | Description                                                                                |
| ------------------------- | ------------------------------------------------------------------------------------------ |
| `OPENAI_BASE_URL`         | API endpoint (`https://api.openai.com/v1` or NVIDIA `https://integrate.api.nvidia.com/v1`) |
| `OPENAI_API_KEY`          | API key (supports project-scoped `sk-proj-...`)                                            |
| `OPENAI_PROJECT_ID`       | Required for `sk-proj-*` keys                                                              |
| `OPENAI_MODEL`            | Model name (e.g., `gpt-4o-mini-2024-07-18`, `nemotron-4-340b-instruct`)                    |
| `AI_BASH_SANDBOX`         | Safe directory for file operations                                                         |
| `AI_BASH_MAX_STDIO_BYTES` | Max captured stdout/stderr bytes (default 131072)                                          |
| `AI_BASH_FAST_MODE`       | Skip planner/critic for faster response (1=on)                                             |
| `AI_BASH_DEBUG`           | Enable debug output (1=on)                                                                 |
| `AI_BASH_AUTO_CONFIRM`    | Automatically run flagged commands (use cautiously)                                        |
| `AI_BASH_NL2CMD`          | Enable NL→CMD conversion logic (1=on)                                                      |

---

## 🧩 How It Works

### 1️⃣ Fast Paths

* `use:` or `run:` executes the command directly (no LLM).
* Works even with natural phrasing:
  `run tree in the current directory` → normalized to `tree .`

### 2️⃣ NL→CMD→RUN

* AI Bash sends your text through `prompts/nl2cmd.md`.
* The model returns JSON:

  ```json
  { "cmd": "find . -type f | sort -nr | head -n 5", "reason": "list largest files", "needs_confirmation": false }
  ```
* The shell executes the command (after confirmation if risky).

### 3️⃣ Tool Loop (Function Calling)

* If no single command fits, the model calls Python tools:

  * `run_cmd` (shell)
  * `read_file`, `write_file`, `append_file`
  * `http_get`
  * `sys_info`, `which`, etc.

---

## 🛡️ Safety & Sandbox

* All commands run under `AI_BASH_SANDBOX`.
* Dangerous patterns are blocked or require confirmation:

  * `rm -rf /`, `mkfs`, `dd if=`, `shutdown`, `reboot`, `sudo`, etc.
* Add or modify patterns in `BANNED_SNIPPETS` inside `src/loop.py`.

---

## 🧪 Troubleshooting

| Issue                            | Fix                                                                                       |
| -------------------------------- | ----------------------------------------------------------------------------------------- |
| **401 Unauthorized**             | Ensure `OPENAI_API_KEY` and `OPENAI_PROJECT_ID` are correct. Use `curl` to test API.      |
| **400 Tool message order error** | You’re already fixed — the current loop properly appends tool calls before results.       |
| **“Command not available”**      | The shell now runs `which <cmd>` to verify availability. If `tree` exists, it runs.       |
| **Command hangs**                | Commands have built-in 20s timeout. For large directory trees, use `find` with `head -n`. |
| **Windows line endings (CRLF)**  | Normalize: `sed -i 's/\r$//' bin/ai-sh src/**/*.py`                                       |

---

## 🧰 Useful Examples

```bash
# Fast file listing
use: find . -type f -printf "%s\t%p\n" | sort -nr | head -n 20

# Show directory tree
use: tree -sh .

# Search logs
use: grep -Rni "ERROR" . | head -n 50

# Summarize kernel logs
run: dmesg | tail -n 200
```

---

## 🧑‍💻 Developer Setup

### Code formatting

```bash
black src/
flake8 src/
```

### Run interactive shell (debug mode)

```bash
export AI_BASH_DEBUG=1
./bin/ai-sh
```

### Update requirements

```bash
pip freeze > requirements.txt
```

### Run locally with different models

```bash
OPENAI_MODEL=nemotron-4-340b-instruct ./bin/ai-sh
```

---

## 📜 License & Credits

**License:** MIT (or choose another if you prefer)

**Credits:**

* Inspired by NVIDIA’s [“Bash Computer-Use Agent”](https://developer.nvidia.com/blog/create-your-own-bash-computer-use-agent-with-nvidia-nemotron-in-one-hour/)
* Extended for cross-provider use, sandboxing, and direct `use:` / `run:` control.

---

### 💬 Example Session

```
🤖 AI Bash: type your task. Ctrl+C to exit.

> show directory structure
# tree -sh .
[4.0K] .
├── bin
│   └── ai-sh
...

> exit
👋 Exiting AI Bash — see you next time!
```

---

```

---
