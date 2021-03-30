from __future__ import print_function
from datetime import datetime
import pickle
import os.path

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from random import choice, randint
from typing import Optional
from aiohttp import request

from discord.ext.commands import Cog, BadArgument, command, cooldown, BucketType
from discord import Member, Embed

COG_ID = "calendar"
CALENDAR_COLOR = 0x0C9C84
SETTING_COLOR = 0x03FC6F

def get_credentials():
    # If modifying these scopes, delete the file token.pickle
    # allows read/write access to Google Calendars
    SCOPES = ["https://www.googleapis.com/auth/calendar"]

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return creds

def create_service():
    service = build("calendar","v3", credentials=get_credentials())
    return service

def get_calendar():
    with open("lib/cogs/calendar_id.0", "r", encoding="utf-8") as tf:
        CALENDAR_ID = tf.read()
    return CALENDAR_ID

def get_events(eventNum):
    CALENDAR_ID = get_calendar()
    service = create_service()

    now = datetime.utcnow().isoformat() + "Z"
    events_result = (
        service.events()
        .list(
            calendarId= CALENDAR_ID,
            timeMin=now,
            maxResults=eventNum,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    return events_result["items"]

def time_conversion(timeString):
    time = int(timeString[11:13])
    if time==0:
        newTime = 12 + timeString[13:16] + " A.M."
    elif time<=12:
        newTime = str(time) + timeString[13:16] + " A.M."
    else:
        newTime = str((time-12)) + timeString[13:16] + " P.M."
    return newTime

def date_conversion(timeString):
    year = timeString[0:4]
    monthNum = int(timeString[5:7])
    day = timeString[8:10]
    MONTHS_OF_YEAR = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    month = MONTHS_OF_YEAR[monthNum-1]
    return month + " " + day + ", " + year


class Calendar(Cog):
    def __init__(self, bot):
        self.bot=bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(COG_ID)

    @command(name="calendar", help="Retrieve a number of specified number of future events in the calendar.", brief="Retrieve events from calendar.")
    async def get_calendar(self, ctx, number):
        result = Embed(title=f"Next {number} Events", colour=CALENDAR_COLOR)
        for event in get_events(number):
            title = event["summary"]
            eventID = event["id"]
            start = event["start"].get("dateTime", event["start"].get("date"))
            end = event["end"].get("dateTime", event["end"].get("date"))
            date = date_conversion(start)
            start = time_conversion(start)
            end = time_conversion(end)
            timezone = event["start"].get("timeZone", event["start"].get("date"))

            #can also add timezone (w/ UTC-XX:00)

            result.add_field(name=title, value=f"Event ID: {eventID}\nDate: {date}\nTimezone: {timezone}\nStart: {start}\nEnd: {end}", inline=False)
        await ctx.send(embed = result)    
        

    @command(name="add", help="Add an event to the calendar. Input date with the format YYYY-MM-DD. Input start and end time with format HH:MM in 24-hour time.", brief="Add an event to the calendar.")
    async def add_event(self, ctx, date, start, end, title, *, description: Optional[str]=" "):
        # add various embeds to promt user to select options such as: timezone, freq, and count or create description
        startTime = date + "T" + start + ":00-04:00"
        endTime = date + "T" + end + ":00-04:00" #defaulted to EST timezone 
        event = {
            'summary': title,
            'description': description,
            'start': {
                'dateTime': startTime, #'2015-05-28T09:00:00-07:00'
                'timeZone': 'America/New_York',
            },
            'end': {
                'dateTime': endTime,
                'timeZone': 'America/New_York',
            },
            'recurrence': [
                'RRULE:FREQ=DAILY;COUNT=1' #add option later for frequency
            ]
        }
        CALENDAR_ID = get_calendar()
        service = create_service()
        event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()

        dateTime = date_conversion(startTime)
        startTime = time_conversion(startTime)
        endTime = time_conversion(endTime)

        eventEmbed = Embed(title = "Event Created",
                        description = f"Title: {title}\nDate: {dateTime}\nStart: {startTime}\nEnd: {endTime}\nDescription: {description}\n URL: {event.get('htmlLink')}",
                        colour = 0x16C77D,
                        timestamp=datetime.utcnow())
        await ctx.send(embed = eventEmbed)

    @command(name="remove", help="Remove an event from the calendar with the ID of the event.", brief="Remove an event from the calendar.")
    async def remove_event(self, ctx, eventID):
        service = create_service()
        CALENDAR_ID = get_calendar()
        event = service.events().get(calendarId=CALENDAR_ID, eventId=eventID).execute()
        title = event["summary"]
        start = event["start"].get("dateTime", event["start"].get("date"))
        end = event["end"].get("dateTime", event["end"].get("date"))

        dateTime = date_conversion(start)
        startTime = time_conversion(start)
        endTime = time_conversion(end)
        
        eventEmbed = Embed(title = "Removing event... Are you sure you want to delete this event?",
                        description = f"**Title:** {title}\n **Date:** {dateTime}\n**Start:** {startTime}\n **End:** {endTime}",
                        colour = 0xFF0000,
                        timestamp=datetime.utcnow())
        eventEmbed.add_field(name="TYPE '1'", value="YES")
        eventEmbed.add_field(name="TYPE '2'", value="NO")
        await ctx.send(embed = eventEmbed)

        try:
            msg = await self.bot.wait_for("message", check=lambda message: message.author == ctx.author, timeout=30)
        except asyncio.TimeoutError:
            await ctx.send(":x: Command has timed out.")
        if msg.content=="1":
            service.events().delete(calendarId=CALENDAR_ID, eventId=eventID).execute()
            await ctx.send(":green_circle:  Event successfully removed.")
        elif msg.content=="2":
            await ctx.send(":red_circle:  Removal of event canceled.")
        else:
            await ctx.send(":x: Invalid choice.")
        
    @command(name="getevent", help="Retrieve event details from the calendar with the ID of the event.", brief="Retrieve event details from the calendar.")
    async def get_event(self, ctx, eventID):
        service = create_service()
        CALENDAR_ID = get_calendar()
        event = service.events().get(calendarId=CALENDAR_ID, eventId=eventID).execute()
        title = event["summary"]
        start = event["start"].get("dateTime", event["start"].get("date"))
        end = event["end"].get("dateTime", event["end"].get("date"))
        description = event["description"]

        dateTime = date_conversion(start)
        startTime = time_conversion(start)
        endTime = time_conversion(end)
        eventEmbed = Embed(title = "Event Retrieved!",
                        description = f"**Title:** {title}\n **Date:** {dateTime}\n**Start:** {startTime}\n **End:** {endTime}\n**Description:** {description}\n **URL:** {event.get('htmlLink')}",
                        colour = CALENDAR_COLOR)
        await ctx.send(embed = eventEmbed)

def setup(bot):
    bot.add_cog(Calendar(bot))
