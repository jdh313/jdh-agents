"""Shared Langfuse access for the eval scripts.

Credentials come from 1Password at run time rather than the environment: the
langfuse plugin's secret is injected only into its own hook process and
``CLAUDE_CODE_SUBPROCESS_ENV_SCRUB`` strips it from ordinary subprocesses, so
there is no ambient copy for a script to read.
"""

from __future__ import annotations

import base64
import json
import subprocess
import sys
import urllib.error
import urllib.request
from functools import lru_cache

OP_ITEM = "Langfuse Code Agent API"


def op_field(label: str, item: str = OP_ITEM) -> str:
    """Read one field of a 1Password item, or exit with a usable message."""
    try:
        out = subprocess.run(
            ["op", "item", "get", item, "--fields", f"label={label}", "--reveal"],
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError:
        sys.exit("op CLI not found — install the 1Password CLI.")
    except subprocess.CalledProcessError as exc:
        sys.exit(f"op could not read {label!r} from {item!r}: {exc.stderr.strip()}")
    return out.stdout.strip()


@lru_cache(maxsize=1)
def credentials() -> tuple[str, str]:
    """Return ``(base_url, basic_auth_header_value)``, read once per process."""
    base_url = op_field("base-url").rstrip("/")
    pair = f"{op_field('public-key')}:{op_field('secret-key')}"
    return base_url, base64.b64encode(pair.encode()).decode()


def api(path: str, payload: dict | None = None, method: str | None = None) -> dict:
    """Call the Langfuse public API. GET when no payload, POST otherwise."""
    base_url, auth = credentials()
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        f"{base_url}{path}",
        data=data,
        headers={"Authorization": f"Basic {auth}", "Content-Type": "application/json"},
        method=method or ("POST" if data else "GET"),
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")[:400]
        sys.exit(f"{method or 'CALL'} {path} failed: HTTP {exc.code} {body}")
    except urllib.error.URLError as exc:
        sys.exit(f"{path} unreachable: {exc.reason} — is the homelab host up?")
