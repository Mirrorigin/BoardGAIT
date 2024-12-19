# Routing and service startup

import random
import logging
from flask import Flask, jsonify, request, render_template
from socketio_config import socketio, app
from game.state import game_state, initialize_game, reset_game_state
# from utils.ai_api import initialize_ai_agent, generate_assistance, generate_ai_descriptions, generate_ai_votes
from utils.ai_mock import initialize_ai_agent, generate_assistance, generate_ai_descriptions, generate_ai_votes
# from game.logic import handle_describe, handle_vote, handle_eliminate

# Configuration logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        # logging.FileHandler("game_debug.log"),    # Output to files
        logging.StreamHandler()
    ]
)

# Missing functionality: if the players says the secret word! They cannot send the message!

@app.before_request
def clear_game_state_on_refresh():
    """Reset game state only for the first page load."""
    referer = request.headers.get('Referer')

    if not referer or "index.html" in referer:
        logging.debug(f"Reset game_state: {game_state}")
        reset_game_state()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/join_game', methods=['POST'])
def join_game():
    data = request.json
    player_name = data.get("player")

    if player_name.startswith("Agent"):
        return jsonify({"error": "Player names cannot start with 'Agent'."}), 400

    if player_name in game_state["players"]:
        return jsonify({"error": "Player already exists."}), 400

    game_state["players"].append(player_name)
    logging.debug(f"Current Player in the game: {game_state['players']}")

    agents, avatars = initialize_game()
    logging.debug(f"Game initializing... Initial game state: {game_state}")
    logging.debug(f"Successfully Generated AI Agents, agents details: {agents}")
    logging.debug(f"Successfully Generated avatars for agents: {avatars}")

    return jsonify({
        "message": f"All players joined the game.",
        "agent_names": list(agents.keys()),
        "agent_infos": list(agents.values()),
        "agent_avatars": avatars}
    )

@app.route('/start_game', methods=['POST'])
def start_game():
    try:
        # Generate identity and word for each player
        player_info = {}
        for i, player_name in enumerate(game_state["players"]):
            role = game_state["roles"][i]
            word = game_state["words"][role]
            player_info[player_name] = {"role": role, "word": word}

            # For AI Agents, initialize and pass the word
            if player_name.startswith("Agent"):
                initialize_ai_agent(player_name, game_state["players"], word)

        logging.debug(f"Player Info: {player_info}")

        # Returns message for all players
        return jsonify({
            "message": "Game started!",
            "player_info": player_info
        })
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/generate_description', methods=['POST'])
def generate_description():
    data = request.get_json()
    player_name = data.get('player')

    if not player_name:
        return jsonify({"message": "Player name is required"}), 400

    try:
        role = game_state["roles"][0]
        word = game_state["words"][role]

        description = generate_assistance(word)

        return jsonify({"description": description}), 200

    except Exception as e:
        print(f"Error generating description: {e}")
        return jsonify({"message": "Error generating description"}), 500

# Players give their description
@app.route('/describe', methods=['POST'])
def describe():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400

        player = data.get("player")
        player_description = data.get("description")
        if not player or not player_description:
            return jsonify({"error": "Missing player or description"}), 400

        logging.debug(f"Player: {player}, Description: {player_description}")

        if player in game_state["descriptions"]:
            if player_description:  # 这里加个判断就是描述有没有包含敏感词
                with app.app_context():
                    socketio.emit('player_description_valid', {
                        "player": player,
                        "player_description": player_description
                    })
            game_state["descriptions"][player] = player_description

        generate_ai_descriptions(game_state)

        logging.debug("Successfully generated all description!")
        logging.debug(f"Current game sate after description: {game_state}")

        # Check if all players have described
        if None in game_state["descriptions"].values():
            return jsonify({"message": f"{player} provided their description."})

        return jsonify({
            "message": "All players have described their word.",
            "descriptions": game_state["descriptions"]
        })
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/vote', methods=['POST'])
def vote():
    data = request.json
    voter = data.get("voter")
    target = data.get("target")

    # Validation
    if target not in game_state["active_players"]:
        return jsonify({"error": "Invalid vote target."}), 400

    game_state["votes"][target] += 1

    generate_ai_votes(game_state)

    # Check to see if voting is complete
    total_votes = sum(game_state["votes"].values())
    if total_votes == len(game_state["active_players"]):
        # Call eliminate logic
        eliminated_player = eliminate()

        # Check the result of elimination
        if eliminated_player == voter:
            # If the voter is eliminated, inform them and prompt exit
            return jsonify({
                "game_status": "exit"
            })

        # Check if the game is over (win condition)
        if game_state["game_over"]:
            # If game over, show the win page
            return jsonify({
                "message": f"Game Over! {game_state['winner']} wins!",
                "game_status": "win"
            })
        else:
            # If the game continues, trigger the next turn
            next_turn()
            return jsonify({
                "game_status": "continue",
                "eliminated": eliminated_player,
                "active_players": list(game_state["active_players"])
            })

    return jsonify({
        "message": f"{voter} voted for {target}. Waiting for other votes..."
    })

@app.route('/eliminate', methods=['POST'])
def eliminate():
    # Find the player with the most votes
    max_votes = max(game_state["votes"].values(), default=0)
    candidates = [player for player, votes in game_state["votes"].items() if votes == max_votes]

    # # Check for a tie
    # if len(candidates) > 1:
    #     return jsonify({
    #         "message": "It's a tie! Additional statements are required from tied players.",
    #         "tie": True,
    #         "tied_players": candidates
    #     })

    # 先只考虑取第一个玩家消除！
    eliminated_player = candidates[0]
    game_state["eliminated"].append(eliminated_player)
    game_state["active_players"].remove(eliminated_player)

    # Check game-ending conditions
    # 目前只适用只有 1 个 undercover 的情况！
    remaining_roles = [game_state["roles"][game_state["players"].index(player)] for player in game_state["active_players"]]

    # 如果被淘汰的玩家是卧底：
    if game_state["roles"][game_state["players"].index(eliminated_player)] == "undercover":
        game_state["game_over"] = True
        game_state["winner"] = "Civilians"
    # 如果仅剩卧底与平民存活：
    elif remaining_roles.count("undercover") == 1 and remaining_roles.count("civilian") == 1:
        game_state["game_over"] = True
        game_state["winner"] = "Undercover"

    return eliminated_player

@app.route('/next_turn', methods=['POST'])
def next_turn():
    # Increments the current turn
    game_state["current_turn"] += 1

    # Clear the data of previous round
    # 注意这里仅清空了 active_players 的数据
    # active_players = [player for player in game_state["players"] if player not in game_state["eliminated"]]
    game_state["descriptions"] = {player: None for player in game_state["active_players"]}
    game_state["votes"] = {player: 0 for player in game_state["active_players"]}

    print("Current game state:", game_state)

@socketio.on('connect')
def handle_connect():
    print("A client connected")

@socketio.on('disconnect')
def handle_disconnect():
    print("A client disconnected")

if __name__ == '__main__':
    socketio.run(app, debug=True)
