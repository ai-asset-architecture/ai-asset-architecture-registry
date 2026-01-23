import os
import re
from pathlib import Path


EXCLUDE_DIRS = {
    ".git",
    ".aaa",
    ".venv",
    "node_modules",
    "dist",
    "build",
    "__pycache__",
}

MAX_BYTES = 1024 * 1024

PATTERNS = [
    ("aws_access_key_id", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("aws_secret_key", re.compile(r"(?i)aws_secret_access_key\s*[:=]\s*['\"]?[0-9a-zA-Z/+=]{40}['\"]?")),
    ("github_token", re.compile(r"gh[pousr]_[0-9A-Za-z]{20,}")),
    ("private_key", re.compile(r"-----BEGIN (RSA|DSA|EC|OPENSSH) PRIVATE KEY-----")),
]


def _should_skip_dir(name: str) -> bool:
    if name in EXCLUDE_DIRS:
        return True
    return name.startswith(".")


def _scan_file(path: Path, repo_root: Path, findings: list[dict]) -> None:
    try:
        if path.stat().st_size > MAX_BYTES:
            return
        content = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return

    for label, pattern in PATTERNS:
        if pattern.search(content):
            findings.append({"path": str(path.relative_to(repo_root)), "match": label})


def check(repo_root: str):
    root = Path(repo_root)
    findings: list[dict] = []

    for current, dirs, files in os.walk(root):
        current_path = Path(current)
        dirs[:] = [d for d in dirs if not _should_skip_dir(d)]
        for name in files:
            if name.endswith(".pyc"):
                continue
            _scan_file(current_path / name, root, findings)
            if len(findings) >= 50:
                break
        if len(findings) >= 50:
            break

    if findings:
        return {"pass": False, "details": findings}
    return {"pass": True, "details": []}
