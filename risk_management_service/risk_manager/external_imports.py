"""
Module helper để import các model từ các service khác
"""
import sys
import os
from typing import Optional, Any

def get_sports_data_match():
    """Import Match model từ sports_data_service"""
    try:
        sports_data_path = os.path.join(os.path.dirname(__file__), '../../sports_data_service')
        if sports_data_path not in sys.path:
            sys.path.append(sports_data_path)
        from sports_data.models import Match  # type: ignore
        return Match
    except ImportError:
        return None

def get_betting_models():
    """Import các model từ betting_service"""
    try:
        betting_path = os.path.join(os.path.dirname(__file__), '../../betting_service')
        if betting_path not in sys.path:
            sys.path.append(betting_path)
        from betting.models import BetSelection, BetSlip  # type: ignore
        return BetSelection, BetSlip
    except ImportError:
        return None, None
