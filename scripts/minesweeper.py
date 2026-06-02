import os
import json
import random
import re

STATE_FILE = "data/minesweeper.json"
README_FILE = "README.md"
ROWS = 5
COLS = 5
MINES = 4

def reset_game():
    board = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    revealed = [[False for _ in range(COLS)] for _ in range(ROWS)]
    mines_placed = 0
    while mines_placed < MINES:
        r, c = random.randint(0, ROWS-1), random.randint(0, COLS-1)
        if board[r][c] != -1:
            board[r][c] = -1
            mines_placed += 1

    # Calculate neighbors
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] == -1: continue
            count = 0
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < ROWS and 0 <= nc < COLS and board[nr][nc] == -1:
                        count += 1
            board[r][c] = count

    return {"board": board, "revealed": revealed, "game_over": False, "winner": False}

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return reset_game()

def save_state(state):
    os.makedirs("data", exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def reveal(state, r, c):
    if state["game_over"] or state["revealed"][r][c]: return
    state["revealed"][r][c] = True
    if state["board"][r][c] == -1:
        state["game_over"] = True
        state["winner"] = False
    else:
        # Check win
        unrevealed_count = sum(row.count(False) for row in state["revealed"])
        if unrevealed_count == MINES:
            state["game_over"] = True
            state["winner"] = True

def render_board(state):
    res = "<!-- BEGIN MINESWEEPER BOARD -->\n"
    res += "### 💣 Community Minesweeper\n"
    res += "Can you clear the grid without hitting a mine?\n\n"

    num_emojis = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣"]

    res += "|   | 1 | 2 | 3 | 4 | 5 |\n"
    res += "|---|---|---|---|---|---|\n"
    for r in range(ROWS):
        line = f"| **{chr(65+r)}** | "
        cells = []
        for c in range(COLS):
            if state["revealed"][r][c]:
                if state["board"][r][c] == -1:
                    cells.append("💥")
                else:
                    cells.append(num_emojis[state["board"][r][c]])
            else:
                if state["game_over"] and state["board"][r][c] == -1:
                    cells.append("💣")
                else:
                    cells.append(f"[?]({ 'https://github.com/meet6949/meet6949/issues/new?title=Minesweeper:+Reveal+' + chr(65+r) + str(c+1) })")
        line += " | ".join(cells) + " |"
        res += line + "\n"

    if state["game_over"]:
        if state["winner"]:
            res += "\n🎉 **Victory! You cleared the field!**\n"
        else:
            res += "\n💥 **Boom! Game Over!**\n"
        res += f"\n[Start New Game](https://github.com/meet6949/meet6949/issues/new?title=Minesweeper:+New+Game)\n"
    else:
        res += "\nClick a `[?]` to reveal a tile!\n"

    res += "\n<!-- END MINESWEEPER BOARD -->"
    return res

def main():
    title = os.getenv("ISSUE_TITLE", "")
    state = load_state()

    if "New Game" in title:
        state = reset_game()
    else:
        match = re.search(r"Reveal ([A-E])(\d)", title)
        if match:
            r = ord(match.group(1)) - 65
            c = int(match.group(2)) - 1
            if 0 <= r < ROWS and 0 <= c < COLS:
                reveal(state, r, c)

    save_state(state)
    board_html = render_board(state)

    with open(README_FILE, "r") as f:
        content = f.read()

    new_content = re.sub(r"<!-- BEGIN MINESWEEPER BOARD -->.*?<!-- END MINESWEEPER BOARD -->", board_html, content, flags=re.DOTALL)

    with open(README_FILE, "w") as f:
        f.write(new_content)

if __name__ == "__main__":
    main()
