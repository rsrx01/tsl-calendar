import requests
from bs4 import BeautifulSoup
from icalendar import Calendar, Event
from datetime import datetime
import pytz
import hashlib
import re

def get_uid(text):
    return hashlib.md5(text.encode()).hexdigest() + "@tsl-bot.local"

def run_sync():
    url = "https://thesmartlocal.com/event-calendar/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    cal = Calendar()
    cal.add('prodid', '-//TSL Events Scraper//EN')
    cal.add('version', '2.0')
    cal.add('x-wr-calname', 'TheSmartLocal Events')

    # 1. ADD SYNC TOKEN
    refresh_event = Event()
    refresh_event.add('summary', '🔄 TSL Calendar Last Synced')
    now = datetime.now(pytz.utc)
    refresh_event.add('dtstart', now)
    refresh_event.add('dtend', now)
    refresh_event.add('uid', 'sync-token-constant@tsl-bot.local')
    cal.add_component(refresh_event)

    # 2. TARGET THE DATE CONTAINERS YOU FOUND
    # We find all divs with that specific class name
    date_containers = soup.find_all('div', class_='event-meta-datetime')
    print(f"Found {len(date_containers)} event date containers.")

    for container in date_containers:
        try:
            # Move up the tree to find the parent "Card" that holds the Title
            # Usually, the title is in an <h3> nearby
            parent_card = container.find_parent(['div', 'article', 'section'], class_=lambda x: x and 'item' in x.lower() or 'post' in x.lower())
            
            title_el = None
            if parent_card:
                title_el = parent_card.find(['h2', 'h3', 'a'], class_=lambda x: x and 'title' in x.lower())
            
            if not title_el:
                continue

            title = title_el.text.strip()
            date_text = container.find('span').text.strip()
            
            # Create the Event
            event = Event()
            event.add('summary', title)
            event.add('description', f"Dates: {date_text}")
            event.add('uid', get_uid(title))
            
            # Logic: Try to find a year in the text to validate it's a real date
            if "2025" in date_text or "2026" in date_text:
                # For now, keep as 'All Day' today so they appear in your list
                event.add('dtstart', datetime.now(pytz.utc).date())
                cal.add_component(event)
                print(f"✅ Added: {title}")

        except Exception as e:
            print(f"❌ Error parsing: {e}")
            continue

    with open('tsl_events.ics', 'wb') as f:
        f.write(cal.to_ical())

if __name__ == "__main__":
    run_sync()
