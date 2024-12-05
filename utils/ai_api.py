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
            You are {payload['agent_name']}, an AI participant in the game 'Who is the Undercover'.
            Your secret word is: {payload['word']}.
            Other players in the game are: {', '.join(payload['players'])}.
            """
    elif task == "describe":
        user_message = f"""
                Based on the current context, generate a creative description for your word:
                Context: {payload['context']}
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
            max_tokens=100
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