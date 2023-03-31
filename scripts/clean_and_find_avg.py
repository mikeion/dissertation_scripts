import csv
import json
import re
import os

def parse_json(parent_folder, output_csv):
    # Initialize a list to store the number of tokens for each file
    num_tokens_list = []
    
    # Create or overwrite the output CSV file
    with open(output_csv, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['File', 'Tokens'])
        
        # Iterate through the subfolders in the parent folder
        for root, dirs, files in os.walk(parent_folder):
            for file in files:
                # Check if the file is a JSON file
                if file.endswith(".json"):
                    # Get the full path to the JSON file
                    json_file_path = os.path.join(root, file)
                    
                    # Open and load the JSON file
                    with open(json_file_path, 'r', encoding='utf-8') as f:
                        json_data = json.load(f)
                    
                    # Check if the 'dialogs' key exists in the JSON data
                    if 'dialogs' in json_data:
                        html_content = json_data['dialogs']
                        # Remove HTML tags
                        html_content = re.sub(r'<[^>]+>', '', html_content)
                        
                        # Tokenize the content by splitting on spaces
                        tokens = html_content.split()
                        num_tokens = len(tokens)
                        
                        # Only include files with tokens in the average calculation
                        if num_tokens > 0:
                            num_tokens_list.append(num_tokens)
                            # Write the number of tokens to the CSV file
                            csv_writer.writerow([file, num_tokens])
    
    # Calculate and print the average number of tokens if applicable
    if num_tokens_list:
        average_tokens = sum(num_tokens_list) / len(num_tokens_list)
        print(f"Average number of tokens: {average_tokens:.2f}")
    else:
        print("No tokens found.")

if __name__ == '__main__':
    # Ask user for the folder name
    folder = input('Enter the folder name: ')
    
    # Ask user for the output CSV file name
    output = input('Enter the output CSV file name: ')
    
    # Call the parse_json function
    parse_json(folder, output)