import json
import datetime
import os

def get_daily_tip(tips_path):
    """Fetches a daily tip from the tips.json file."""
    try:
        if not os.path.exists(tips_path):
            print(f"Error: Tips file not found at {tips_path}")
            return "Stay curious and keep coding!"

        with open(tips_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        tips = data.get('tips', [])
        if not tips:
            return "Stay curious and keep coding!"

        # Use day of the year in UTC to select a tip consistently
        day_of_year = datetime.datetime.now(datetime.timezone.utc).timetuple().tm_yday
        return tips[day_of_year % len(tips)]
    except Exception as e:
        print(f"Error fetching tip: {e}")
        return "Stay curious and keep coding!"

def update_readme(readme_path, tips_path):
    """Updates the README.md file with the latest status and tip."""
    tip = get_daily_tip(tips_path)
    # Use timezone-aware datetime for UTC
    current_time = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')

    try:
        if not os.path.exists(readme_path):
            print(f"Error: README.md not found at {readme_path}")
            return

        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()

        start_marker = '<!-- SYSTEM_STATUS_START -->'
        end_marker = '<!-- SYSTEM_STATUS_END -->'

        if start_marker not in content or end_marker not in content:
            print("Error: Markers not found in README.md")
            return

        status_section = (
            f"{start_marker}\n"
            f"| 🛰️ Status | 🟢 Operational |\n"
            f"| :--- | :--- |\n"
            f"| **Last Synchronized** | `{current_time}` |\n"
            f"| **Tactical Tip** | `{tip}` |\n"
            f"| **Neural Uplinks** | ![Visitors](https://komarev.com/ghpvc/?username=meet6949&color=00D9FF&style=flat-square) |\n"
            f"{end_marker}"
        )

        # Find markers and replace content
        start_idx = content.find(start_marker)
        end_idx = content.find(end_marker) + len(end_marker)

        new_content = content[:start_idx] + status_section + content[end_idx:]

        if new_content == content:
            print("No changes detected in README.md content.")
            return

        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"README successfully updated at {current_time}")
        print(f"Selected Tip: {tip}")

    except Exception as e:
        print(f"Error updating README: {e}")

if __name__ == "__main__":
    # Get absolute paths to files relative to the script's directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    readme_file = os.path.join(base_dir, 'README.md')
    tips_file = os.path.join(base_dir, 'data', 'tips.json')

    update_readme(readme_file, tips_file)
