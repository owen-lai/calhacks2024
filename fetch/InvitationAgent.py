from uagents import Agent, Context, Model
from ics import Calendar
import sys
import os
import pytz
import base64
import requests
import time
import requests
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

thread_id, latest_message_id, subject, sender, body, labelIds, pdfPath, in_reply_to, references = get_latest_email()
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


from datetime import datetime, timedelta
import pytz  # Use for timezone handling

def get_transport_options(api_key, origin, destination, arrival_time, timezone='America/Los_Angeles'):
    """
    Find transportation options from Location A to Location B using Google Maps Directions API.

    Args:
        api_key (str): Google API key.
        origin (str): Start location (Location A).
        destination (str): End location (Location B).
        arrival_time (int): Arrival time in Unix timestamp.
        timezone (str): Timezone for the locations (default is 'America/Los_Angeles').

    Returns:
        dict: Dictionary containing transportation options for each mode of transport.
    """
    base_url = "https://maps.googleapis.com/maps/api/directions/json"
    
    # Modes of transport to check
    transport_modes = ['driving', 'walking', 'bicycling', 'transit']
    transport_options = {}

    # Convert the Unix timestamp into a localized datetime object
    local_tz = pytz.timezone(timezone)
    arrival_time_dt = datetime.fromtimestamp(arrival_time, tz=local_tz)

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

def display_transport_options(transport_options, arrival_time, timezone='America/Los_Angeles'):
    """
    Display the transportation options retrieved from the Google Maps Directions API,
    including calculated departure times for modes other than transit.

    Args:
        transport_options (dict): Dictionary of transportation options by mode.
        arrival_time (int): Desired arrival time in Unix timestamp format.
        timezone (str): Timezone for the locations (default is 'America/Los_Angeles').
    """
    res = ""
    
    # Convert the arrival_time Unix timestamp to a localized datetime object
    local_tz = pytz.timezone(timezone)
    arrival_time_dt = datetime.fromtimestamp(arrival_time, tz=local_tz)  # Convert Unix timestamp to local time
    
    for mode, routes in transport_options.items():
        res += f"\n--- {mode.upper()} TRANSPORT OPTIONS ---"
        for route in routes:
            leg = route['legs'][0]
            distance = leg['distance']['text']
            duration_text = leg['duration']['text']
            duration_seconds = leg['duration']['value']  # Duration in seconds
            start_address = leg['start_address']
            end_address = leg['end_address']

            # Calculate departure time for non-transit modes
            if mode != 'transit':
                calculated_departure_time = arrival_time_dt - timedelta(seconds=duration_seconds)
                departure_time = calculated_departure_time.strftime("%I:%M %p")
                arrival_time_str = arrival_time_dt.strftime("%I:%M %p")
            else:
                # Use provided departure and arrival times for transit mode
                departure_time = leg.get('departure_time', {}).get('text', 'N/A')
                arrival_time_str = leg.get('arrival_time', {}).get('text', 'N/A')

            res += f"From: {start_address}\n"
            res += f"To: {end_address}\n"
            res += f"Distance: {distance}\n"
            res += f"Duration: {duration_text}\n"
            res += f"Departure Time: {departure_time}\n"
            res += f"Arrival Time: {arrival_time_str}\n"
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

def get_user_coordinates():
    """
    Get the user's current coordinates based on their IP address.
    """
    response = requests.get("https://ipinfo.io")
    
    if response.status_code == 200:
        data = response.json()
        location = data.get("loc").split(",")  # "loc" contains the lat and long as "lat,long"
        latitude, longitude = location[0], location[1]
        return str(latitude) + ", " + str(longitude)
    else:
        raise Exception(f"Error: {response.status_code} - Unable to fetch location")

def get_location_coordinates(api_key, location_name):
    
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": location_name,
        "key": api_key
    }
    
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        geocode_data = response.json()
        
        if geocode_data['status'] == 'OK':
            location = geocode_data['results'][0]['geometry']['location']
            latitude, longitude = location['lat'], location['lng']
            return str(latitude) + ", " + str(longitude)
        else:
            raise Exception(f"Geocoding API error: {geocode_data['status']}")
    else:
        raise Exception(f"Error: {response.status_code} - Unable to fetch location data")

 
@InvitationAgent.on_message(model=Message)
async def message_handler(ctx: Context, sender: str, msg: Message):
    path = is_email_invitation(get_service(), 'me', latest_message_id)
    ctx.logger.info(path)
    if path != "":
        ctx.logger.info("path is valid")
        ctx.logger.info(open_and_parse_ics(path))
        start_time, end_location = open_and_parse_ics(path)
        api_key = "AIzaSyCyqDRfZygvU-AWOuvI-RtjM2vxwug3nRU"
        # Locations
        origin = "37.78437260699507, -122.40336710947442" # get_user_coordinates()
        # ctx.logger.info(origin)
        # "37.872813212049145, -122.25356288057456" Example: San Francisco, CA
        destination = get_location_coordinates(api_key, end_location)
        # "37.6213,-122.3789" Example: San Francisco International Airport, CA
        # Convert desired arrival time to Unix timestamp (seconds since epoch)
        desired_arrival_time = iso_to_unix(start_time)
        # Get transportation options
        transport_options = get_transport_options(api_key, origin, destination, desired_arrival_time)
        # Display transportation options
        if transport_options:
            await ctx.send(sender, display_transport_options(transport_options, desired_arrival_time))
            # ctx.logger.info(display_transport_options(transport_options, desired_arrival_time))
 
 
if __name__ == "__main__":
   InvitationAgent.run()