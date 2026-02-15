from flask import Flask, request, jsonify, render_template
import json

app = Flask(__name__)

# Function to load tasks from local storage (JSON)
def load_tasks():
    try:
        with open("todo.json", "r") as f:
            tasks = json.load(f)
    except FileNotFoundError:
        tasks = []
    return tasks

# Function to save tasks to local storage (JSON)
def save_tasks(tasks):
    with open("todo.json", "w") as f:
        json.dump(tasks, f)

@app.route('/')
def index():
    tasks = load_tasks()
    return render_template('index.html', tasks=tasks)


@app.route('/add', methods=['POST'])
def add_task():
    task_name = request.form.get('task', '')
    description = request.form.get('description', '')
    priority = request.form.get('priority', 'medium')
    due_date = request.form.get('due_date', '')
    
    tasks = load_tasks()
    task = {
        "id": len(tasks) + 1,
        "name": task_name,
        "description": description,
        "priority": priority,
        "due_date": due_date,
        "completed": False,
        "created_at": __import__('datetime').datetime.now().isoformat()
    }
    tasks.append(task)
    save_tasks(tasks)
    return jsonify(tasks)
@app.route('/update/<int:task_id>', methods=['POST'])
def update_task(task_id):
    tasks = load_tasks()
    for task in tasks:
        if task['id'] == task_id:
            task['completed'] = not task['completed']
            break
    save_tasks(tasks)
    return jsonify(tasks)


@app.route('/delete/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    tasks = load_tasks()
    tasks = [task for task in tasks if task['id'] != task_id]
    save_tasks(tasks)
    return jsonify(tasks)

@app.route('/task/<int:task_id>', methods=['GET'])
def get_task(task_id):
    tasks = load_tasks()
    for task in tasks:
        if task['id'] == task_id:
            return jsonify(task)
    return jsonify({'error': 'Task not found'}), 404

@app.route('/task/<int:task_id>/update', methods=['POST'])
def update_task_full(task_id):
    tasks = load_tasks()
    for task in tasks:
        if task['id'] == task_id:
            task['name'] = request.form.get('name', task['name'])
            task['description'] = request.form.get('description', task.get('description', ''))
            task['priority'] = request.form.get('priority', task.get('priority', 'medium'))
            task['due_date'] = request.form.get('due_date', task.get('due_date', ''))
            break
    save_tasks(tasks)
    return jsonify(tasks)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
