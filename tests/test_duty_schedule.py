import unittest
from datetime import date, datetime, timedelta
from unittest.mock import patch

from dateutil.rrule import rrulestr

import generate_calendar as calendar
from plugins.daily_life import generate


class DutyScheduleTests(unittest.TestCase):
    def setUp(self):
        self.config = {"duty_schedule": {"start": "2026-10-13", "interval_days": 3}}

    def test_all_day_recurrence_and_dates(self):
        events = generate(self.config)
        self.assertEqual(len(events), 1)
        event = events[0]
        self.assertTrue(event.all_day)
        text = calendar.event_to_ics(event)
        self.assertIn("DTSTART;VALUE=DATE:20261013\r\n", text)
        self.assertIn("DTEND;VALUE=DATE:20261014\r\n", text)
        self.assertIn("RRULE:FREQ=DAILY;INTERVAL=3\r\n", text)
        self.assertNotIn("UNTIL=", text)
        self.assertNotIn("COUNT=", text)
        rule = rrulestr(event.rrule, dtstart=datetime.fromisoformat(event.start))
        expected = [13, 16, 19, 22, 25, 28, 31]
        self.assertEqual([d.day for d in rule[:7]], expected)
        # Cross year, leap day and the existing five-year generation horizon.
        for target in (date(2027, 1, 1), date(2028, 2, 29), date(2035, 1, 1)):
            next_day = rule.after(datetime.combine(target, datetime.min.time()), inc=True).date()
            self.assertLess((next_day - target).days, 3)
            self.assertEqual((next_day - date(2026, 10, 13)).days % 3, 0)

    def test_uid_stays_stable_after_regeneration_and_schedule_edit(self):
        first = generate(self.config)[0]
        second = generate(self.config)[0]
        edited = generate({"duty_schedule": {"start": "2026-10-16", "interval_days": 3}})[0]
        self.assertEqual(calendar.uid(first.uid_seed), calendar.uid(second.uid_seed))
        self.assertEqual(calendar.uid(first.uid_seed), calendar.uid(edited.uid_seed))

    def test_config_enables_exactly_one_duty_event(self):
        self.assertEqual(calendar.CONFIG["enabled_plugins"].count("daily_life"), 1)
        # Keep this test independent of the holiday plugin's remote API.
        with patch.dict(calendar.CONFIG, {"enabled_plugins": ["daily_life"]}):
            events = calendar.load_events()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].start, "2026-10-13")

    def test_missing_schedule_and_invalid_intervals(self):
        self.assertEqual(generate({}), [])
        for interval in (0, -3, 1.5, True, "3"):
            with self.assertRaises(ValueError):
                generate({"duty_schedule": {"start": "2026-10-13", "interval_days": interval}})

    def test_non_recurring_event_is_unchanged(self):
        from plugins.base import CalendarEvent
        event = CalendarEvent(title="既有事件", start="2026-10-13", uid_seed="existing")
        self.assertNotIn("RRULE:", calendar.event_to_ics(event))


if __name__ == "__main__":
    unittest.main()
