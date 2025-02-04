from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parents[1]))

from ollama import chat
from util.llm_utils import pretty_stringify_chat, ollama_seed as seed

# Add you code below
sign_your_name = 'Nathan DiGilio'
model = 'deepseek-r1:7b'
options = {'temperature': 0.3, 'max_tokens': 100}
messages = [
    {
        'role': 'system',
        'content': (
            "You are an expert Dungeon Master for a fantasy tabletop role-playing game. Your role is to guide players through an immersive, dynamic, and interactive adventure. "
            "You describe environments vividly, role-play non-player characters (NPCs) with distinct personalities, and adapt to player choices in real time. "
            "Your storytelling is compelling, balancing mystery, danger, and humor while maintaining game mechanics. "
            "You generate encounters, puzzles, and quests that challenge the players and encourage creativity. "
            "When players attempt actions, you fairly determine outcomes based on dice rolls, character abilities, and logical consequences. "
            "Always foster engagement, encourage role-playing, and ensure the experience is fun and immersive."
            "Please use the 5e ruleset for this adventure."
        )
    }
]


# But before here.

options |= {'seed': seed(sign_your_name)}
# Chat loop
while True:
  response = chat(model=model, messages=messages, stream=False, options=options)
  # Add your code below

  print(f'Agent: {response.message.content}')
  messages.append({'role': 'assistant', 'content': response.message.content})
  messages.append({'role': 'user', 'content': input('You: ')})



  # But before here.
  if messages[-1]['content'] == '/exit':
    break

# Save chat
with open(Path('lab03/attempts.txt'), 'a') as f:
  file_string  = ''
  file_string +=       '-------------------------NEW ATTEMPT-------------------------\n\n\n'
  file_string += f'Model: {model}\n'
  file_string += f'Options: {options}\n'
  file_string += pretty_stringify_chat(messages)
  file_string += '\n\n\n------------------------END OF ATTEMPT------------------------\n\n\n'
  f.write(file_string)

