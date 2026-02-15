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
    task_name = request.form['task']
    tasks = load_tasks()
    task = {"id": len(tasks) + 1, "name": task_name, "completed": False}
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

    @app.route('/search', methods=['GET'])
    def search_tasks():
        """Search tasks by title and description"""
        query = request.args.get('q', '').lower()
        tasks = load_tasks()
    
        if not query:
            return jsonify(tasks)
    
        # Filter tasks by title and description
        filtered_tasks = []
        for task in tasks:
            task_name = task.get('name', '').lower()
            task_desc = task.get('description', '').lower()
        
            if query in task_name or query in task_desc:
                filtered_tasks.append(task)
    
        return jsonify(filtered_tasks)

    @app.route('/stats', methods=['GET'])
    def get_stats():
        """Get task statistics"""
        tasks = load_tasks()
    
        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if t.get('completed', False))
    
        # Count overdue tasks
        from datetime import datetime
        overdue_tasks = 0
        today = datetime.now().date()
        for task in tasks:
            if not task.get('completed', False) and task.get('due_date'):
                try:
                    due = datetime.strptime(task['due_date'], '%Y-%m-%d').date()
                    if due < today:
                        overdue_tasks += 1
                except ValueError:
                    pass
    
        return jsonify({
            'total': total_tasks,
            'completed': completed_tasks,
            'pending': total_tasks - completed_tasks,
            'overdue': overdue_tasks
        })
