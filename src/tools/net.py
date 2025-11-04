import urllib.request
from .utils import redact
def http_get(url, max_kb=128):
    with urllib.request.urlopen(url, timeout=10) as r:
        data = r.read(max_kb*1024)
    return {"url": url, "content": redact(data.decode("utf-8", errors="replace"))}
