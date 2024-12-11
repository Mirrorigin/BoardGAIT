# For testing... save tokens!

def initialize_ai_agent_mock(agent_name, players, word):
    # Mock implementation: simply print the initialization parameters
    print(f"Mock initialize: {agent_name} with players {players} and word {word}")
    return {"status": "initialized"}


def generate_ai_descriptions_mock(game_state):
    """
    Mock implementation of generating AI descriptions.
    :param game_state: Current game state
    :return: Mock descriptions
    """
    mock_descriptions = {}
    for ai_player in [p for p in game_state["active_players"] if
                      p.startswith("Agent") and game_state["descriptions"].get(p) is None]:
        mock_descriptions[ai_player] = f"Mock description for {ai_player}"

    # Update the game state with mock descriptions
    game_state["descriptions"].update(mock_descriptions)
    return game_state["descriptions"]


def generate_ai_votes_mock(game_state):
    """
    Mock implementation of generating AI votes.
    :param game_state: Current game state
    :return: Mock votes
    """
    for ai_player in [p for p in game_state["active_players"] if p.startswith("Agent")]:
        # Pick a random player from the active players except the AI itself
        vote_target = next(p for p in game_state["active_players"] if p != ai_player)

        # Update votes
        if vote_target in game_state["votes"]:
            game_state["votes"][vote_target] += 1
        else:
            game_state["votes"][vote_target] = 1

    return game_state["votes"]
