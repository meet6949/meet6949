# import requests
# import os
# import random

# USERNAME = "meet6949"
# TOKEN = os.getenv("GITHUB_TOKEN")

# OUTPUT = "dist/space.svg"


# def fetch_data():
#     query = """
#     query($userName:String!) {
#       user(login: $userName){
#         contributionsCollection {
#           contributionCalendar {
#             weeks {
#               contributionDays {
#                 contributionCount
#               }
#             }
#           }
#         }
#       }
#     }
#     """

#     headers = {}
#     if TOKEN:
#         headers["Authorization"] = f"bearer {TOKEN}"

#     try:
#         res = requests.post(
#             "https://api.github.com/graphql",
#             json={"query": query, "variables": {"userName": USERNAME}},
#             headers=headers,
#             timeout=10
#         )

#         res.raise_for_status()
#         data = res.json()

#         weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]

#         days = []
#         for w in weeks:
#             for d in w["contributionDays"]:
#                 days.append(d["contributionCount"])

#         return days

#     except Exception as e:
#         print("API ERROR → using fallback:", e)
#         return [0] * 371


# def get_color(c):
#     if c == 0: return "#161b22"
#     if c < 3: return "#0e4429"
#     if c < 6: return "#006d32"
#     if c < 9: return "#26a641"
#     return "#39d353"


# def generate_svg(days):
#     width, height = 900, 220
#     cell, gap = 10, 3

#     start_x, start_y = 50, 30
#     rocket_x, rocket_y = 760, 140

#     svg = []

#     # SVG START (IMPORTANT: valid structure)
#     svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">')

#     # background
#     svg.append('<rect width="100%" height="100%" fill="#0d1117"/>')

#     # stars
#     random.seed(42)
#     for _ in range(50):
#         svg.append(f'<circle cx="{random.randint(0,width)}" cy="{random.randint(0,height)}" r="1" fill="white" opacity="0.5"/>')

#     # grid
#     targets = []
#     i = 0

#     for w in range(53):
#         for d in range(7):
#             if i >= len(days):
#                 break

#             x = start_x + w * (cell + gap)
#             y = start_y + d * (cell + gap)

#             c = days[i]
#             svg.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" fill="{get_color(c)}"/>')

#             if c > 0:
#                 targets.append((x + 5, y + 5))

#             i += 1

#     # rocket
#     svg.append(f'''
#     <g>
#         <polygon points="{rocket_x},{rocket_y} {rocket_x+30},{rocket_y-10} {rocket_x+30},{rocket_y+10}" fill="#8b5cf6"/>
#         <circle cx="{rocket_x+20}" cy="{rocket_y}" r="4" fill="#22c55e"/>
#     </g>
#     ''')

#     # bullets (simple visible movement)
#     delay = 1.5
#     for i, (tx, ty) in enumerate(targets[-5:]):
#         svg.append(f'''
#         <circle cx="{rocket_x}" cy="{rocket_y}" r="3" fill="#facc15">
#             <animate attributeName="cx" from="{rocket_x}" to="{tx}" dur="0.5s" begin="{delay + i*0.4}s" fill="freeze"/>
#             <animate attributeName="cy" from="{rocket_y}" to="{ty}" dur="0.5s" begin="{delay + i*0.4}s" fill="freeze"/>
#         </circle>
#         ''')

#     svg.append('</svg>')

#     return "\n".join(svg)


# def main():
#     print("Generating SVG...")

#     days = fetch_data()

#     os.makedirs("dist", exist_ok=True)

#     svg = generate_svg(days)

#     with open(OUTPUT, "w", encoding="utf-8") as f:
#         f.write(svg)

#     print("✅ DONE → dist/space.svg created")


# if __name__ == "__main__":
#     main()
import requests
import os
from datetime import datetime
import random

# Configuration
USERNAME = "meet6949"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OUTPUT_FILE = "dist/space-contribution-graph.svg"

# Colors
SPACE_BG = "#0d1117"
STAR_COLOR = "#ffffff"
ROCKET_COLOR = "#7c3aed"
PROJECTILE_COLOR = "#ffeb3b" # Bright yellow for bullets

def fetch_contributions():
    query = """
    query($userName:String!) {
      user(login: $userName){
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                contributionCount
                date
              }
            }
          }
        }
      }
    }
    """
    headers = {"Authorization": f"bearer {GITHUB_TOKEN}"}
    try:
        response = requests.post("https://api.github.com/graphql", 
                               json={"query": query, "variables": {"userName": USERNAME}}, 
                               headers=headers)
        response.raise_for_status()
        data = response.json()
        weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
        contributions = []
        for week in weeks:
            for day in week["contributionDays"]:
                contributions.append({"date": day["date"], "count": day["contributionCount"]})
        return contributions
    except Exception as e:
        print(f"Error: {e}")
        return []

