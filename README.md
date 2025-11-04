---

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
│   └── ai-sh
├── prompts/
│   ├── system_shell.md
│   ├── tool_instructions.md
│   ├── planner.md
│   ├── critic.md
│   └── nl2cmd.md
├── src/
│   ├── cli.py
│   ├── agent.py
│   ├── loop.py
│   ├── policy.py
│   ├── schema.py
│   └── tools/
│       ├── shell.py
│       ├── fs.py
│       ├── net.py
│       ├── sysinfo.py
│       └── utils.py
└── pyproject.toml

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
git clone https://github.com/<your-username>/ai-bash.git
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
nano .env
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

Confirm key load:

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
| `OPENAI_API_KEY`          | API key (supports project-scoped `sk-proj-*`)                                              |
| `OPENAI_PROJECT_ID`       | Required for `sk-proj-*` keys                                                              |
| `OPENAI_MODEL`            | Model name (e.g., `gpt-4o-mini-2024-07-18`)                                                |
| `AI_BASH_SANDBOX`         | Safe directory for file operations                                                         |
| `AI_BASH_MAX_STDIO_BYTES` | Max captured stdout/stderr bytes                                                           |
| `AI_BASH_FAST_MODE`       | Skip planner/critic (1=on)                                                                 |
| `AI_BASH_DEBUG`           | Enable debug output (1=on)                                                                 |
| `AI_BASH_AUTO_CONFIRM`    | Automatically run flagged commands (use with caution)                                      |
| `AI_BASH_NL2CMD`          | Enable NL→CMD conversion logic (1=on)                                                      |

---

## 🧩 How It Works

### 1️⃣ Fast Paths

* `use:` or `run:` executes the command directly (no LLM).
* Example: `run tree in the current directory` → normalized to `tree .`

### 2️⃣ NL→CMD→RUN

* AI Bash sends your input to `prompts/nl2cmd.md`.
* The model returns strict JSON:

  ```json
  { "cmd": "find . -type f | sort -nr | head -n 5", "reason": "list largest files", "needs_confirmation": false }
  ```
* Shell executes the command safely (after confirmation if required).

### 3️⃣ Tool Loop (Function Calling)

* When tasks are more complex, the LLM calls registered tools:

  * `run_cmd`
  * `read_file`, `write_file`, `append_file`
  * `http_get`
  * `sys_info`, `which`

---

## 🛡️ Safety & Sandbox

* Commands execute only inside `AI_BASH_SANDBOX`.
* Risky commands (`rm -rf /`, `mkfs`, `dd`, `sudo`, etc.) are blocked or require confirmation.
* Customize allowed patterns in `BANNED_SNIPPETS` in `src/loop.py`.

---

## 🧪 Troubleshooting

| Issue                 | Resolution                                                                    |
| --------------------- | ----------------------------------------------------------------------------- |
| **401 Unauthorized**  | Verify `OPENAI_API_KEY` and `OPENAI_PROJECT_ID`. Test with `curl`.            |
| **400 Bad Request**   | Already fixed — ensure correct tool message order.                            |
| **Command not found** | The tool verifies with `which <cmd>` before reporting missing.                |
| **Command hangs**     | Commands have 20s timeout. Prefer lightweight alternatives (`find` + `head`). |
| **CRLF line endings** | Normalize: `sed -i 's/\r$//' bin/ai-sh src/**/*.py`                           |

---

## 🧰 Useful Examples

```bash
# Largest files
use: find . -type f -printf "%s\t%p\n" | sort -nr | head -n 20

# Directory tree
use: tree -sh .

# Search logs
use: grep -Rni "ERROR" . | head -n 50

# Summarize system logs
run: dmesg | tail -n 200
```

---

## 🧑‍💻 Developer Setup

### Formatting and Linting

```bash
black src/
flake8 src/
```

### Run in Debug Mode

```bash
export AI_BASH_DEBUG=1
./bin/ai-sh
```

### Update Dependencies

```bash
pip freeze > requirements.txt
```

### Test with Another Model

```bash
OPENAI_MODEL=nemotron-4-340b-instruct ./bin/ai-sh
```

---

## 📜 License & Credits

**License:** MIT (or your preferred license)

**Credits:**

* Inspired by NVIDIA’s [Bash Computer-Use Agent](https://developer.nvidia.com/blog/create-your-own-bash-computer-use-agent-with-nvidia-nemotron-in-one-hour/).
* Extended for sandboxing, OpenAI/Nemotron integration, and natural-language-to-command execution.

---

## 💬 Example Session

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

```

---
