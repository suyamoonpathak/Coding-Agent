import argparse
import requests

# Define the API URL for generating code
API_URL = "http://localhost:8000/generate_code/"

def generate_code_cli(prompt: str):
    """Generates code from the FastAPI server."""
    payload = {"prompt": prompt}

    try:
        # Send POST request to the FastAPI server to generate code
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()  # Raise an error for non-2xx responses
        result = response.json()
        generated_code = result.get("generated_code", "")
        print(generated_code)
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
        with open("inference_feedback.txt", "a") as f:
            f.write(f"User feedback: {issue_details}\n")

def main():
    parser = argparse.ArgumentParser(description="Autonomous Coding Agent (Inference)")
    
    # Add arguments for generating code and feedback
    parser.add_argument("command", help="The command to execute (e.g., generate_code, feedback)")
    parser.add_argument("--prompt", help="The prompt to generate code (use with 'generate_code')", default="")
    
    args = parser.parse_args()

    if args.command == "generate_code":
        if args.prompt:
            generate_code_cli(args.prompt)
        else:
            print("Please provide a prompt using --prompt")

    elif args.command == "feedback":
        collect_feedback()
    else:
        print("Unknown command. Use 'generate_code' or 'feedback'.")

if __name__ == "__main__":
    main()
