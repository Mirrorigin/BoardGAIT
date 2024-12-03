# Routing and service startup

from flask import Flask, jsonify, request, render_template
from game.state import game_state, initialize_game
from game.logic import handle_describe, handle_vote, handle_eliminate

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/join_game', methods=['POST'])
def join_game():
    data = request.json
    player_name = data.get("player")
    if player_name in game_state["players"]:
        return jsonify({"error": "Player already exists."}), 400
    game_state["players"].append(player_name)
    return jsonify({"message": f"{player_name} joined the game.", "players": game_state["players"]})

@app.route('/start_game', methods=['POST'])
def start_game():
    try:
        initialize_game()

        # Generate identity and word information for each player
        player_info = {}
        for i, player_name in enumerate(game_state["players"]):
            role = game_state["roles"][i]
            word = game_state["words"][role]
            player_info[player_name] = {"role": role, "word": word}

        # Returns message for all players
        return jsonify({
            "message": "Game started!",
            "player_info": player_info
        })
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/get_identity', methods=['POST'])
def get_identity():
    data = request.json
    player_name = data.get("player")
    if player_name not in game_state["players"]:
        return jsonify({"error": "Player not found."}), 404
    player_index = game_state["players"].index(player_name)
    role = game_state["roles"][player_index]
    word = game_state["words"][role]
    return jsonify({
        "player": player_name,
        "role": role,
        "word": word
    })

# Players give their description
@app.route('/describe', methods=['POST'])
def describe():
    data = request.json
    player = data.get("player")
    description = data.get("description")

    if player in game_state["descriptions"]:
        game_state["descriptions"][player] = description
        # game_state["current_turn"] += 1

    # Generate descriptions for AI agents
    for ai_player in [p for p in game_state["players"] if p.startswith("Agent")]:
        if game_state["descriptions"][ai_player] is None:
            game_state["descriptions"][ai_player] = "This will be replace by Generative AI "

    # Check if all players have described
    if None in game_state["descriptions"].values():
        return jsonify({"message": f"{player} provided their description."})
    # game_state["current_turn"] = 0  # Reset turn for voting
    print("111")
    return jsonify({
        "message": "All players have described their word.",
        "descriptions": game_state["descriptions"]
    })

@app.route('/vote', methods=['POST'])
def vote():
    data = request.json
    voter = data.get("voter")
    target = data.get("target")
    if target in game_state["votes"]:
        game_state["votes"][target] += 1
        return jsonify({"message": f"{voter} voted for {target}.", "votes": game_state["votes"]})
    return jsonify({"error": "Invalid vote target."})

@app.route('/eliminate', methods=['POST'])
def eliminate():
    # Find the player with the most votes
    max_votes = max(game_state["votes"].values())
    eliminated = [player for player, votes in game_state["votes"].items() if votes == max_votes]
    eliminated_player = eliminated[0]
    game_state["eliminated"].append(eliminated_player)

    # Check game-ending conditions
    if game_state["roles"][game_state["players"].index(eliminated_player)] == "undercover":
        game_state["game_over"] = True
        game_state["winner"] = "Civilians"
    elif len(game_state["players"]) - len(game_state["eliminated"]) <= 1:
        game_state["game_over"] = True
        game_state["winner"] = "Undercover"

    return jsonify({
        "message": f"{eliminated_player} was eliminated.",
        "eliminated": eliminated_player,
        "game_over": game_state["game_over"],
        "winner": game_state["winner"]
    })

if __name__ == '__main__':
    app.run(debug=True)
