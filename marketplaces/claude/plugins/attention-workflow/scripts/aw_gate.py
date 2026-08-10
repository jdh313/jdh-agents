#!/usr/bin/env python3
"""Blocking authorization gate: one page on loopback, one decision back.

The agent cannot proceed past an authorization point until a human resolves
this gate, so every failure mode here costs the operator their session. The
semantics are taken from systems that have already paid for them:

* **RFC 8628** (OAuth device grant) keeps ``access_denied`` and
  ``expired_token`` as *separate* terminal codes. Denial is a decision;
  expiry is the absence of one. Conflating them would write a decision the
  operator never made into the record that exists to hold their decisions.
* **RFC 8252 §7.3** (OAuth for native apps) fixes the local-server rules:
  loopback bind, OS-assigned ephemeral port, a high-entropy state token, and
  a listener that dies the moment it has served its purpose.
* **macOS Authorization Services** and **polkit** independently settle on 300
  seconds for "a human is present and expected to act now". The device grant
  allows 600-1800s, but that budget buys time to pick up a phone; the
  operator here is at the same machine with the page already open.

The timeout is not optional. Plannotator -- the closest prior art -- documents
that a review session which never receives its first client never resolves,
and that the caller must impose its own limit. A hook without one hangs
forever.

Standard library only, like the rest of the plugin.
"""

from __future__ import annotations

import html
import json
import secrets
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlparse

# 300s: macOS Authorization Services rule timeout and polkit's re-ask window
# both land here for a decision the human is present for.
DEFAULT_TIMEOUT_SECONDS = 300

# Terminal states, deliberately three. "abandoned" is not a quiet synonym for
# "denied" and must never be recorded as one.
AUTHORIZED = "authorized"
DENIED = "denied"
ABANDONED = "abandoned"

# What the operator may answer, per card kind. The values are the operator's
# own tokens; status language never appears here (see the Tenerife note in
# aw_state.render_card).
RESPONSES: dict[str, tuple[tuple[str, str, str], ...]] = {
    # (token, terminal state, css class)
    "authorize": (
        ("AUTHORIZE", AUTHORIZED, "go"),
        ("REVISE", DENIED, "edit"),
        ("STOP", DENIED, "halt"),
    ),
    "reconcile": (
        ("READY", AUTHORIZED, "go"),
        ("NOT READY", DENIED, "halt"),
    ),
}


class GateResult:
    """The outcome of one gate, including how it ended."""

    def __init__(self, state: str, token: str = "", note: str = "") -> None:
        self.state = state
        self.token = token
        self.note = note

    def as_dict(self) -> dict[str, Any]:
        return {"decision": self.state, "token": self.token, "note": self.note}

    @property
    def is_decision(self) -> bool:
        """Did a human actually answer? Abandonment is not an answer."""
        return self.state in (AUTHORIZED, DENIED)


