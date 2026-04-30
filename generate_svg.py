import requests

username = "meet6949"

# GitHub contribution SVG fetch
url = f"https://github.com/users/{username}/contributions"

res = requests.get(url)
svg_data = res.text

# Modify SVG (left shift + scale)
modified_svg = svg_data.replace(
    '<svg',
    '<svg transform="translate(20,20) scale(0.9)"'
)

# Add spaceship + bullets
animation = """
<g>
  <polygon points="0,10 40,0 80,10 40,20" fill="#8b5cf6">
    <animateTransform attributeName="transform"
      type="translate"
      from="1000 140"
      to="750 140"
      dur="2s"
      fill="freeze"/>
  </polygon>
</g>

<circle cx="750" cy="150" r="3" fill="yellow">
  <animate attributeName="cx" from="750" to="300" dur="0.5s" begin="2s"/>
</circle>
"""

final_svg = svg_data.replace("</svg>", animation + "</svg>")

# Save
with open("output/game.svg", "w") as f:
    f.write(final_svg)
