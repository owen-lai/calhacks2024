from uagents import Agent, Context, Model
from ics import Calendar
import sys
import os
import base64
import requests
import time
from datetime import datetime, timedelta
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from GmailAPI.getemail import get_latest_email
from GmailAPI.sendemail import gmail_create_draft
from GmailAPI.util import get_service
 
class Message(Model):
   message: str
 
 
InvitationAgent = Agent(
   name="InvitationAgent",
   port=8080,
   seed="InvitationAgent secret phrase",
   endpoint=["http://127.0.0.1:8080/submit"],
)

thread_id, latest_message_id, subject, sender, body, labelIds = get_latest_email()
# print(InvitationAgent.address)
# get service from util.py, user_id="me", message_id from calling get_latest_email()
def is_email_invitation(service, user_id, message_id):
    message = service.users().messages().get(userId=user_id, id=message_id, format='full').execute()
    email_data = message['payload']
    if 'parts' in email_data:
        for part in email_data['parts']:
            if part['filename']:
                attachment_id = part['body']['attachmentId']
                attachment = service.users().messages().attachments().get(userId=user_id, messageId=message_id, id=attachment_id).execute()
                file_data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))
                path = os.path.join("", part['filename'])

                # Save the attachment to the specified directory
                with open(part['filename'], 'wb') as f:
                    f.write(file_data)
                
                #return (f"Attachment {part['filename']} saved to {path}")
                return path
    return part['filename']

def open_and_parse_ics(file_path):
    """
    Open and parse an .ics file using the ics library.

    Args:
    file_path (str): The path to the .ics file.

    Returns:
    None
    """
    with open(file_path, 'r') as f:
        calendar = Calendar(f.read())

        # Print calendar events
        if len(list(calendar.events)) == 1:
            event_name = list(calendar.events)[0].name
            location = list(calendar.events)[0].location
            start_time = list(calendar.events)[0].begin.isoformat()
            end_time = list(calendar.events)[0].end.isoformat()
            return start_time, location
            #for description: event.description
        else: 
            #error out because there should be only one event
            return "There's 0 or more than 1 events"


def get_transport_options(api_key, origin, destination, arrival_time):
    """
    Find transportation options from Location A to Location B using Google Maps Directions API.

    Args:
        api_key (str): Google API key.
        origin (str): Start location (Location A).
        destination (str): End location (Location B).
        arrival_time (int): Arrival time in Unix timestamp.

    Returns:
        dict: Dictionary containing transportation options for each mode of transport.
    """
    base_url = "https://maps.googleapis.com/maps/api/directions/json"
    
    # Modes of transport to check
    transport_modes = ['driving', 'walking', 'bicycling', 'transit']
    transport_options = {}

    # Loop over each mode of transport and make a request
    for mode in transport_modes:
        # Parameters for the API request
        params = {
            "origin": origin,
            "destination": destination,
            "arrival_time": arrival_time,
            "mode": mode,
            "key": api_key
        }
        
        # Send the GET request to the API
        response = requests.get(base_url, params=params)
        
        # Check if the response is successful
        if response.status_code == 200:
            # Parse the JSON response
            directions_data = response.json()
            
            if directions_data['status'] == 'OK':
                # Save the transport option details in the dictionary
                transport_options[mode] = directions_data['routes']
            else:
                print(f"No routes found for mode: {mode}")
        else:
            print(f"Error: {response.status_code}")
    
    return transport_options

def display_transport_options(transport_options, arrival):
    """
    Display the transportation options retrieved from the Google Maps Directions API.

    Args:
        transport_options (dict): Dictionary of transportation options by mode.
        arrival (int): arrival time in unix time
    """
    res = ""
    arrival_time_dt = datetime.utcfromtimestamp(arrival)
    for mode, routes in transport_options.items():
        res += f"\n--- {mode.upper()} TRANSPORT OPTIONS ---"
        for route in routes:
            leg = route['legs'][0]
            distance = leg['distance']['text']
            duration = leg['duration']['text']
            duration_seconds = leg['duration']['value']
            start_address = leg['start_address']
            end_address = leg['end_address']

            if mode == "transit":
                departure_time = leg.get('departure_time', {}).get('text', 'N/A')
                arrival_time = leg.get('arrival_time', {}).get('text', 'N/A')
            else:
                calculated_departure_time = arrival_time_dt - timedelta(seconds=duration_seconds)
                departure_time = calculated_departure_time.strftime("%I:%M %p")
                arrival_time = arrival_time_dt.strftime("%I:%M %p")
        
            res += f"From: {start_address}\n"
            res += f"To: {end_address}\n"
            res += f"Distance: {distance}\n"
            res += f"Duration: {duration}\n"
            res += f"Departure Time: {departure_time}\n"
            res += f"Arrival Time: {arrival_time}\n"
            res += "\nSteps:\n"
                
            for step in leg['steps']:
                travel_mode = step['travel_mode']
                instruction = step['html_instructions']
                step_distance = step['distance']['text']
                res += f"{travel_mode}: {instruction} ({step_distance})\n"
            res += "\n"
    return res


def iso_to_unix(iso_time):
    # Parse the ISO 8601 string into a datetime object
    dt = datetime.fromisoformat(iso_time)
    
    # Convert the datetime object to a Unix timestamp (seconds since epoch)
    unix_timestamp = int(dt.timestamp())
    
    return unix_timestamp

 
@InvitationAgent.on_event("startup")
async def message_handler(ctx: Context):
    path = is_email_invitation(get_service(), 'me', latest_message_id)
    ctx.logger.info(path)
    if path != False:
        ctx.logger.info("path is valid")
        ctx.logger.info(open_and_parse_ics(path))
        start_time, end_location = open_and_parse_ics(path)
        api_key = "AIzaSyCyqDRfZygvU-AWOuvI-RtjM2vxwug3nRU"
        # Locations
        origin = "37.872813212049145, -122.25356288057456"  # Example: San Francisco, CA
        destination = "37.6213,-122.3789"  # Example: San Francisco International Airport, CA
        # Convert desired arrival time to Unix timestamp (seconds since epoch)
        desired_arrival_time = iso_to_unix(start_time)
        # Get transportation options
        transport_options = get_transport_options(api_key, origin, destination, desired_arrival_time)
        # Display transportation options
        if transport_options:
            ctx.logger.info(display_transport_options(transport_options, desired_arrival_time))
        # ctx.logger.info(open_and_parse_ics
        # send the response
        # await ctx.send(sender, Message(message="Cool! Let's get started!"))
 
 
if __name__ == "__main__":
   InvitationAgent.run()