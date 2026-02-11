from flask import Blueprint, render_template, request, redirect, url_for, flash, session, Flask
from app import db
from app.models import Task

tasks_bp=Blueprint('tasks',__name__)

@tasks_bp.route('/')
def view_tasks():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    tasks=Task.query.all()
    return render_template('tasks.html',tasks=tasks)

@tasks_bp.route('/add', methods=["POST"])
def add_tasks():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    title=request.form.get('title')
    if title:
        new_task=Task(title=title,status='pending')
        db.session.add(new_task)
        db.session.commit()
        flash('Task added successfully','success')
    else:
        flash('Title required')
    return redirect(url_for('tasks.view_tasks'))

#changing task status
@tasks_bp.route('/toggle/<int:task_id>', methods=["POST"])
def toggle_status(task_id):
    task=Task.query.get(task_id)
    if task:
        if task.status=='pending':
            task.status='working'
        elif task.status=='working':
            task.status='done'
        else:
            task.status='pending'
        db.session.commit()
    return redirect(url_for('tasks.view_tasks'))

#deleting all tasks
@tasks_bp.route('/clear', methods=["POST"])
def clear_tasks():
    Task.query.delete()
    db.session.commit()
    flash('All tasks cleared!','info')
    return redirect(url_for('tasks.view_tasks'))