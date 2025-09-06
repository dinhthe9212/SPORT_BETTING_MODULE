"""
Providers Module - Tích hợp với các external API providers

Module này cung cấp:
- Multi-sports data provider
- Circuit breaker pattern
- Provider health monitoring
- Data source management

Classes:
- MultiSportsDataProvider: Quản lý nhiều providers
- CircuitBreaker: Circuit breaker pattern implementation
- APISportsProvider: Tích hợp với API-Sports.io
- TheOddsAPIProvider: Tích hợp với The-Odds-API
- OpenLigaDBProvider: Tích hợp với OpenLigaDB
- TheSportsDBProvider: Tích hợp với TheSportsDB
"""

from .multi_sports_provider import MultiSportsDataProvider
from .circuit_breaker import CircuitBreaker, CircuitBreakerManager, circuit_breaker_manager

__all__ = [
    'MultiSportsDataProvider',
    'CircuitBreaker',
    'CircuitBreakerManager',
    'circuit_breaker_manager'
]
