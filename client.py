import requests

# Base URL of the API
# TODO: Replace with PythonAnywhere URL when hosted
BASE_URL = "https://sc21ca.pythonanywhere.com/api/"

# Send a register request to create a user account
def handle_register(session, username, email, password):
    try:
        response = session.post(BASE_URL + "register", data={"username": username, "email": email, "password": password})
        if response.status_code == 200:
            return response.text
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Request failed: {e}"

# Send a login request to log in the session
def handle_login(session, url, username, password):
    try:
        # TODO: Keep http here?
        response = session.post('http://' + url + "/api/login", data={"username": username, "password": password})
        if response.status_code == 200:
            return response.text
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Request failed: {e}"

# Send a logout request to end the logged-in session
def handle_logout(session):
    try:
        response = session.post(BASE_URL + "logout")
        if response.status_code == 200:
            return response.text
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Request failed: {e}"
    
# Send a list request to view a list of all module instances
def handle_list(session):
    try:
        response = session.get(BASE_URL + "list")
        if response.status_code == 200:
            data = response.json()
            output_lines = []
            output_lines.append('Code |   Name   | Year | Semester |  Taught by')
            output_lines.append('---------------------------------------------------------------')
            for row in data:
                output_lines.append(f'{row["module_code"]}     {row["module_name"]}   {row["year"]}     {row["semester"]}         {row["taught_by"][0]}')
                for i in range(1, len(row["taught_by"])):
                    output_lines.append(f'                                     {row["taught_by"][i]}')
                output_lines.append('---------------------------------------------------------------')
            output = "\n".join(output_lines)
            return output
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Request failed: {e}"
    
# Send a view request to view the ratings of all professors
def handle_view(session):
    try:
        response = session.get(BASE_URL + "view")
        if response.status_code == 200:
            data = response.json()
            output_lines = []
            for row in data:
                if (row["average_rating"] is not None):
                    output_lines.append(f'The rating of Professor {row["professor_name"]} ({row["professor_code"]}) is {'*' * row["average_rating"]}')
                else:
                    output_lines.append(f'No ratings exist for Professor {row["professor_name"]} ({row["professor_code"]})')
            output = "\n".join(output_lines)
            return output
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Request failed: {e}"
    
# Send an average request to see the average rating of a professor in a module
def handle_average(session, professorCode, moduleCode):
    try:
        response = session.get(BASE_URL + "average", params={"professor_code": professorCode, "module_code": moduleCode})
        if response.status_code == 200:
            data = response.json()
            if data["average_rating"] is not None:
                output = f'The rating of Professor {data["professor_name"]} ({data["professor_code"]}) in module {data["module_name"]} ({data["module_code"]}) is {'*' * data["average_rating"]}'
            else:
                output = f'Rating unavailable'
            return output
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Request failed: {e}"

# Send a rate request to rate a module instance
def handle_rate(session, professorCode, moduleCode, year, semester, rating):
    try:
        response = session.post(BASE_URL + "rate", data={"professorCode": professorCode, "moduleCode": moduleCode, "year": year, "semester": semester, "rating": rating})
        if response.status_code == 200:
            return response.text
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Request failed: {e}"

# Send a seed request to populate database
def handle_seed(session):
    try:
        response = session.get(BASE_URL + "seed")
        if response.status_code == 200:
            return response.text
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Request failed: {e.message}"

# Main command loop
def main():
    print("Welcome to the API Client. Type 'exit' to quit.")
    session = requests.session()
    
    # Continually ask for input
    while True:
        parts = input("Enter command: ").split()
        command = parts[0]
        
        # Switch over sanitized command string
        match command.lower():
            case 'exit':
                print("Exiting...")
                break
            case 'register':
                if len(parts) != 1:
                    print("Invalid 'register' command. Format: register")
                    continue
                username = input("Please enter a username: ")
                email = input("Please enter an email: ")
                password = input("Please enter a password: ")
                response = handle_register(session, username, email, password)
                print(response)
            case 'login':
                if len(parts) != 2:
                    print("Invalid 'login' command. Format: login [url] (omit the preceding 'http://', 'https://' and subsequent '/')")
                    continue
                url = parts[1]
                username = input("Please enter your username: ")
                password = input("Please enter your password: ")
                response = handle_login(session, url, username, password)
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
                professorCode = parts[1]
                moduleCode = parts[2]
                response = handle_average(session, professorCode, moduleCode)
                print(response)
            case 'rate':
                if len(parts) != 6:
                    print("Invalid 'rate' command. Format: rate [professorCode] [moduleCode] [year] [semester] [rating]")
                    continue
                professorCode = parts[1]
                moduleCode = parts[2]
                year = parts[3]
                semester = parts[4]
                rating = parts[5]
                response = handle_rate(session, professorCode, moduleCode, year, semester, rating)
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
