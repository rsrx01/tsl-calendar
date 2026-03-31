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

    # 1. ADD SYNC TOKEN
    refresh_event = Event()
    refresh_event.add('summary', '🔄 TSL Calendar Last Synced')
    now = datetime.now(pytz.utc)
    refresh_event.add('dtstart', now)
    refresh_event.add('dtend', now)
    refresh_event.add('uid', 'sync-token-constant@tsl-bot.local')
    cal.add_component(refresh_event)

    # 2. FIND ALL DATE CONTAINERS
    date_containers = soup.find_all('div', class_='event-meta-datetime')
    print(f"Found {len(date_containers)} event date containers.")

    for container in date_containers:
        try:
            # The title 'a' tag you sent is a 'previous sibling' or in a previous div
            # We search backwards from the date to find the nearest 'link-secondary'
            title_el = container.find_previous('a', class_='link-secondary')
            
            if title_el:
                title_text = title_el.text.strip()
                
                # Create the Event
                event = Event()
                event.add('summary', title_text)
                event.add('description', f"Details: {container.text.strip()}\nLink: {title_el.get('href')}")
                event.add('uid', get_uid(title_text))
                
                # Set as All-Day event for today
                event.add('dtstart', datetime.now(pytz.utc).date())
                
                cal.add_component(event)
                print(f"✅ Successfully linked: {title_text}")
            else:
                print("⚠️ Could not find a link-secondary tag near this date.")

        except Exception as e:
            print(f"❌ Error: {e}")
            continue

    # 3. WRITE THE FILE
    with open('tsl_events.ics', 'wb') as f:
        f.write(cal.to_ical())

if __name__ == "__main__":
    run_sync()
