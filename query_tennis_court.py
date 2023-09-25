from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
from datetime import datetime, timedelta
import sys


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
def extract_session_info(session):
    time_span = session.find('span', class_='available-booking-slot')
    name_span = session.find('span', class_='cost')

    # Return None for any missing value
    session_time = time_span.text if time_span and time_span.text else "NA"
    session_name = name_span.text if name_span and name_span.text else "NA"
    # print("TTTT")
    # print(time_span)
    # print(time_span.text)
    # print(name_span)
    # print(name_span.text)

    return session_time, session_name

def off_work_hours(input_string: str):
    try:
        # Split the string by '-' to separate the time ranges
        time_ranges = input_string.split('-')

        # Extract the start and end times from the time_ranges list
        start_time_str = time_ranges[0].split('at')[1].strip()
        end_time_str = time_ranges[1].strip()

        # Convert the start and end times to datetime objects
        time_format = '%H:%M'
        start_time = datetime.strptime(start_time_str, time_format)
        end_time = datetime.strptime(end_time_str, time_format)

        # Now, you can compare these datetime objects with the specified target times (10:00 and 18:00)
        target_time1 = datetime.strptime('8:00', time_format)
        target_time2 = datetime.strptime('10:00', time_format)
        
        target_time3 = datetime.strptime('18:00', time_format)
        # target_time4 = datetime.strptime('18:00', time_format)

        if end_time <= target_time2 and start_time >= target_time1:
            return True
        if start_time >= target_time3:
            return True
        else:
            return False

    except ValueError:
        print(f"Time data '{input_string}' does not match format '%H:%M'")


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
        resource_sessions = soup.find_all('div', class_='resource-session')

        # Extract the session names and times
        res = []
        for session in resource_sessions:
            item = extract_session_info(session)
            if item[0] != "NA" and off_work_hours(item[0]) and not is_weekend:
                res.append(item)
            # print(item)
            # break

        print(place)
        print(date)
        print(res)

# Set up the driver (assuming Chrome and chromedriver in this example)
driver = webdriver.Chrome()  # Update the path

if len(sys.argv) > 1:  # Check if arguments are provided
    for i, arg in enumerate(sys.argv[1:], 1):
        if i == 1:
            dates = [arg]
        if i == 2:
            places = [arg]
else:
    dates = generate_dates('2023-09-25', '2023-09-25')

places = ['SouthwarkPark', 'PoplarRecGround', 'BethnalGreenGardens', 'RopemakersFieldLONDON', 'KingEdwardMemorialPark', 'StJohnsParkLondon', 'VictoriaParkLONDON', 'WappingGardens', 'MillfieldsParkMiddlesex', 'LondonFieldsPark', 'SpringHillParkTennis', 'HackneyDowns', 'ClissoldParkHackney', 'BrunswickPark', 'BurgessParkSouthwark', 'TannerStPark']

print(dates)
print(places)
is_weekend = False

for date in dates:
    for place in places:
        find_slots(driver, date, place, is_weekend)
driver.quit()

    
