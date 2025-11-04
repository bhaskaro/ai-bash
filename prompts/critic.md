Critique the plan and commands for:
- correctness, portability, least-privilege, sandbox path safety
- secrets exposure, sudo/install usage
- destructive actions (rm -rf, chmod -R, mv over)
If risky or ambiguous, propose safer alternatives or request confirmation.
Return JSON {"ok": bool, "reasons": [...], "fixes": [...]}.
