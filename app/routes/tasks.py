from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.db import get_cursor

tasks_bp=Blueprint('tasks',__name__)

@tasks_bp.route('/')
def view_tasks():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    with get_cursor() as (cur, _):
        cur.execute("SELECT id, title, status FROM tasks WHERE user_id = %s ORDER BY id", (session['user_id'],))
        rows = cur.fetchall()
    tasks = [{'id': r[0], 'title': r[1], 'status': r[2]} for r in rows]
    return render_template('tasks.html', tasks=tasks)

@tasks_bp.route('/add', methods=["POST"])
def add_tasks():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    title = request.form.get('title', '').strip()
    if title:
        with get_cursor() as (cur, _):
            cur.execute("INSERT INTO tasks (title, status, user_id) VALUES (%s, %s, %s)", (title, 'pending', session['user_id']))
        flash('Task added successfully', 'success')
    else:
        flash('Title required', 'danger')
    return redirect(url_for('tasks.view_tasks'))

#changing task status
@tasks_bp.route('/toggle/<int:task_id>', methods=["POST"]) 
def toggle_status(task_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    with get_cursor() as (cur, _):
        cur.execute("SELECT status FROM tasks WHERE id = %s AND user_id = %s", (task_id, session['user_id']))
        row = cur.fetchone()
        if row:
            status = row[0]
            if status == 'pending':
                next_status = 'working'
            elif status == 'working':
                next_status = 'done'
            else:
                next_status = 'pending'
            cur.execute("UPDATE tasks SET status = %s WHERE id = %s AND user_id = %s", (next_status, task_id, session['user_id']))
    return redirect(url_for('tasks.view_tasks'))

#deleting all tasks
@tasks_bp.route('/clear', methods=["POST"]) 
def clear_tasks():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    with get_cursor() as (cur, _):
        cur.execute("DELETE FROM tasks WHERE user_id = %s", (session['user_id'],))
    flash('All your tasks cleared!', 'info')
    return redirect(url_for('tasks.view_tasks'))