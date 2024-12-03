# Routing and service startup

import random
from flask import Flask, jsonify, request, render_template
from game.state import game_state, initialize_game, reset_game_state
# from game.logic import handle_describe, handle_vote, handle_eliminate

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
    voter = data.get("voter")   #
    target = data.get("target")

    # Player Vote
    if target in game_state["votes"]:
        game_state["votes"][target] += 1
    else:
        return jsonify({"error": "Invalid vote target."})

    # Automatically collect descriptions and trigger AI voting
    active_players = [player for player in game_state["players"] if player not in game_state["eliminated"]]
    descriptions = game_state["descriptions"]
    ai_votes = {}  # Store the voting results of each AI player

    # 投票还有个逻辑就是很显然大家不会投给自己！
    for ai_player in [p for p in active_players if p.startswith("Agent")]:
        ai_vote = random.choice(active_players)  # AI randomly votes targets
        game_state["votes"][ai_vote] += 1  # Updated AI voting results
        ai_votes[ai_player] = ai_vote  # Store AI voting records

    return jsonify({
        "message": f"{voter} voted for {target}. AI players also voted.",
        "votes": game_state["votes"],
        "ai_votes": ai_votes,
        "descriptions": descriptions
    })

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

@app.route('/next_turn', methods=['POST'])
def next_turn():
    # Increments the current turn
    game_state["current_turn"] += 1

    # Clear the data of previous round
    game_state["descriptions"] = {player: None for player in game_state["players"] if player not in game_state["eliminated"]}
    game_state["votes"] = {player: 0 for player in game_state["players"] if player not in game_state["eliminated"]}

    # Check if there is only 1 player or the game is over
    active_players = [player for player in game_state["players"] if player not in game_state["eliminated"]]
    if len(active_players) <= 1 or game_state["game_over"]:
        return jsonify({
            "message": "Game over. No further turns.",
            "game_over": True,
            "winner": game_state["winner"]
        })

    return jsonify({
        "message": "Next turn started.",
        "active_players": active_players,
        "descriptions": game_state["descriptions"],
        "votes": game_state["votes"]
    })

@app.route('/exit_game', methods=['POST'])
def exit_game():
    reset_game_state()
    # print("Game state after reset:", game_state)
    return jsonify({"message": "Game state cleared. You can start a new game."})

if __name__ == '__main__':
    app.run(debug=True)
