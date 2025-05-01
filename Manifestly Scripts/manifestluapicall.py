

import requests

# Your Manifestly API key
API_KEY = 'NOKEY'

# API endpoint to fetch active workflows
url = 'https://api.manifest.ly/api/v1/checklists'

# Headers with Authorization
headers = {
    'Authorization': API_KEY,
    'Content-Type': 'application/json'
}

# Make the GET request
response = requests.get(url, headers=headers)

# Print status and response
print(f"Status Code: {response.status_code}")
try:
    print(response.json())
except Exception as e:
    print(f"Failed to parse JSON: {e}")
    print(response.text)
