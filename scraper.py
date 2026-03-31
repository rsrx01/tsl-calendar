import requests
from bs4 import BeautifulSoup
from icalendar import Calendar, Event
from datetime import datetime
import pytz
import hashlib

def get_uid(text):
    # Standardizing the UID so Apple Calendar recognizes the same event tomorrow
    return hashlib.md5(text.encode()).hexdigest() + "@tsl-bot.local"

def run_sync():
    url = "https://thesmartlocal.com/event-calendar/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    cal = Calendar()
    # REQUIRED HEADERS for Apple Calendar/Validator
    cal.add('prodid', '-//TSL Events Scraper//EN')
    cal.add('version', '2.0')
    cal.add('x-wr-calname', 'TheSmartLocal Events')
    cal.add('x-published-ttl', 'PT12H')

    # ADD A "SYNC" EVENT (So the file is never empty)
    refresh_event = Event()
    refresh_event.add('summary', '🔄 TSL Calendar Last Synced')
    now = datetime.now(pytz.utc)
    refresh_event.add('dtstart', now)
    refresh_event.add('dtend', now)
    refresh_event.add('description', f'Last successful scrape at: {datetime.now(pytz.timezone("Asia/Singapore"))}')
    refresh_event.add('uid', 'sync-token-constant@tsl-bot.local')
    cal.add_component(refresh_event)

    # SCRAPE ACTUAL EVENTS
    # Note: If the website structure changes, we update these classes
    events = soup.find_all('div', class_='elementor-post__card')
    print(f"Scraper found {len(events)} events.")

    for item in events:
        try:
            title_el = item.find('h3', class_='elementor-post__title')
            if not title_el: continue
            
            title = title_el.text.strip()
            uid = get_uid(title)
            
            event = Event()
            event.add('summary', title)
            event.add('uid', uid)
            
            # For your Year 2 project, we'll set these as "All Day" events 
            # until you write the logic to parse the specific date strings
            event.add('dtstart', datetime.now(pytz.utc).date())
            
            cal.add_component(event)
        except Exception as e:
            print(f"Error skipping one event: {e}")
            continue

    # WRITE FILE
    with open('tsl_events.ics', 'wb') as f:
        f.write(cal.to_ical())

if __name__ == "__main__":
    run_sync()
