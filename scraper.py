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
    Cleans '03 - 12 Apr 2026 10:00 am...' into proper start/end dates.
    """
    try:
        # 1. Clean the string: remove times and extra whitespace
        # We split by 'am' or 'pm' and take the first part to get just the date
        clean_str = re.split(r'\d{1,2}:\d{2}', date_str)[0].strip()
        
        # 2. Split into Start and End
        if ' - ' in clean_str:
            parts = clean_str.split(' - ')
            start_raw = parts[0].strip()
            end_raw = parts[1].strip()
            
            # If the end date doesn't have a year (e.g., '12 Apr'), 
            # we borrow the year from the start date or current year
            start_dt = date_parser.parse(start_raw).replace(tzinfo=pytz.timezone("Asia/Singapore"))
            end_dt = date_parser.parse(end_raw, default=start_dt).replace(tzinfo=pytz.timezone("Asia/Singapore"))
        else:
            # Single day event
            start_dt = date_parser.parse(clean_str).replace(tzinfo=pytz.timezone("Asia/Singapore"))
            end_dt = start_dt
            
        return start_dt, end_dt
    except Exception as e:
        print(f"Parsing failed for '{date_str}': {e}")
        # Fallback to today if parsing fails
        today = datetime.now(pytz.utc)
        return today, today

import re # Add this at the top of your file!

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
                # Get the text from the span
                raw_date_text = container.find('span').get_text(separator=" ").strip()
                
                start_dt, end_dt = parse_tsl_date(raw_date_text)

                event = Event()
                event.add('summary', title_text)
                event.add('uid', get_uid(title_text))
                event.add('dtstart', start_dt)
                event.add('dtend', end_dt)
                event.add('description', f"Details: {raw_date_text}\nLink: {title_el.get('href')}")
                
                cal.add_component(event)
                print(f"✅ Map Synced: {title_text} -> {start_dt.strftime('%Y-%m-%d')}")

        except Exception as e:
            continue

    with open('tsl_events.ics', 'wb') as f:
        f.write(cal.to_ical())

if __name__ == "__main__":
    run_sync()
