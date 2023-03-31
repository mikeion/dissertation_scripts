# Split the long message logs into separate conversations

import json
import os
from datetime import datetime
from pytz import all_timezones, timezone

eastern = timezone('US/Eastern')


def process_file(file):
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    conversation_id = 1

    for message in data['messages']:
        timestamp = datetime.fromisoformat(message['timestamp'][:-6]).replace(tzinfo=timezone.utc).astimezone(eastern)
        message['timestamp'] = timestamp.strftime('%m/%d/%Y %H:%M:%S')
        
        if timestamp >= datetime(2021, 10, 29, tzinfo=eastern):
            message['conversation_id'] = conversation_id
            if len(message['embeds']) > 0 and message['embeds'][0]['title'] == 'Channel closed':
                conversation_id += 1
            if message['author']['name'] == 'DeletedUser':
                author_id = message['author']['id']
                message['author'] = {'id': author_id, 'name': 'DeletedUser', 'discriminator': ''}
            else:
                message['author'] = {'id': message['author']['id'], 'name': message['author']['name'], 'discriminator': message['author']['discriminator']}

    new_file = os.path.splitext(file)[0] + '_processed' + os.path.splitext(file)[1]

    with open(new_file, 'w') as f:
        json.dump(data, f, indent=4)

def process_directory(directory):
    for file in os.listdir(directory):
        if file.endswith('.json'):
            process_file(os.path.join(directory, file))

if __name__ == '__main__':
    user_input = input('Enter the file name or directory: ')

    if os.path.isfile(user_input):
        process_file(user_input)
    elif os.path.isdir(user_input):
        process_directory(user_input)
    else:
        print('Invalid input. Please enter a valid file or directory.')
