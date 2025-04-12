#!/usr/bin/env python3

import argparse
import datetime
import json
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pydantic import ValidationError

from typing import Optional, List
from pydantic import BaseModel, Field


class Reminder(BaseModel):
    method: str = Field(
        ..., description="Reminder method (e.g., 'popup', 'email')"
    )
    minutes: int = Field(..., description="Minutes before the event to trigger the reminder")


class Event(BaseModel):
    date: str = Field(..., description="Event date in YYYY-MM-DD format")
    start_time: Optional[str] = Field(
        None, description="Event start time in HH:MM format (24-hour)"
    )
    end_time: Optional[str] = Field(
        None, description="Event end time in HH:MM format (24-hour)"
    )
    summary: str = Field(..., description="Event summary or title")
    description: Optional[str] = Field(None, description="Event description")
    location: Optional[str] = Field(None, description="Event location")
    reminders: Optional[Reminder] = Field(
        None, description="Reminder settings for the event"
    )


class EventList(BaseModel):
    events: List[Event]

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]


def create_event(service, event_data: Event, calendar_id: str): 
    """Creates an event on Google Calendar."""
    try:
        date_str = event_data.date
        start_time_str = event_data.start_time
        end_time_str = event_data.end_time

        if start_time_str and end_time_str:
            start_datetime = datetime.datetime.fromisoformat(
                f"{date_str}T{start_time_str}:00"
            )
            end_datetime = datetime.datetime.fromisoformat(
                f"{date_str}T{end_time_str}:00"
            )

            start = start_datetime.isoformat()
            end = end_datetime.isoformat()
        else:
            start_datetime = datetime.datetime.fromisoformat(f"{date_str}T00:00:00")
            end_datetime = datetime.datetime.fromisoformat(f"{date_str}T23:59:59")

            start = start_datetime.isoformat()
            end = end_datetime.isoformat()

        event = {
            "summary": event_data.summary,
            "description": event_data.description,
            "location": event_data.location,
            "start": {"dateTime": start, "timeZone": "America/Los_Angeles"},
            "end": {"dateTime": end, "timeZone": "America/Los_Angeles"},
            "reminders": {
                "useDefault": False,
                "overrides": [event_data.reminders.dict()],
            } if event_data.reminders else {"useDefault": True},
        }

        event = (
            service.events()
            .insert(calendarId=calendar_id, body=event)
            .execute()
        )
        print(f"Event created: {event.get('htmlLink')}")

    except HttpError as error:
        print(f"An error occurred: {error}")


def main(json_file_path: str, credentials_file_path: str, calendar_id: str):  
    creds = None

    token_file = "token.json"
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refreshing token: {e}. Deleting token file and re-authenticating.")
                os.remove(token_file) 
                creds = None 

        if not creds or not creds.valid:
            from google_auth_oauthlib.flow import InstalledAppFlow
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_file_path, SCOPES
                )
                creds = flow.run_local_server(port=0)
            except FileNotFoundError:
                print(f"Error: Credentials file not found at {credentials_file_path}")
                return
            except Exception as e:
                print(f"Error during authentication flow: {e}")
                return
        with open(token_file, "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)

        with open(json_file_path, "r") as f:
            events_data = json.load(f)

        try:
            events = EventList(**events_data)
        except ValidationError as e:
            print(f"Validation Error: {e}")
            return

        for event_data in events.events:
            create_event(service, event_data, calendar_id)

    except HttpError as error:
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Add events from a JSON file to Google Calendar."
    )
    parser.add_argument(
        "json_file_path", type=str, help="Path to the JSON file containing event data."
    )
    parser.add_argument(
        "--credentials",
        type=str,
        default="credentials.json", 
        help="Path to the Google API credentials file (e.g., client_secrets.json). Defaults to 'credentials.json'.",
    )
    parser.add_argument( 
        "--calendar-id",
        type=str,
        default="primary",
        help="The ID of the calendar to add events to. Defaults to 'primary'. Use 'primary' for the user's main calendar or provide a specific calendar ID.",
    )
    args = parser.parse_args()

    if not os.path.exists(args.credentials):
        print(f"Error: Credentials file '{args.credentials}' not found.")
        print("Please provide the correct path using the --credentials argument or place the file in the specified location.")
        exit(1) 

    main(args.json_file_path, args.credentials, args.calendar_id)
