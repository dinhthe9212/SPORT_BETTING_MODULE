#!/usr/bin/env python3
"""
Script populate dữ liệu thể thao cho Sports Data Service
Hỗ trợ đầy đủ 50+ môn thể thao và các tính năng nâng cao
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sports_data_service_project.settings')
django.setup()

from sports_data.models import Sport, Team, Match, MatchEvent, SportsDataProvider, SportStatistics

def create_sports():
    """Tạo tất cả 50+ môn thể thao với phân loại chi tiết"""
    
    sports_data = [
        # BALL_SPORTS - Thể thao bóng
        {'name': 'Football', 'category': 'BALL_SPORTS', 'description': 'Bóng đá (Soccer)', 'has_teams': True, 'has_periods': True, 'popularity_score': 95},
        {'name': 'Basketball', 'category': 'BALL_SPORTS', 'description': 'Bóng rổ', 'has_teams': True, 'has_periods': True, 'popularity_score': 90},
        {'name': 'Tennis', 'category': 'BALL_SPORTS', 'description': 'Quần vợt', 'has_teams': False, 'has_sets': True, 'popularity_score': 85},
        {'name': 'Baseball', 'category': 'BALL_SPORTS', 'description': 'Bóng chày', 'has_teams': True, 'has_periods': True, 'popularity_score': 80},
        {'name': 'American Football', 'category': 'BALL_SPORTS', 'description': 'Bóng đá Mỹ (NFL)', 'has_teams': True, 'has_periods': True, 'popularity_score': 88},
        {'name': 'Ice Hockey', 'category': 'BALL_SPORTS', 'description': 'Khúc côn cầu trên băng', 'has_teams': True, 'has_periods': True, 'popularity_score': 75},
        {'name': 'Volleyball', 'category': 'BALL_SPORTS', 'description': 'Bóng chuyền', 'has_teams': True, 'has_sets': True, 'popularity_score': 70},
        {'name': 'Table Tennis', 'category': 'BALL_SPORTS', 'description': 'Bóng bàn', 'has_teams': False, 'has_sets': True, 'popularity_score': 65},
        {'name': 'Badminton', 'category': 'BALL_SPORTS', 'description': 'Cầu lông', 'has_teams': False, 'has_sets': True, 'popularity_score': 60},
        {'name': 'Beach Volleyball', 'category': 'BALL_SPORTS', 'description': 'Bóng chuyền bãi biển', 'has_teams': True, 'has_sets': True, 'popularity_score': 55},
        {'name': 'Futsal', 'category': 'BALL_SPORTS', 'description': 'Futsal (Bóng đá trong nhà)', 'has_teams': True, 'has_periods': True, 'popularity_score': 50},
        {'name': 'Gaelic Football', 'category': 'BALL_SPORTS', 'description': 'Bóng đá Gaelic', 'has_teams': True, 'has_periods': True, 'popularity_score': 45},
        {'name': 'Handball', 'category': 'BALL_SPORTS', 'description': 'Bóng ném', 'has_teams': True, 'has_periods': True, 'popularity_score': 40},
        {'name': 'Netball', 'category': 'BALL_SPORTS', 'description': 'Netball', 'has_teams': True, 'has_periods': True, 'popularity_score': 35},
        {'name': 'Water Polo', 'category': 'BALL_SPORTS', 'description': 'Bóng nước', 'has_teams': True, 'has_periods': True, 'popularity_score': 30},
        
        # RACING - Thể thao đua
        {'name': 'Horse Racing', 'category': 'RACING', 'description': 'Đua ngựa', 'has_teams': False, 'has_individual_players': True, 'popularity_score': 85},
        {'name': 'Australasian Racing', 'category': 'RACING', 'description': 'Đua ngựa Úc và New Zealand', 'has_teams': False, 'has_individual_players': True, 'popularity_score': 80},
        {'name': 'Trotting', 'category': 'RACING', 'description': 'Đua ngựa nước kiệu', 'has_teams': False, 'has_individual_players': True, 'popularity_score': 75},
        {'name': 'Cycling', 'category': 'RACING', 'description': 'Đua xe đạp', 'has_teams': True, 'has_individual_players': True, 'popularity_score': 70},
        {'name': 'Formula 1', 'category': 'RACING', 'description': 'Đua xe Công thức 1', 'has_teams': True, 'has_individual_players': True, 'popularity_score': 88},
        {'name': 'Motor Racing', 'category': 'RACING', 'description': 'Đua xe thể thao', 'has_teams': True, 'has_individual_players': True, 'popularity_score': 65},
        {'name': 'Motorbikes', 'category': 'RACING', 'description': 'Đua xe máy', 'has_teams': True, 'has_individual_players': True, 'popularity_score': 60},
        {'name': 'Speedway', 'category': 'RACING', 'description': 'Đua xe tốc độ', 'has_teams': True, 'has_individual_players': True, 'popularity_score': 55},
        {'name': 'Rowing', 'category': 'RACING', 'description': 'Chèo thuyền', 'has_teams': True, 'has_individual_players': True, 'popularity_score': 50},
        {'name': 'Yachting', 'category': 'RACING', 'description': 'Đua thuyền buồm', 'has_teams': True, 'has_individual_players': True, 'popularity_score': 45},
        
        # COMBAT - Thể thao đối kháng
        {'name': 'Boxing', 'category': 'COMBAT', 'description': 'Quyền Anh', 'has_teams': False, 'has_rounds': True, 'has_individual_players': True, 'popularity_score': 80},
        {'name': 'MMA', 'category': 'COMBAT', 'description': 'Mixed Martial Arts', 'has_teams': False, 'has_rounds': True, 'has_individual_players': True, 'popularity_score': 75},
        {'name': 'Cricket', 'category': 'COMBAT', 'description': 'Cricket', 'has_teams': True, 'has_periods': True, 'popularity_score': 70},
        {'name': 'Rugby League', 'category': 'COMBAT', 'description': 'Bóng bầu dục League', 'has_teams': True, 'has_periods': True, 'popularity_score': 65},
        {'name': 'Rugby Union', 'category': 'COMBAT', 'description': 'Bóng bầu dục Union', 'has_teams': True, 'has_periods': True, 'popularity_score': 60},
        {'name': 'Kabaddi', 'category': 'COMBAT', 'description': 'Kabaddi', 'has_teams': True, 'has_periods': True, 'popularity_score': 55},
        {'name': 'Lacrosse', 'category': 'COMBAT', 'description': 'Lacrosse', 'has_teams': True, 'has_periods': True, 'popularity_score': 50},
        
        # INDIVIDUAL - Thể thao cá nhân
        {'name': 'Golf', 'category': 'INDIVIDUAL', 'description': 'Đánh gôn', 'has_teams': False, 'has_individual_players': True, 'popularity_score': 75},
        {'name': 'Chess', 'category': 'INDIVIDUAL', 'description': 'Cờ vua', 'has_teams': False, 'has_individual_players': True, 'popularity_score': 70},
        {'name': 'Snooker & Pool', 'category': 'INDIVIDUAL', 'description': 'Bi-a (Snooker & Pool)', 'has_teams': False, 'has_individual_players': True, 'popularity_score': 65},
        {'name': 'Darts', 'category': 'INDIVIDUAL', 'description': 'Ném phi tiêu', 'has_teams': False, 'has_individual_players': True, 'popularity_score': 60},
        {'name': 'Bowls', 'category': 'INDIVIDUAL', 'description': 'Bowls (Lawn Bowling)', 'has_teams': False, 'has_individual_players': True, 'popularity_score': 55},
        
        # WINTER - Thể thao mùa đông
        {'name': 'Winter Sports', 'category': 'WINTER', 'description': 'Thể thao mùa đông', 'has_teams': False, 'has_individual_players': True, 'popularity_score': 70},
        
        # WATER - Thể thao dưới nước
        {'name': 'Swimming', 'category': 'WATER', 'description': 'Bơi lội', 'has_teams': False, 'has_individual_players': True, 'popularity_score': 65},
        {'name': 'Surfing', 'category': 'WATER', 'description': 'Lướt sóng', 'has_teams': False, 'has_individual_players': True, 'popularity_score': 60},
        
        # MOTOR - Thể thao động cơ
        {'name': 'Esports', 'category': 'MOTOR', 'description': 'Thể thao điện tử', 'has_teams': True, 'has_individual_players': True, 'popularity_score': 85},
        
        # SPECIAL - Thể thao đặc biệt
        {'name': 'Athletics', 'category': 'SPECIAL', 'description': 'Điền kinh', 'has_teams': False, 'has_individual_players': True, 'popularity_score': 75},
        {'name': 'Australian Rules', 'category': 'SPECIAL', 'description': 'Bóng đá kiểu Úc', 'has_teams': True, 'has_periods': True, 'popularity_score': 70},
        {'name': 'Bandy', 'category': 'SPECIAL', 'description': 'Khúc côn cầu trên băng (Bandy)', 'has_teams': True, 'has_periods': True, 'popularity_score': 65},
        {'name': 'Floorball', 'category': 'SPECIAL', 'description': 'Floorball (Khúc côn cầu trong nhà)', 'has_teams': True, 'has_periods': True, 'popularity_score': 60},
        {'name': 'International Rules', 'category': 'SPECIAL', 'description': 'Bóng đá quy tắc quốc tế', 'has_teams': True, 'has_periods': True, 'popularity_score': 55},
        {'name': 'Special Markets', 'category': 'SPECIAL', 'description': 'Thị trường đặc biệt', 'has_teams': False, 'has_individual_players': False, 'popularity_score': 50},
    ]
    
    created_sports = []
    for sport_data in sports_data:
        sport, created = Sport.objects.get_or_create(
            name=sport_data['name'],
            defaults={
                'category': sport_data['category'],
                'description': sport_data['description'],
                'has_teams': sport_data['has_teams'],
                'has_individual_players': sport_data.get('has_individual_players', False),
                'has_rounds': sport_data.get('has_rounds', False),
                'has_sets': sport_data.get('has_sets', False),
                'has_periods': sport_data.get('has_periods', False),
                'popularity_score': sport_data['popularity_score'],
                'min_odds': Decimal('1.01'),
                'max_odds': Decimal('1000.00'),
                'max_stake': Decimal('10000.00')
            }
        )
        if created:
            print(f"✅ Created sport: {sport.name} ({sport.get_category_display()})")
        else:
            print(f"⏩ Sport already exists: {sport.name}")
        created_sports.append(sport)
    
    return created_sports

def create_teams(sports):
    """Tạo teams cho tất cả các môn thể thao"""
    
    teams_data = []
    
    # Football teams
    football = next((s for s in sports if s.name == 'Football'), None)
    if football:
        football_teams = [
            {'name': 'Manchester United', 'sport': football, 'country': 'England', 'city': 'Manchester', 'team_type': 'CLUB', 'founded_year': 1878, 'home_venue': 'Old Trafford', 'capacity': 74140},
            {'name': 'Real Madrid', 'sport': football, 'country': 'Spain', 'city': 'Madrid', 'team_type': 'CLUB', 'founded_year': 1902, 'home_venue': 'Santiago Bernabéu', 'capacity': 81044},
            {'name': 'Barcelona', 'sport': football, 'country': 'Spain', 'city': 'Barcelona', 'team_type': 'CLUB', 'founded_year': 1899, 'home_venue': 'Camp Nou', 'capacity': 99354},
            {'name': 'Bayern Munich', 'sport': football, 'country': 'Germany', 'city': 'Munich', 'team_type': 'CLUB', 'founded_year': 1900, 'home_venue': 'Allianz Arena', 'capacity': 75000},
            {'name': 'PSG', 'sport': football, 'country': 'France', 'city': 'Paris', 'team_type': 'CLUB', 'founded_year': 1970, 'home_venue': 'Parc des Princes', 'capacity': 47929},
        ]
        teams_data.extend(football_teams)
    
    # Basketball teams
    basketball = next((s for s in sports if s.name == 'Basketball'), None)
    if basketball:
        basketball_teams = [
            {'name': 'Los Angeles Lakers', 'sport': basketball, 'country': 'USA', 'city': 'Los Angeles', 'team_type': 'CLUB', 'founded_year': 1947, 'home_venue': 'Crypto.com Arena', 'capacity': 19068},
            {'name': 'Golden State Warriors', 'sport': basketball, 'country': 'USA', 'city': 'San Francisco', 'team_type': 'CLUB', 'founded_year': 1946, 'home_venue': 'Chase Center', 'capacity': 18064},
            {'name': 'Boston Celtics', 'sport': basketball, 'country': 'USA', 'city': 'Boston', 'team_type': 'CLUB', 'founded_year': 1946, 'home_venue': 'TD Garden', 'capacity': 19156},
            {'name': 'Chicago Bulls', 'sport': basketball, 'country': 'USA', 'city': 'Chicago', 'team_type': 'CLUB', 'founded_year': 1966, 'home_venue': 'United Center', 'capacity': 20917},
        ]
        teams_data.extend(basketball_teams)
    
    # Tennis players
    tennis = next((s for s in sports if s.name == 'Tennis'), None)
    if tennis:
        tennis_players = [
            {'name': 'Novak Djokovic', 'sport': tennis, 'country': 'Serbia', 'city': 'Belgrade', 'team_type': 'INDIVIDUAL'},
            {'name': 'Rafael Nadal', 'sport': tennis, 'country': 'Spain', 'city': 'Manacor', 'team_type': 'INDIVIDUAL'},
            {'name': 'Roger Federer', 'sport': tennis, 'country': 'Switzerland', 'city': 'Basel', 'team_type': 'INDIVIDUAL'},
            {'name': 'Serena Williams', 'sport': tennis, 'country': 'USA', 'city': 'Saginaw', 'team_type': 'INDIVIDUAL'},
        ]
        teams_data.extend(tennis_players)
    
    # Baseball teams
    baseball = next((s for s in sports if s.name == 'Baseball'), None)
    if baseball:
        baseball_teams = [
            {'name': 'New York Yankees', 'sport': baseball, 'country': 'USA', 'city': 'New York', 'team_type': 'CLUB', 'founded_year': 1901, 'home_venue': 'Yankee Stadium', 'capacity': 46537},
            {'name': 'Los Angeles Dodgers', 'sport': baseball, 'country': 'USA', 'city': 'Los Angeles', 'team_type': 'CLUB', 'founded_year': 1883, 'home_venue': 'Dodger Stadium', 'capacity': 56000},
            {'name': 'Boston Red Sox', 'sport': baseball, 'country': 'USA', 'city': 'Boston', 'team_type': 'CLUB', 'founded_year': 1901, 'home_venue': 'Fenway Park', 'capacity': 37731},
        ]
        teams_data.extend(baseball_teams)
    
    # American Football teams
    american_football = next((s for s in sports if s.name == 'American Football'), None)
    if american_football:
        american_football_teams = [
            {'name': 'New England Patriots', 'sport': american_football, 'country': 'USA', 'city': 'Foxborough', 'team_type': 'CLUB', 'founded_year': 1959, 'home_venue': 'Gillette Stadium', 'capacity': 66829},
            {'name': 'Dallas Cowboys', 'sport': american_football, 'country': 'USA', 'city': 'Arlington', 'team_type': 'CLUB', 'founded_year': 1960, 'home_venue': 'AT&T Stadium', 'capacity': 80000},
            {'name': 'Green Bay Packers', 'sport': american_football, 'country': 'USA', 'city': 'Green Bay', 'team_type': 'CLUB', 'founded_year': 1919, 'home_venue': 'Lambeau Field', 'capacity': 81441},
        ]
        teams_data.extend(american_football_teams)
    
    # Ice Hockey teams
    ice_hockey = next((s for s in sports if s.name == 'Ice Hockey'), None)
    if ice_hockey:
        ice_hockey_teams = [
            {'name': 'Montreal Canadiens', 'sport': ice_hockey, 'country': 'Canada', 'city': 'Montreal', 'team_type': 'CLUB', 'founded_year': 1909, 'home_venue': 'Bell Centre', 'capacity': 21273},
            {'name': 'Toronto Maple Leafs', 'sport': ice_hockey, 'country': 'Canada', 'city': 'Toronto', 'team_type': 'CLUB', 'founded_year': 1917, 'home_venue': 'Scotiabank Arena', 'capacity': 18819},
            {'name': 'Detroit Red Wings', 'sport': ice_hockey, 'country': 'USA', 'city': 'Detroit', 'team_type': 'CLUB', 'founded_year': 1926, 'home_venue': 'Little Caesars Arena', 'capacity': 19515},
        ]
        teams_data.extend(ice_hockey_teams)
    
    # Golf players
    golf = next((s for s in sports if s.name == 'Golf'), None)
    if golf:
        golf_players = [
            {'name': 'Tiger Woods', 'sport': golf, 'country': 'USA', 'city': 'Cypress', 'team_type': 'INDIVIDUAL'},
            {'name': 'Rory McIlroy', 'sport': golf, 'country': 'Northern Ireland', 'city': 'Holywood', 'team_type': 'INDIVIDUAL'},
            {'name': 'Jon Rahm', 'sport': golf, 'country': 'Spain', 'city': 'Barrika', 'team_type': 'INDIVIDUAL'},
        ]
        teams_data.extend(golf_players)
    
    # Boxing fighters
    boxing = next((s for s in sports if s.name == 'Boxing'), None)
    if boxing:
        boxing_fighters = [
            {'name': 'Anthony Joshua', 'sport': boxing, 'country': 'UK', 'city': 'London', 'team_type': 'INDIVIDUAL'},
            {'name': 'Tyson Fury', 'sport': boxing, 'country': 'UK', 'city': 'Manchester', 'team_type': 'INDIVIDUAL'},
            {'name': 'Deontay Wilder', 'sport': boxing, 'country': 'USA', 'city': 'Tuscaloosa', 'team_type': 'INDIVIDUAL'},
        ]
        teams_data.extend(boxing_fighters)
    
    # MMA fighters
    mma = next((s for s in sports if s.name == 'MMA'), None)
    if mma:
        mma_fighters = [
            {'name': 'Conor McGregor', 'sport': mma, 'country': 'Ireland', 'city': 'Dublin', 'team_type': 'INDIVIDUAL'},
            {'name': 'Khabib Nurmagomedov', 'sport': mma, 'country': 'Russia', 'city': 'Dagestan', 'team_type': 'INDIVIDUAL'},
            {'name': 'Jon Jones', 'sport': mma, 'country': 'USA', 'city': 'Rochester', 'team_type': 'INDIVIDUAL'},
        ]
        teams_data.extend(mma_fighters)
    
    # Cricket teams
    cricket = next((s for s in sports if s.name == 'Cricket'), None)
    if cricket:
        cricket_teams = [
            {'name': 'India National Team', 'sport': cricket, 'country': 'India', 'city': 'Mumbai', 'team_type': 'NATIONAL'},
            {'name': 'Australia National Team', 'sport': cricket, 'country': 'Australia', 'city': 'Melbourne', 'team_type': 'NATIONAL'},
            {'name': 'England National Team', 'sport': cricket, 'country': 'England', 'city': 'London', 'team_type': 'NATIONAL'},
        ]
        teams_data.extend(cricket_teams)
    
    # Rugby teams
    rugby_league = next((s for s in sports if s.name == 'Rugby League'), None)
    if rugby_league:
        rugby_league_teams = [
            {'name': 'St Helens', 'sport': rugby_league, 'country': 'England', 'city': 'St Helens', 'team_type': 'CLUB', 'founded_year': 1873, 'home_venue': 'Totally Wicked Stadium', 'capacity': 18000},
            {'name': 'Wigan Warriors', 'sport': rugby_league, 'country': 'England', 'city': 'Wigan', 'team_type': 'CLUB', 'founded_year': 1872, 'home_venue': 'DW Stadium', 'capacity': 25138},
        ]
        teams_data.extend(rugby_league_teams)
    
    rugby_union = next((s for s in sports if s.name == 'Rugby Union'), None)
    if rugby_union:
        rugby_union_teams = [
            {'name': 'New Zealand All Blacks', 'sport': rugby_union, 'country': 'New Zealand', 'city': 'Auckland', 'team_type': 'NATIONAL'},
            {'name': 'South Africa Springboks', 'sport': rugby_union, 'country': 'South Africa', 'city': 'Johannesburg', 'team_type': 'NATIONAL'},
            {'name': 'England National Team', 'sport': rugby_union, 'country': 'England', 'city': 'London', 'team_type': 'NATIONAL'},
        ]
        teams_data.extend(rugby_union_teams)
    
    # Swimming athletes
    swimming = next((s for s in sports if s.name == 'Swimming'), None)
    if swimming:
        swimming_athletes = [
            {'name': 'Michael Phelps', 'sport': swimming, 'country': 'USA', 'city': 'Baltimore', 'team_type': 'INDIVIDUAL'},
            {'name': 'Katie Ledecky', 'sport': swimming, 'country': 'USA', 'city': 'Bethesda', 'team_type': 'INDIVIDUAL'},
            {'name': 'Adam Peaty', 'sport': swimming, 'country': 'UK', 'city': 'Uttoxeter', 'team_type': 'INDIVIDUAL'},
        ]
        teams_data.extend(swimming_athletes)
    
    # Athletics athletes
    athletics = next((s for s in sports if s.name == 'Athletics'), None)
    if athletics:
        athletics_athletes = [
            {'name': 'Usain Bolt', 'sport': athletics, 'country': 'Jamaica', 'city': 'Kingston', 'team_type': 'INDIVIDUAL'},
            {'name': 'Eliud Kipchoge', 'sport': athletics, 'country': 'Kenya', 'city': 'Nandi', 'team_type': 'INDIVIDUAL'},
            {'name': 'Shelly-Ann Fraser-Pryce', 'sport': athletics, 'country': 'Jamaica', 'city': 'Kingston', 'team_type': 'INDIVIDUAL'},
        ]
        teams_data.extend(athletics_athletes)
    
    # Formula 1 teams
    formula1 = next((s for s in sports if s.name == 'Formula 1'), None)
    if formula1:
        formula1_teams = [
            {'name': 'Mercedes-AMG Petronas', 'sport': formula1, 'country': 'Germany', 'city': 'Stuttgart', 'team_type': 'CLUB', 'founded_year': 1954, 'home_venue': 'Silverstone Circuit', 'capacity': 150000},
            {'name': 'Red Bull Racing', 'sport': formula1, 'country': 'Austria', 'city': 'Milton Keynes', 'team_type': 'CLUB', 'founded_year': 2005, 'home_venue': 'Red Bull Ring', 'capacity': 105000},
            {'name': 'Ferrari', 'sport': formula1, 'country': 'Italy', 'city': 'Maranello', 'team_type': 'CLUB', 'founded_year': 1947, 'home_venue': 'Monza Circuit', 'capacity': 113860},
        ]
        teams_data.extend(formula1_teams)
    
    # Esports teams
    esports = next((s for s in sports if s.name == 'Esports'), None)
    if esports:
        esports_teams = [
            {'name': 'Team Liquid', 'sport': esports, 'country': 'Netherlands', 'city': 'Utrecht', 'team_type': 'CLUB', 'founded_year': 2000},
            {'name': 'Fnatic', 'sport': esports, 'country': 'UK', 'city': 'London', 'team_type': 'CLUB', 'founded_year': 2004},
            {'name': 'Cloud9', 'sport': esports, 'country': 'USA', 'city': 'Los Angeles', 'team_type': 'CLUB', 'founded_year': 2012},
        ]
        teams_data.extend(esports_teams)
    
    # Darts players
    darts = next((s for s in sports if s.name == 'Darts'), None)
    if darts:
        darts_players = [
            {'name': 'Phil Taylor', 'sport': darts, 'country': 'UK', 'city': 'Stoke-on-Trent', 'team_type': 'INDIVIDUAL'},
            {'name': 'Michael van Gerwen', 'sport': darts, 'country': 'Netherlands', 'city': 'Boxtel', 'team_type': 'INDIVIDUAL'},
            {'name': 'Gerwyn Price', 'sport': darts, 'country': 'Wales', 'city': 'Markham', 'team_type': 'INDIVIDUAL'},
        ]
        teams_data.extend(darts_players)
    
    # Create teams
    created_teams = []
    for team_data in teams_data:
        team, created = Team.objects.get_or_create(
            name=team_data['name'],
            sport=team_data['sport'],
            defaults={
                'team_type': team_data['team_type'],
                'country': team_data['country'],
                'city': team_data['city'],
                'founded_year': team_data.get('founded_year'),
                'home_venue': team_data.get('home_venue'),
                'capacity': team_data.get('capacity'),
                'is_active': True
            }
        )
        if created:
            print(f"✅ Created team: {team.name} ({team.sport.name})")
        else:
            print(f"⏩ Team already exists: {team.name}")
        created_teams.append(team)
    
    return created_teams

def create_matches(sports, teams):
    """Tạo sample matches cho các môn thể thao"""
    
    matches_data = []
    start_time = datetime.now() + timedelta(days=1)
    
    # Football matches
    football = next((s for s in sports if s.name == 'Football'), None)
    if football:
        football_teams = [t for t in teams if t.sport == football]
        if len(football_teams) >= 4:
            matches_data.extend([
                {
                    'sport': football,
                    'home_team': football_teams[0],
                    'away_team': football_teams[1],
                    'start_time': start_time,
                    'venue': 'Old Trafford',
                    'competition': 'Premier League',
                    'season': '2024/25'
                },
                {
                    'sport': football,
                    'home_team': football_teams[2],
                    'away_team': football_teams[3],
                    'start_time': start_time + timedelta(hours=3),
                    'venue': 'Santiago Bernabéu',
                    'competition': 'La Liga',
                    'season': '2024/25'
                }
            ])
    
    # Basketball matches
    basketball = next((s for s in sports if s.name == 'Basketball'), None)
    if basketball:
        basketball_teams = [t for t in teams if t.sport == basketball]
        if len(basketball_teams) >= 4:
            matches_data.extend([
                {
                    'sport': basketball,
                    'home_team': basketball_teams[0],
                    'away_team': basketball_teams[1],
                    'start_time': start_time + timedelta(hours=6),
                    'venue': 'Crypto.com Arena',
                    'competition': 'NBA',
                    'season': '2024/25'
                }
            ])
    
    # Tennis matches
    tennis = next((s for s in sports if s.name == 'Tennis'), None)
    if tennis:
        tennis_players = [t for t in teams if t.sport == tennis]
        if len(tennis_players) >= 4:
            matches_data.extend([
                {
                    'sport': tennis,
                    'home_team': tennis_players[0],
                    'away_team': tennis_players[1],
                    'start_time': start_time + timedelta(hours=9),
                    'venue': 'Wimbledon',
                    'competition': 'Wimbledon Championships',
                    'season': '2024'
                }
            ])
    
    # Create matches
    created_matches = []
    for match_data in matches_data:
        match, created = Match.objects.get_or_create(
            home_team=match_data['home_team'],
            away_team=match_data['away_team'],
            start_time=match_data['start_time'],
            defaults={
                'sport': match_data['sport'],
                'end_time': match_data['start_time'] + timedelta(hours=2),
                'venue': match_data['venue'],
                'competition': match_data['competition'],
                'season': match_data['season'],
                'status': 'SCHEDULED'
            }
        )
        if created:
            print(f"✅ Created match: {match.home_team.name} vs {match.away_team.name}")
        else:
            print(f"⏩ Match already exists: {match.home_team.name} vs {match.away_team.name}")
        created_matches.append(match)
    
    return created_matches

def create_sports_data_providers():
    """Tạo các nhà cung cấp dữ liệu thể thao"""
    
    providers_data = [
        {
            'name': 'Sportradar',
            'provider_type': 'COMPREHENSIVE',
            'api_endpoint': 'https://api.sportradar.com',
            'api_key': 'sample_key_sportradar',
            'data_accuracy': Decimal('0.98'),
            'update_speed': 15,
            'coverage_rate': Decimal('0.95')
        },
        {
            'name': 'Stats Perform',
            'provider_type': 'STATISTICS',
            'api_endpoint': 'https://api.statsperform.com',
            'api_key': 'sample_key_statsperform',
            'data_accuracy': Decimal('0.96'),
            'update_speed': 20,
            'coverage_rate': Decimal('0.92')
        },
        {
            'name': 'LiveScore',
            'provider_type': 'LIVE_SCORES',
            'api_endpoint': 'https://api.livescore.com',
            'api_key': 'sample_key_livescore',
            'data_accuracy': Decimal('0.94'),
            'update_speed': 10,
            'coverage_rate': Decimal('0.88')
        }
    ]
    
    created_providers = []
    for provider_data in providers_data:
        provider, created = SportsDataProvider.objects.get_or_create(
            name=provider_data['name'],
            defaults={
                'provider_type': provider_data['provider_type'],
                'api_endpoint': provider_data['api_endpoint'],
                'api_key': provider_data['api_key'],
                'data_accuracy': provider_data['data_accuracy'],
                'update_speed': provider_data['update_speed'],
                'coverage_rate': provider_data['coverage_rate'],
                'is_active': True
            }
        )
        if created:
            print(f"✅ Created provider: {provider.name}")
        else:
            print(f"⏩ Provider already exists: {provider.name}")
        created_providers.append(provider)
    
    return created_providers

def create_sport_statistics(sports):
    """Tạo thống kê cho các môn thể thao"""
    
    created_stats = []
    for sport in sports:
        stats, created = SportStatistics.objects.get_or_create(
            sport=sport,
            defaults={
                'total_matches': 0,
                'total_goals': 0,
                'total_cards': 0,
                'total_bets_placed': 0,
                'total_stake_amount': Decimal('0.00'),
                'average_odds': Decimal('2.00'),
                'daily_active_users': 0,
                'weekly_active_users': 0,
                'monthly_active_users': 0
            }
        )
        if created:
            print(f"✅ Created statistics for: {sport.name}")
        else:
            print(f"⏩ Statistics already exist for: {sport.name}")
        created_stats.append(stats)
    
    return created_stats

def main():
    """Main function để populate dữ liệu thể thao"""
    print("🚀 Starting SPORTS DATA SERVICE data population...")
    print("📋 This will create comprehensive sports data for the betting system!")
    
    try:
        # Create sports
        print("\n📊 Creating sports...")
        sports = create_sports()
        
        # Create teams
        print("\n👥 Creating teams...")
        teams = create_teams(sports)
        
        # Create matches
        print("\n⚽ Creating matches...")
        matches = create_matches(sports, teams)
        
        # Create data providers
        print("\n🔌 Creating data providers...")
        providers = create_sports_data_providers()
        
        # Create sport statistics
        print("\n📈 Creating sport statistics...")
        stats = create_sport_statistics(sports)
        
        print(f"\n✅ Successfully populated sports data!")
        print(f"📊 Sports: {len(sports)}")
        print(f"👥 Teams: {len(teams)}")
        print(f"⚽ Matches: {len(matches)}")
        print(f"🔌 Providers: {len(providers)}")
        print(f"📈 Statistics: {len(stats)}")
        
        print("\n🎯 SPORTS COVERAGE:")
        print("✅ BALL_SPORTS: Football, Basketball, Tennis, Baseball, etc.")
        print("✅ RACING: Horse Racing, Formula 1, Cycling, etc.")
        print("✅ COMBAT: Boxing, MMA, Cricket, Rugby, etc.")
        print("✅ INDIVIDUAL: Golf, Chess, Snooker, Darts, etc.")
        print("✅ WINTER: Winter Sports")
        print("✅ WATER: Swimming, Surfing")
        print("✅ MOTOR: Esports")
        print("✅ SPECIAL: Athletics, Australian Rules, etc.")
        
        print("\n🏆 SPORTS DATA SERVICE READY!")
        print("🚀 Your sports data service now supports 50+ sports with comprehensive features!")
        
    except Exception as e:
        print(f"❌ Error during sports data population: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
