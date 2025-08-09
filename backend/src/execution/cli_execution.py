import argparse
import requests

# Define the API URL for executing code
API_URL = "http://localhost:5000/execute_code/"

def execute_code_cli(code: str):
    """Executes code via the FastAPI endpoint."""
    payload = {"code": code}
    
    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()  # Raise an error for 4xx/5xx responses
        result = response.json()
        print(f"{result['output']}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

def collect_feedback():
    """Collect feedback from the user on the generated code."""
    feedback = input("Do you think the generated code is correct? (y/n): ")
    if feedback.lower() == "y":
        print("Thank you for your feedback!")
    else:
        print("Please provide more details about the issue:")
        issue_details = input("Your feedback: ")
        print(f"Feedback received: {issue_details}")
        # Here you can save the feedback for future analysis
        with open("execution_feedback.txt", "a") as f:
            f.write(f"User feedback: {issue_details}\n")

def main():
    parser = argparse.ArgumentParser(description="Autonomous Coding Agent")
    
    # Add commands for code execution and feedback collection
    parser.add_argument("command", help="The command to execute (e.g., execute_code, feedback)")
    parser.add_argument("--code", help="The code to execute (use with 'execute_code')", default="")
    
    args = parser.parse_args()

    if args.command == "execute_code":
        if args.code:
            execute_code_cli(args.code)
        else:
            print("Please provide the code to execute using --code")

    elif args.command == "feedback":
        collect_feedback()
    else:
        print("Unknown command. Use 'execute_code' or 'feedback'.")

if __name__ == "__main__":
    main()
