import os, platform, shutil
def sys_info():
    return {
        "os": platform.system(),
        "kernel": platform.release(),
        "cpu": platform.processor(),
        "user": os.getenv("USER") or os.getenv("USERNAME"),
        "cwd": os.getcwd(),
    }

def which(command):
    return {"command": command, "path": shutil.which(command)}
