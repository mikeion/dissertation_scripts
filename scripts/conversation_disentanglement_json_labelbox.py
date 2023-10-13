import json
import os
from pytz import utc, timezone
from datetime import datetime

eastern = timezone('US/Eastern')


def process_file(file, output_dir):
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    

    conversations = []
    conversation = {"type": "application/vnd.labelbox.conversational", "version": 1, "messages": []}
    message_id = 0

    for message in data['messages']:
        if 'embeds' in message and message['embeds'] and message['embeds'][0]['title'] == 'Channel closed':
            conversations.append(conversation)
            conversation = {"type": "application/vnd.labelbox.conversational", "version": 1, "messages": []}
            message_id = 0
            continue
        timestamp_str = message['timestamp'][:-6]
        if '.' in timestamp_str:
            seconds, fraction = timestamp_str.split('.')
            fraction = fraction.ljust(6, '0')  # pad the fractional part with zeros to ensure it has 6 digits
            timestamp_str = f"{seconds}.{fraction}"
        timestamp = datetime.fromisoformat(timestamp_str).replace(tzinfo=utc).astimezone(eastern)
        timestamp_str = timestamp.isoformat()
        message_obj = {
            "messageId": f"message-{message_id}", 
            "timestampUsec": timestamp_str,
            "content": message['content'],
            "user": {
                "userId": message['author']['id'],
                "name": message['author']['name']
            },
            "align": "right" if message['author']['name'] == 'Mathematics Bot' or message['author']['name'] == 'TexIt' else "left",
            "canLabel": message['author']['name'] != 'Mathematics Bot'
        }
        conversation["messages"].append(message_obj)
        message_id += 1

    if conversation["messages"]:
        conversations.append(conversation)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for i, conversation in enumerate(conversations, 1):
        new_file = os.path.join(output_dir, f'conversation_{i}.json')
        with open(new_file, 'w') as f:
            json.dump(conversation, f, indent=4)

def process_directory(directory, output_dir):
    for file in os.listdir(directory):
        if file.endswith('.json'):
            process_file(os.path.join(directory, file), output_dir)

if __name__ == '__main__':
    input_path = input('Enter the file name or directory: ')
    # Make a new directoy for the output files with the same name as the input file name
    output_dir = os.path.splitext(input_path)[0] + '_labelbox'
    if os.path.isfile(input_path):
        process_file(input_path, output_dir)
    elif os.path.isdir(input_path):
        process_directory(input_path, output_dir)
    else:
        print('Invalid input. Please enter a valid file or directory.')
