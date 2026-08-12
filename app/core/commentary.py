# app/core/commentary.py
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"


def generate_commentary(move_data: dict) -> str:

    move = move_data["move"]
    player = move_data.get("player", "The player")
    quality = move_data["quality"]
    cpl = move_data["centipawn_loss"]
    best_move = move_data["best_move"]
    eval_before = move_data["eval_before"]
    eval_after = move_data["eval_after"]
    move_number = move_data["move_number"]
    is_checkmate = move_data.get("is_checkmate", False)

    if is_checkmate:
        prompt = f"""Move {move_number}: {player} played {move}, delivering checkmate and winning the game.

Write one short, exciting sentence announcing that {player} has just won by checkmate with the move {move}.
Do not invent details (no promotions, no piece names) beyond what is stated here — just react to the win itself."""
    else:
        prompt = f"""You are a chess commentator. Give a single short commentary sentence (max 2 sentences) for this move.

Move number: {move_number}
Player: {player}
Move played: {move}
Quality: {quality}
Centipawn loss: {cpl}
Best move was: {best_move}
Eval before (White's perspective): {eval_before}
Eval after (White's perspective): {eval_after}

Rules:
- Always refer to the mover as "{player}" — do not guess or swap sides
- If quality is Blunder, explain it was a big mistake and hint at the better move
- If quality is Best or Excellent, praise the move briefly
- If quality is Mistake or Inaccuracy, note it was suboptimal
- Keep it short, natural, like a chess coach talking
- Do not use bullet points, just plain text
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL, "prompt": prompt, "stream": False},
            timeout=30,
        )
    except requests.exceptions.RequestException:
        return "(commentary unavailable — Ollama not reachable)"

    if response.status_code == 200:
        return response.json().get("response", "").strip()

    return "(commentary unavailable)"
