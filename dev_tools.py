import subprocess
from pathlib import Path
from config import PROJECTS


# ============================================================
# GET GIT STATUS
# ============================================================

def git_status(project_name):
    project_name = project_name.lower().strip()

    if project_name not in PROJECTS:
        return f"I don't know the project called {project_name}."

    project_path = PROJECTS[project_name]

    if not project_path.exists():
        return f"The project folder does not exist: {project_path}"

    try:
        result = subprocess.run(
            ["git", "status", "--short", "--branch"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=15
        )

        if result.returncode != 0:
            return f"Git returned an error: {result.stderr.strip()}"

        output = result.stdout.strip()

        if not output:
            return "Your Git repository is clean."

        lines = output.split('\n')
        # Skip the branch info line if it's there
        changed_files = [line for line in lines if not line.startswith('##')]
        
        if not changed_files:
            return "Your Git repository is clean."
            
        file_count = len(changed_files)
        if file_count == 1:
            return "You have one modified file in your repository."
        else:
            return f"You have {file_count} modified files in your repository."

    except Exception as error:
        return f"I couldn't check Git status: {error}"


# ============================================================
# GET CURRENT GIT BRANCH
# ============================================================

def git_branch(project_name):
    project_name = project_name.lower().strip()

    if project_name not in PROJECTS:
        return f"I don't know the project called {project_name}."

    project_path = PROJECTS[project_name]

    try:
        result = subprocess.run(
            [
                "git",
                "branch",
                "--show-current"
            ],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=15
        )

        if result.returncode != 0:
            return f"Git returned an error: {result.stderr.strip()}"

        branch = result.stdout.strip()
        return f"You're currently on the {branch} branch."

    except Exception as error:
        return f"I couldn't check the Git branch: {error}"


# ============================================================
# OPEN PROJECT IN VS CODE
# ============================================================

def open_project(project_name):
    project_name = project_name.lower().strip()

    if project_name not in PROJECTS:
        return f"I don't know the project called {project_name}."

    project_path = PROJECTS[project_name]

    if not project_path.exists():
        return f"The project folder does not exist: {project_path}"

    try:
        subprocess.Popen(
            [
                "code",
                str(project_path)
            ],
            shell=True
        )

        return f"Sure, opening {project_name} in VS Code."

    except Exception as error:
        return f"I couldn't open {project_name}: {error}"


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    print(git_status("ai assistant"))

# ============================================================
# SAFE SERVER MANAGEMENT
# ============================================================

from config import DEV_SERVERS

# Keep track of running server processes
RUNNING_SERVERS = {}

def start_server(project_name, service_name):
    project_name = project_name.lower().strip()
    service_name = service_name.lower().strip()
    
    if project_name not in DEV_SERVERS:
        return f"I don't have server configs for the project {project_name}."
        
    if service_name not in DEV_SERVERS[project_name]:
        return f"I don't have a {service_name} server configured for {project_name}."
        
    server_key = f"{project_name}_{service_name}"
    if server_key in RUNNING_SERVERS:
        # Check if it's actually still running
        if RUNNING_SERVERS[server_key].poll() is None:
            return f"The {service_name} server for {project_name} is already running."
        else:
            del RUNNING_SERVERS[server_key]
        
    config_details = DEV_SERVERS[project_name][service_name]
    cmd = config_details["command"]
    cwd = config_details["cwd"]
    
    if not Path(cwd).exists():
        return f"The directory for {service_name} at {cwd} does not exist."
    
    try:
        # We use CREATE_NEW_PROCESS_GROUP so we can kill it and its children gracefully on Windows
        process = subprocess.Popen(
            cmd,
            cwd=cwd,
            shell=True,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        )
        RUNNING_SERVERS[server_key] = process
        return f"Sure, I've started the {service_name} server for {project_name}."
    except Exception as e:
        return f"I couldn't start the {service_name} server. {e}"

def stop_server(project_name, service_name):
    project_name = project_name.lower().strip()
    service_name = service_name.lower().strip()
    
    server_key = f"{project_name}_{service_name}"
    
    if server_key not in RUNNING_SERVERS:
        return f"The {service_name} server for {project_name} is not currently running."
        
    process = RUNNING_SERVERS[server_key]
    
    try:
        if process.poll() is None:
            # Kill the process tree on Windows using taskkill
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(process.pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        del RUNNING_SERVERS[server_key]
        return f"I have stopped the {service_name} server for {project_name}."
    except Exception as e:
        return f"I encountered an error while trying to stop the server: {e}"
    print()
    print(git_branch("ai assistant"))