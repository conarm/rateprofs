import requests

# Base URL of the API
# TODO: Replace with PythonAnywhere URL when hosted
BASE_URL = "http://127.0.0.1:8000/api/"

def handle_login(session, username, password):
    try:
        response = session.post(BASE_URL + "login", data={"username": username, "password": password})
        if response.status_code == 200:
            return response.text
        else:
            return f"Error: {response.status_code} - {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}"
    
def handle_logout(session):
    try:
        response = session.post(BASE_URL + "logout")
        if response.status_code == 200:
            return response.text
        else:
            return f"Error: {response.status_code} - {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}"
    
def handle_list(session):
    try:
        response = session.get(BASE_URL + "list")
        if response.status_code == 200:
            return response.text
        else:
            return f"Error: {response.status_code} - {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}"
    
def handle_view(session):
    try:
        response = session.get(BASE_URL + "view")
        if response.status_code == 200:
            return response.text
        else:
            return f"Error: {response.status_code} - {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}"
    
# TODO: change these to ID/code according to the API
def handle_average(session, professorCode, moduleCode):
    try:
        response = session.get(BASE_URL + "average", params={"professor_code": professorCode, "module_code": moduleCode})
        if response.status_code == 200:
            return response.text
        else:
            return f"Error: {response.status_code} - {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}"
    
def handle_rate(session, professorCode, moduleCode, year, semester, rating):
    try:
        response = session.post(BASE_URL + "login", data={"professorCode": professorCode, "moduleCode": moduleCode, "year": year, "semester": semester, "rating": rating})
        if response.status_code == 200:
            return response.text
        else:
            return f"Error: {response.status_code} - {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}"
    
def handle_seed(session):
    try:
        response = session.get(BASE_URL + "seed")
        if response.status_code == 200:
            return response.text
        else:
            return f"Error: {response.status_code} - {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}"

# Main loop to interact with the user
def main():
    print("Welcome to the API Client. Type 'exit' to quit.")
    session = requests.session()
    
    while True:
        parts = input("Enter command: ").split()
                
        match parts[0].lower():
            case 'exit':
                print("Exiting...")
                break
            case 'login':
                if len(parts) != 3:
                    print("Invalid 'login' command. Format: login [username] [password]")
                    continue
                response = handle_login(session, parts[1], parts[2])
                print(response)
            case 'logout':
                if len(parts) != 1:
                    print("Invalid 'logout' command. Format: logout")
                    continue
                response = handle_logout(session)
                print(response)
            case 'list':
                if len(parts) != 1:
                    print("Invalid 'list' command. Format: list")
                    continue
                response = handle_list(session)
                print(response)
            case 'view':
                if len(parts) != 1:
                    print("Invalid 'view' command. Format: view")
                    continue
                response = handle_view(session)
                print(response)
            case 'average':
                if len(parts) != 3:
                    print("Invalid 'average' command. Format: average [professorCode] [moduleCode]")
                    continue
                response = handle_average(session, parts[1], parts[2])
                print(response)
            case 'rate':
                if len(parts) != 6:
                    print("Invalid 'rate' command. Format: rate [professorCode] [moduleCode] [year] [semester] [rating]")
                    continue
                response = handle_rate(session, parts[1], parts[2], parts[3], parts[4], parts[5])
                print(response)
            case 'seed':
                # TODO: Remove before submission? Use this for testing
                if len(parts) != 1:
                    print("Invalid 'seed' command. Format: seed")
                    continue
                response = handle_seed(session)
                print(response)
            case _:
                print("Invalid command")
                

if __name__ == '__main__':
    main()
