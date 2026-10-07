# Series Scheduling — compute_publish_times

Used by `weekly_series.py` to compute RFC 3339 publish timestamps for 2-part episodes.

## Algorithm

```python
from datetime import datetime, timedelta

def compute_publish_times(now: datetime, force: bool = False):
    if force or now.weekday() != 1:  # not Tuesday → catch-up mode
        p1 = (now + timedelta(days=1)).replace(hour=12, minute=0, second=0, microsecond=0)
        p2 = (now + timedelta(days=2)).replace(hour=12, minute=0, second=0, microsecond=0)
    else:
        p1 = now.replace(hour=12, minute=0, second=0, microsecond=0)
        p2 = (now + timedelta(days=2)).replace(hour=12, minute=0, second=0, microsecond=0)
    return {
        "part1": p1.astimezone().isoformat(timespec="seconds"),
        "part2": p2.astimezone().isoformat(timespec="seconds"),
    }
```

## Account state observed

After 2 successful 2-part series uploads (4 videos total), the channel still returned:
```
HttpError 403 — "The authenticated user doesn't have permissions to upload
and set custom video thumbnails."
```

This error fires on `youtube.thumbnails.set` even when video upload succeeds. It is NOT just a <48h restriction — it persists through early uploads on phone-verified channels. YouTube lifts it automatically after enough upload history.

## Cron configuration

```
0 6 * * 2 cd /root/projets/youtube-automation && /usr/bin/python3 weekly_series.py >> output/cron.log 2>&1
```

- Runs Tuesday 06:00 Switzerland time (Europe/Zurich)
- Part 1 publishes Tuesday 12:00 (4h delay between script gen and publish)
- Part 2 publishes Thursday 12:00
- Logs go to `output/cron.log`
- On catch-up (`--now`): Part 1 next-day 12:00, Part 2 +2 days 12:00

## Verification

After cron runs:
```bash
cat /root/projets/youtube-automation/output/cron.log | tail -20
cat /root/projets/youtube-automation/output/series_state.json
```