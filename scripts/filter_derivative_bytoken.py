import os
import json
import shutil

def search_for_word(word, json_data):
    for key, value in json_data.items():
        if isinstance(value, dict):
            if search_for_word(word, value):
                return True
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    if search_for_word(word, item):
                        return True
                elif isinstance(item, str) and word in item:
                    return True
        elif isinstance(value, str) and word in value:
            return True
    return False


def copy_files_with_word(word, src_folder, dest_folder):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    for root, _, files in os.walk(src_folder):
        for file_name in files:
            if file_name.endswith('.json'):
                file_path = os.path.join(root, file_name)
                with open(file_path, 'r', encoding='utf-8') as file:
                    try:
                        json_data = json.load(file)
                    except json.JSONDecodeError:
                        print(f"Error: Unable to parse '{file_path}'. Skipping file.")
                        continue

                if search_for_word(word, json_data):
                    relative_path = os.path.relpath(root, src_folder)
                    dest_subfolder = os.path.join(dest_folder, relative_path)
                    if not os.path.exists(dest_subfolder):
                        os.makedirs(dest_subfolder)

                    dest_path = os.path.join(dest_subfolder, file_name)
                    shutil.copy(file_path, dest_path)
                    print(f"Copied '{file_path}' to '{dest_path}'.")
                    
if __name__ == "__main__":
    print("Please enter the path to the source folder:")
    src_folder = input().strip()
    print("Please enter the path to the destination folder:")
    dest_folder = input().strip()
    print("Please enter the word to search for:")
    word = input().strip()

    copy_files_with_word(word, src_folder, dest_folder)