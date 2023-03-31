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
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)

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
        message_data = {
            'id': message['id'],
            'author_id': author_id,
            'author_name': author_name,
            'timestamp': timestamp,
            'content': message['content'],
            'attachments': message.get('attachments', []),
            'mentions': message.get('mentions', []),
            'conversation_id': conversation_id
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

def output_dialogue(conversation_id, messages, output_dir):
    dialogs = []

    for message in messages:
        content = message["content"]

        if "attachments" in message and message["attachments"]:
            for attachment in message["attachments"]:
                if "url" in attachment:
                    content += f'<br><img src="{attachment["url"]}" style="max-width: 300px; max-height: 300px;">'

        dialogs.append(f'<div style="clear: both"><div style="display: inline-block; border: 1px solid #D5F5E3; background-color: #EAFAF1; border-radius: 5px; padding: 7px; margin: 10px 0;"><p><b>{message["author_name"]} ({message["timestamp"]}):</b> {content}</p></div></div>')

    dialogs_html = '<div style="max-width: 750px">' + ''.join(dialogs) + '</div>'
    output_data = {"dialogs": dialogs_html}

    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f'dialogue_{conversation_id}.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)

    print(f'Dialogue {conversation_id} outputted to {output_file}')
    
def process_directory(directory):
    for file in os.listdir(directory):
        if file.endswith('.json'):
            output_dir = os.path.join(directory, 'output', os.path.splitext(file)[0])
            messages = process_file(os.path.join(directory, file))
            conversations = group_messages(messages)
            for conversation_id, messages in conversations.items():
                output_dialogue(conversation_id, messages, output_dir)

if __name__ == '__main__':
    user_input = input('Enter the directory containing the JSON files: ')
    process_directory(user_input)