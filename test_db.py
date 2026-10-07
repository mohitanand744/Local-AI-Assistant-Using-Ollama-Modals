from database import init_db, add_task, get_pending_tasks

init_db()

add_task("Complete MiniBC API integration")
add_task("Push staging changes")
add_task("Work on NextChapter")

for task_id, title in get_pending_tasks():
    print(task_id, title)