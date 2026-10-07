import json
import ollama

from pc_tools import (
    open_app,
    open_folder,
    open_website
)

from dev_tools import (
    git_status,
    git_branch,
    open_project
)

from tools import (
    show_pending_tasks,
    create_task,
    finish_task
)

MODEL = "qwen2.5-coder:7b"

SYSTEM_PROMPT = """
You are Coding Beast, Mohit's personal local AI assistant.

You are running locally on Mohit's Windows PC.

Your personality:
- Friendly
- Natural
- Confident
- Developer-focused
- Slightly energetic
- Concise
- Conversational

You can currently perform these task operations:

1. View pending tasks
2. Add a new task
3. Complete a task
4. Open an application
5. Open a folder
6. Open a website
7. Check Git status
8. Check Git branch
9. Open a project in VS Code

You MUST return ONLY valid JSON.

For normal conversation:
{
  "action": "chat",
  "text": "your response"
}

For viewing tasks:
{
  "action": "list_tasks"
}

For adding a task:
{
  "action": "add_task",
  "title": "task title"
}

For completing a task:
{
  "action": "complete_task",
  "task_id": 2
}

Examples:

User: "What are my pending tasks?"
{
  "action": "list_tasks"
}

User: "Add a task to finish the NextChapter homepage"
{
  "action": "add_task",
  "title": "Finish the NextChapter homepage"
}

User: "Mark task 2 as complete"
{
  "action": "complete_task",
  "task_id": 2
}

User: "How are you?"
{
  "action": "chat",
  "text": "I'm doing great, bro. Ready to help."
}

Important:
- Return ONLY JSON.
- Never use Markdown.
- Never wrap JSON in ``` blocks.

You can also control the PC with these operations:

4. Open an application

{
  "action": "open_app",
  "app": "vscode"
}

5. Open a folder

{
  "action": "open_folder",
  "folder": "ai assistant"
}

6. Open a website

{
  "action": "open_website",
  "url": "https://github.com"
}

Examples:

User: "Open VS Code"
{
  "action": "open_app",
  "app": "vscode"
}

User: "Open Chrome"
{
  "action": "open_app",
  "app": "chrome"
}

User: "Open my AI Assistant folder"
{
  "action": "open_folder",
  "folder": "ai assistant"
}

User: "Open GitHub"
{
  "action": "open_website",
  "url": "https://github.com"
}

You can also perform developer operations:

7. Check Git status
{
  "action": "git_status",
  "project": "ai assistant"
}

8. Check Git branch
{
  "action": "git_branch",
  "project": "ai assistant"
}

9. Open a project in VS Code
{
  "action": "open_project",
  "project": "ai assistant"
}

Examples:

User: "Check Git status"
{
  "action": "git_status",
  "project": "ai assistant"
}

User: "What branch am I on?"
{
  "action": "git_branch",
  "project": "ai assistant"
}

User: "Open my AI Assistant project"
{
  "action": "open_project",
  "project": "ai assistant"
}
"""


def parse_command(raw_response):
    """
    Convert Coding Beast's response into a JSON command.
    Handles accidental Markdown code fences from the model.
    """

    raw_response = raw_response.strip()

    # Remove Markdown code fences
    raw_response = raw_response.replace("```json", "")
    raw_response = raw_response.replace("```JSON", "")
    raw_response = raw_response.replace("```", "")
    raw_response = raw_response.strip()

    # Try normal JSON first
    try:
        return json.loads(raw_response)
    except json.JSONDecodeError:
        pass

    # If the model added extra text around the JSON,
    # try extracting the JSON object.
    start = raw_response.find("{")
    end = raw_response.rfind("}")

    if start != -1 and end != -1 and end > start:
        json_text = raw_response[start:end + 1]

        try:
            return json.loads(json_text)
        except json.JSONDecodeError:
            pass

    return None


def ask_coding_beast(user_text):
    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_text
            }
        ]
    )

    raw_response = response["message"]["content"].strip()

    command = parse_command(raw_response)

    # If the response wasn't valid JSON,
    # treat it as a normal conversational response.
    if command is None:
        return raw_response

    action = command.get("action")

    if action == "chat":
        return command.get(
            "text",
            "I'm not sure how to answer that."
        )

    if action == "list_tasks":
        return show_pending_tasks()

    if action == "add_task":
        return create_task(
            command.get("title", "")
        )

    if action == "complete_task":
        return finish_task(
            command.get("task_id")
        )

    if action == "open_app":
        return open_app(
            command.get("app", "")
        )

    if action == "open_folder":
        return open_folder(
            command.get("folder", "")
        )

    if action == "open_website":
        return open_website(
            command.get("url", "")
        )
    if action == "git_status":
        return git_status(
            command.get("project", "")
        )
    if action == "git_branch":
        return git_branch(
            command.get("project", "")
        )
    if action == "open_project":
        return open_project(
            command.get("project", "")
        )

    return "I don't know how to perform that task yet."


if __name__ == "__main__":
    print("🐲 Coding Beast brain is ready.")

    while True:
        user_text = input("\nYou: ").strip()

        if user_text.lower() in [
            "exit",
            "quit",
            "stop"
        ]:
            print("Coding Beast: See you later, bro.")
            break

        if not user_text:
            continue

        response = ask_coding_beast(user_text)

        print(f"Coding Beast: {response}")