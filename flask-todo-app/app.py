from flask import Flask, request, jsonify, render_template
import json
from datetime import datetime, timedelta

app = Flask(__name__)
DATA_FILE = "todo.json"

# Load and save
def load_tasks():
    try:
        with open(DATA_FILE, "r") as f:
            tasks = json.load(f)
    except FileNotFoundError:
        tasks = []
    return tasks

def save_tasks(tasks):
    with open(DATA_FILE, "w") as f:
        json.dump(tasks, f)

# Ensure schema defaults
def ensure_task_schema(tasks):
    changed = False
    for t in tasks:
        if 'created_at' not in t:
            t['created_at'] = datetime.now().isoformat()
            changed = True
        if 'priority' not in t:
            t['priority'] = 'medium'
            changed = True
        if 'description' not in t:
            t['description'] = ''
            changed = True
        if 'due_date' not in t:
            t['due_date'] = ''
            changed = True
    if changed:
        save_tasks(tasks)

@app.route('/')
def index():
    tasks = load_tasks()
    ensure_task_schema(tasks)
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add_task():
    task_name = request.form.get('task', '').strip()
    description = request.form.get('description', '').strip()
    priority = request.form.get('priority', 'medium')
    due_date = request.form.get('due_date', '').strip()

    tasks = load_tasks()
    new_id = max([t.get('id', 0) for t in tasks], default=0) + 1
    task = {
        'id': new_id,
        'name': task_name,
        'description': description,
        'priority': priority,
        'due_date': due_date,
        'completed': False,
        'created_at': datetime.now().isoformat()
    }
    tasks.append(task)
    save_tasks(tasks)
    return jsonify(tasks)

@app.route('/update/<int:task_id>', methods=['POST'])
def toggle_task(task_id):
    tasks = load_tasks()
    for task in tasks:
        if task.get('id') == task_id:
            task['completed'] = not task.get('completed', False)
            break
    save_tasks(tasks)
    return jsonify(tasks)

@app.route('/task/<int:task_id>/update', methods=['POST'])
def update_task_full(task_id):
    tasks = load_tasks()
    for task in tasks:
        if task.get('id') == task_id:
            task['name'] = request.form.get('name', task.get('name', ''))
            task['description'] = request.form.get('description', task.get('description', ''))
            task['priority'] = request.form.get('priority', task.get('priority', 'medium'))
            task['due_date'] = request.form.get('due_date', task.get('due_date', ''))
            break
    save_tasks(tasks)
    return jsonify(tasks)

@app.route('/delete/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    tasks = load_tasks()
    tasks = [t for t in tasks if t.get('id') != task_id]
    save_tasks(tasks)
    return jsonify(tasks)

@app.route('/task/<int:task_id>', methods=['GET'])
def get_task(task_id):
    tasks = load_tasks()
    for task in tasks:
        if task.get('id') == task_id:
            return jsonify(task)
    return jsonify({'error': 'Task not found'}), 404

@app.route('/search', methods=['GET'])
def search_tasks():
    q = request.args.get('q', '').strip().lower()
    tasks = load_tasks()
    if not q:
        return jsonify(tasks)
    out = []
    for t in tasks:
        name = t.get('name', '').lower()
        desc = t.get('description', '').lower()
        if q in name or q in desc:
            out.append(t)
    return jsonify(out)

@app.route('/stats', methods=['GET'])
def get_stats():
    tasks = load_tasks()
    total = len(tasks)
    completed = sum(1 for t in tasks if t.get('completed'))
    pending = total - completed

    today = datetime.now().date()
    overdue = 0
    for t in tasks:
        if not t.get('completed') and t.get('due_date'):
            try:
                due = datetime.fromisoformat(t['due_date'])
                if due.date() < today:
                    overdue += 1
            except Exception:
                try:
                    due = datetime.strptime(t['due_date'], '%Y-%m-%d')
                    if due.date() < today:
                        overdue += 1
                except Exception:
                    pass

    # simple trend: completed in last 7 days
    seven_days_ago = datetime.now() - timedelta(days=7)
    completed_last_7 = 0
    for t in tasks:
        if t.get('completed') and t.get('created_at'):
            try:
                c = datetime.fromisoformat(t['created_at'])
                if c >= seven_days_ago:
                    completed_last_7 += 1
            except Exception:
                pass

    return jsonify({
        'total': total,
        'completed': completed,
        'pending': pending,
        'overdue': overdue,
        'completed_last_7': completed_last_7
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
