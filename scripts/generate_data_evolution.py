import requests
import os
import random
from datetime import datetime

# Configuration
USERNAME = "meet6949"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OUTPUT_FILE = "dist/data-evolution-dashboard.svg"

def fetch_stats():
    """Fetch user stats from GitHub GraphQL API"""
    if not GITHUB_TOKEN:
        print("⚠️ No GITHUB_TOKEN found. Using mock data for local generation.")
        return {
            "totalCommits": 150,
            "totalPRs": 12,
            "totalIssues": 5,
            "stars": 45,
            "followers": 31,
            "contributions": 240
        }

    query = """
    query($userName:String!) {
      user(login: $userName){
        contributionsCollection {
          totalCommitContributions
          totalPullRequestContributions
          totalIssueContributions
          contributionCalendar {
            totalContributions
          }
        }
        starredRepositories {
          totalCount
        }
        followers {
          totalCount
        }
      }
    }
    """

    headers = {"Authorization": f"bearer {GITHUB_TOKEN}"}

    try:
        response = requests.post(
            "https://api.github.com/graphql",
            json={"query": query, "variables": {"userName": USERNAME}},
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()["data"]["user"]

        return {
            "totalCommits": data["contributionsCollection"]["totalCommitContributions"],
            "totalPRs": data["contributionsCollection"]["totalPullRequestContributions"],
            "totalIssues": data["contributionsCollection"]["totalIssueContributions"],
            "stars": data["starredRepositories"]["totalCount"],
            "followers": data["followers"]["totalCount"],
            "contributions": data["contributionsCollection"]["contributionCalendar"]["totalContributions"]
        }
    except Exception as e:
        print(f"Error fetching stats: {e}")
        return None

def generate_svg(stats):
    """Generate a Data Science / ML themed 'Training' dashboard SVG"""

    # Calculate derived ML-themed metrics
    # Let's say:
    # Epochs = (Commits // 10) + 1
    # Accuracy = min(99.9, 85 + (PRs * 0.5) + (Stars * 0.1))
    # Loss = max(0.01, 0.5 - (Commits * 0.001))

    epochs = (stats["totalCommits"] // 10) + 1
    accuracy = min(99.9, 85 + (stats["totalPRs"] * 0.5) + (stats["stars"] * 0.1))
    loss = max(0.01, 0.5 - (stats["totalCommits"] * 0.001))

    width = 480
    height = 200
    bg_color = "#1a1b27" # TokyoNight background
    accent_color = "#7aa2f7" # TokyoNight blue
    text_color = "#c0caf5" # TokyoNight text

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    svg = f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" xmlns="http://www.w3.org/2000/svg">
    <style>
        .header {{ font: bold 14px 'Courier New', monospace; fill: {accent_color}; }}
        .stat-label {{ font: 12px 'Courier New', monospace; fill: {text_color}; }}
        .stat-value {{ font: bold 12px 'Courier New', monospace; fill: {accent_color}; }}
        .log-text {{ font: 10px 'Courier New', monospace; fill: #8b949e; }}

        @keyframes blink {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0; }}
        }}
        .cursor {{ animation: blink 1s infinite; fill: {accent_color}; }}

        @keyframes progress {{
            0% {{ width: 0%; }}
            100% {{ width: {min(100, (stats["totalCommits"] % 10) * 10)}%; }}
        }}
        .progress-bar {{ animation: progress 2s ease-out forwards; }}

        @keyframes scanline {{
            0% {{ transform: translateY(0); }}
            100% {{ transform: translateY({height}px); }}
        }}
        .scanline {{
            width: 100%;
            height: 2px;
            background: linear-gradient(to bottom, transparent, rgba(56, 189, 248, 0.1), transparent);
            animation: scanline 4s linear infinite;
            position: absolute;
        }}
    </style>

    <rect width="{width}" height="{height}" rx="10" fill="{bg_color}" stroke="#30363d" stroke-width="2"/>

    <!-- Header -->
    <text x="20" y="30" class="header">INITIALIZING NEURAL_NETWORK.EXE...</text>
    <rect x="20" y="40" width="{width-40}" height="1" fill="#30363d"/>

    <!-- Training Stats -->
    <text x="20" y="65" class="stat-label">EPOCH:</text>
    <text x="120" y="65" class="stat-value">{epochs}/1000</text>

    <text x="20" y="85" class="stat-label">LOSS:</text>
    <text x="120" y="85" class="stat-value">{loss:.4f}</text>

    <text x="200" y="85" class="stat-label">ACCURACY:</text>
    <text x="300" y="85" class="stat-value">{accuracy:.2f}%</text>

    <!-- Progress Bar Label -->
    <text x="20" y="115" class="stat-label">CURRENT BATCH PROGRESS:</text>

    <!-- Progress Bar -->
    <rect x="20" y="125" width="{width-40}" height="15" rx="3" fill="#161b22" stroke="#30363d"/>
    <rect class="progress-bar" x="20" y="125" height="15" rx="3" fill="{accent_color}" opacity="0.8"/>

    <!-- Logs -->
    <g transform="translate(20, 160)">
        <text y="0" class="log-text">[ {now} ] Weights optimized from commit activity.</text>
        <text y="15" class="log-text">[ {now} ] Backpropagation complete for {stats["totalPRs"]} Pull Requests.</text>
        <text y="30" class="log-text">[ {now} ] Model status: <tspan fill="#22c55e">STABLE</tspan></text>
        <rect x="180" y="22" width="6" height="10" class="cursor"/>
    </g>

    <!-- Decorative elements -->
    <circle cx="{width-30}" cy="25" r="5" fill="#22c55e">
        <animate attributeName="opacity" values="1;0.2;1" dur="2s" repeatCount="indefinite" />
    </circle>
</svg>'''
    return svg

def main():
    print("🧠 Starting Data Evolution Dashboard generator...")
    stats = fetch_stats()

    if not stats:
        print("❌ Failed to fetch stats.")
        return

    svg_content = generate_svg(stats)

    os.makedirs("dist", exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"✅ Dashboard generated: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
