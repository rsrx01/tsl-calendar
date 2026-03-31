import requests
from bs4 import BeautifulSoup
from icalendar import Calendar, Event
from datetime import datetime
import pytz
import hashlib
from dateutil import parser as date_parser

def get_uid(text):
    return hashlib.md5(text.encode()).hexdigest() + "@tsl-bot.local"

def parse_tsl_date(date_str):
    """
    Turns '11 Dec 2025 - 12 Apr 2026' into two datetime objects.
    """
    try:
        # Split the range (e.g., '11 Dec 2025 - 12 Apr 2026')
        parts = date_str.split('-')
        start_raw = parts[0].strip()
        
        # Parse the start date
        start_dt = date_parser.parse(start_raw).replace(tzinfo=pytz.timezone("Asia/Singapore"))
        
        # If there's an end date, parse it; otherwise, make it a 1-day event
        if len(parts) > 1:
            end_dt = date_parser.parse(parts[1].strip()).replace(tzinfo=pytz.timezone("Asia/Singapore"))
        else:
            end_dt = start_dt
            
        return start_dt, end_dt
    except:
        # Fallback to today if parsing fails
        today = datetime.now(pytz.utc)
        return today, today

def run_sync():
    url = "https://thesmartlocal.com/event-calendar/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    cal = Calendar()
    cal.add('prodid', '-//TSL Events Scraper//EN')
    cal.add('version', '2.0')
    cal.add('x-wr-calname', 'TheSmartLocal Events')

    date_containers = soup.find_all('div', class_='event-meta-datetime')

    for container in date_containers:
        try:
            title_el = container.find_previous('a', class_='link-secondary')
            if title_el:
                title_text = title_el.text.strip()
                raw_date_text = container.find('span').text.strip()
                
                # Get the real start and end times!
                start_dt, end_dt = parse_tsl_date(raw_date_text)

                event = Event()
                event.add('summary', title_text)
                event.add('uid', get_uid(title_text))
                event.add('dtstart', start_dt)
                event.add('dtend', end_dt)
                event.add('description', f"Source: {title_el.get('href')}")
                
                cal.add_component(event)
                print(f"✅ Synced: {title_text} for {start_dt.date()}")

        except Exception as e:
            print(f"❌ Date Error: {e}")
            continue

    with open('tsl_events.ics', 'wb') as f:
        f.write(cal.to_ical())

if __name__ == "__main__":
    run_sync()
