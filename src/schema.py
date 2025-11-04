TOOL_SCHEMAS = [
  {
    "type": "function",
    "function": {
      "name": "run_cmd",
      "description": "Run a non-interactive shell command in sandbox (resource limited).",
      "parameters": {
        "type": "object",
        "properties": {
          "command": {"type": "string"},
          "timeout_s": {"type": "integer", "minimum": 1, "maximum": 180}
        },
        "required": ["command"]
      }
    }
  },
  {
    "type": "function",
    "function": {
      "name": "read_file",
      "parameters": {"type":"object","properties":{"path":{"type":"string"},"max_kb":{"type":"integer"}},"required":["path"]}
    }
  },
  {
    "type": "function",
    "function": {
      "name": "write_file",
      "parameters": {"type":"object","properties":{"path":{"type":"string"},"content":{"type":"string"},"mode":{"type":"string"}},"required":["path","content"]}
    }
  },
  {
    "type": "function",
    "function": {
      "name":"append_file",
      "parameters":{"type":"object","properties":{"path":{"type":"string"},"content":{"type":"string"}},"required":["path","content"]}
    }
  },
  {
    "type": "function",
    "function": {
      "name":"list_dir",
      "parameters":{"type":"object","properties":{"path":{"type":"string"}}}
    }
  },
  {
    "type": "function",
    "function": {
      "name":"find_text",
      "parameters":{"type":"object","properties":{"path":{"type":"string"},"pattern":{"type":"string"}},"required":["path","pattern"]}
    }
  },
  {
    "type":"function",
    "function":{
      "name":"http_get",
      "parameters":{"type":"object","properties":{"url":{"type":"string"},"max_kb":{"type":"integer"}},"required":["url"]}
    }
  },
  {
    "type":"function",
    "function":{
      "name":"sys_info",
      "parameters":{"type":"object","properties":{}}
    }
  },
  {
    "type":"function",
    "function":{
      "name":"which",
      "parameters":{"type":"object","properties":{"command":{"type":"string"}},"required":["command"]}
    }
  }
]
