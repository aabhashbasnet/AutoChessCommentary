# AutoChessCommentary

A FastAPI-based chess game analyzer that leverages the Stockfish engine for precise move evaluation and Ollama (LLM) for natural language commentary. It detects blunders, calculates centipawn loss, classifies move quality, and optionally persists game history per user in PostgreSQL.

## Table of Contents

- [How It Works](#how-it-works)
- [What is a Centipawn?](#what-is-a-centipawn)
- [What is PGN?](#what-is-pgn)
- [Move Quality Classification](#move-quality-classification)
- [Centipawn Loss Calculation](#centipawn-loss-calculation)
- [AI Commentary](#ai-commentary)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Environment Variables](#environment-variables)
- [API Endpoints](#api-endpoints)
- [Authentication](#authentication)
- [Example Requests & Responses](#example-requests--responses)

## How It Works

This system analyzes a chess game provided in PGN (Portable Game Notation) format. It uses `python-chess` to parse the game, `Stockfish` for engine evaluation, and `Ollama` to generate human-readable commentary for each move.

### 🔄 Flow Overview

```mermaid
flowchart TD
    A["PGN Input"] --> B["Parse Game with python-chess"]
    B --> C["Iterate Through Each Move"]

    C --> D1["Get FEN Before Move"]
    D1 --> D2["Stockfish: eval_before + best_move"]
    D2 --> D3["Push Move on Board"]
    D3 --> D4["Get FEN After Move"]
    D4 --> D5["Stockfish: eval_after"]
    D5 --> D6["Normalize to White Perspective"]
    D6 --> D7["Calculate Centipawn Loss"]
    D7 --> D8["Classify Move Quality"]
    D8 --> D9["Detect Game State"]
    D9 --> D10["Send to Ollama for Commentary"]
    D10 --> C

    C --> E["Generate Full Analysis"]
    E --> F["Return Move-by-Move Breakdown + Commentary + Result"]
    F --> G{"User Logged In?"}
    G -- Yes --> H["Save Game & Moves to PostgreSQL"]
    G -- No --> I["Return Response Only"]
```

## What is a Centipawn?

A **centipawn (cp)** is the unit chess engines use to measure positional advantage.

> **The Conversion:**
> 1 pawn = 100 centipawns

### 📊 Evaluation Examples

| Value       | Meaning                       |
| :---------- | :---------------------------- |
| **+350 cp** | White is up roughly 3.5 pawns |
| **-200 cp** | Black is up roughly 2.0 pawns |
| **0 cp**    | Perfectly equal position      |

### How It Works

Stockfish evaluates everything—material, king safety, pawn structure, and piece mobility—and collapses it all into one centipawn number.

**Important:** Stockfish always returns the evaluation from the side-to-move's perspective. Since the turn flips after every move, the sign flips too. This system **normalizes all evaluations to White's absolute perspective** before calculating loss.
l evaluations to White's absolute perspective before calculating loss.

## What is PGN?

**PGN (Portable Game Notation)** is the standard text format for recording chess games. It is designed to be both human-readable and easily parsed by computers.

### 📜 Anatomy of a Move

`1. e4 e5 2. Bc4 Nc6 3. Qh5 Nf6 4. Qxf7#`

- **Move Pairs:** Each number represents a turn (White's move followed by Black's).
- **#**: Checkmate
- **+**: Check
- **??**: Blunder (Annotation)
- **O-O**: Kingside Castling
- **O-O-O**: Queenside Castling

### 🧪 Example PGNs for Testing

Use these common openings to test the analyzer:

| Opening            | PGN Sequence                              |
| :----------------- | :---------------------------------------- |
| **Scholar's Mate** | `1. e4 e5 2. Bc4 Nc6 3. Qh5 Nf6 4. Qxf7#` |
| **Fool's Mate**    | `1. f3 e5 2. g4 Qh4#`                     |
| **Ruy Lopez**      | `1. e4 e5 2. Nf3 Nc6 3. Bb5 a6`           |

## Move Quality Classification

Each move is classified based on the **Centipawn Loss (CPL)**, which represents the difference between the engine's best move and the move actually played.

| Centipawn Loss      | Classification | Indicator |
| :------------------ | :------------- | :-------: |
| **0 – 9**           | Best           |    🔥     |
| **10 – 29**         | Excellent      |    ✅     |
| **30 – 79**         | Good           |    🟢     |
| **80 – 149**        | Inaccuracy     |    🟡     |
| **150 – 299**       | Mistake        |    🟠     |
| **300+**            | Blunder        |    🔴     |
| **Delivering mate** | Checkmate      |    🏆     |

## Centipawn Loss (CPL) Calculation

CPL measures how much the evaluation dropped compared to the best available move. A lower CPL indicates a more accurate move.

### 🧬 The Process

1.  **Get eval before move:** Fetch the engine evaluation from the moving side's perspective.
2.  **Push the move:** Apply the move to the board.
3.  **Get eval after move:** Fetch the new evaluation (now from the opponent's perspective).
4.  **Normalize:** Convert both evaluations to **White's absolute perspective**.
5.  **Calculate Loss:** Compare the "before" and "after" based on which side moved.

### 🧮 The Formula

```python
if White_moved:
    CPL = max(0, eval_before_white - eval_after_white)
elif Black_moved:
    CPL = max(0, eval_after_white - eval_before_white)
```

### 📝 Example: White plays `e4`

- **Eval Before:** `+49` (White to move, White is up 49cp).
- **Eval After:** `-36` (Black to move, meaning White is still up 36cp).

**Normalization:**

- `eval_before_white` = `+49`
- `eval_after_white` = `+36` (Sign flipped because it is now Black's turn)

**Result:**
`CPL = max(0, 49 - 36) = 13 cp` → **Classification: Excellent ✅**

## AI Commentary

Each move receives human-readable commentary generated by a local LLM via **Ollama**. This ensures the project remains free, private, and runs entirely on your own hardware without requiring external API keys.

### ⚙️ How It Works

The system passes the technical engine data through a specialized prompt pipeline:

1.  **Data Collection:** Gathers `move`, `quality`, `CPL`, `best_move`, and `evaluation`.
2.  **Context Building:** A prompt is constructed describing the board state and the engine's verdict.
3.  **Local Inference:** Data is sent to the Ollama API: `http://localhost:11434/api/generate`.
4.  **Integration:** The LLM returns a 1–2 sentence explanation, which is injected into the final JSON response.

### 💬 Example Output

```json
{
  "move": "Nf6",
  "quality": "Blunder 🔴",
  "centipawn_loss": 350,
  "best_move": "g7g6",
  "commentary": "A catastrophic blunder! Black develops the knight but walks straight into a tactical nightmare. Playing g6 first would have chased the queen away and stabilized the position."
}
```

## AI Commentary Persona

To ensure the LLM remains helpful and concise, the system prompts **Ollama** using specific style rules based on the move classification:

| Move Quality               | Commentary Style                                                  |
| :------------------------- | :---------------------------------------------------------------- |
| **Best 🔥 / Excellent ✅** | Brief praise for finding the top-tier engine move.                |
| **Good 🟢**                | Acknowledgement of solid, standard play.                          |
| **Inaccuracy 🟡**          | Notes that the move was slightly suboptimal or missed a nuance.   |
| **Mistake 🟠**             | Points out the specific better alternative and why it was missed. |
| **Blunder 🔴**             | Explains the tactical error and highlights the winning response.  |
| **Checkmate 🏆**           | Short, exciting sentence announcing the game’s conclusion.        |

> **Note:** The prompt is engineered to keep responses to **1–2 sentences** to ensure the analysis remains fast and scannable.

## 🦙 Ollama Setup

Follow these steps to get the local LLM running for your commentary:

1.  **Download:** Get the Windows installer from [ollama.com/download](https://ollama.com/download).
2.  **Pull the Model:** Open your terminal and download the recommended model:
    ```bash
    ollama pull llama3
    ```
3.  **Start the Server:**
    ```bash
    ollama serve
    ```
4.  **Verify the Connection:** Run this command to ensure the API is responding correctly:
    ```bash
    curl http://localhost:11434/api/generate \
      -d "{\"model\": \"llama3\", \"prompt\": \"Say hello\", \"stream\": false}"
    ```

> **Note:** If you are using a different model (like `mistral` or `phi3`), make sure to update your `.env` file accordingly.

## 🤖 Recommended Models

Depending on your hardware (CPU/RAM), you can choose different models. **Llama3** is the default recommendation for the best balance of speed and chess understanding.

| Model       | Size   | Commentary Quality               |
| :---------- | :----- | :------------------------------- |
| **Llama3**  | 4.0 GB | **Best** (Highly Recommended) ✅ |
| **Mistral** | 4.1 GB | **Good** (Great alternative)     |
| **Phi3**    | 2.3 GB | **Decent** (Lightweight/Faster)  |

### Check Installed Models

To see which models you already have locally, run:

```bash
ollama list
```

## 📂 Project Structure

```text
AutoChessCommentary/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── auth.py          # User registration and login
│   │       ├── chess.py         # Analysis and game history endpoints
│   │       └── users.py         # Profiles, stats, and account management
│   ├── core/
│   │   ├── analyzer.py          # Core Stockfish engine analysis logic
│   │   ├── commentary.py        # Ollama AI commentary generation pipeline
│   │   ├── config.py            # Environment & global settings
│   │   ├── dependencies.py      # JWT authentication dependencies
│   │   └── security.py          # Password hashing and JWT creation
│   ├── db/
│   │   ├── __init__.py
│   │   ├── models.py            # SQLAlchemy models (User, Game, Move)
│   │   └── session.py           # PostgreSQL connection handling
│   ├── models/
│   │   └── schemas.py           # Pydantic request/response schemas
│   ├── utils/
│   │   └── stockfish.py         # Stockfish engine loader/wrapper
│   └── main.py                  # FastAPI application entry point
├── .env                         # Environment variables (Secrets/Paths)
├── .gitignore                   # Files ignored by Git
├── requirements.txt             # Python dependencies
└── README.md                    # Project documentation
```

## 🚀 Setup & Installation

Follow these steps to get your local environment up and running.

### 1. Clone the Repo

```bash
git clone https://github.com/yourname/AutoChessCommentary.git
cd AutoChessCommentary
```

### 2. Create Virtual Environment

```bash
python -m venv env
# Activate for Windows:
env\Scripts\activate
# Activate for Linux/Mac:
source env/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Stockfish

- **Windows:** Download from [stockfishchess.org](https://stockfishchess.org/download) and copy the `.exe` path.
- **Mac:** `brew install stockfish`
- **Linux:** `sudo apt install stockfish`

### 5. Set up PostgreSQL

Log into your Postgres terminal and run:

```sql
CREATE DATABASE autochess;
```

### 6. Run the Server

```bash
uvicorn app.main:app --reload
```

Once running, visit **[http://localhost:8000/docs](http://localhost:8000/docs)** to view the interactive Swagger UI and test the endpoints.

---

## 🔑 Environment Variables

Create a `.env` file in the project root and populate it with your specific configurations:

```env
STOCKFISH_PATH="C:/path/to/stockfish.exe"
DATABASE_URL="postgresql://postgres:password@localhost:5432/autochess"
SECRET_KEY="your-super-secret-key-change-this"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
OLLAMA_MODEL="llama3"
```

## 📡 API Endpoints

### 🔐 Authentication

| Method | Endpoint         | Auth | Description             |
| :----- | :--------------- | :--: | :---------------------- |
| `POST` | `/auth/register` |  No  | Create a new account    |
| `POST` | `/auth/login`    |  No  | Login and get JWT token |

### ♟️ Chess Analysis

| Method | Endpoint         |  Auth   | Description                                |
| :----- | :--------------- | :-----: | :----------------------------------------- |
| `POST` | `/chess/analyze` |   Opt   | Analyze a PGN game and generate commentary |
| `GET`  | `/chess/history` | **Yes** | Retrieve your past analyzed games          |

### 👤 User Management

| Method   | Endpoint          |  Auth   | Description                     |
| :------- | :---------------- | :-----: | :------------------------------ |
| `GET`    | `/users/me`       | **Yes** | Get current user profile        |
| `GET`    | `/users/me/stats` | **Yes** | View aggregated game stats      |
| `DELETE` | `/users/me`       | **Yes** | Delete your account and history |

### ⚙️ System

| Method | Endpoint | Auth | Description                    |
| :----- | :------- | :--: | :----------------------------- |
| `GET`  | `/`      |  No  | Health check and server status |

## 🔐 Authentication

This API uses **JWT (JSON Web Token)** based authentication to secure user data and game history.

### Register

`POST /auth/register`

```json
{
  "username": "kasparov",
  "email": "kasparov@chess.com",
  "password": "securepassword"
}
```

### Login

`POST /auth/login`

```json
{
  "email": "kasparov@chess.com",
  "password": "securepassword"
}
```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Using the Token

Pass the token in the **Authorization** header for all protected routes:
`Authorization: Bearer YOUR_TOKEN_HERE`

---

## 🧪 Example Requests & Responses

### Analyze a Game (Guest)

`POST /chess/analyze`

```json
{
  "pgn": "1. e4 e5 2. Bc4 Nc6 3. Qh5 Nf6 4. Qxf7#",
  "depth": 15,
  "time_per_move": 1
}
```

**Response:**

```json
{
  "game_result": "White wins",
  "moves": [
    {
      "move_number": 1,
      "move": "e4",
      "eval_before": 49,
      "eval_after": 36,
      "centipawn_loss": 13,
      "quality": "Excellent ✅",
      "commentary": "Solid opening choice, controlling the center effectively."
    },
    {
      "move_number": 6,
      "move": "Nf6",
      "eval_before": -50,
      "eval_after": 10000,
      "centipawn_loss": 10050,
      "best_move": "g7g6",
      "quality": "Blunder 🔴",
      "commentary": "A catastrophic oversight that leads directly to checkmate."
    }
  ]
}
```

### Analyze with Login (Persistence)

When the same request is sent with an `Authorization` header, the game and its moves are automatically saved to the database. The response will include a `game_id`:

```json
{
  "game_id": 1,
  "game_result": "White wins",
  "moves": [...]
}
```

---

## 🗄️ Database Schema

The system uses **PostgreSQL** with the following relational structure:

- **`users`**: `id`, `username`, `email`, `password`, `created_at`
- **`games`**: `id`, `user_id (FK)`, `pgn`, `opening`, `accuracy`, `result`, `created_at`
- **`moves`**: `id`, `game_id (FK)`, `move_number`, `move`, `quality`, `centipawn_loss`, `best_move`, `eval_before`, `eval_after`

---

## 🛠️ Tech Stack

| Layer             | Technology                              |
| :---------------- | :-------------------------------------- |
| **Framework**     | [FastAPI](https://tiangolo.com)         |
| **AI Commentary** | [Ollama](https://ollama.com)            |
| **Chess Engine**  | [Stockfish](https://stockfishchess.org) |
| **Chess Logic**   | [python-chess](https://github.com)      |
| **Database**      | PostgreSQL + SQLAlchemy                 |
| **Auth**          | JWT (python-jose) + bcrypt (passlib)    |
| **Server**        | Uvicorn                                 |
