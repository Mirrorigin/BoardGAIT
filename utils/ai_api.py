import os
import requests
import random
import openai
from openai import OpenAI, OpenAIError
from utils.text_to_speech import audio_gen, elevenlabs_client
from socketio_config import socketio, app
from dotenv import load_dotenv

load_dotenv()

openai_client = OpenAI()

# Get all voice in Elevenlabs (language == 'en')
voices = elevenlabs_client.voices.get_all()
all_en_voices = []
for voice_list in voices:
    for voice_info in voice_list[1]:
        if voice_info.fine_tuning.language == 'en':
            all_en_voices.append(voice_info.name)

print(all_en_voices)

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

        Your main task includes: initialize, ready, describe and vote. Please wait for instructions to act.
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
            Welcome to this game! {payload['context']}
            Only return the response in the format: {payload['format']}.
            - Your name should start with "Agent_".
            - Do NOT add any extra text or comments outside this format.
            - Example: Agent_Omega, A logical and observant participant with a sharp and analytical speaking style.
            """
    elif task == "ready":
        user_message = f"""
            Game Start and Initialized! Your code name in this game is {payload['agent_name']}.
            Your secret word is: {payload['word']}.
            Other players in the game are: {', '.join(payload['players'])}.
            Please wait for instructions to describe your word.
            """
    elif task == "describe":
        user_message = f"""
                It's your turn to describe, {payload['agent_name']}.  
                Your word: {payload['word']}.  
                Other players' descriptions: {payload['context']}.  
                
                Analyze the other players' descriptions carefully to identify any common themes or shared elements. 
                Think strategically: if your word is different from the majority, avoid revealing it too clearly. 
                Instead, craft a description that highlights subtle similarities between your word and theirs, 
                while hiding its unique traits. Write in your unique style: {payload['style']}.
        
                Now provide a concise, creative one sentence description that fits your style.
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

def generate_agent_details(num_players):
    """
    Use OpenAI API to generate agent names, descriptions, and avatars.
    :param num_players: Total number of agents to generate
    :return: agent_infos, agent_avatars, agent_voices
    """
    agent_infos = {}
    agent_avatars = []
    agent_voices = {}

    for i in range(num_players-1):

        try:
            payload = {
                "context": f"Create a unique and memorable name for yourself, and provide a short description of your "
                           f"personality and speaking style. Your description should define how you will communicate "
                           f"throughout the game. Make sure your personality aligns with your language style.",
                "format": "<Name>, <Personality Description and Language Style>"
            }
            agent_details = call_openai_api("initialize", payload)
            print("Generated agent_details:", agent_details)
            name, style = map(str.strip, agent_details.split(",", 1))
            agent_infos[name] = style

            # Invoke OpenAI image generation API to generate avatars
            avatar_response = openai.images.generate(
                prompt=f"Create a pixel-art, gender-neutral avatar portrait or symbol,"
                       f"reflecting the described style: {style}",
                n=1,
                size="256x256",
                response_format="url"
            )
            avatar_url = avatar_response.data[0].url
            print("AVATAR:", avatar_url)
            agent_avatars.append(avatar_url)

            selected_voice = random.choice(all_en_voices)
            agent_voices[name] = selected_voice
            print(f"Selected Voice for {name}: {agent_voices[name]}")

        except Exception as e:
            print(f"Error generating agent details: {e}")

    print(agent_infos)
    return agent_infos, agent_avatars, agent_voices


def initialize_ai_agent(agent_name, players, word):
    payload = {
        "agent_name": agent_name,
        "players": players,
        "word": word
    }
    call_openai_api("ready", payload)

def generate_ai_descriptions(game_state):
    """
    Generate descriptions for all AI players who have not yet generated descriptions, and update the game status.
    :param game_state: Current game state
    :return: Updated descriptions
    """

    # Generate descriptions for active AI agents
    ai_descriptions = {}
    for ai_player in [p for p in game_state["active_players"] if
                      p.startswith("Agent") and game_state["descriptions"][p] is None]:
        player_index = game_state["players"].index(ai_player)
        role = game_state["roles"][player_index]
        word = game_state["words"][role]
        style = game_state["agents"][ai_player]

        payload = {
            "agent_name": ai_player,
            "word": word,
            "context": game_state['descriptions'],
            "style": style
        }
        ai_descriptions[ai_player] = call_openai_api("describe", payload)

        with app.app_context():
            socketio.emit('ai_description_generated', {
                "player": ai_player,
                "player_description": ai_descriptions[ai_player]
            })
        # Play generated audio
        audio_gen(ai_descriptions[ai_player], game_state["voices"][ai_player])

        # Update game state
        game_state["descriptions"][ai_player] = ai_descriptions[ai_player]

    # Check if all AI descriptions are generated, and if so, emit the signal to enable the vote button
    if len(ai_descriptions) == len(game_state["active_players"]) - 1:
        print("Finished description generation!")
        socketio.emit('all_descriptions_generated', {"active_players": game_state["active_players"]})

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
