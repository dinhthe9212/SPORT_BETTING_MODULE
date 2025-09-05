import os
import django
import datetime
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "betting_service.settings")
django.setup()

from betting.models import Match

def update_match_statuses():
    print("Starting match status update...")
    now = timezone.now()

    # Update SCHEDULED to LIVE
    # For simplicity, let's say matches start 5 minutes before their start_time for live status
    # In a real system, this would be triggered by actual match start events from sports data provider
    scheduled_to_live_matches = Match.objects.filter(
        status='SCHEDULED',
        start_time__lte=now + datetime.timedelta(minutes=5) # Matches starting within next 5 mins
    )
    updated_live_count = 0
    for match in scheduled_to_live_matches:
        match.status = 'LIVE'
        match.save()
        updated_live_count += 1
    print(f"Updated {updated_live_count} matches from SCHEDULED to LIVE.")

    # Update LIVE to FINISHED
    # For simplicity, let's say matches finish 100 minutes after their start_time
    # In a real system, this would be triggered by actual match end events
    live_to_finished_matches = Match.objects.filter(
        status='LIVE',
        start_time__lte=now - datetime.timedelta(minutes=100) # Matches that started 100 mins ago
    )
    updated_finished_count = 0
    for match in live_to_finished_matches:
        match.status = 'FINISHED'
        match.save()
        updated_finished_count += 1
    print(f"Updated {updated_finished_count} matches from LIVE to FINISHED.")

    print("Match status update completed.")

if __name__ == "__main__":
    update_match_statuses()


