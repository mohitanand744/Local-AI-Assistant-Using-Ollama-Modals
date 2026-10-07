import subprocess
from pathlib import Path


# ============================================================
# PROJECTS
# ============================================================

PROJECTS = {
    "ai assistant": Path(r"C:\AI-Assistant"),

    # Add your actual project paths here later.
    # Example:
    # "nextchapter": Path(r"C:\Users\mohit\Projects\NextChapter"),
}


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
            return "The Git repository is clean."

        return output

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

        return f"You are currently on the {branch} branch."

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

        return f"Opened {project_name} in VS Code."

    except Exception as error:
        return f"I couldn't open {project_name}: {error}"


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    print(git_status("ai assistant"))
    print()
    print(git_branch("ai assistant"))