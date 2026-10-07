from database import (
    get_pending_tasks,
    add_task,
    complete_task
)


def show_pending_tasks():
    tasks = get_pending_tasks()

    if not tasks:
        return "You don't have any pending tasks."

    if len(tasks) == 1:
        return f"You have one pending task: {tasks[0][1]}."

    task_text = ", ".join(
        f"task {task_id}: {title}"
        for task_id, title in tasks
    )

    return f"You have {len(tasks)} pending tasks. {task_text}."


def create_task(title):
    title = title.strip()

    if not title:
        return "I need a task title."

    add_task(title)

    return f"Added the task: {title}."


def finish_task(task_id):
    try:
        task_id = int(task_id)
    except ValueError:
        return "I need a valid task ID."

    complete_task(task_id)

    return f"Marked task {task_id} as completed."