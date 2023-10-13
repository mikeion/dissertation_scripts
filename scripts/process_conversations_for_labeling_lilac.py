import json
import os
from dateutil.parser import parse
from dateutil import tz
import re


def convert_timestamp(timestamp):
    eastern = tz.gettz('US/Eastern')
    timestamp = parse(timestamp)
    return timestamp.astimezone(eastern).strftime('%m/%d/%Y %H:%M:%S')


def process_file(file):
    try:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.decoder.JSONDecodeError:
        print(f"Error: Invalid JSON syntax in {file}. Skipping this file.")
        return []

    messages = []
    conversation_id = 1
    for message in data['messages']:
        if message['author']['name'] == 'DeletedUser':
            author_id = message['author']['id']
            author_name = 'DeletedUser'
        else:
            author_id = message['author']['id']
            author_name = message['author']['name']
        timestamp = convert_timestamp(message['timestamp'])
        
        # Check for empty content and attachments and replace content if needed
        content = message['content']
        if not content and not message['attachments']:
            if message['embeds']:
                embed = message['embeds'][0]
                content = embed.get('title') or embed.get('author', {}).get('name')
        
        # Check if content is "Pinned a message."
        reference = None
        if content == "Pinned a message.":
            reference = message.get('reference', {})
        
        message_data = {
            'id': message['id'],
            'author_id': author_id,
            'author_name': author_name,
            'timestamp': timestamp,
            'content': content,
            'attachments': message.get('attachments', []),
            'mentions': message.get('mentions', []),
            'conversation_id': conversation_id,
            'reference': reference
        }
        
        messages.append(message_data)
        
        if len(message['embeds']) > 0 and message['embeds'][0]['title'] == 'Channel closed':
            conversation_id += 1

    return messages

def group_messages(messages):
    conversations = {}
    for message in messages:
        conversation_id = message['conversation_id']
        if conversation_id not in conversations:
            conversations[conversation_id] = []
        conversations[conversation_id].append(message)
    return conversations


def output_dialogue(conversation_id, messages, output_dir, original_file_name):
    output_file_name = f"{original_file_name}_dialogue_{conversation_id}.json"
    output_file_path = os.path.join(output_dir, output_file_name)

    # Ensure the directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Convert list of messages to desired output format
    output_data = {
        'conversation_id': conversation_id,
        'messages': messages
    }

    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)

    



def process_directory(directory):
    for file in os.listdir(directory):
        if file.endswith('.json'):
            original_file_name = os.path.splitext(file)[0]
            
            # Search for 'help-' followed by a number
            help_match = re.search(r'help-\d+', original_file_name)
            help_part = help_match.group(0) if help_match else 'unknown'
            
            # Search for 'part' followed by a number
            part_match = re.search(r'part \d+', original_file_name)
            part_part = part_match.group(0).replace(' ', '_') if part_match else 'part_1'
            
            # Construct a short name using the extracted parts
            short_file_name = f"{help_part}_{part_part}"
            
            output_dir = os.path.join(directory, 'derived', short_file_name)
            messages = process_file(os.path.join(directory, file))
            if messages: # Only process if the list is not empty
                conversations = group_messages(messages)
                for conversation_id, messages in conversations.items():
                    output_dialogue(conversation_id, messages, output_dir, short_file_name)
if __name__ == '__main__':
    user_input = input('Enter the directory containing the JSON files: ')
    process_directory(user_input)