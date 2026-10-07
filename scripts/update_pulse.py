#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import html
import json
import os
import urllib.request
from pathlib import Path

OWNER = "dilipna"
REPOS = ["OPsVerse", "axon-fde", "Pro2ProAgent", "wc26-mlops"]
OUT = Path("assets/live-pulse.svg")
TOKEN = os.environ.get("GITHUB_TOKEN", "")

def api(path: str):
    req = urllib.request.Request(
        "https://api.github.com" + path,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "dilip-profile-readme",
            **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}),
        },
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)

def ago(iso: str) -> str:
    t = dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))
    now = dt.datetime.now(dt.timezone.utc)
    delta = now - t
    if delta.days >= 1:
        return f"{delta.days}d ago"
    hours = max(0, delta.seconds // 3600)
    if hours:
        return f"{hours}h ago"
    mins = max(1, delta.seconds // 60)
    return f"{mins}m ago"

def trim(s: str, n: int = 34) -> str:
    s = " ".join(s.split())
    return s if len(s) <= n else s[: n - 1] + "…"

def esc(s):
    return html.escape(str(s), quote=True)

cards = []
for name in REPOS:
    repo = api(f"/repos/{OWNER}/{name}")
    commits = api(f"/repos/{OWNER}/{name}/commits?per_page=1")
    commit = commits[0]["commit"]
    when = commit["committer"]["date"]
    cards.append({
        "name": name,
        "language": repo.get("language") or "Mixed",
        "stars": repo.get("stargazers_count", 0),
        "when": ago(when),
        "msg": trim(commit["message"].splitlines()[0]),
    })

now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
w = 1280
card_w = 286
gap = 14
x0 = 38

parts = []
parts.append(f'<svg width="{w}" height="236" viewBox="0 0 {w} 236" fill="none" xmlns="http://www.w3.org/2000/svg">')
parts.append('''<defs>
  <linearGradient id="g" x1="0" y1="0" x2="1280" y2="236"><stop stop-color="#151311"/><stop offset="1" stop-color="#26170F"/></linearGradient>
  <style>
    .mono { font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace }
    @keyframes p { 0%,100%{opacity:.35} 50%{opacity:1} }
    .p { animation:p 2.2s ease-in-out infinite }
  </style>
</defs>''')
parts.append(f'<rect width="{w}" height="236" rx="22" fill="url(#g)"/>')
parts.append(f'<rect x="1" y="1" width="{w-2}" height="234" rx="21" stroke="#3C3029"/>')
parts.append('<circle cx="43" cy="39" r="5" fill="#77EF88" class="p"/>')
parts.append('<text x="58" y="43" fill="#FF8A56" class="mono" font-size="11" letter-spacing="2">ENGINEERING PULSE / LIVE</text>')
parts.append('<text x="38" y="76" fill="#F7F0E9" font-family="Arial, sans-serif" font-size="25" font-weight="700">What changed recently</text>')
parts.append(f'<text x="1242" y="43" fill="#7E7067" class="mono" font-size="9" text-anchor="end">{esc(now)}</text>')

for i, c in enumerate(cards):
    x = x0 + i * (card_w + gap)
    parts.append(f'''
<g>
  <rect x="{x}" y="102" width="{card_w}" height="96" rx="14" fill="#201C19" stroke="#493B33"/>
  <text x="{x+16}" y="126" fill="#F6EFE8" class="mono" font-size="12" font-weight="700">{esc(c["name"])}</text>
  <text x="{x+16}" y="146" fill="#A99A90" class="mono" font-size="9">{esc(c["language"])} · ★ {c["stars"]} · {esc(c["when"])}</text>
  <text x="{x+16}" y="171" fill="#D7CCC3" class="mono" font-size="9">{esc(c["msg"])}</text>
  <circle cx="{x+card_w-18}" cy="121" r="4" fill="#FF7A3D"/>
</g>''')

parts.append('</svg>')
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("".join(parts), encoding="utf-8")
print(f"Wrote {OUT}")
