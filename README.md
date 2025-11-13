# Community Calendar - Social Network

A community-focused social network for building and managing monthly calendars together. Users can post events to a timeline (similar to Facebook), view events on an interactive calendar, and engage with the community through comments.

## Features

- **User Authentication**: Complete registration, login, and profile management system
- **Profile Management**: Upload profile images and customize your display name
- **Timeline UI**: Facebook-style feed for posting and viewing events
- **Calendar View**: Interactive calendar powered by FullCalendar library
- **Event Details**: Click events on the calendar to view full details and comments in a modal
- **Comments**: Engage with events through a commenting system
- **Admin Panel**: Manage users, promote/demote admins, and moderate events
- **Secure by Default**: Built on Google's Secure Scaffold with CSRF protection, CSP headers, and more

## Tech Stack

- **Backend**: Python Flask 3.0
- **Database**: Google Cloud Datastore (NDB)
- **Frontend**: Bootstrap 5, FullCalendar, Font Awesome
- **Platform**: Google App Engine (Python 3.11)
- **Security**: Flask-Talisman (CSP), Flask-SeaSurf (CSRF protection)

## Project Structure

```
community-calendar/
├── main.py                 # Main Flask application
├── models.py               # Database models (User, Event, Comment)
├── settings.py             # Flask configuration
├── requirements.txt        # Python dependencies
├── app.yaml               # App Engine configuration
├── run.sh                 # Local development script
├── templates/             # HTML templates
│   ├── base.html          # Base template with navbar
│   ├── login.html         # Login page
│   ├── register.html      # Registration page
│   ├── profile.html       # User profile page
│   ├── timeline.html      # Timeline feed
│   ├── event.html         # Single event view
│   ├── calendar.html      # Calendar view
│   └── admin.html         # Admin panel
└── static/                # Static assets
    ├── css/
    │   └── style.css      # Custom styles
    ├── js/                # Custom JavaScript
    ├── img/               # Images
    │   └── default-avatar.svg
    └── uploads/           # User uploaded images
```

## Setup Instructions

### Prerequisites

1. Install Python 3.11 or higher
2. Install the [Google Cloud SDK](https://cloud.google.com/sdk/install)
3. Initialize the SDK: `gcloud init`

### Local Development

1. **Clone or navigate to the project directory**:
   ```bash
   cd community-calendar
   ```

2. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the Cloud Datastore Emulator** (in a separate terminal):
   ```bash
   gcloud beta emulators datastore start --no-store-on-disk --consistency=1.0 --host-port=localhost:8081
   ```

5. **Set environment variables**:
   ```bash
   export DATASTORE_EMULATOR_HOST=localhost:8081
   export DATASTORE_PROJECT_ID=community-calendar-dev
   ```

6. **Run the Flask development server**:
   ```bash
   python main.py
   ```

   Or use the provided script (Unix/Linux/Mac):
   ```bash
   ./run.sh
   ```

7. **Visit the application**:
   Open your browser to http://localhost:8080

### First Time Setup

1. Register a new account at http://localhost:8080/register
2. The first user you create should be made an admin manually in the database, or you can modify the code temporarily to set `is_admin=True` for your first user
3. Once you have an admin account, you can promote other users to admin through the Admin Panel

## Deploying to Google App Engine

### Before Deployment

1. **Create a Google Cloud Project**:
   ```bash
   gcloud projects create community-calendar-prod --name="Community Calendar"
   gcloud config set project community-calendar-prod
   ```

2. **Enable required APIs**:
   ```bash
   gcloud services enable datastore.googleapis.com
   gcloud services enable cloudbuild.googleapis.com
   ```

3. **Initialize App Engine**:
   ```bash
   gcloud app create --region=us-central
   ```

4. **Update the secret key** in `settings.py` or set it as an environment variable in `app.yaml`:
   ```yaml
   env_variables:
     SECRET_KEY: "your-production-secret-key-here"
   ```

### Deploy

```bash
gcloud app deploy --project community-calendar-prod app.yaml
```

After deployment, visit: https://community-calendar-prod.appspot.com

### View Logs

```bash
gcloud app logs tail -s default
```

## Usage Guide

### For Regular Users

1. **Register/Login**: Create an account or log in
2. **Create Events**: Use the timeline to post new events with date, time, location, and description
3. **View Timeline**: See all community events in a feed format
4. **View Calendar**: Switch to calendar view to see events on an interactive calendar
5. **Comment**: Click on events to view details and add comments
6. **Update Profile**: Upload a profile image and update your display name

### For Administrators

1. **Access Admin Panel**: Click "Admin" in the navigation bar
2. **Manage Users**: View all users, promote/demote admin status
3. **Moderate Events**: View and delete any event
4. **View Statistics**: See total users, events, and admin count

## Key Routes

- `/` or `/timeline` - Main timeline feed (requires login)
- `/calendar` - Calendar view (requires login)
- `/register` - User registration
- `/login` - User login
- `/logout` - User logout
- `/profile` - User profile management
- `/event/<id>` - View single event with comments
- `/admin` - Admin panel (requires admin privileges)
- `/api/events` - JSON API for calendar events
- `/api/event/<id>` - JSON API for event details

## Security Features

- **CSRF Protection**: All forms protected with CSRF tokens via Flask-SeaSurf
- **Content Security Policy**: Strict CSP headers via Flask-Talisman
- **HTTPS Only**: All traffic forced to HTTPS
- **Secure Headers**: X-Frame-Options, X-Content-Type-Options, HSTS
- **Password Hashing**: Passwords hashed with SHA-256
- **Session Security**: Secure, HttpOnly, SameSite cookies

## Customization

### Adding More Admin Features

Edit `main.py` and add routes with the `@admin_required` decorator:

```python
@app.route('/admin/custom-feature')
@admin_required
@ndb_context
def custom_admin_feature():
    # Your code here
    return flask.render_template('custom.html')
```

### Changing Styles

Edit `static/css/style.css` to customize the appearance.

### Using Google Cloud Storage for Images

The current implementation saves uploaded images locally. For production, modify the `upload_profile_image()` function in `main.py` to upload to Google Cloud Storage instead.

## Troubleshooting

### Datastore Emulator Issues

If you get connection errors:
1. Make sure the emulator is running on port 8081
2. Ensure environment variables are set correctly
3. Try restarting the emulator

### CSP Errors

If external resources don't load:
1. Check `settings.py` CSP_POLICY configuration
2. Add the domain to the appropriate CSP directive

### Import Errors

If you get import errors:
```bash
pip install --upgrade -r requirements.txt
```

## License

Copyright 2025 Community Calendar

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

## Built With

This project is built on [Google's Secure Scaffold for App Engine](https://github.com/google/gae-secure-scaffold-python3).

## Support

For issues, questions, or contributions, please open an issue on the project repository.
