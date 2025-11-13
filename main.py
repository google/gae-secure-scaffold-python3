# Copyright 2025 Community Calendar
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

import os
import json
from datetime import datetime, date
from functools import wraps

import flask
from flask import session, redirect, url_for, request, jsonify
import securescaffold
from google.cloud import ndb, storage
from werkzeug.utils import secure_filename

from models import User, Event, Comment


app = securescaffold.create_app(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize NDB client
ndb_client = ndb.Client()


def ndb_context(func):
    """Decorator to provide NDB context for database operations."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        with ndb_client.context():
            return func(*args, **kwargs)
    return wrapper


def login_required(func):
    """Decorator to require user login."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flask.flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login', next=request.url))
        return func(*args, **kwargs)
    return wrapper


def admin_required(func):
    """Decorator to require admin privileges."""
    @wraps(func)
    @login_required
    @ndb_context
    def wrapper(*args, **kwargs):
        user = User.get_by_id(session['user_id'])
        if not user or not user.is_admin:
            flask.flash('Admin access required.', 'danger')
            return redirect(url_for('timeline'))
        return func(*args, **kwargs)
    return wrapper


def get_current_user():
    """Get the currently logged-in user."""
    if 'user_id' in session:
        with ndb_client.context():
            return User.get_by_id(session['user_id'])
    return None


@app.context_processor
def inject_user():
    """Make current user available in all templates."""
    return {'current_user': get_current_user()}


# Authentication Routes
@app.route('/register', methods=['GET', 'POST'])
@ndb_context
def register():
    """User registration page."""
    if 'user_id' in session:
        return redirect(url_for('timeline'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        display_name = request.form.get('display_name')

        # Validation
        if not all([email, password, confirm_password, display_name]):
            flask.flash('All fields are required.', 'danger')
            return redirect(url_for('register'))

        if password != confirm_password:
            flask.flash('Passwords do not match.', 'danger')
            return redirect(url_for('register'))

        if User.get_by_email(email):
            flask.flash('Email already registered.', 'danger')
            return redirect(url_for('register'))

        # Create user
        user = User(
            email=email,
            password_hash=User.hash_password(password),
            display_name=display_name
        )
        user.put()

        session['user_id'] = user.key.id()
        flask.flash('Registration successful!', 'success')
        return redirect(url_for('timeline'))

    return flask.render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
@ndb_context
def login():
    """User login page."""
    if 'user_id' in session:
        return redirect(url_for('timeline'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.get_by_email(email)

        if user and user.check_password(password):
            session['user_id'] = user.key.id()
            flask.flash('Login successful!', 'success')
            next_url = request.args.get('next', url_for('timeline'))
            return redirect(next_url)
        else:
            flask.flash('Invalid email or password.', 'danger')

    return flask.render_template('login.html')


@app.route('/logout')
def logout():
    """User logout."""
    session.pop('user_id', None)
    flask.flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))


@app.route('/profile', methods=['GET', 'POST'])
@login_required
@ndb_context
def profile():
    """User profile page."""
    user = User.get_by_id(session['user_id'])

    if request.method == 'POST':
        display_name = request.form.get('display_name')

        if display_name:
            user.display_name = display_name
            user.put()
            flask.flash('Profile updated successfully!', 'success')

        return redirect(url_for('profile'))

    return flask.render_template('profile.html', user=user)


# Timeline Routes
@app.route('/')
@app.route('/timeline')
@login_required
@ndb_context
def timeline():
    """Timeline view - main feed of events."""
    events = Event.query().order(-Event.created_at).fetch(50)
    return flask.render_template('timeline.html', events=events)


@app.route('/event/create', methods=['POST'])
@login_required
@ndb_context
def create_event():
    """Create a new event."""
    title = request.form.get('title')
    description = request.form.get('description')
    event_date_str = request.form.get('event_date')
    event_time = request.form.get('event_time')
    location = request.form.get('location')

    # Validation
    if not title or not event_date_str:
        flask.flash('Title and date are required.', 'danger')
        return redirect(url_for('timeline'))

    try:
        event_date = datetime.strptime(event_date_str, '%Y-%m-%d').date()
    except ValueError:
        flask.flash('Invalid date format.', 'danger')
        return redirect(url_for('timeline'))

    # Create event
    user = User.get_by_id(session['user_id'])
    event = Event(
        title=title,
        description=description,
        event_date=event_date,
        event_time=event_time,
        location=location,
        author_key=user.key
    )
    event.put()

    flask.flash('Event created successfully!', 'success')
    return redirect(url_for('timeline'))


@app.route('/event/<int:event_id>')
@login_required
@ndb_context
def view_event(event_id):
    """View a single event with comments."""
    event = Event.get_by_id(event_id)

    if not event:
        flask.flash('Event not found.', 'danger')
        return redirect(url_for('timeline'))

    comments = Comment.query(Comment.event_key == event.key).order(Comment.created_at).fetch()

    return flask.render_template('event.html', event=event, comments=comments)


@app.route('/event/<int:event_id>/comment', methods=['POST'])
@login_required
@ndb_context
def add_comment(event_id):
    """Add a comment to an event."""
    event = Event.get_by_id(event_id)

    if not event:
        flask.flash('Event not found.', 'danger')
        return redirect(url_for('timeline'))

    content = request.form.get('content')

    if not content:
        flask.flash('Comment cannot be empty.', 'danger')
        return redirect(url_for('view_event', event_id=event_id))

    user = User.get_by_id(session['user_id'])
    comment = Comment(
        content=content,
        author_key=user.key,
        event_key=event.key
    )
    comment.put()

    flask.flash('Comment added!', 'success')
    return redirect(url_for('view_event', event_id=event_id))


@app.route('/event/<int:event_id>/delete', methods=['POST'])
@login_required
@ndb_context
def delete_event(event_id):
    """Delete an event (author or admin only)."""
    event = Event.get_by_id(event_id)

    if not event:
        flask.flash('Event not found.', 'danger')
        return redirect(url_for('timeline'))

    user = User.get_by_id(session['user_id'])

    if event.author_key != user.key and not user.is_admin:
        flask.flash('You do not have permission to delete this event.', 'danger')
        return redirect(url_for('timeline'))

    # Delete associated comments
    comments = Comment.query(Comment.event_key == event.key).fetch()
    for comment in comments:
        comment.key.delete()

    event.key.delete()

    flask.flash('Event deleted successfully.', 'success')
    return redirect(url_for('timeline'))


# Calendar Routes
@app.route('/calendar')
@login_required
@ndb_context
def calendar():
    """Calendar view using FullCalendar."""
    return flask.render_template('calendar.html')


@app.route('/api/events')
@login_required
@ndb_context
def api_events():
    """API endpoint to get events in FullCalendar format."""
    events = Event.query().fetch()
    events_data = [event.to_fullcalendar_dict() for event in events]
    return jsonify(events_data)


@app.route('/api/event/<int:event_id>')
@login_required
@ndb_context
def api_event_detail(event_id):
    """API endpoint to get event details with comments."""
    event = Event.get_by_id(event_id)

    if not event:
        return jsonify({'error': 'Event not found'}), 404

    comments = Comment.query(Comment.event_key == event.key).order(Comment.created_at).fetch()

    return jsonify({
        'event': event.to_dict(),
        'comments': [comment.to_dict() for comment in comments]
    })


# Admin Routes
@app.route('/admin')
@admin_required
@ndb_context
def admin_panel():
    """Admin panel."""
    users = User.query().fetch()
    events = Event.query().order(-Event.created_at).fetch()
    return flask.render_template('admin.html', users=users, events=events)


@app.route('/admin/user/<int:user_id>/toggle-admin', methods=['POST'])
@admin_required
@ndb_context
def toggle_admin(user_id):
    """Toggle admin status for a user."""
    user = User.get_by_id(user_id)

    if not user:
        flask.flash('User not found.', 'danger')
        return redirect(url_for('admin_panel'))

    user.is_admin = not user.is_admin
    user.put()

    flask.flash(f'Admin status updated for {user.email}.', 'success')
    return redirect(url_for('admin_panel'))


# Profile Image Upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload-profile-image', methods=['POST'])
@login_required
@ndb_context
def upload_profile_image():
    """Upload profile image."""
    if 'profile_image' not in request.files:
        flask.flash('No file selected.', 'danger')
        return redirect(url_for('profile'))

    file = request.files['profile_image']

    if file.filename == '':
        flask.flash('No file selected.', 'danger')
        return redirect(url_for('profile'))

    if file and allowed_file(file.filename):
        user = User.get_by_id(session['user_id'])
        filename = secure_filename(f"{user.key.id()}_{file.filename}")

        # For local development, save to static/uploads
        # For production, you'd upload to Google Cloud Storage
        upload_folder = os.path.join('static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)

        user.profile_image_url = f'/static/uploads/{filename}'
        user.put()

        flask.flash('Profile image updated!', 'success')
        return redirect(url_for('profile'))

    flask.flash('Invalid file type.', 'danger')
    return redirect(url_for('profile'))


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
