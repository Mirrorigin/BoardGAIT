# Processing logic for easy extension
# 后续把路由中涉及到的逻辑移到这里，防止在路由写太多逻辑

from flask import jsonify
from game.state import game_state


def handle_describe(data):
    player = data.get("player")
    description = data.get("description")

    if player in game_state["descriptions"]:
        game_state["descriptions"][player] = description
        game_state["current_turn"] += 1

    if game_state["current_turn"] >= len(game_state["players"]):
        game_state["current_turn"] = 0
        return jsonify({
            "message": "All players have described their word.",
            "descriptions": game_state["descriptions"]
        })
    return jsonify({"message": f"{player} provided their description."})


def handle_vote(data):
    voter = data.get("voter")
    target = data.get("target")

    if target in game_state["votes"]:
        game_state["votes"][target] += 1
        return jsonify({"message": f"{voter} voted for {target}.", "votes": game_state["votes"]})
    return jsonify({"error": "Invalid vote target."})


def handle_eliminate():
    max_votes = max(game_state["votes"].values())
    eliminated = [player for player, votes in game_state["votes"].items() if votes == max_votes]
    eliminated_player = eliminated[0]
    game_state["eliminated"].append(eliminated_player)

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