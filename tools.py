from database import (
    get_pending_tasks,
    add_task,
    complete_task
)


def show_pending_tasks():
    tasks = get_pending_tasks()

    if not tasks:
        return "You don't have any pending tasks."

    titles = [title for _, title in tasks]
    
    if len(titles) == 1:
        return f"You have one pending task: {titles[0]}."
    
    if len(titles) == 2:
        return f"You have two pending tasks: {titles[0]}, and {titles[1]}."
        
    last = titles.pop()
    joined = ", then ".join(titles)
    return f"You have {len(tasks)} pending tasks. The first is {titles[0]}, then {joined[len(titles[0])+7:]}, and finally {last}."


def create_task(title):
    title = title.strip()

    if not title:
        return "I need a task title."

    add_task(title)

    return f"Done. I've added the task to {title}."


def finish_task(task_id):
    try:
        task_id = int(task_id)
    except ValueError:
        return "I need a valid task ID."

    complete_task(task_id)

    return f"Awesome. I've marked task {task_id} as complete."