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
    open_project,
    start_server,
    stop_server
)

from codebase_tools import (
    index_project,
    search_code,
    explain_codebase,
    code_index_status
)

from tools import (
    show_pending_tasks,
    create_task,
    finish_task
)
from config import OLLAMA_MODEL

MODEL = OLLAMA_MODEL

# Maintain conversation context (memory)
chat_history = []

SYSTEM_PROMPT = """
You are Coding Beast, Mohit's personal local AI assistant running on Windows.

Your personality:
- Friendly, calm, natural, helpful, slightly casual, concise, and confident.
- You are a highly intelligent coding assistant and conversational partner (like ChatGPT). 
- If the user wants to learn, ask them insightful questions or test their knowledge.
- Speak naturally like a human assistant (e.g., "Sure, opening VS Code", "I can help with that", "You're welcome").
- Keep responses short unless details are requested.
- Never use robotic wording, corporate language, or repeating sentence structures.
- NEVER use numbered lists unless explicitly asked.

You can perform tasks. You MUST return ONLY valid JSON.

For normal conversation or questions about what you can do:
{
  "action": "chat",
  "text": "I can manage your tasks, open apps and websites, check Git status, and open projects. Just tell me what you need!"
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

User: "What's pending?"
{
  "action": "list_tasks"
}

User: "Add a task to finish the homepage"
{
  "action": "add_task",
  "title": "Finish the homepage"
}

User: "Thanks"
{
  "action": "chat",
  "text": "You're welcome."
}

User: "What can you do?"
{
  "action": "chat",
  "text": "I can manage your tasks, open apps, folders and websites, check Git status and branches, and open your projects in VS Code."
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

10. Start a development server
{
  "action": "start_server",
  "project": "nextchapter",
  "service": "frontend"
}

11. Stop a development server
{
  "action": "stop_server",
  "project": "nextchapter",
  "service": "frontend"
}

You can also use Codebase Intelligence (RAG) to index and query local code:

12. Index a project
Use this before answering questions about a project's codebase, or if the user asks to update the index.
{
  "action": "index_project",
  "project": "ai assistant"
}

13. Explain codebase
Use this to answer questions like "How does auth work?" or "Explain config.py".
{
  "action": "explain_codebase",
  "project": "ai assistant",
  "query": "How does authentication work?"
}

14. Search code
Use this to find specific files or API endpoints, like "Find the login API."
{
  "action": "search_code",
  "project": "ai assistant",
  "query": "Login API endpoint"
}

15. Check code index status
{
  "action": "code_index_status",
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
    global chat_history

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]
    messages.extend(chat_history)
    messages.append({"role": "user", "content": user_text})

    response = ollama.chat(
        model=MODEL,
        messages=messages
    )

    raw_response = response["message"]["content"].strip()

    command = parse_command(raw_response)

    # If the response wasn't valid JSON,
    # treat it as a normal conversational response.
    if command is None:
        return raw_response

    action = command.get("action")

    if action == "chat":
        result = command.get("text", "I'm not sure how to answer that.")
    elif action == "list_tasks":
        result = show_pending_tasks()
    elif action == "add_task":
        result = create_task(command.get("title", ""))
    elif action == "complete_task":
        result = finish_task(command.get("task_id"))
    elif action == "open_app":
        result = open_app(command.get("app", ""))
    elif action == "open_folder":
        result = open_folder(command.get("folder", ""))
    elif action == "open_website":
        result = open_website(command.get("url", ""))
    elif action == "git_status":
        result = git_status(command.get("project", ""))
    elif action == "git_branch":
        result = git_branch(command.get("project", ""))
    elif action == "open_project":
        result = open_project(command.get("project", ""))
    elif action == "start_server":
        result = start_server(command.get("project", ""), command.get("service", ""))
    elif action == "stop_server":
        result = stop_server(command.get("project", ""), command.get("service", ""))
    elif action == "index_project":
        result = index_project(command.get("project", ""))
    elif action == "search_code":
        result = search_code(command.get("project", ""), command.get("query", ""))
    elif action == "explain_codebase":
        result = explain_codebase(command.get("project", ""), command.get("query", ""))
    elif action == "code_index_status":
        result = code_index_status(command.get("project", ""))
    else:
        result = "I don't know how to perform that task yet."

    # Prevent the LLM from hallucinating its own speaker name in the text
    result = str(result).replace("Coding Beast:", "").replace("Coding Beast :", "").strip()
    
    # Remove identical consecutive lines (LLM stuttering)
    lines = [line.strip() for line in result.split('\n') if line.strip()]
    unique_lines = []
    for line in lines:
        if not unique_lines or unique_lines[-1] != line:
            unique_lines.append(line)
            
    final_output = " ".join(unique_lines)
    
    # Save the interaction to memory
    chat_history.append({"role": "user", "content": user_text})
    
    # We must store the assistant's reply in the JSON format it was instructed to use,
    # otherwise the LLM sees plain text in its history and its JSON logic degrades!
    import json
    assistant_json = json.dumps({"action": "chat", "text": final_output})
    chat_history.append({"role": "assistant", "content": assistant_json})
    
    # Keep only the last 10 messages (5 turns) to prevent context bloat
    if len(chat_history) > 10:
        chat_history = chat_history[-10:]
        
    return final_output


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