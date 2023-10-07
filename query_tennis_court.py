from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
from datetime import datetime, timedelta
import sys
import argparse
import re

TIME_FORMAT = '%H:%M'
WORK_DAY_NO_EARILER_THAN = 8
WORK_DAY_NO_LATER_THAN = 10
WORK_NIGHT_NO_EARILER_THAN = 18
WEEKEND_NO_EARILER_THAN = 9

def generate_dates(start_date, end_date):
    """
    Generate date strings in the format MM-DD for a given date range.

    Args:
    - start_date (str): The start date in the format YYYY-MM-DD.
    - end_date (str): The end date in the format YYYY-MM-DD.

    Returns:
    - List[str]: List of date strings in MM-DD format.
    """
    
    # Convert the string dates to datetime objects
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Generate the date strings
    date_strings = []
    current = start
    while current <= end:
        date_strings.append(current.strftime('%m-%d'))
        current += timedelta(days=1)

    return date_strings

# Function to extract session info
def extract_session_info(time_span):
    session_time = time_span.text if time_span and time_span.text else "NA"
    return session_time

def convert_time_string_to_number(time_string: str) -> int:
    # Parse the string to a datetime object
    time_object = datetime.strptime(time_string, "%H:%M")
    # Convert to decimal number
    return time_object.hour + time_object.minute/60.0

def parse_time(input_string: str) -> int:
    try:
        # Split the string by '-' to separate the time ranges
        time_ranges = input_string.split('-')

        # Extract the start and end times from the time_ranges list
        start_time_str = time_ranges[0].split('at')[1].strip()
        end_time_str = time_ranges[1].strip()

        # Convert the start and end times to datetime objects
        TIME_FORMAT = '%H:%M'
        start_time = convert_time_string_to_number(start_time_str)
        end_time = convert_time_string_to_number(end_time_str)
        return start_time, end_time

    except ValueError:
        print(f"Time data '{input_string}' does not match format '%H:%M'")

def is_weekend_friendly(start_time, end_time):
    

    if start_time <= WEEKEND_NO_EARILER_THAN:
        return False
    return True


def is_workday_friendly(start_time, end_time):
    TIME_FORMAT = '%H:%M'
    at_eighteen = datetime.strptime('18:00', TIME_FORMAT)

    if end_time <= WORK_DAY_NO_LATER_THAN and start_time >= WORK_DAY_NO_EARILER_THAN:
        return True
    if start_time >= WORK_NIGHT_NO_EARILER_THAN:
        return True
    else:
        return False

def print_debug(msg):
    print(f'DEBUG: {msg}')

def merge_time_slots(slots):
    # Sort the slots
    slots.sort()
    
    merged_slots = []
    current_start, current_end = slots[0]
    
    for start, end in slots[1:]:
        if start <= current_end:  # Overlapping
            current_end = max(current_end, end)  # Extend the current interval
        else:  # Non-overlapping
            merged_slots.append((current_start, current_end))
            current_start, current_end = start, end
    
    # Save the last interval
    merged_slots.append((current_start, current_end))
    
    return merged_slots

# def merge_time_slots(slots):
#     print_debug(f'SSSSS: {slots}')
#     # Extract time intervals and sort them
#     time_intervals = sorted([
#         (
#             datetime.strptime(re.search(r"(\d{2}:\d{2})", slot).group(), TIME_FORMAT),
#             datetime.strptime(re.search(r"- (\d{2}:\d{2})", slot).group(1), TIME_FORMAT)
#         )
#         for slot in slots
#     ])
    
#     merged_intervals = []
#     # Initialize with the first interval
#     current_start, current_end = time_intervals[0]
    
#     for start, end in time_intervals[1:]:
#         if start <= current_end:  # Overlapping
#             current_end = max(current_end, end)  # Extend the current interval
#         else:  # Non-overlapping
#             # Save the previous interval and move to the next
#             merged_intervals.append((current_start, current_end))
#             current_start, current_end = start, end
    
#     # Save the last interval
#     merged_intervals.append((current_start, current_end))
    
#     # Convert intervals to desired string format
#     merged_slots = [f"Book at {start.strftime(TIME_FORMAT)} - {end.strftime(TIME_FORMAT)}" for start, end in merged_intervals]
    
#     return merged_slots


def find_slots(driver, date: str, place: str, is_weekend = True):

    # Navigate to the page
    driver.get(f'https://clubspark.lta.org.uk/{place}/Booking/BookByDate#?date=2023-{date}&role=guest')

    try:
        # Wait until a specific element is loaded (you'll need to determine an appropriate element and its identifier)
        element = WebDriverWait(driver, 8).until(
            EC.presence_of_element_located((By.ID, "someElementID"))  # Replace with a suitable selector
        )
    except TimeoutException:
        print(">>>>>>>>>>>>>>>>>>> TIME OUT >>>>>>>>>>>>>>>>>>>")
    finally:
        # Once the page is loaded (or the wait times out), print the page source
        html_content = driver.page_source

        # Parse the HTML content
        soup = BeautifulSoup(html_content, 'lxml')

        # Find all the resource sessions
        resource_sessions = soup.find_all('span', class_='available-booking-slot')

        # Extract the session names and times
        slots = []
        for session in resource_sessions:
            item = extract_session_info(session)

            if item and item != "NA":
                start_time, end_time = parse_time(item)

                if is_weekend:
                    if is_weekend_friendly(start_time, end_time):
                        slots.append((start_time, end_time))
                elif is_workday_friendly(start_time, end_time):
                    slots.append((start_time, end_time))
        print(place)
        print(date)

        if len(slots) > 1:
            merged_slots = merge_time_slots(slots)
            print(merged_slots)
        else:
            print(slots)

# Set up the driver (assuming Chrome and chromedriver in this example)
driver = webdriver.Chrome()  # Update the path

workday_places = ['MillfieldsParkMiddlesex', 'SouthwarkPark', 'BethnalGreenGardens', 'RopemakersFieldLONDON', 'KingEdwardMemorialPark', 'VictoriaParkLONDON', 'WappingGardens', 'LondonFieldsPark', 'HackneyDowns', 'ClissoldParkHackney', 'BurgessParkSouthwark', 'TannerStPark']
weekend_places = ['SouthwarkPark', 'PoplarRecGround', 'BethnalGreenGardens', 'RopemakersFieldLONDON', 'KingEdwardMemorialPark', 'StJohnsParkLondon', 'VictoriaParkLONDON', 'WappingGardens', 'LondonFieldsPark', 'BrunswickPark', 'BurgessParkSouthwark', 'TannerStPark']


parser = argparse.ArgumentParser(description='A simple argparse example.')
parser.add_argument('--places', nargs='*')
parser.add_argument('--start-date')
parser.add_argument('--end-date')
parser.add_argument('--is-weekend')

args = parser.parse_args()

is_weekend = True if args.is_weekend == 'true' else False
places = args.places if args.places else (weekend_places if is_weekend else workday_places)
start_date = args.start_date
end_date = args.end_date

dates = generate_dates(start_date, end_date)
print(f'Is weekend?: {is_weekend}')
print(dates)
print(places)

for date in dates:
    for place in places:
        find_slots(driver, date, place, is_weekend)
driver.quit()

    
