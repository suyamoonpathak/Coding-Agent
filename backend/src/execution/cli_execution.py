import argparse
import os
import sys
import requests


def execute_code_cli(base_url: str, code: str, stream: bool) -> None:
    if stream:
        url = base_url.rstrip("/") + "/execute_code_stream/"
        resp = requests.post(url, json={"code": code}, stream=True)
        resp.raise_for_status()
        for chunk in resp.iter_content(chunk_size=None):
            if chunk:
                sys.stdout.write(chunk.decode("utf-8", errors="ignore"))
                sys.stdout.flush()
        return

    url = base_url.rstrip("/") + "/execute_code/"
    try:
        response = requests.post(url, json={"code": code})
        response.raise_for_status()
        result = response.json()
        logs = result.get("logs", "")
        exit_code = result.get("exit_code")
        if logs:
            print(logs, end="")
        if exit_code is not None:
            print(f"\nExit code: {exit_code}")
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
    parser.add_argument("command", help="execute_code or feedback")
    parser.add_argument("--code", help="Code to execute (use with 'execute_code')", default="")
    parser.add_argument("--base-url", help="Execution API base URL", default=os.environ.get("EXEC_BASE_URL", "http://localhost:5000"))
    parser.add_argument("--stream", help="Stream output from server", action="store_true")
    args = parser.parse_args()

    if args.command == "execute_code":
        if args.code:
            execute_code_cli(args.base_url, args.code, args.stream)
        else:
            print("Please provide the code to execute using --code")
    elif args.command == "feedback":
        collect_feedback()
    else:
        print("Unknown command. Use 'execute_code' or 'feedback'.")

if __name__ == "__main__":
    main()
