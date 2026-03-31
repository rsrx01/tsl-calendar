import requests
from bs4 import BeautifulSoup
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import pytz
import hashlib

def get_uid(text):
    return hashlib.md5(text.encode()).hexdigest() + "@tsl-bot.local"

def run_sync():
    url = "https://thesmartlocal.com/event-calendar/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    cal = Calendar()
    cal.add('x-wr-calname', 'TheSmartLocal Events')
    cal.add('x-published-ttl', 'PT12H') # Suggests Apple refresh every 12h

    events = soup.find_all('div', class_='elementor-post__card')

    for item in events:
        try:
            title = item.find('h3', class_='elementor-post__title').text.strip()
            # Generate a unique ID based on title so it doesn't duplicate
            uid = get_uid(title)
            
            event = Event()
            event.add('summary', title)
            event.add('uid', uid)
            
            # Placeholder: In a real scenario, you'd parse the actual date from the HTML
            # For now, we set it to tomorrow at 10 AM for testing
            start_time = datetime.now(pytz.timezone('Asia/Singapore')) + timedelta(days=1)
            event.add('dtstart', start_time.replace(hour=10, minute=0))
            event.add('dtend', start_time.replace(hour=12, minute=0))
            
            cal.add_component(event)
        except Exception as e:
            continue

    with open('tsl_events.ics', 'wb') as f:
        f.write(cal.to_ical())

if __name__ == "__main__":
    run_sync()