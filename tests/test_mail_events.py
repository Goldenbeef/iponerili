import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from plugins import mail_events
from generate_calendar import event_to_ics, uid

class MailEventsTest(unittest.TestCase):
    def test_event_and_idempotence(self):
        first = mail_events.generate({})
        self.assertEqual(first, mail_events.generate({}))
        self.assertEqual(len(first), 1)
        self.assertIn('DTSTART;VALUE=DATE:20270114', event_to_ics(first[0]))
        self.assertIn('DTEND;VALUE=DATE:20270115', event_to_ics(first[0]))
        self.assertNotIn('RRULE:', event_to_ics(first[0]))
        old_uid = uid(first[0].uid_seed)
        data = json.loads(mail_events.DATA.read_text())
        data['events'][0]['date'] = '2027-01-15'
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'events.json'
            p.write_text(json.dumps(data))
            with patch.object(mail_events, 'DATA', p):
                self.assertEqual(old_uid, uid(mail_events.generate({})[0].uid_seed))
                data['events'].append(data['events'][0].copy())
                p.write_text(json.dumps(data))
                with self.assertRaises(ValueError):
                    mail_events.generate({})

if __name__ == '__main__':
    unittest.main()
