import requests

# Send a GET request to the API and print the text
# Note: POST requests will be blocked if no CSRF token is sent
r = requests.get('http://127.0.0.1:8000/api')
print(r.text)