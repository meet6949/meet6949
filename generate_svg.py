import requests

username = "meet6949"

url = f"https://github.com/users/{username}/contributions"

headers = {
    "User-Agent": "Mozilla/5.0"
}

res = requests.get(url, headers=headers)

if res.status_code != 200:
    raise Exception("Failed to fetch contributions")

svg_data = res.text

# Simple overlay (safe)
animation = """
<g>
  <circle cx="750" cy="150" r="3" fill="yellow">
    <animate attributeName="cx" from="750" to="300" dur="0.5s" begin="2s"/>
  </circle>
</g>
"""

# inject animation safely
if "</svg>" in svg_data:
    final_svg = svg_data.replace("</svg>", animation + "</svg>")
else:
    raise Exception("Invalid SVG format")

# save
import os
os.makedirs("output", exist_ok=True)

with open("output/game.svg", "w", encoding="utf-8") as f:
    f.write(final_svg)

print("SVG generated successfully")
