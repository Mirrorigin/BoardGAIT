import openai
from secret import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

SYSTEM_MESSAGE = """
        You are a player in a game called 'Who is the Undercover'.

        Game rules:
        1. Each player receives a secret word. Most players share the same word, but the 'Undercover' has a slightly different word.
        2. In each round, every player describes their word in one sentence. Repeated or vague descriptions might raise doubts.
        3. After everyone describes, players vote to eliminate the most suspicious person.
        4. The game ends when the Undercover is eliminated, or only one Civilian and the Undercover remain.

        Your task includes:
        - Generate a description for your word.
        - Vote for the most suspicious player.
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
            Your code name in this game is {payload['agent_name']}.
            Your secret word is: {payload['word']}.
            Other players in the game are: {', '.join(payload['players'])}.
            Please wait for the instructions of the next step.
            """
    elif task == "describe":
        user_message = f"""
                It's your turn for describing, {payload['agent_name']}.
                Based on the other players' descriptions, generate a creative description for your word {payload['word']}:
                Current descriptions: {payload['context']}
                """
    elif task == "vote":
        user_message = f"""
                Analyze the descriptions and vote for the most suspicious player from the following options:
                {', '.join(payload['options'])}
                """
    else:
        raise ValueError(f"Invalid task: {task}")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_MESSAGE},
                {"role": "user", "content": user_message}
            ],
            max_tokens=1000
        )
        return response["choices"][0]["message"]["content"].strip()
    except openai.error.OpenAIError as e:
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