def _page(kind: str, body_html: str, state_token: str) -> str:
    """The decision page. Self-contained: no network, no external assets."""
    choices = RESPONSES.get(kind, RESPONSES["authorize"])
    buttons = "\n".join(
        '<button class="token {cls}" data-token="{tok}" accesskey="{key}">'
        "{tok}<kbd>{key}</kbd></button>".format(
            cls=cls, tok=html.escape(token), key=token[0].lower()
        )
        for token, _state, cls in choices
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>{html.escape(kind)} — attention-workflow</title>
<style>
  :root {{
    --bg:#f2f5f4; --surface:#fff; --sunken:#eaefee; --ink:#141a1a;
    --ink-soft:#465150; --ink-faint:#6f7c7a; --rule:#d6dedc; --rule-hard:#b9c5c2;
    --accent:#15605c; --go:#2f7a52; --edit:#a86a1f; --halt:#a33a32;
    --mono:ui-monospace,"SF Mono",Menlo,monospace;
    --sans:-apple-system,BlinkMacSystemFont,system-ui,sans-serif;
  }}
  @media (prefers-color-scheme:dark) {{
    :root {{
      --bg:#0e1413; --surface:#151d1c; --sunken:#101817; --ink:#e6ecea;
      --ink-soft:#a3b0ad; --ink-faint:#7b8987; --rule:#253130; --rule-hard:#354443;
      --accent:#63b6ac; --go:#6cba8b; --edit:#d9a55c; --halt:#e0847c;
    }}
  }}
  *{{box-sizing:border-box}}
  body{{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);
       font-size:15px;line-height:1.55;font-variant-numeric:tabular-nums}}
  .page{{max-width:52rem;margin:0 auto;padding:2.5rem 1.25rem 5rem}}
  .card{{background:var(--surface);border:1px solid var(--rule);border-radius:3px;
        overflow:hidden}}
  .head{{display:flex;gap:.8rem;align-items:baseline;padding:.85rem 1.25rem;
        border-bottom:1px solid var(--rule-hard);background:var(--sunken)}}
  .kind{{font-family:var(--mono);font-size:.72rem;font-weight:700;
        letter-spacing:.14em;text-transform:uppercase;color:var(--accent)}}
  .sec{{border-top:1px solid var(--rule)}}
  .head+.sec{{border-top:0}}
  .eyebrow{{padding:1.1rem 1.25rem .35rem;font-family:var(--mono);font-size:.68rem;
           letter-spacing:.1em;color:var(--ink-faint)}}
  .row{{display:grid;grid-template-columns:8.5rem 1fr;gap:0 1rem;
       padding:.4rem 1.25rem;align-items:start}}
  .row+.row{{border-top:1px solid var(--rule)}}
  .lab{{font-family:var(--mono);font-size:.7rem;font-weight:600;letter-spacing:.08em;
       text-transform:uppercase;color:var(--ink-faint);padding:.22rem .5rem 0 0;
       border-right:1px solid var(--rule)}}
  .val{{max-width:60ch}}
  .val ul{{margin:0;padding-left:1.05rem}}
  .resp{{border-top:1px solid var(--rule-hard);background:var(--sunken);
        padding:1rem 1.25rem;display:flex;flex-direction:column;gap:.6rem}}
  .tokens{{display:flex;flex-wrap:wrap;gap:.5rem}}
  .token{{font-family:var(--mono);font-size:.82rem;font-weight:650;letter-spacing:.06em;
         padding:.45rem .8rem;border:1px solid var(--rule-hard);border-radius:2px;
         background:var(--surface);color:var(--ink);cursor:pointer;
         display:flex;align-items:center;gap:.5rem}}
  .token:hover{{border-color:var(--accent)}}
  .token:focus-visible{{outline:2px solid var(--accent);outline-offset:2px}}
  .token.go{{border-color:var(--go);color:var(--go)}}
  .token.edit{{border-color:var(--edit);color:var(--edit)}}
  .token.halt{{border-color:var(--halt);color:var(--halt)}}
  kbd{{font-family:var(--mono);font-size:.62rem;opacity:.6;border:1px solid currentColor;
      border-radius:2px;padding:0 .22rem}}
  textarea{{width:100%;font-family:var(--sans);font-size:.9rem;padding:.5rem;
           border:1px solid var(--rule-hard);border-radius:2px;
           background:var(--surface);color:var(--ink);resize:vertical}}
  small{{color:var(--ink-faint);font-size:.8rem}}
  .done{{padding:3rem 1.25rem;text-align:center;font-family:var(--mono);
        color:var(--ink-soft)}}
  @media (prefers-reduced-motion:reduce){{*{{transition:none!important}}}}
</style></head><body>
<div class="page" id="page">
  <article class="card">
{body_html}
    <footer class="resp">
      <div class="tokens">{buttons}</div>
      <textarea id="note" rows="2" placeholder="the decisive observation or mismatch, one sentence"></textarea>
      <small>This page is served on loopback for this decision only, and closes
        as soon as you answer. Nothing is sent anywhere.</small>
    </footer>
  </article>
