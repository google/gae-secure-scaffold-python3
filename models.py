# Copyright 2025 Community Calendar
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from google.cloud import ndb
from datetime import datetime
import hashlib


class User(ndb.Model):
    """User model for authentication and profile management."""
    email = ndb.StringProperty(required=True)
    password_hash = ndb.StringProperty(required=True)
    display_name = ndb.StringProperty(required=True)
    profile_image_url = ndb.StringProperty(default='/static/img/default-avatar.svg')
    is_admin = ndb.BooleanProperty(default=False)
    created_at = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def get_by_email(cls, email):
        """Get user by email address."""
        return cls.query(cls.email == email).get()

    @staticmethod
    def hash_password(password, salt=None):
        """Hash a password with SHA-256."""
        if salt is None:
            salt = 'community-calendar-salt'
        return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()

    def check_password(self, password):
        """Check if provided password matches stored hash."""
        return self.password_hash == self.hash_password(password)

    def to_dict(self):
        """Convert user to dictionary (excluding password)."""
        return {
            'id': self.key.id(),
            'email': self.email,
            'display_name': self.display_name,
            'profile_image_url': self.profile_image_url,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Event(ndb.Model):
    """Event model for calendar events and timeline posts."""
    title = ndb.StringProperty(required=True)
    description = ndb.TextProperty()
    event_date = ndb.DateProperty(required=True)
    event_time = ndb.StringProperty()  # Store as string like "14:30"
    location = ndb.StringProperty()
    author_key = ndb.KeyProperty(kind=User, required=True)
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    updated_at = ndb.DateTimeProperty(auto_now=True)

    @property
    def author(self):
        """Get the author user object."""
        return self.author_key.get()

    def to_dict(self, include_author=True):
        """Convert event to dictionary."""
        event_dict = {
            'id': self.key.id(),
            'title': self.title,
            'description': self.description,
            'event_date': self.event_date.isoformat() if self.event_date else None,
            'event_time': self.event_time,
            'location': self.location,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        if include_author and self.author:
            event_dict['author'] = self.author.to_dict()

        return event_dict

    def to_fullcalendar_dict(self):
        """Convert event to FullCalendar format."""
        # Combine date and time for FullCalendar
        start = self.event_date.isoformat()
        if self.event_time:
            start = f"{start}T{self.event_time}"

        return {
            'id': str(self.key.id()),
            'title': self.title,
            'start': start,
            'extendedProps': {
                'description': self.description,
                'location': self.location,
                'author': self.author.to_dict() if self.author else None
            }
        }


class Comment(ndb.Model):
    """Comment model for comments on events."""
    content = ndb.TextProperty(required=True)
    author_key = ndb.KeyProperty(kind=User, required=True)
    event_key = ndb.KeyProperty(kind=Event, required=True)
    created_at = ndb.DateTimeProperty(auto_now_add=True)

    @property
    def author(self):
        """Get the author user object."""
        return self.author_key.get()

    @property
    def event(self):
        """Get the event object."""
        return self.event_key.get()

    def to_dict(self, include_author=True):
        """Convert comment to dictionary."""
        comment_dict = {
            'id': self.key.id(),
            'content': self.content,
            'event_id': self.event_key.id(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

        if include_author and self.author:
            comment_dict['author'] = self.author.to_dict()

        return comment_dict
