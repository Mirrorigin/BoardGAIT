# Game state and initialization

import random
import time

# Configurable player numbers
NUM_PLAYERS = 4  # Default: 4 players
NUM_UNDERCOVER = 1  # Default: 1 undercover
NUM_CIVILIANS = NUM_PLAYERS - NUM_UNDERCOVER  # Automatically calculated

# Initialized global game state
game_state = {
    "players": [],
    "roles": [],
    "words": {"civilian": None, "undercover": None},
    "descriptions": {},
    "votes": {},
    "eliminated": [],
    "current_turn": 1,
    "active_players": [],
    "game_over": False,
    "winner": None
}

# Word library (can be replaced by AI later)
word_library = [
    ("apple", "orange"),
    ("cat", "dog"),
    ("sun", "moon"),
    ("table", "chair")
]

def generate_agent_details():
    # Use AI
    agent_infos = {}
    agent_avatars = []
    for i in range(NUM_PLAYERS -1):
        agent_name = f"Agent_{chr(65 + i)}"
        agent_infos[agent_name] = f"{agent_name} is active"
        agent_avatars.append(f"https://via.placeholder.com/150?text={agent_name}")  # Mock avatar URL

    return agent_infos, agent_avatars

def initialize_game():

    time.sleep(2)   # mock

    # Generate agents
    agents, avatars = generate_agent_details()

    # Assign AI Agent names
    agent_names = agents.keys()
    game_state["players"].extend(agent_names)

    if len(game_state["players"]) < 4:
        raise ValueError("The game requires at least 4 players.")

    # Assign roles
    game_state["roles"] = ["civilian"] * NUM_CIVILIANS + ["undercover"] * NUM_UNDERCOVER
    random.shuffle(game_state["roles"])

    # Assign words
    word_pair = random.choice(word_library)
    game_state["words"] = {"civilian": word_pair[0], "undercover": word_pair[1]}

    # Reset game state
    game_state["descriptions"] = {player: None for player in game_state["players"]}
    game_state["votes"] = {player: 0 for player in game_state["players"]}
    game_state["eliminated"] = []
    game_state["current_turn"] = 1
    game_state["active_players"] = game_state["players"].copy()
    game_state["game_over"] = False
    game_state["winner"] = None

    return agents, avatars

def reset_game_state():

    global game_state
    game_state.clear()
    game_state.update({
        "players": [],
        "roles": [],
        "words": {"civilian": None, "undercover": None},
        "descriptions": {},
        "votes": {},
        "eliminated": [],
        "current_turn": 1,
        "active_players": [],
        "game_over": False,
        "winner": None
    })
