#!/usr/bin/env python3
"""Production preflight for Promptwright.

Checks that no secrets or debug code are present, that the Content-Security-Policy
script hashes match the inline scripts, and that required files exist.

  python scripts/preflight.py          check only
  python scripts/preflight.py --fix    rewrite the CSP script hashes after you edit index.html
"""
import base64, hashlib, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
CSP_FILES = [INDEX, ROOT / "_headers", ROOT / "vercel.json"]
FIX = "--fix" in sys.argv
problems = []

html = INDEX.read_text(encoding="utf-8")

def script_hashes(text):
    return ["'sha256-" + base64.b64encode(hashlib.sha256(m.group(1).encode()).digest()).decode() + "'"
            for m in re.finditer(r"<script>(.*?)</script>", text, re.S)]

expected = "script-src " + " ".join(script_hashes(html)) + ";"

# 1. CSP hashes
for f in CSP_FILES:
    if not f.exists():
        problems.append(f"missing file: {f.name}")
        continue
    text = f.read_text(encoding="utf-8")
    m = re.search(r"script-src [^;]+;", text)
    if not m:
        problems.append(f"{f.name}: no script-src directive found")
    elif m.group(0) != expected:
        if FIX:
            f.write_text(text.replace(m.group(0), expected), encoding="utf-8")
            print(f"fixed CSP hashes in {f.name}")
            if f == INDEX:
                html = f.read_text(encoding="utf-8")
        else:
            problems.append(f"{f.name}: CSP script hashes are stale (run with --fix)")

# 2. Secrets
SECRET_PATTERNS = {
    "generic API key": r"(?i)(api[_-]?key|secret[_-]?key|access[_-]?token)\s*[:=]\s*['\"][A-Za-z0-9_\-]{16,}['\"]",
    "Anthropic/OpenAI style key": r"\bsk-[A-Za-z0-9_\-]{20,}",
    "AWS access key": r"\bAKIA[0-9A-Z]{16}\b",
    "GitHub token": r"\bgh[pousr]_[A-Za-z0-9]{30,}\b",
    "private key block": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    "Slack token": r"\bxox[abprs]-[A-Za-z0-9-]{10,}",
}
for path in ROOT.rglob("*"):
    if not path.is_file() or ".git" in path.parts or path.suffix in {".png", ".jpg", ".zip"}:
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    for name, pat in SECRET_PATTERNS.items():
        if re.search(pat, text):
            problems.append(f"{path.relative_to(ROOT)}: looks like a {name}")

# 3. Debug and unsafe code
BANNED = {
    "console.": "console output left in",
    "debugger": "debugger statement",
    "eval(": "eval()",
    "new Function": "dynamic Function",
    "document.write": "document.write",
    "document.cookie": "cookie access (this site should not use cookies)",
    "http://": "insecure http:// URL",
}
for token, why in BANNED.items():
    if token in html:
        problems.append(f"index.html: {why} ({token})")
if re.search(r'\son[a-z]+="', html):
    problems.append("index.html: inline event handler attribute (breaks the strict CSP)")

# 4. Required files
for name in [".gitignore", ".env.example", "SECURITY.md", "README.md", "_headers", "vercel.json"]:
    if not (ROOT / name).exists():
        problems.append(f"missing file: {name}")
if (ROOT / ".env").exists():
    problems.append(".env exists in the repo folder; make sure it is git-ignored and never committed")

if problems:
    print("PREFLIGHT FAILED")
    for p in problems:
        print(" -", p)
    sys.exit(1)
print("PREFLIGHT PASSED: no secrets, no debug code, CSP hashes match.")
