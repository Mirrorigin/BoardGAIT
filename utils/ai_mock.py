# For testing... save tokens!

import time
import random
from socketio_config import socketio, app

def generate_agent_details(num_players):
    # Use AI
    agent_infos = {}
    agent_avatars = []
    agent_voices = {}
    for i in range(num_players -1):
        agent_name = f"Agent_{chr(65 + i)}"
        agent_infos[agent_name] = f"{agent_name} is active"
        agent_avatars.append(f"https://via.placeholder.com/150?text={agent_name}")  # Mock avatar URL
        agent_voices[agent_name] = "default"

    return agent_infos, agent_avatars, agent_voices

def initialize_ai_agent(agent_name, players, word):
    # Mock implementation: simply print the initialization parameters
    print(f"Mock initialize: {agent_name} with players {players} and word {word}")
    return {"status": "initialized"}

def generate_assistance(word):
    time.sleep(2)
    description = f"This is a mock description for word {word}!"
    return description

def generate_ai_descriptions(game_state):
    """
    Mock implementation of generating AI descriptions.
    :param game_state: Current game state
    :return: Mock descriptions
    """
    mock_descriptions = {}
    for ai_player in [p for p in game_state["active_players"] if
                      p.startswith("Agent") and game_state["descriptions"].get(p) is None]:
        mock_descriptions[ai_player] = f"Mock description for {ai_player}"

        game_state["descriptions"][ai_player] = mock_descriptions[ai_player]

        time.sleep(2)  # mock

        print(f"Descriptions for {ai_player} is: {mock_descriptions[ai_player]}")

        with app.app_context():
            socketio.emit('ai_description_generated', {
                "player": ai_player,
                "player_description": mock_descriptions[ai_player]
            })

    # Check if all AI descriptions are generated, and if so, emit the signal to enable the vote button
    print(len(mock_descriptions), len(game_state["active_players"])-1)
    if len(mock_descriptions) == len(game_state["active_players"]) - 1:
        print("Finished description generation!")
        socketio.emit('all_descriptions_generated', {"active_players": game_state["active_players"]})

    return game_state["descriptions"]


def generate_ai_votes(game_state):
    """
    Mock implementation of generating AI votes.
    :param game_state: Current game state
    :return: Mock votes
    """
    for ai_player in [p for p in game_state["active_players"] if p.startswith("Agent")]:
        # Pick a random player from the active players except the AI itself
        options = [p for p in game_state["active_players"] if p != ai_player]
        vote_target = random.choice(options)
        if vote_target in game_state["votes"]:
            game_state["votes"][vote_target] += 1

    time.sleep(3)

    return game_state["votes"]