def get_color_for_count(count):
    if count == 0: return "#161b22"
    elif count < 3: return "#0e4429"
    elif count < 6: return "#006d32"
    elif count < 9: return "#26a641"
    else: return "#39d353"

def generate_svg(contributions):
    width, height = 900, 280
    cell_size, cell_gap = 10, 3
    grid_start_x, grid_start_y = 50, 50
    # Rocket position - now at the bottom, facing UP
    rocket_base_y = height - 40 

    svg = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
    <style>
        @keyframes rocket-move {{
            0%, 100% {{ transform: translateX(0px); }}
            50% {{ transform: translateX({width - 150}px); }}
        }}
        @keyframes fire-bullet {{
            0% {{ transform: translateY(0); opacity: 1; }}
            80% {{ opacity: 1; }}
            100% {{ transform: translateY(var(--dist)); opacity: 0; }}
        }}
        @keyframes blast {{
            0% {{ transform: scale(1); filter: brightness(1); }}
            50% {{ transform: scale(1.5); filter: brightness(2) drop-shadow(0 0 5px yellow); }}
            100% {{ transform: scale(1); filter: brightness(1); }}
        }}
        .rocket-unit {{ animation: rocket-move 10s ease-in-out infinite; }}
        .bullet {{ animation: fire-bullet 0.8s linear infinite; }}
        .dot-active {{ animation: blast 0.8s linear infinite; }}
        .star {{ animation: twinkle 2s infinite; }}
        @keyframes twinkle {{ 0%, 100% {{ opacity: 0.3; }} 50% {{ opacity: 1; }} }}
    </style>
    <rect width="100%" height="100%" fill="{SPACE_BG}"/>
    '''

    # Stars
    for _ in range(50):
        svg += f'<circle cx="{random.randint(0,width)}" cy="{random.randint(0,height)}" r="{random.random()*2}" fill="white" class="star" style="animation-delay: {random.random()*2}s"/>'

    # Contribution Grid
    recent = contributions[-371:]
    for i, contrib in enumerate(recent):
        week = i // 7
        day = i % 7
        x = grid_start_x + (week * (cell_size + cell_gap))
        y = grid_start_y + (day * (cell_size + cell_gap))
        color = get_color_for_count(contrib['count'])
        
        # Blast effect only on actual contribution dots
        cls = "dot-active" if contrib['count'] > 0 else ""
        delay = random.random() * 5 
        
        svg += f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" fill="{color}" rx="2" class="{cls}" style="animation-delay: {delay}s"/>'
        
        # Adding bullets for active dots
        if contrib['count'] > 0:
            # This logic creates a visual effect of bullets hitting the dots
            dist = y - rocket_base_y
            svg += f'<circle cx="{x+5}" cy="{rocket_base_y}" r="2" fill="yellow" class="bullet" style="--dist: {dist}px; animation-delay: {delay}s;"/>'

    # Rocket (Facing Upwards towards dots)
    svg += f'''
    <g class="rocket-unit">
        <g transform="translate(50, {rocket_base_y}) rotate(-90)">
            <!-- Rocket Body -->
            <path d="M 0 0 L 20 -10 L 30 0 L 20 10 Z" fill="#7c3aed" />
            <!-- Nose -->
            <path d="M 30 0 L 40 0 L 30 0" stroke="white" stroke-width="2" />
            <!-- Fins -->
            <path d="M 5 -10 L 0 -15 L 10 -10 Z" fill="#a855f7" />
            <path d="M 5 10 L 0 15 L 10 10 Z" fill="#a855f7" />
            <!-- Flame -->
            <path d="M -5 0 Q -15 10 -25 0 Q -15 -10 -5 0" fill="orange">
                <animate attributeName="opacity" values="0.5;1;0.5" dur="0.1s" repeatCount="indefinite" />
            </path>
        </g>
    </g>
    '''
    
    svg += '</svg>'
    return svg

def main():
    os.makedirs("dist", exist_ok=True)
    data = fetch_contributions()
    if data:
        with open(OUTPUT_FILE, "w") as f:
            f.write(generate_svg(data))
        print("Success!")

if __name__ == "__main__":
    main()
