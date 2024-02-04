import os
import requests
import base64

# Repository details
GITHUB_USERNAME = 'ajohn19'
REPO_NAME = 'TEST'
FOLDER_NAME = 'qx'

# GitHub API URL
GITHUB_API = 'https://api.github.com'

# Headers for using the default GITHUB_TOKEN provided by GitHub Actions
headers = {
    'Authorization': f'token {os.getenv("GITHUB_TOKEN")}',
    'Accept': 'application/vnd.github.v3+json'
}

def get_file_list(folder_name):
    contents_url = f"{GITHUB_API}/repos/{GITHUB_USERNAME}/{REPO_NAME}/contents/{folder_name}"
    response = requests.get(contents_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching repo contents: {response.status_code}")
        return None

def update_file(file_path, b64_encoded_content, sha):
    update_url = f"{GITHUB_API}/repos/{GITHUB_USERNAME}/{REPO_NAME}/contents/{file_path}"
    message = f"Add custom header to {file_path}"
    data = {
        'message': message,
        'content': b64_encoded_content,
        'sha': sha
    }
    response = requests.put(update_url, headers=headers, json=data)
    if response.status_code == 200:
        print(f"File updated successfully: {file_path}")
    else:
        print(f"Error updating file: {response.status_code}, Response: {response.json()}")

# Fetch the list of files
files = get_file_list(FOLDER_NAME)

for file in files:
    file_name, file_extension = os.path.splitext(file['name'])
    if file_extension in ('.js', '.conf', '.snippet'):
        download_url = file['download_url']
        file_sha = file['sha']
        
        # Download the existing file content
        file_content_response = requests.get(download_url)
        if file_content_response.status_code == 200:
            file_content = file_content_response.content.decode('utf-8')
            
            # Custom header
            custom_header = f"""
// qx引用地址： https://raw.githubusercontent.com/{GITHUB_USERNAME}/{REPO_NAME}/{FOLDER_NAME}/{file_name}{file_extension}
// surge/shadowrocket 模块地址： https://raw.githubusercontent.com/{GITHUB_USERNAME}/{REPO_NAME}/surge/{file_name}.sgmodule
// loon 插件地址： https://raw.githubusercontent.com/{GITHUB_USERNAME}/{REPO_NAME}/loon/{file_name}.plugin
// stash 覆写地址： https://raw.githubusercontent.com/{GITHUB_USERNAME}/{REPO_NAME}/stash/{file_name}.stoverride
"""

            # Combine custom header with existing content
            new_file_content = custom_header + '\n' + file_content

            # Encode the new file content in base64
            b64_encoded_content = base64.b64encode(new_file_content.encode('utf-8')).decode('utf-8')

            # Update the file on GitHub
            update_file(file['path'], b64_encoded_content, file_sha)
        else:
            print(f"Failed to download file content: {file_content_response.status_code}")
