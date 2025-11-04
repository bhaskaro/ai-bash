Given the user's request and available tools, produce:
- "plan": 2-5 bullet steps, each step referencing a tool call.
- "requires_confirmation": true/false
- "dangerous_commands": array of commands that could modify files, install packages, or escalate privileges
- "commands": array of commands you intend to run in order (max 3)
- "notes": brief assumptions or questions if any

Output strictly as JSON.
