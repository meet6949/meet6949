"""
Neural Scanner — generates an animated SVG that "scans" the user's real
GitHub contribution graph with a glowing crimson probe, lighting up each
active cell as it passes. Unique alternative to the common snake/pacman
contribution-eater widgets.

Usage (in CI):
    python scripts/generate_scanner.py <github_username>
Requires env var GH_TOKEN with a token that has read:user scope.
Writes output to: scanner.svg
"""

import os
import sys
import json
import urllib.request

GRAPHQL_URL = "https://api.github.com/graphql"

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        weeks {
          contributionDays {
            date
            contributionCount
            weekday
          }
        }
      }
    }
  }
}
"""


def fetch_contributions(username: str, token: str):
    body = json.dumps({"query": QUERY, "variables": {"login": username}}).encode()
    req = urllib.request.Request(
        GRAPHQL_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "neural-scanner",
        },
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
    weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    return weeks


def intensity_class(count: int) -> int:
    if count == 0:
        return 0
    if count < 3:
        return 1
    if count < 6:
        return 2
    if count < 10:
        return 3
    return 4


# crimson intensity ramp — matches the profile's terminal theme
FILL_BY_LEVEL = {
    0: "#1c0f0f",
    1: "#5a1f1f",
    2: "#8f2b2b",
    3: "#c23a3a",
    4: "#ef4444",
}

CELL = 11
GAP = 3
PAD_TOP = 30
PAD_LEFT = 20


def build_svg(weeks) -> str:
    n_weeks = len(weeks)
    width = PAD_LEFT * 2 + n_weeks * (CELL + GAP)
    height = PAD_TOP + 7 * (CELL + GAP) + 20

    cells = []
    scan_stops = []  # (x_center, begin_time) for the glow beam timing
    total_duration = max(4.0, n_weeks * 0.09)

    for wi, week in enumerate(weeks):
        x = PAD_LEFT + wi * (CELL + GAP)
        begin = (wi / max(1, n_weeks - 1)) * total_duration
        scan_stops.append((x + CELL / 2, begin))
        for day in week["contributionDays"]:
            wd = day["weekday"]
            y = PAD_TOP + wd * (CELL + GAP)
            level = intensity_class(day["contributionCount"])
            fill = FILL_BY_LEVEL[level]
            flash_begin = round(begin, 2)
            cells.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" '
                f'fill="{fill}" stroke="#2e1515" stroke-width="0.5">'
                + (
                    f'<animate attributeName="opacity" '
                    f'values="0.55;1;0.85" keyTimes="0;0.15;1" '
                    f'dur="0.6s" begin="{flash_begin}s" fill="freeze"/>'
                    if level > 0 else ""
                )
                + "</rect>"
            )

    beam_x0, _ = scan_stops[0]
    beam_x1, _ = scan_stops[-1]

    svg = f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="beamGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#ef4444" stop-opacity="0"/>
      <stop offset="50%" stop-color="#fca5a5" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="#ef4444" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <rect width="{width}" height="{height}" fill="#0a0505" rx="10"/>
  <text x="{PAD_LEFT}" y="18" font-family="'JetBrains Mono',monospace" font-size="11" fill="#7f1d1d">neural_scanner.scan(contributions)</text>
  {''.join(cells)}
  <rect x="{beam_x0 - 6}" y="{PAD_TOP - 6}" width="12" height="{7 * (CELL + GAP) + 6}" fill="url(#beamGrad)">
    <animate attributeName="x" values="{beam_x0 - 6};{beam_x1 - 6}" dur="{total_duration}s" repeatCount="indefinite"/>
  </rect>
</svg>"""
    return svg


def main():
    username = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("GH_USERNAME")
    token = os.environ.get("GH_TOKEN")
    if not username or not token:
        print("Usage: GH_TOKEN=... python generate_scanner.py <username>", file=sys.stderr)
        sys.exit(1)
    weeks = fetch_contributions(username, token)
    svg = build_svg(weeks)
    with open("scanner.svg", "w") as f:
        f.write(svg)
    print("scanner.svg written")


if __name__ == "__main__":
    main()
