import docker

CONTAINER_NAME = "model-execution-container"  # Change this to the actual container name

client = docker.from_env()

def execute_code_in_container(code: str):
    try:
        container = client.containers.get(CONTAINER_NAME)
        exec_log = container.exec_run(f"python -c \"{code}\"", stdout=True, stderr=True, demux=True)
        stdout, stderr = exec_log.output
        if stderr:
            return f"Error: {stderr.decode('utf-8')}"
        return stdout.decode('utf-8')
    except docker.errors.NotFound:
        return f"Error: Container {CONTAINER_NAME} not found."
    except Exception as e:
        return f"Error: {str(e)}"
