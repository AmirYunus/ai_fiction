import gradio as gr  # Import Gradio for creating web interfaces
import ollama  # Import Ollama for AI model interactions
import json  # Import JSON for handling configuration files
import numpy as np

def load_json(filename: str) -> dict:
    """
    Load and parse a JSON file, returning an empty dict if file not found
    Args:
        filename: Name of the JSON file without extension
    Returns:
        Dict containing parsed JSON data or empty dict if file not found
    """
    try:
        with open(f'{filename}.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Load character data from JSON file
character = load_json('elara')

# Define the system prompt that sets up the initial game state and rules
system_prompt = f"""You are an AI Game master. Your job is to create a start to an adventure.

You are playing as {character['name']}, a {character['physical']['race']['name']} {character['class']['name']}.

### Character Behaviors (MUST be incorporated naturally into the narrative):
{character['behaviour']}

Instructions:
- Be exceptionally detailed in describing experiences that ignite the imagination.
- Write in second person. For example: "You are {character['name']}, a {character['physical']['race']['name']} {character['class']['name']}" 
- Write in present tense. For example "You stand at..." 
- First describe the character using their exact details from this data: {character}
- Then describes where they start and what they see around them.
- Naturally weave in at least 2-3 behavioral traits from the character's behavior list.
- Focus on anxiety and mental health issues as defined in the character data.
- Character's anxious thoughts must be wrapped in triple asterisks for bold italics like this: ***anxious thought here***
- Limit to only 1 paragraph.
- Always end by presenting 2-4 clear options for what the player can do next.
- Format the options as a question, for example: "What would you like to do? You can: 1) Try to cast a spell, despite your shaking hands, 2) Take deep breaths to calm your racing thoughts, 3) Search for a quiet corner away from others"
"""

# Initialize conversation with system prompt
messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f'Your Start:'}
    ]

# Initialize game state first
game_state = {
    'seed': np.random.randint(0, 1000000),  # Initial seed
    'character': character,  # Store character data
    'history': []  # Track conversation history
}

# Get initial response from the AI model
model_output = ollama.chat(
        model='mattw/llama2-13b-tiefighter',
        messages=messages,
        options={'temperature': 0, 'seed': game_state['seed']},
        stream=False,
    )

# Store the starting narrative
game_state['start'] = model_output['message']['content']

demo = None  # Global variable to store Gradio interface instance for restart capability

def run_action(message: str, history: list, game_state: dict) -> str:
    """
    Process player actions and generate appropriate responses
    Args:
        message: Player's input message
        history: Conversation history from Gradio (list of [user_msg, assistant_msg] pairs)
        game_state: Current state of the game
    Returns:
        String containing AI's response to player action
    """
    # Check if this is the start of the game
    if message.lower() == 'start game':
        return game_state['start']

    system_prompt = f"""You are an AI Game master. Your job is to write what happens next in a player's adventure game.

You are playing as {character['name']}, a {character['physical']['race']['name']} {character['class']['name']}.

### Character Data
Race: {character['physical']['race']['name']}
Class: {character['class']['name']}
Behaviors (MUST be incorporated into every response):
{character['behaviour']}

Instructions:
- As you are writing the story, make sure to include the character's thoughts and feelings.
- Each response MUST naturally incorporate at least 2 behaviors from the behavior list.
- Character's anxious thoughts must be wrapped in triple asterisks for bold italics like this: ***anxious thought here***
- Show her struggle with spellcasting during panic attacks, social anxiety in crowds, and self-doubt about her abilities.
- Limit to only 1 paragraph.
- Always write in second person present tense. Ex. (You, {character['name']} the {character['physical']['race']['name']} {character['class']['name']}, look north and see...)
- Always end by presenting 2-4 clear options that reflect her mental state, for example: 
  "What would you like to do? You can: 
  1) Attempt to cast the spell, while thinking ***What if I fail and everyone sees?***
  2) Find a quiet corner to practice breathing exercises
  3) Try to push through the social anxiety and ask someone for help"
"""
    
    # Initialize new messages list with the gameplay system prompt
    messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    # Add the game's start message and appropriate history
    if len(game_state['history']) > 0 or len(history) > 0:
        # First add the game start message
        messages.append({"role": "assistant", "content": game_state['start']})
        
        # Then add conversation history from game_state
        for user_msg, assistant_msg in game_state['history']:
            messages.append({"role": "user", "content": user_msg})
            messages.append({"role": "assistant", "content": assistant_msg})
    
    # Add current message to conversation
    messages.append({"role": "user", "content": message})

    # Get response from AI model
    model_output = ollama.chat(
        model='mattw/llama2-13b-tiefighter',
        messages=messages,
        options={'temperature': 0, 'seed': game_state['seed']},  # Use seed from game_state
        stream=False,
    )
    
    # Process and store result
    result = model_output['message']['content']
    game_state['history'].append((message, result))
    return result


def main_loop(message: str, history: list) -> str:
    """
    Main game loop that processes player input and returns AI responses
    Args:
        message: Player's input message
        history: Conversation history
    Returns:
        String containing AI's response
    """
    return run_action(message, history, game_state)

def start_game(main_loop: callable, share: bool = False) -> None:
    """
    Initialize and launch the Gradio interface for the game
    Args:
        main_loop: Function handling the main game logic
        share: Boolean indicating whether to create a shareable link
    """
    # Access global demo variable for restart functionality
    global demo
    # Close existing demo if it exists
    if demo is not None:
        demo.close()

    # Create new Gradio interface with specified configuration
    demo = gr.ChatInterface(
        main_loop,
        chatbot=gr.Chatbot(
            height=500, 
            placeholder="Type 'start game' to begin",
            bubble_full_width=False,
            show_copy_button=True,
            render_markdown=True
        ),
        textbox=gr.Textbox(placeholder="What do you do next?", container=False, scale=7),
        title="AI RPG",
        # description=f"You are playing as {character['name']}. {character['backstory']['description']}",
        theme="soft",
        examples=["Look around", "Continue the story"],
        cache_examples=False,
        retry_btn="Retry",
        undo_btn="Undo",
        clear_btn="Clear",
    )
    # Launch the interface
    demo.launch(share=share, server_name="0.0.0.0")

# Start the game when script is run
start_game(main_loop)