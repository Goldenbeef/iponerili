"""Confirmed, privacy-minimal one-off all-day events from mail or user input."""
import json
from datetime import date
from pathlib import Path
from .base import CalendarEvent

DATA = Path(__file__).resolve().parents[1] / 'data' / 'mail_events.json'

def plugin_name():
    return 'mail_events'

def generate(config):
    data = json.loads(DATA.read_text(encoding='utf-8'))
    if data.get('schema_version') != 1:
        raise ValueError('Unsupported mail_events schema')
    events, identities, occurrences = [], set(), set()
    for item in data['events']:
        identity = item['identity']
        if not identity or identity in identities:
            raise ValueError('Duplicate or empty event identity')
        identities.add(identity)
        if item['status'] in ('cancelled', 'pending_confirmation'):
            continue
        if item['status'] != 'confirmed':
            raise ValueError('Unknown event status')
        start = date.fromisoformat(item['date']).isoformat()
        title = item['title'].strip()
        occurrence = (title, start)
        if not title or occurrence in occurrences:
            raise ValueError('Duplicate or empty event')
        occurrences.add(occurrence)
        events.append(CalendarEvent(title=title, start=start, all_day=True,
            description=item.get('description', ''), categories=['个人日程'],
            uid_seed='mail-event:' + identity))
    return events
