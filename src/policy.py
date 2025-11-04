DANGEROUS_PATTERNS = [
  "sudo ", "chmod -R", "chown -R", "rm -rf", "mv ", "dd if=", "mkfs", "iptables", "shutdown", "reboot", "useradd", "usermod"
]

def needs_confirmation(cmd: str) -> bool:
    return any(p in cmd for p in DANGEROUS_PATTERNS)

CONFIRM_TEMPLATE = """\
About to run a potentially destructive command:

{cmd}

Reason: {reason}

Type 'yes' to proceed, anything else to cancel.
"""
