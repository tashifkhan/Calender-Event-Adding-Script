# Google Calendar Event Adder

This Python script allows you to bulk-add events to your Google Calendar by reading event data from a JSON file. It utilizes the Google Calendar API v3 and Pydantic for data validation.

## Features

*   Adds multiple events from a structured JSON file.
*   Supports specifying start/end times or creating all-day events.
*   Allows setting event summaries, descriptions, and locations.
*   Configurable reminders (popup or email) for each event.
*   Uses OAuth 2.0 for secure authentication with Google Calendar.
*   Validates the input JSON format using Pydantic.
*   Flexible command-line arguments for specifying input file, credentials, and target calendar.

## Prerequisites

1.  **Python 3:** The script is written for Python 3. Ensure you have it installed. The script includes a shebang `#!/usr/bin/env python3` for direct execution on Unix-like systems.
2.  **Google Account:** You need a Google account to access Google Calendar.
3.  **Google Cloud Project & API Credentials:**
    *   Go to the [Google Cloud Console](https://console.cloud.google.com/).
    *   Create a new project or select an existing one.
    *   Enable the **Google Calendar API** for your project.
    *   Create **OAuth 2.0 Client ID** credentials:
        *   Select **Desktop app** as the application type.
        *   Give it a name (e.g., "Calendar Script").
        *   Download the credentials JSON file. Rename it to `credentials.json` (or use a different name and specify it with the `--credentials` flag).

## Setup

1.  **Clone the repository (or download the script):**
    ```bash
    git clone https://github.com/tashifkhan/Calender-Event-Adding-Script/
    cd Calender-Event-Adding-Script
    ```
    Or simply save the script code as a `.py` file (e.g., `add_calendar_events.py`).

2.  **Place Credentials File:** Put the downloaded `credentials.json` file in the same directory as the script, or note its path to use with the `--credentials` flag.

3.  **Install Dependencies:** Create a `requirements.txt` file with the following content:

    ```txt
    google-api-python-client
    google-auth-httplib2
    google-auth-oauthlib
    pydantic
    ```

    Then, install the required packages using pip:
    ```bash
    pip install -r requirements.txt
    ```

4.  **(Optional) Make the script executable (macOS/Linux):**
    ```bash
    chmod +x add_calendar_events.py
    ```

## JSON Input Format

The script expects a JSON file containing a single top-level key `"events"` which holds a list of event objects. Each event object should have the following structure:

```python
{
    "events": [
        {
            "date": "YYYY-MM-DD",             # Required: Event date
            "start_time": "HH:MM",            # Optional: Start time (24-hour format). If omitted (with end_time), creates an all-day event.
            "end_time": "HH:MM",              # Optional: End time (24-hour format). Required if start_time is present.
            "summary": "Event Title",         # Required: The main title/summary of the event.
            "description": "More details...", # Optional: A longer description for the event.
            "location": "Event Location",     # Optional: Physical location or meeting link.
            "reminders": {                    # Optional: Reminder settings. If omitted, calendar defaults are used.
                "method": "popup" or "email", # Required if reminders object is present: Type of reminder.
                "minutes": 30                 # Required if reminders object is present: Minutes before event to remind.
            }
        },
        {
            "date": "2025-05-05",
            "summary": "Project Deadline",   # Example of an all-day event (no start/end time)
            "description": "Submit final deliverables",
            "reminders": {
                "method": "popup",
                "minutes": 120
            }
        }
        # ... more event objects
    ]
}
```

**Example JSON (`events.json`):**

```json
{
    "events": [
        {
            "date": "2025-04-20",
            "start_time": "10:00",
            "end_time": "11:00",
            "summary": "Meeting with Team",
            "description": "Discuss project progress",
            "location": "Conference Room A",
            "reminders": {
                "method": "popup",
                "minutes": 30
            }
        },
        {
            "date": "2025-05-01",
            "start_time": "14:00",
            "end_time": "15:30",
            "summary": "Client Presentation",
            "description": "Present the new design",
            "location": "Client's Office",
            "reminders": {
                "method": "email",
                "minutes": 60
            }
        },
        {
            "date": "2025-05-05",
            "summary": "Project Deadline",
            "description": "Submit final deliverables",
            "reminders": {
                "method": "popup",
                "minutes": 120
            }
        }
    ]
}
```

## Usage

Run the script from your terminal, providing the path to your JSON event file.

**Basic Usage (using defaults):**

```bash
./add_calendar_events.py path/to/your/events.json
```
*(Assumes `credentials.json` is in the same directory and adds to the primary calendar)*

**Specifying Credentials File:**

```bash
./add_calendar_events.py path/to/your/events.json --credentials /path/to/your/client_secrets.json
```

**Specifying Target Calendar ID:**

```bash
./add_calendar_events.py path/to/your/events.json --calendar-id your_calendar_id@group.calendar.google.com
```
*(Replace `your_calendar_id@...` with the actual ID found in your Google Calendar settings)*

**Using All Options:**

```bash
./add_calendar_events.py events.json --credentials client_secrets.json --calendar-id secondary_calendar@group.calendar.google.com
```

**Command-Line Arguments:**

*   `json_file_path` (Required): Positional argument for the path to the input JSON file.
*   `--credentials` (Optional): Path to the Google API credentials file. Defaults to `credentials.json` in the script's directory.
*   `--calendar-id` (Optional): The ID of the calendar to add events to. Defaults to `primary` (the user's main calendar).

## Authentication Flow

*   **First Run:** When you run the script for the first time, it will open a web browser window asking you to log in to your Google Account and grant the script permission to manage your calendar events.
*   **`token.json`:** After successful authorization, the script creates a `token.json` file in the same directory. This file stores your access and refresh tokens, so you don't have to re-authorize every time.
*   **Security:** **Do NOT share your `credentials.json` or `token.json` files.** Add `token.json` to your `.gitignore` file if using Git.
*   **Token Refresh:** The script attempts to refresh the access token if it expires. If refreshing fails (e.g., permissions revoked), it will delete the `token.json` file and prompt you to re-authenticate.

## Dependencies

The required Python packages are listed in `requirements.txt`:

*   `google-api-python-client`: Google API Client Library for Python.
*   `google-auth-httplib2`: Google Authentication Library for Python with httplib2.
*   `google-auth-oauthlib`: Google Authentication Library for Python using OAuthlib.
*   `pydantic`: Data validation and settings management using Python type annotations.

## Contributing

Feel free to open issues or submit pull requests if you find bugs or have suggestions for improvements.

## License

MIT LICENSE

---
