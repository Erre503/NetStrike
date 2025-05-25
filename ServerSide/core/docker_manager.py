# docker_manager.py
import docker
import os
import threading
import logging

class DockerManager:
    def __init__(self):
        self.client = docker.from_env()

    def identify_language(self, path_script):
        ext = os.path.splitext(path_script)[1]
        if ext == ".py":
            return "python"
        elif ext in [".sh"]:
            return "bash"
        else:
            with open(path_script) as f:
                first_line = f.readline()
            if "python" in first_line:
                return "python"
            elif "bash" in first_line:
                return "bash"
        raise ValueError("Lang not recognized")

    def run_script(self, path_script):
        lang = self.identify_language(path_script)
        script_dir = os.path.dirname(path_script)
        script_name = os.path.basename(path_script)

        if lang == "python":
            image = "python:3.9-slim"
            cmd = [
                "bash", "-c",
                f"pip install pipreqs && pipreqs . && pip install -r requirements.txt && python {script_name}"
            ]
        elif lang == "bash":
            image = "ubuntu:latest"
            cmd = ["bash", script_name]
        else:
            logging.error(f"Lang {lang} not supported")
            return

        def _threaded_run():
            try:
                logging.info(f"executing {script_name} on docker...")
                output = self.client.containers.run(
                    image=image,
                    command=cmd,
                    volumes={script_dir: {'bind': '/app', 'mode': 'ro'}},
                    working_dir="/app",
                    stdout=True, stderr=True, remove=True
                )
                logging.info(f"Output from {script_name}:\n{output.decode()}")
            except Exception as e:
                logging.error(f"Error during {script_name}: {e}")

        threading.Thread(target=_threaded_run).start()
