# Routing and service startup

from flask import Flask, jsonify, request, render_template
from game.state import game_state, initialize_game
from game.logic import handle_describe, handle_vote, handle_eliminate

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/start_game', methods=['POST'])
def start_game():
    data = request.json
    player_names = data.get("players")
    try:
        initialize_game(player_names)

        # Generate identity and word info. for each player
        player_info = {}
        for i, player_name in enumerate(game_state["players"]):
            role = game_state["roles"][i]
            word = game_state["words"][role]
            player_info[player_name] = {"role": role, "word": word}

        # Returns message for all players
        return jsonify({
            "message": "Game started!",
            "player_info": player_info  # 每个玩家通过前端只看到自己的信息
        })
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/describe', methods=['POST'])
def describe():
    data = request.json
    return handle_describe(data)

@app.route('/vote', methods=['POST'])
def vote():
    data = request.json
    return handle_vote(data)

@app.route('/eliminate', methods=['POST'])
def eliminate():
    return handle_eliminate()

if __name__ == '__main__':
    app.run(debug=True)
