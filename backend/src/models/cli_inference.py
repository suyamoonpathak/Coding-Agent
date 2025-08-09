import argparse
import os
import sys
import requests


def stream_generate(url: str, prompt: str) -> None:
    resp = requests.post(url, json={"prompt": prompt}, stream=True)
    resp.raise_for_status()
    for chunk in resp.iter_content(chunk_size=None):
        if chunk:
            sys.stdout.write(chunk.decode("utf-8", errors="ignore"))
            sys.stdout.flush()


def generate_code_cli(base_url: str, prompt: str, stream: bool) -> None:
    if stream:
        stream_url = base_url.rstrip("/") + "/generate_code_stream"
        stream_generate(stream_url, prompt)
        return

    url = base_url.rstrip("/") + "/generate_code/"
    try:
        response = requests.post(url, json={"prompt": prompt})
        response.raise_for_status()
        result = response.json()
        print(result.get("generated_code", ""))
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
    parser.add_argument("command", help="generate_code or feedback")
    parser.add_argument("--prompt", help="Prompt to generate code", default="")
    parser.add_argument("--base-url", help="Model service base URL", default=os.environ.get("MODEL_BASE_URL", "http://localhost:8000"))
    parser.add_argument("--stream", help="Stream tokens from server", action="store_true")
    args = parser.parse_args()

    if args.command == "generate_code":
        if not args.prompt:
            print("Please provide a prompt using --prompt")
            return
        generate_code_cli(args.base_url, args.prompt, args.stream)
    elif args.command == "feedback":
        collect_feedback()
    else:
        print("Unknown command. Use 'generate_code' or 'feedback'.")

if __name__ == "__main__":
    main()
