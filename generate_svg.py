import requests
import os
import random

USERNAME = "meet6949"
TOKEN = os.getenv("GITHUB_TOKEN")

OUTPUT = "dist/space.svg"

def fetch_data():
    query = """
    query($userName:String!) {
      user(login: $userName){
        contributionsCollection {
          contributionCalendar {
            weeks {
              contributionDays {
                contributionCount
              }
            }
          }
        }
      }
    }
    """

    headers = {"Authorization": f"bearer {TOKEN}"}

    res = requests.post(
        "https://api.github.com/graphql",
        json={"query": query, "variables": {"userName": USERNAME}},
        headers=headers,
        timeout=10
    )

    res.raise_for_status()
    data = res.json()

    weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]

    days = []
    for w in weeks:
        for d in w["contributionDays"]:
            days.append(d["contributionCount"])

    return days


def color(c):
    if c == 0: return "#161b22"
    if c < 3: return "#0e4429"
    if c < 6: return "#006d32"
    if c < 9: return "#26a641"
    return "#39d353"


def generate(days):
    width, height = 900, 220
    cell, gap = 10, 3

    start_x, start_y = 50, 30

    rocket_x = 760
    rocket_y = 150

    svg = f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">'

    # background
    svg += f'<rect width="100%" height="100%" fill="#0d1117"/>'

    # stars
    random.seed(42)
    for _ in range(60):
        svg += f'<circle cx="{random.randint(0,width)}" cy="{random.randint(0,height)}" r="1" fill="white" opacity="0.5"/>'

    # grid
    targets = []
    i = 0

    for w in range(53):
        for d in range(7):
            if i >= len(days): break

            x = start_x + w * (cell + gap)
            y = start_y + d * (cell + gap)

            c = days[i]
            svg += f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" fill="{color(c)}"/>'

            if c > 0:
                targets.append((x+5, y+5))

            i += 1

    # rocket (clean design)
    svg += f'''
    <g>
        <polygon points="{rocket_x},{rocket_y} {rocket_x+30},{rocket_y-10} {rocket_x+30},{rocket_y+10}" fill="#8b5cf6"/>
        <circle cx="{rocket_x+20}" cy="{rocket_y}" r="4" fill="#22c55e"/>
        <ellipse cx="{rocket_x-8}" cy="{rocket_y}" rx="10" ry="4" fill="orange"/>
    </g>
    '''

    # bullets (perfect sync)
    base_delay = 1.5

    for i, (tx, ty) in enumerate(targets[-5:]):
        svg += f'''
        <circle cx="{rocket_x}" cy="{rocket_y}" r="3" fill="#facc15">
            <animate attributeName="cx" from="{rocket_x}" to="{tx}" dur="0.5s" begin="{base_delay+i*0.4}s" fill="freeze"/>
            <animate attributeName="cy" from="{rocket_y}" to="{ty}" dur="0.5s" begin="{base_delay+i*0.4}s" fill="freeze"/>
        </circle>
        '''

    svg += "</svg>"

    return svg


def main():
    data = fetch_data()

    os.makedirs("dist", exist_ok=True)

    svg = generate(data)

    with open(OUTPUT, "w") as f:
        f.write(svg)

    print("SVG generated")


if __name__ == "__main__":
    main()