</div>
<script>
  var TOKEN = {json.dumps(state_token)};
  function answer(tok) {{
    var note = document.getElementById("note").value;
    fetch("/decide", {{
      method: "POST",
      headers: {{"Content-Type": "application/json"}},
      body: JSON.stringify({{state: TOKEN, token: tok, note: note}})
    }}).then(function () {{
      document.getElementById("page").innerHTML =
        '<div class="done">' + tok + ' recorded. You can close this tab.</div>';
    }});
  }}
  document.querySelectorAll(".token").forEach(function (b) {{
    b.addEventListener("click", function () {{ answer(b.dataset.token); }});
  }});
</script>
</body></html>"""


def serve_decision(
    page_body: str,
    kind: str,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    open_browser: bool = True,
    announce: Any = sys.stderr,
) -> GateResult:
    """Serve one decision page on loopback and block until it resolves.

    Returns a :class:`GateResult` whose ``state`` is one of ``authorized``,
    ``denied``, or ``abandoned``. Abandonment is reported, never inferred as a
    denial.
    """
    state_token = secrets.token_urlsafe(32)
    page = _page(kind, page_body, state_token)
    resolved = threading.Event()
    outcome: dict[str, Any] = {}
    # A gate answers once. RFC 8252 requires rejecting a replayed callback, and
    # a second answer to an authorization is meaningless anyway -- the first one
    # already moved the state.
    spent = threading.Lock()
    claimed = {"value": False}

    lookup = {token: (state, token) for token, state, _cls in RESPONSES.get(kind, ())}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args: Any) -> None:  # noqa: A003 - silence access logs
            return

        def _send(self, code: int, body: bytes, content_type: str) -> None:
            self.send_response(code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            # The page is for one human on this machine; nothing may frame it
            # or read it cross-origin.
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
            parsed = urlparse(self.path)
            if parsed.path != "/":
                self._send(404, b"not found", "text/plain; charset=utf-8")
                return
            query = parse_qs(parsed.query)
            # The state token gates the page itself, not just the callback:
            # another local process that guesses the port still cannot read the
            # grant without the token.
            if query.get("state", [""])[0] != state_token:
                self._send(403, b"bad state", "text/plain; charset=utf-8")
                return
            self._send(200, page.encode("utf-8"), "text/html; charset=utf-8")

        def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
            if urlparse(self.path).path != "/decide":
                self._send(404, b"not found", "text/plain; charset=utf-8")
                return
            length = int(self.headers.get("Content-Length") or 0)
            try:
                payload = json.loads(self.rfile.read(length) or b"{}")
            except json.JSONDecodeError:
                self._send(400, b"bad request", "text/plain; charset=utf-8")
                return
            if not secrets.compare_digest(str(payload.get("state") or ""), state_token):
                self._send(403, b"bad state", "text/plain; charset=utf-8")
                return
            choice = lookup.get(str(payload.get("token") or "").upper())
            if choice is None:
                self._send(400, b"unknown token", "text/plain; charset=utf-8")
                return
            with spent:
                if claimed["value"]:
                    self._send(409, b"already answered", "text/plain; charset=utf-8")
                    return
                claimed["value"] = True
            outcome["state"] = choice[0]
            outcome["token"] = choice[1]
            outcome["note"] = str(payload.get("note") or "").strip()
            self._send(200, b'{"ok":true}', "application/json")
            resolved.set()

    # Port 0: the OS assigns an ephemeral port. Loopback only -- never 0.0.0.0.
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    port = server.server_address[1]
    url = f"http://127.0.0.1:{port}/?state={state_token}"

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        # Print the URL unconditionally rather than detecting headlessness.
        # RFC 8252 and `gh auth login` both do this: try to open a browser, and
        # leave a working manual path when that fails. A fallback that is always
        # present is a fallback that is always tested.
        if announce is not None:
            announce.write(f"attention-workflow gate: {url}\n")
            announce.flush()
        if open_browser:
            try:
                webbrowser.open(url)
            except Exception:  # noqa: BLE001 - a failed open is not a failed gate
                pass
        if resolved.wait(timeout):
            return GateResult(outcome["state"], outcome.get("token", ""), outcome.get("note", ""))
        return GateResult(ABANDONED)
    finally:
        # The listener dies with the decision, answered or not.
        server.shutdown()
        server.server_close()
