import os
from openai import OpenAI, OpenAIError
# from secret import OPENAI_API_KEY

openai_client = OpenAI()

SYSTEM_MESSAGE = """
        You are a player in a game called 'Who is the Undercover'.

        Game rules:
        1. Each player receives a secret word. Most players share the same word, but the 'Undercover' has a slightly different word.
        2. In each round, every player describes their word in one sentence. The secret word must not be mentioned directly.
        3. You are not allowed to lie or pretend your word is the same as the others.
        4. After everyone describes their word, all players vote to eliminate the person they suspect has a different word (the Undercover).
        5. The game ends when the Undercover is eliminated, or only one Civilian and the Undercover remain.
        
        Guidelines for optimal play:
        - During the description phase, overly specific descriptions might expose your word, while overly vague or repetitive descriptions might also raise doubts.
        - If your word differs from others', focus on subtle similarities to blend in without fabricating or misrepresenting your word.
        - During the voting phase, assess other players' descriptions carefully. Look for inconsistencies, overly specific details, or vague statements to identify who might have a different word.

        Main task includes: initialize, describe and vote. Please wait for instructions to act.
        """

def call_openai_api(task, payload):
    """
    :param task: "initialize", "describe" or "vote"
    :param payload: task data
    :return: AI generated result
    """

    # Generate user messages based on different tasks
    if task == "initialize":
        user_message = f"""
            Game Start and Initialized! Your code name in this game is {payload['agent_name']}.
            Your secret word is: {payload['word']}.
            Other players in the game are: {', '.join(payload['players'])}.
            Please wait for instructions to describe your word.
            """
    elif task == "describe":
        user_message = f"""
                It's your turn for describing, {payload['agent_name']}.
                Based on the other players' descriptions, generate a creative description for your word {payload['word']}:
                Current descriptions: {payload['context']}
                """
    elif task == "vote":
        user_message = f"""
                It's your turn for voting, {payload['agent_name']}.
                Here are the descriptions from all players:
                {', '.join([f'{k}: {v}' for k, v in payload['descriptions'].items()])}.
                Based on these descriptions, vote for the most suspicious player from the following options:
                {', '.join(payload['options'])}.
                Return their name only.
                """
    else:
        raise ValueError(f"Invalid task: {task}")

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_MESSAGE},
                {"role": "user", "content": user_message}
            ],
            max_tokens=1000
        )
        print(response.choices[0].message.content)
        return response.choices[0].message.content

    except OpenAIError as e:
        print(f"OpenAI API Error: {e}")
        return "Fallback response"

def initialize_ai_agent(agent_name, players, word):
    payload = {
        "agent_name": agent_name,
        "players": players,
        "word": word
    }
    call_openai_api("initialize", payload)

def generate_ai_descriptions(game_state):
    """
    Generate descriptions for all AI players who have not yet generated descriptions, and update the game status.
    :param game_state: Current game state
    :return: Updated descriptions
    """

    # Generate descriptions for active AI agents
    for ai_player in [p for p in game_state["active_players"] if
                      p.startswith("Agent") and game_state["descriptions"][p] is None]:
        player_index = game_state["players"].index(ai_player)
        role = game_state["roles"][player_index]
        word = game_state["words"][role]

        payload = {
            "agent_name": ai_player,
            "word": word,
            "context": game_state['descriptions']
        }
        ai_description = call_openai_api("describe", payload)

        # Update game state
        game_state["descriptions"][ai_player] = ai_description

    return game_state["descriptions"]

def generate_ai_votes(game_state):
    """
    Generate votes for all AI players and update the game status.
    :param game_state: Current game state
    :return: Update Votes
    """

    # Generate votes for active AI agents
    for ai_player in [p for p in game_state["active_players"] if p.startswith("Agent")]:
        payload = {
            "agent_name": ai_player,
            "descriptions": game_state["descriptions"],
            "options": [p for p in game_state["active_players"] if p != ai_player]  # can't vote for yourself
        }

        ai_vote = call_openai_api("vote", payload)

        # Check whether vote is valid
        if ai_vote in game_state["votes"]:
            game_state["votes"][ai_vote] += 1

    return game_state["votes"]
