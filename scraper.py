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
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    cal = Calendar()
    cal.add('prodid', '-//TSL Events Scraper//EN')
    cal.add('version', '2.0')
    cal.add('x-wr-calname', 'TheSmartLocal Events')

    # SYNC TOKEN
    refresh_event = Event()
    refresh_event.add('summary', '🔄 TSL Calendar Last Synced')
    now = datetime.now(pytz.utc)
    refresh_event.add('dtstart', now)
    refresh_event.add('dtend', now)
    refresh_event.add('uid', 'sync-token-constant@tsl-bot.local')
    cal.add_component(refresh_event)

    # UPDATED SCRAPER LOGIC
    # We target the 'article' tag which is common for Elementor posts
    events = soup.find_all('article') 
    print(f"Found {len(events)} potential event blocks.")

    for item in events:
        try:
            # Look for titles in h3 or h2
            title_el = item.find(['h3', 'h2', 'a'], class_=lambda x: x and 'title' in x.lower())
            if not title_el:
                continue
            
            title = title_el.text.strip()
            
            # Find the date/metadata section
            meta_divs = item.find_all('div', class_=lambda x: x and 'excerpt' in x.lower())
            description = ""
            if meta_divs:
                description = "\n".join([m.text.strip() for m in meta_divs])

            event = Event()
            event.add('summary', title)
            event.add('description', description)
            event.add('uid', get_uid(title))
            
            # Setting to "All Day" for the current day for testing
            event.add('dtstart', datetime.now(pytz.utc).date())
            
            cal.add_component(event)
            print(f"✅ Successfully added: {title}")
            
        except Exception as e:
            print(f"❌ Error parsing event: {e}")
            continue

    with open('tsl_events.ics', 'wb') as f:
        f.write(cal.to_ical())

if __name__ == "__main__":
    run_sync()
