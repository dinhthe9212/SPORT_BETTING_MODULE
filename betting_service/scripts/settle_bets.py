import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "betting_service.settings")
django.setup()

from betting.models import Match, BetSlip

def settle_bets():
    print("Starting bet settlement...")
    finished_matches = Match.objects.filter(status='FINISHED', score_home__isnull=False, score_away__isnull=False)

    for match in finished_matches:
        print(f"Settling bets for match: {match.home_team.name} vs {match.away_team.name}")
        bet_slips_to_settle = BetSlip.objects.filter(selections__odd__match=match, is_settled=False).distinct()

        for bet_slip in bet_slips_to_settle:
            is_won = True
            for selection in bet_slip.selections.all():
                odd = selection.odd
                # This is a simplified logic. Real settlement would be more complex.
                # Example: If outcome is 'Home Win' and home_score > away_score, then won.
                # This needs to be expanded based on actual bet types and outcomes.
                if odd.outcome == 'Home Win':
                    if not (match.score_home > match.score_away):
                        is_won = False
                        break
                elif odd.outcome == 'Away Win':
                    if not (match.score_away > match.score_home):
                        is_won = False
                        break
                elif odd.outcome == 'Draw':
                    if not (match.score_home == match.score_away):
                        is_won = False
                        break
                # Add more conditions for other bet types (e.g., Over/Under, handicaps)

            bet_slip.is_won = is_won
            bet_slip.is_settled = True
            bet_slip.save()

            if is_won:
                print(f"BetSlip #{bet_slip.id} won. Potential payout: {bet_slip.potential_payout}")
                # In a real system, trigger wallet credit here
            else:
                print(f"BetSlip #{bet_slip.id} lost.")

    print("Bet settlement completed.")

if __name__ == "__main__":
    settle_bets()


