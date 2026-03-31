import requests
from bs4 import BeautifulSoup
from icalendar import Calendar, Event
from datetime import datetime
import pytz
import hashlib

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

    # 1. ADD SYNC TOKEN (Always keep this so the file isn't empty)
    refresh_event = Event()
    refresh_event.add('summary', '🔄 TSL Calendar Last Synced')
    now = datetime.now(pytz.utc)
    refresh_event.add('dtstart', now)
    refresh_event.add('dtend', now)
    refresh_event.add('uid', 'sync-token-constant@tsl-bot.local')
    cal.add_component(refresh_event)

    # 2. FIND ALL EVENT BLOCKS
    # We look for the date containers you found
    date_containers = soup.find_all('div', class_='event-meta-datetime')
    print(f"Found {len(date_containers)} event date containers.")

    for container in date_containers:
        try:
            # BROAD SEARCH: Look for the nearest Heading (h3 or h2)
            # We go up to the parent container and look for the title there
            parent = container.find_parent('div', class_=lambda x: x and 'event' in x.lower())
            if not parent:
                parent = container.parent.parent # Fallback to higher parent

            # Find the title (usually the first h2, h3, or bold link)
            title_el = parent.find(['h2', 'h3', 'a'], class_=lambda x: x and 'title' in x.lower())
            if not title_el:
                title_el = parent.find(['h2', 'h3']) # If no 'title' class, just take the heading

            if title_el:
                title_text = title_el.text.strip()
                date_text = container.text.strip()

                event = Event()
                event.add('summary', title_text)
                event.add('description', f"Event Details: {date_text}")
                event.add('uid', get_uid(title_text))
                event.add('dtstart', datetime.now(pytz.utc).date()) # All day today
                
                cal.add_component(event)
                print(f"✅ Successfully added: {title_text}")
            else:
                print("⚠️ Found a date but couldn't find a title near it.")

        except Exception as e:
            print(f"❌ Error: {e}")
            continue

    with open('tsl_events.ics', 'wb') as f:
        f.write(cal.to_ical())

if __name__ == "__main__":
    run_sync()
