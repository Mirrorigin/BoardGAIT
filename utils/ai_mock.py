# For testing... save tokens!

import random
def initialize_ai_agent(agent_name, players, word):
    # Mock implementation: simply print the initialization parameters
    print(f"Mock initialize: {agent_name} with players {players} and word {word}")
    return {"status": "initialized"}


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
        game_state["descriptions"][ai_player].update(mock_descriptions)

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

    return game_state["votes"]
