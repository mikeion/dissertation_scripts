import os
import re
import json
from datetime import datetime
from collections import defaultdict

def process_file(file):
    with open(file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    conversations = defaultdict(list)
    message = {}
    conversation_id = 1
    buffer = ''

    for line in lines:
        if re.match('\[\d{2}/\d{2}/\d{4} \d{1,2}:\d{2} (AM|PM)\]', line):
            if message:
                conversations[conversation_id].append(message)
            message = {'content': '', 'urls': []}
            timestamp, content = line.split('] ', 1)
            timestamp = datetime.strptime(timestamp[1:], '%m/%d/%Y %I:%M %p')
            message['timestamp'] = timestamp.strftime('%m/%d/%Y %H:%M:%S')
            message['content'] += content.strip()
            buffer = content.strip()
        elif 'Use `.reopen` if this was a mistake.' in buffer:
            if message:
                conversations[conversation_id].append(message)
            conversation_id += 1
            buffer = ''  # clear the buffer
        elif message:
            message['content'] += ' ' + line.strip()
            buffer += ' ' + line.strip()  # add the line to the buffer

    if message:
        conversations[conversation_id].append(message)

    directory_name = os.path.splitext(file)[0] + '_processed'
    os.makedirs(directory_name, exist_ok=True)

    url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')  # regex to match URLs

    for i, messages in conversations.items():
        new_file = os.path.join(directory_name, f'conversation_{i}.txt')
        new_json = os.path.join(directory_name, f'conversation_{i}.json')
        with open(new_file, 'w', encoding='utf-8') as f, open(new_json, 'w', encoding='utf-8') as jf:
            json_data = []
            for message in messages:
                content = message['content']
                # extract and highlight URLs
                urls = url_pattern.findall(content)
                for url in urls:
                    content = content.replace(url, f'<<<{url}>>>')
                message['urls'] = urls
                f.write(f"{message['timestamp']} {content}\n")
                json_data.append({'timestamp': message['timestamp'], 'content': content, 'urls': message['urls'], 'conversation_id': i})
            json.dump(json_data, jf, indent=4)

def process_directory(directory):
    for file in os.listdir(directory):
        if file.endswith('.txt'):
            process_file(os.path.join(directory, file))

if __name__ == '__main__':
    user_input = input('Enter the file name or directory: ')

    if os.path.isfile(user_input):
        process_file(user_input)
    elif os.path.isdir(user_input):
        process_directory(user_input)
    else:
        print('Invalid input. Please enter a valid file or directory.')
