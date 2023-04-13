import json
import os
from datetime import datetime
from pytz import timezone
from dateutil.parser import parse as parse_date
import csv
import re

eastern = timezone('US/Eastern')

def replace_mentions_with_pseudonyms(text, author_name_to_pseudonym):
    def replace_mention(match):
        mention = match.group(0)
        author_name = mention[1:]  # Remove "@" symbol
        pseudonym = author_name_to_pseudonym.get(author_name, author_name)
        return "@" + pseudonym

    # Replace mentions with pseudonyms
    text = re.sub(r"@\w+", replace_mention, text)
    # Remove newline characters
    text = text.replace('\n\n', ' ')
    return text

def process_file(file, pseudonyms, output_directory):
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    conversation_id = 1
    conversations = {}
    help_number = data['channel']['name'].split("-")[-1]
    author_pseudonyms_mapping = {}
    author_name_to_pseudonym = {}  # Create a mapping between author names and pseudonyms
    pseudonym_index = 0
    
    # Make sure the output directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for message in data['messages']:
        timestamp = parse_date(message['timestamp']).astimezone(eastern)
        message['timestamp'] = timestamp.strftime('%m/%d/%Y %H:%M:%S')

        if timestamp >= datetime(2021, 10, 29, tzinfo=eastern):  
            # Extract author name and check if it's "Mathematics Bot"
            author_name = message['author']['name']
            author_id = message['author']['id']
            if author_name == 'Mathematics Bot':
                author_pseudonym = author_name
                author_name_to_pseudonym[author_name] = author_pseudonym
            else:
                if author_id not in author_pseudonyms_mapping:
                    author_pseudonym = pseudonyms[pseudonym_index]
                    author_pseudonyms_mapping[author_id] = author_pseudonym
                    pseudonym_index += 1
                    # Update author_name_to_pseudonym mapping
                    author_name = message['author']['name']
                    author_name_to_pseudonym[author_name] = author_pseudonym
                else:
                    author_pseudonym = author_pseudonyms_mapping[author_id]

            conversation_key = f"help-{help_number}-{conversation_id}"
            if conversation_key not in conversations:
                conversations[conversation_key] = []

            text = message['content']
            

            attachments = message.get('attachments', [])
            attachment_url = attachments[0]['url'] if attachments else None

            if author_name == 'Mathematics Bot' and not text:
                if message['embeds']:
                    if 'author' in message['embeds'][0] and 'name' in message['embeds'][0]['author']:
                        text = message['embeds'][0]['author']['name']
                    elif 'description' in message['embeds'][0]:
                        text = message['embeds'][0]['description']
            
        # Replace mentions with pseudonyms in the text
        text = replace_mentions_with_pseudonyms(text, author_name_to_pseudonym)


        conversation = {
            "author": f"{author_pseudonym}:",
            "text": text,
            "timestamp": message['timestamp'],
            "url": attachment_url
        }

        conversation = {key: value for key, value in conversation.items() if value is not None}
        
        conversations[conversation_key].append(conversation)

        if len(message['embeds']) > 0 and message['embeds'][0]['title'] == 'Channel closed':
            conversation_id += 1

        for conversation_key in conversations:
            
            
            # Construct the absolute path for the output file
            output_file = os.path.join(output_directory, f'{help_number}-{conversation_id}.json')
            with open(output_file, 'w', encoding='utf-8') as f:
                formatted_data = {"dialogue": conversations[conversation_key]}
                json.dump(formatted_data, f, ensure_ascii=False, indent=2)

def generate_pseudonyms():
    # Get the psuedonyms from ./disentangle-help-channels/scripts/pseudonyms.csv using os.path.join
    pseudonyms = []
    # Need to use encoding='utf-8' to read the csv file.
    with open(os.path.join(os.path.dirname(__file__), 'pseudonyms.csv'), 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            pseudonyms.append(row[0])
    return pseudonyms

def extract_help_number(file_name):
    # Define a regex pattern to match "help-" followed by one or more digits
    pattern = r"help-\d+"
    
    # Search for the pattern in the file_name and extract the match
    match = re.search(pattern, file_name)
    
    # Return the matched value if found, otherwise return None
    return match.group(0) if match else None

if __name__ == '__main__':

    user_input = input('Enter the file name or directory: ')
    
    help_number = extract_help_number(user_input)
    print(f'help_number: {help_number}')
          
    # Get the directory path of the user_input file
    file_directory = os.path.dirname(user_input)
    
    # Create an output directory in the same directory as the input JSON file
    output_directory = os.path.join(os.path.dirname(os.path.abspath(user_input)), f'output_{help_number}')
    
    
    
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    pseudonyms = generate_pseudonyms()

    if os.path.isfile(user_input):
        process_file(user_input, pseudonyms, output_directory)
    elif os.path.isdir(user_input):
        for file in os.listdir(user_input):
            if file.endswith('.json'):
                process_file(os.path.join(user_input, file), pseudonyms, output_directory)
    else:
        print('Invalid input. Please enter a valid file or directory.')
