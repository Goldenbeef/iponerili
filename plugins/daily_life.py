from datetime import date

from .base import CalendarEvent


def plugin_name():
    return "daily_life"

def generate(config):
    schedule = config.get("duty_schedule")
    if not schedule:
        return []

    start = date.fromisoformat(schedule["start"])
    interval = schedule["interval_days"]
    if type(interval) is not int or interval < 1:
        raise ValueError("duty_schedule.interval_days must be a positive integer")

    return [CalendarEvent(
        title="值班",
        start=start.isoformat(),
        all_day=True,
        description=f"从 {start.isoformat()} 起每 {interval} 天值班一次，全天，长期有效。",
        categories=["值班"],
        uid_seed="daily-life-duty",
        rrule=f"FREQ=DAILY;INTERVAL={interval}",
    )]
