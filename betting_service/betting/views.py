from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction, models
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.admin.views.decorators import staff_member_required


import requests
import json
import logging
from decimal import Decimal
from .models import (
    Sport, Team, Match, BetType, Odd, OddsHistory, BetSlip, BetSelection,
    BetSlipPurchase, ResponsibleGamingPolicy, UserActivityLog, CashOutConfiguration, CashOutHistory,
    BetSlipOwnership, OrderBook, MarketSuspension, TradingSession, P2PTransaction,
    UserStatistics, BettingStatistics, PerformanceMetrics
)
from .services import (
    BetPlacementService, DynamicOddsService, FractionalTradingService, P2PMarketplaceService,
    OddsManagementService, StatisticsCalculationService, PerformanceMetricsService, LeaderboardService,
    BettingStatisticsService, CashOutService, SportsDataWebhookService, AutomaticMarketSuspensionService,
    MatchCancellationService, RiskCheckService
)
from .serializers import (
    SportSerializer, TeamSerializer, MatchSerializer, BetTypeSerializer,
    OddSerializer, BetSlipSerializer, BetSelectionSerializer, BetSlipPurchaseSerializer,
    ResponsibleGamingPolicySerializer, UserActivityLogSerializer,
    CashOutRequestSerializer, CashOutConfirmationSerializer, CashOutConfigurationSerializer,
    CashOutHistorySerializer, UserStatisticsSerializer, LeaderboardSerializer, 
    BettingStatisticsSerializer, PerformanceMetricsSerializer,
    BetSlipOwnershipSerializer, OrderBookSerializer, MarketSuspensionSerializer, TradingSessionSerializer,
    P2PTransactionSerializer
)

logger = logging.getLogger(__name__)

class SportViewSet(viewsets.ModelViewSet):
    queryset = Sport.objects.all()
    serializer_class = SportSerializer

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

class MatchViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer

    @action(detail=True, methods=["get"])
    def odds(self, request, pk=None):
        match = self.get_object()
        odds = match.odds.all()
        serializer = OddSerializer(odds, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def by_stake_type(self, request):
        """Lọc matches theo loại stake (FREE hoặc FIXED)"""
        stake_type = request.query_params.get('stake_type', 'FREE')
        
        if stake_type not in ['FREE', 'FIXED']:
            return Response(
                {"detail": "stake_type phải là 'FREE' hoặc 'FIXED'"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        matches = Match.objects.filter(stake_type=stake_type)
        
        # Thêm thông tin chi tiết về stake
        for match in matches:
            if match.stake_type == 'FIXED':
                match.stake_info = f"Fixed Stake: {match.fixed_stake_value}"
            else:
                match.stake_info = "Free Stake - Không giới hạn số tiền cược"
        
        serializer = self.get_serializer(matches, many=True)
        return Response({
            "stake_type": stake_type,
            "count": matches.count(),
            "matches": serializer.data
        })

    @action(detail=False, methods=["get"])
    def stake_summary(self, request):
        """Tổng quan về phân loại stake của tất cả matches"""
        total_matches = Match.objects.count()
        free_stake_matches = Match.objects.filter(stake_type='FREE').count()
        fixed_stake_matches = Match.objects.filter(stake_type='FIXED').count()
        
        # Tính tổng giá trị fixed stake
        total_fixed_stake_value = Match.objects.filter(
            stake_type='FIXED'
        ).aggregate(
            total=models.Sum('fixed_stake_value')
        )['total'] or 0
        
        return Response({
            "summary": {
                "total_matches": total_matches,
                "free_stake_matches": free_stake_matches,
                "fixed_stake_matches": fixed_stake_matches,
                "total_fixed_stake_value": float(total_fixed_stake_value)
            },
            "percentage": {
                "free_stake": round((free_stake_matches / total_matches * 100), 2) if total_matches > 0 else 0,
                "fixed_stake": round((fixed_stake_matches / total_matches * 100), 2) if total_matches > 0 else 0
            }
        })

    @action(detail=False, methods=["get"])
    def by_sport(self, request):
        """Lọc matches theo môn thể thao"""
        sport_id = request.query_params.get('sport_id')
        sport_name = request.query_params.get('sport_name')
        
        if not sport_id and not sport_name:
            return Response({
                "detail": "Cần cung cấp sport_id hoặc sport_name"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = Match.objects.all()
        
        if sport_id:
            try:
                sport_id = int(sport_id)
                queryset = queryset.filter(sport_id=sport_id)
            except ValueError:
                return Response({
                    "detail": "sport_id phải là số nguyên"
                }, status=status.HTTP_400_BAD_REQUEST)
        
        if sport_name:
            queryset = queryset.filter(sport__name__icontains=sport_name)
        
        matches = queryset.order_by('start_time')
        serializer = self.get_serializer(matches, many=True)
        
        return Response({
            "sport_filter": {
                "sport_id": sport_id,
                "sport_name": sport_name
            },
            "count": matches.count(),
            "matches": serializer.data
        })

    @action(detail=False, methods=["get"])
    def by_date(self, request):
        """Lọc matches theo ngày"""
        from datetime import datetime, date
        from django.utils import timezone
        
        date_str = request.query_params.get('date')  # Format: YYYY-MM-DD
        start_date = request.query_params.get('start_date')  # Format: YYYY-MM-DD
        end_date = request.query_params.get('end_date')  # Format: YYYY-MM-DD
        
        queryset = Match.objects.all()
        
        try:
            if date_str:
                # Lọc theo một ngày cụ thể
                filter_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                queryset = queryset.filter(start_time__date=filter_date)
                
            elif start_date and end_date:
                # Lọc theo khoảng thời gian
                start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(start_time__date__range=[start_dt, end_dt])
                
            elif start_date:
                # Lọc từ ngày bắt đầu
                start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(start_time__date__gte=start_dt)
                
            elif end_date:
                # Lọc đến ngày kết thúc
                end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(start_time__date__lte=end_dt)
            else:
                return Response({
                    "detail": "Cần cung cấp date, start_date, hoặc end_date"
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except ValueError:
            return Response({
                "detail": "Định dạng ngày không hợp lệ. Sử dụng YYYY-MM-DD"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        matches = queryset.order_by('start_time')
        serializer = self.get_serializer(matches, many=True)
        
        return Response({
            "date_filter": {
                "date": date_str,
                "start_date": start_date,
                "end_date": end_date
            },
            "count": matches.count(),
            "matches": serializer.data
        })

    @action(detail=False, methods=["get"])
    def by_status(self, request):
        """Lọc matches theo trạng thái"""
        status_filter = request.query_params.get('status')
        
        if not status_filter:
            return Response({
                "detail": "Cần cung cấp status parameter"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        valid_statuses = ['SCHEDULED', 'LIVE', 'FINISHED', 'CANCELLED', 'POSTPONED']
        if status_filter not in valid_statuses:
            return Response({
                "detail": f"Status phải là một trong: {', '.join(valid_statuses)}"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        matches = Match.objects.filter(status=status_filter).order_by('start_time')
        serializer = self.get_serializer(matches, many=True)
        
        return Response({
            "status_filter": status_filter,
            "count": matches.count(),
            "matches": serializer.data
        })

    @action(detail=False, methods=["get"])
    def search(self, request):
        """Tìm kiếm và lọc matches với nhiều tham số"""
        from datetime import datetime
        
        # Lấy tất cả query parameters
        sport_id = request.query_params.get('sport_id')
        sport_name = request.query_params.get('sport_name')
        team_name = request.query_params.get('team_name')
        status_filter = request.query_params.get('status')
        stake_type = request.query_params.get('stake_type')
        date_str = request.query_params.get('date')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = Match.objects.all()
        
        # Filter theo sport
        if sport_id:
            try:
                sport_id = int(sport_id)
                queryset = queryset.filter(sport_id=sport_id)
            except ValueError:
                return Response({
                    "detail": "sport_id phải là số nguyên"
                }, status=status.HTTP_400_BAD_REQUEST)
        
        if sport_name:
            queryset = queryset.filter(sport__name__icontains=sport_name)
        
        # Filter theo team
        if team_name:
            queryset = queryset.filter(
                models.Q(home_team__name__icontains=team_name) |
                models.Q(away_team__name__icontains=team_name)
            )
        
        # Filter theo status
        if status_filter:
            valid_statuses = ['SCHEDULED', 'LIVE', 'FINISHED', 'CANCELLED', 'POSTPONED']
            if status_filter in valid_statuses:
                queryset = queryset.filter(status=status_filter)
        
        # Filter theo stake type
        if stake_type:
            if stake_type in ['FREE', 'FIXED']:
                queryset = queryset.filter(stake_type=stake_type)
        
        # Filter theo date
        try:
            if date_str:
                filter_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                queryset = queryset.filter(start_time__date=filter_date)
            elif start_date and end_date:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(start_time__date__range=[start_dt, end_dt])
            elif start_date:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(start_time__date__gte=start_dt)
            elif end_date:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(start_time__date__lte=end_dt)
        except ValueError:
            return Response({
                "detail": "Định dạng ngày không hợp lệ. Sử dụng YYYY-MM-DD"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        matches = queryset.order_by('start_time')
        serializer = self.get_serializer(matches, many=True)
        
        return Response({
            "filters_applied": {
                "sport_id": sport_id,
                "sport_name": sport_name,
                "team_name": team_name,
                "status": status_filter,
                "stake_type": stake_type,
                "date": date_str,
                "start_date": start_date,
                "end_date": end_date
            },
            "count": matches.count(),
            "matches": serializer.data
        })

class BetTypeViewSet(viewsets.ModelViewSet):
    queryset = BetType.objects.all()
    serializer_class = BetTypeSerializer

class OddViewSet(viewsets.ModelViewSet):
    queryset = Odd.objects.all()
    serializer_class = OddSerializer

class BetSlipViewSet(viewsets.ModelViewSet):
    queryset = BetSlip.objects.all()
    serializer_class = BetSlipSerializer

    @action(detail=False, methods=["post"])
    def create_bet(self, request):
        """Tạo bet slip mới với hỗ trợ multiple bets và parlay"""
        try:
            # Lấy dữ liệu từ request
            selections_data = request.data.get('selections', [])
            total_stake = request.data.get('total_stake')
            bet_type = request.data.get('bet_type', 'SINGLE')
            user_id = request.data.get('user_id') or request.user.id
            
            if not user_id:
                return Response({
                    "detail": "User ID required"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not selections_data or not total_stake:
                return Response({
                    "detail": "selections and total_stake are required"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({
                    "detail": "User not found"
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Validation trước khi tạo
            bet_placement_service = BetPlacementService()
            validation_result = bet_placement_service.validate_bet_with_risk_check(
                user, selections_data, total_stake
            )
            
            if not validation_result['valid']:
                return Response({
                    "detail": "Bet validation failed",
                    "errors": validation_result['errors']
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Tạo bet slip
            bet_slip = BetPlacementService.create_bet_slip(
                user, selections_data, total_stake, bet_type
            )
            
            # Lấy thông tin tổng quan
            bet_summary = BetPlacementService.get_bet_summary(bet_slip)
            
            response_data = {
                "message": "Bet slip created successfully",
                "bet_slip_id": bet_slip.id,
                "bet_summary": bet_summary
            }
            
            # Thêm thông tin rủi ro nếu có
            if validation_result.get('risk_check'):
                response_data['risk_info'] = {
                    'risk_level': validation_result['risk_check'].get('risk_level'),
                    'recommendations': validation_result['risk_check'].get('recommendations', [])
                }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except ValueError as e:
            return Response({
                "detail": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error creating bet slip: {str(e)}")
            return Response({
                "detail": "Internal server error"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=["post"])
    def place_bet(self, request, pk=None):
        """Đặt cược với Risk Management và Saga Pattern"""
        try:
            bet_slip = self.get_object()
            
            # Kiểm tra trạng thái bet
            if bet_slip.bet_status != 'PENDING':
                return Response({
                    "detail": f"Bet slip không thể đặt cược. Trạng thái hiện tại: {bet_slip.bet_status}"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Lấy thông tin user từ request
            user_id = request.data.get('user_id') or request.user.id
            if not user_id:
                return Response({"detail": "User ID required"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Kiểm tra rủi ro trước khi đặt cược
            risk_check_result = self._perform_final_risk_check(bet_slip, user_id)
            
            if not risk_check_result['approved']:
                return Response({
                    "detail": "Bet bị từ chối do rủi ro",
                    "rejection_reason": risk_check_result.get('rejection_reason'),
                    "recommendations": risk_check_result.get('recommendations', []),
                    "risk_level": risk_check_result.get('risk_level')
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Bắt đầu Saga transaction
            saga_data = {
                "bet_slip_id": bet_slip.id,
                "user_id": user_id,
                "total_stake": float(bet_slip.total_stake),
                "potential_payout": float(bet_slip.potential_payout) if bet_slip.potential_payout else None,
                "risk_check_passed": True,
                "risk_level": risk_check_result.get('risk_level')
            }
            
            # Gọi Saga Orchestrator để bắt đầu workflow
            saga_response = self._start_betting_saga(saga_data)
            
            if saga_response.get('success'):
                return Response({
                    "message": "Bet placement initiated successfully",
                    "saga_transaction_id": saga_response.get('saga_transaction_id'),
                    "bet_slip_id": bet_slip.id,
                    "status": "processing",
                    "risk_info": {
                        "risk_level": risk_check_result.get('risk_level'),
                        "liability_impact": risk_check_result.get('liability_impact'),
                        "recommendations": risk_check_result.get('recommendations', [])
                    }
                }, status=status.HTTP_202_ACCEPTED)
            else:
                return Response({
                    "detail": "Failed to start bet placement saga",
                    "error": saga_response.get('error')
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Error in place_bet: {str(e)}")
            return Response({
                "detail": "Internal server error during bet placement"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _start_betting_saga(self, saga_data):
        """Khởi tạo Betting Saga workflow"""
        try:
            # Gọi Saga Orchestrator service
            saga_url = "http://saga_orchestrator:8000/api/sagas/start/"
            payload = {
                "saga_type": "betting_flow",
                "user_id": saga_data["user_id"],
                "input_data": saga_data
            }
            
            response = requests.post(saga_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "saga_transaction_id": result.get("correlation_id")
                }
            else:
                logger.error(f"Saga orchestrator error: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"Saga orchestrator error: {response.status_code}"
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to connect to saga orchestrator: {str(e)}")
            return {
                "success": False,
                "error": "Saga orchestrator service unavailable"
            }
        except Exception as e:
            logger.error(f"Unexpected error in _start_betting_saga: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _perform_final_risk_check(self, bet_slip, user_id):
        """Thực hiện kiểm tra rủi ro cuối cùng trước khi đặt cược"""
        try:
            risk_check_service = RiskCheckService()
            
            # Tạo dữ liệu risk check cho tất cả selections
            selections_data = []
            for selection in bet_slip.selections.all():
                selections_data.append({
                    'user_id': user_id,
                    'match_id': selection.odd.match.id,
                    'bet_type_id': selection.odd.bet_type.id,
                    'outcome': selection.odd.outcome,
                    'stake_amount': float(selection.odd.value),  # Sử dụng odds value làm stake
                    'odds_value': float(selection.odd.value)
                })
            
            # Kiểm tra rủi ro cho từng selection
            risk_results = []
            for selection_data in selections_data:
                risk_result = risk_check_service.check_bet_risk(selection_data)
                risk_results.append(risk_result)
                
                # Nếu có lỗi kết nối, sử dụng fallback
                if risk_result.get('fallback'):
                    logger.warning(f"Using fallback risk check for user {user_id}")
                    continue
                
                # Nếu không được chấp nhận, trả về kết quả
                if not risk_result.get('approved'):
                    return risk_result
            
            # Tất cả selections đều được chấp nhận
            # Tính toán risk level tổng thể
            overall_risk_level = self._calculate_overall_risk_level(risk_results)
            
            return {
                'approved': True,
                'risk_level': overall_risk_level,
                'liability_impact': sum(r.get('liability_impact', 0) for r in risk_results),
                'recommendations': ['Tất cả selections đều được chấp nhận']
            }
            
        except Exception as e:
            logger.error(f"Error in _perform_final_risk_check: {str(e)}")
            return {
                'approved': False,
                'error': f'Lỗi kiểm tra rủi ro: {str(e)}',
                'risk_level': 'UNKNOWN'
            }
    
    def _calculate_overall_risk_level(self, risk_results):
        """Tính toán risk level tổng thể từ các risk results"""
        if not risk_results:
            return 'UNKNOWN'
        
        # Đếm số lượng mỗi risk level
        risk_counts = {}
        for result in risk_results:
            level = result.get('risk_level', 'UNKNOWN')
            risk_counts[level] = risk_counts.get(level, 0) + 1
        
        # Xác định risk level tổng thể
        if risk_counts.get('HIGH', 0) > 0:
            return 'HIGH'
        elif risk_counts.get('MEDIUM', 0) > 0:
            return 'MEDIUM'
        elif risk_counts.get('LOW', 0) > 0:
            return 'LOW'
        elif risk_counts.get('VERY_LOW', 0) > 0:
            return 'VERY_LOW'
        else:
            return 'UNKNOWN'

    @action(detail=False, methods=["post"])
    def validate_bet(self, request):
        """Validation endpoint cho Saga - Kiểm tra tính hợp lệ của bet"""
        try:
            bet_slip_id = request.data.get('bet_slip_id')
            user_id = request.data.get('user_id')
            total_stake = request.data.get('total_stake')
            
            if not all([bet_slip_id, user_id, total_stake]):
                return Response({
                    "detail": "Missing required fields: bet_slip_id, user_id, total_stake"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Kiểm tra bet slip tồn tại
            try:
                bet_slip = BetSlip.objects.get(id=bet_slip_id, user_id=user_id)
            except BetSlip.DoesNotExist:
                return Response({
                    "detail": "Bet slip not found or unauthorized"
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Kiểm tra trạng thái
            if bet_slip.bet_status != 'PENDING':
                return Response({
                    "detail": f"Bet slip không thể đặt cược. Trạng thái: {bet_slip.bet_status}"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Kiểm tra số tiền cược
            if float(total_stake) != float(bet_slip.total_stake):
                return Response({
                    "detail": "Total stake mismatch"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Kiểm tra có selections không
            if not bet_slip.selections.exists():
                return Response({
                    "detail": "Bet slip must have at least one selection"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validation thành công
            return Response({
                "valid": True,
                "bet_slip_id": bet_slip_id,
                "message": "Bet validation successful"
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in validate_bet: {str(e)}")
            return Response({
                "valid": False,
                "detail": "Validation failed",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=["post"])
    def confirm_bet(self, request):
        """Xác nhận bet sau khi trừ tiền thành công - Endpoint cho Saga"""
        try:
            bet_slip_id = request.data.get('bet_slip_id')
            wallet_transaction_id = request.data.get('wallet_transaction_id')
            
            if not all([bet_slip_id, wallet_transaction_id]):
                return Response({
                    "detail": "Missing required fields: bet_slip_id, wallet_transaction_id"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            with transaction.atomic():
                # Lấy bet slip
                bet_slip = BetSlip.objects.select_for_update().get(id=bet_slip_id)
                
                # Cập nhật thông tin
                bet_slip.wallet_transaction_id = wallet_transaction_id
                bet_slip.confirm_bet()  # Sử dụng method đã tạo
                
                # Tính toán potential payout nếu chưa có
                if not bet_slip.potential_payout:
                    bet_slip.potential_payout = self._calculate_potential_payout(bet_slip)
                    bet_slip.save()
                
                logger.info(f"Bet {bet_slip_id} confirmed successfully with wallet transaction {wallet_transaction_id}")
                
                return Response({
                    "success": True,
                    "bet_slip_id": bet_slip_id,
                    "bet_status": bet_slip.bet_status,
                    "wallet_transaction_id": wallet_transaction_id,
                    "message": "Bet confirmed successfully"
                }, status=status.HTTP_200_OK)
                
        except BetSlip.DoesNotExist:
            return Response({
                "detail": "Bet slip not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in confirm_bet: {str(e)}")
            return Response({
                "detail": "Failed to confirm bet",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _calculate_potential_payout(self, bet_slip):
        """Tính toán potential payout dựa trên odds và stake"""
        try:
            total_odds = 1.0
            for selection in bet_slip.selections.all():
                # Sử dụng odds snapshot tại thời điểm đặt cược
                total_odds *= float(selection.odds_at_placement)
            
            return bet_slip.total_stake * total_odds
            
        except Exception as e:
            logger.error(f"Error calculating potential payout: {str(e)}")
            return bet_slip.total_stake * 2.0  # Fallback value

    @action(detail=True, methods=["post"])
    def settle_bet(self, request, pk=None):
        try:
            bet_slip = self.get_object()
        except BetSlip.DoesNotExist:
            return Response({"detail": "BetSlip not found."}, status=status.HTTP_404_NOT_FOUND)

        if bet_slip.is_settled:
            return Response({"detail": "BetSlip already settled."}, status=status.HTTP_400_BAD_REQUEST)

        is_won = request.data.get("is_won")
        if is_won is None:
            return Response({"detail": "'is_won' parameter is required (true/false)."}, status=status.HTTP_400_BAD_REQUEST)

        bet_slip.is_won = bool(is_won)
        bet_slip.is_settled = True
        bet_slip.save()

        # In a real system, if is_won is True, you would trigger a transaction
        # to credit the user's wallet with the potential_payout.

        return Response({"message": "BetSlip settled successfully", "is_won": bet_slip.is_won}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def cash_out(self, request, pk=None):
        """
        API endpoint cũ - giữ lại để tương thích ngược
        Sẽ được thay thế bằng các API mới
        """
        try:
            bet_slip = self.get_object()
        except BetSlip.DoesNotExist:
            return Response({"detail": "BetSlip not found."}, status=status.HTTP_404_NOT_FOUND)

        # Sử dụng CashOutService mới
        cashout_service = CashOutService()
        
        try:
            # Kiểm tra tính đủ điều kiện
            eligibility = cashout_service.get_cash_out_eligibility(bet_slip)
            if not eligibility['can_cash_out']:
                return Response({
                    "detail": "Cash out not available for this bet slip.",
                    "reasons": eligibility['reasons']
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Mock live odds data (trong thực tế sẽ lấy từ Risk Management Service)
            mock_live_odds = [{
                'match_id': bet_slip.selections.first().odd.match.id,
                'bet_type_id': bet_slip.selections.first().odd.bet_type.id,
                'outcome': bet_slip.selections.first().odd.outcome,
                'live_odds': bet_slip.selections.first().odd.value * 0.8  # Mock giảm 20%
            }]
            
            # Tính toán giá trị Cash Out
            cash_out_data = cashout_service.calculate_cash_out_value(
                bet_slip, mock_live_odds
            )
            
            # Xử lý yêu cầu Cash Out
            cashout_history = cashout_service.process_cash_out_request(bet_slip, request.user.id)
            
            # Hoàn thành Cash Out (trong thực tế sẽ qua Saga)
            cashout_service.complete_cash_out(cashout_history, cash_out_data)
            
            return Response({
                "message": "Cash out successful",
                "cash_out_value": cash_out_data['cash_out_value'],
                "fair_value": cash_out_data['fair_value'],
                "fee_amount": cash_out_data['fee_amount'],
                "fee_percentage": cash_out_data['fee_percentage']
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "detail": f"Cash out failed: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)

class BetSelectionViewSet(viewsets.ModelViewSet):
    queryset = BetSelection.objects.all()
    serializer_class = BetSelectionSerializer

class BetSlipPurchaseViewSet(viewsets.ModelViewSet):
    queryset = BetSlipPurchase.objects.all()
    serializer_class = BetSlipPurchaseSerializer

    @action(detail=True, methods=["post"])
    def buy_bet_slip(self, request, pk=None):
        # Logic to handle buying a bet slip
        return Response({"message": "Bet slip purchased successfully"})



class ResponsibleGamingPolicyViewSet(viewsets.ModelViewSet):
    queryset = ResponsibleGamingPolicy.objects.all()
    serializer_class = ResponsibleGamingPolicySerializer

    def get_queryset(self):
        user_id = self.request.headers.get("X-User-ID")
        if user_id:
            return ResponsibleGamingPolicy.objects.filter(user__id=user_id)
        return ResponsibleGamingPolicy.objects.none()

    @action(detail=False, methods=["post"])
    def set_limits(self, request):
        user_id = request.headers.get("X-User-ID")
        if not user_id:
            return Response({"detail": "User ID required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        policy, created = ResponsibleGamingPolicy.objects.get_or_create(user=user)
        serializer = self.get_serializer(policy, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        error = serializer.errors
        if error:
            return Response({"detail": "Invalid data", "errors": error}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        return Response({"message": "Responsible gaming policy updated successfully."}, status=status.HTTP_200_OK)


class UserActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UserActivityLog.objects.all()
    serializer_class = UserActivityLogSerializer

    def get_queryset(self):
        user_id = self.request.headers.get("X-User-ID")
        if user_id:
            return UserActivityLog.objects.filter(user__id=user_id).order_by("-timestamp")
        return UserActivityLog.objects.none()

    @action(detail=False, methods=["post"])
    def log_activity(self, request):
        user_id = request.headers.get("X-User-ID")
        if not user_id:
            return Response({"detail": "User ID required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        activity_type = request.data.get("activity_type")
        details = request.data.get("details", {})
        ip_address = request.META.get("REMOTE_ADDR")

        if not activity_type:
            return Response({"detail": "Activity type is required."}, status=status.HTTP_400_BAD_REQUEST)

        log = UserActivityLog.objects.create(
            user=user,
            activity_type=activity_type,
            details=details,
            ip_address=ip_address
        )
        return Response(UserActivityLogSerializer(log).data, status=status.HTTP_201_CREATED)


# ============================================================================
# ODDS MANAGEMENT ENDPOINTS
# ============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def get_odds_for_match(request, match_id):
    """Lấy tất cả odds của một match"""
    try:
        match = Match.objects.get(id=match_id)
        odds = Odd.objects.filter(match=match, is_active=True)
        
        odds_data = []
        for odd in odds:
            odds_data.append({
                'id': odd.id,
                'bet_type': odd.bet_type.name,
                'outcome': odd.outcome,
                'value': float(odd.value),
                'odds_type': odd.odds_type,
                'odds_status': odd.odds_status,
                'base_value': float(odd.base_value) if odd.base_value else None,
                'risk_multiplier': float(odd.risk_multiplier),
                'current_liability': float(odd.current_liability),
                'liability_threshold': float(odd.liability_threshold) if odd.liability_threshold else None,
                'min_value': float(odd.min_value) if odd.min_value else None,
                'max_value': float(odd.max_value) if odd.max_value else None,
                'auto_adjust_enabled': odd.auto_adjust_enabled,
                'last_risk_update': odd.last_risk_update.isoformat() if odd.last_risk_update else None,
                'last_updated': odd.last_updated.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'match_id': match_id,
            'match': f"{match.home_team.name} vs {match.away_team.name}",
            'odds': odds_data
        })
        
    except Match.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Match không tồn tại'
        }, status=404)
    except Exception as e:
        logger.error(f"Lỗi lấy odds cho match {match_id}: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Lỗi server'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_odds_history(request, odd_id):
    """Lấy lịch sử thay đổi odds"""
    try:
        limit = int(request.GET.get('limit', 100))
        odd = Odd.objects.get(id=odd_id)
        
        history = OddsHistory.objects.filter(odd=odd).order_by('-timestamp')[:limit]
        
        history_data = []
        for record in history:
            history_data.append({
                'id': record.id,
                'old_value': float(record.old_value),
                'new_value': float(record.new_value),
                'change_reason': record.change_reason,
                'change_percentage': record.change_percentage,
                'is_significant_change': record.is_significant_change,
                'risk_liability': float(record.risk_liability) if record.risk_liability else None,
                'risk_multiplier': float(record.risk_multiplier) if record.risk_multiplier else None,
                'additional_data': record.additional_data,
                'changed_by': record.changed_by.username if record.changed_by else None,
                'timestamp': record.timestamp.isoformat(),
                'ip_address': record.ip_address
            })
        
        return JsonResponse({
            'success': True,
            'odd_id': odd_id,
            'odd_info': f"{odd.match} - {odd.bet_type.name}: {odd.outcome}",
            'history': history_data
        })
        
    except Odd.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Odds không tồn tại'
        }, status=404)
    except Exception as e:
        logger.error(f"Lỗi lấy lịch sử odds {odd_id}: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Lỗi server'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_significant_odds_changes(request, match_id):
    """Lấy các thay đổi odds đáng kể của một match"""
    try:
        hours = int(request.GET.get('hours', 24))
        
        dynamic_service = DynamicOddsService()
        changes = dynamic_service.get_significant_changes(match_id, hours)
        
        changes_data = []
        for change in changes:
            changes_data.append({
                'id': change.id,
                'odd_id': change.odd.id,
                'bet_type': change.odd.bet_type.name,
                'outcome': change.odd.outcome,
                'old_value': float(change.old_value),
                'new_value': float(change.new_value),
                'change_reason': change.change_reason,
                'change_percentage': change.change_percentage,
                'risk_liability': float(change.risk_liability) if change.risk_liability else None,
                'timestamp': change.timestamp.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'match_id': match_id,
            'period_hours': hours,
            'changes_count': len(changes_data),
            'changes': changes_data
        })
        
    except Exception as e:
        logger.error(f"Lỗi lấy thay đổi odds đáng kể cho match {match_id}: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Lỗi server'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@staff_member_required
def adjust_odds_manually(request, odd_id):
    """Điều chỉnh odds thủ công (chỉ admin)"""
    try:
        data = json.loads(request.body)
        new_value = Decimal(str(data.get('new_value')))
        reason = data.get('reason', 'Manual adjustment')
        
        odd = Odd.objects.get(id=odd_id)
        odds_service = OddsManagementService()
        
        if odds_service.adjust_odds_manually(odd, new_value, reason, request.user.id):
            return JsonResponse({
                'success': True,
                'message': f'Đã điều chỉnh odds từ {odd.value} thành {new_value}',
                'odd_id': odd_id,
                'old_value': float(odd.value),
                'new_value': float(new_value)
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Không có thay đổi nào được thực hiện'
            })
        
    except Odd.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Odds không tồn tại'
        }, status=404)
    except (KeyError, ValueError) as e:
        return JsonResponse({
            'success': False,
            'error': f'Dữ liệu không hợp lệ: {str(e)}'
        }, status=400)
    except Exception as e:
        logger.error(f"Lỗi điều chỉnh odds {odd_id}: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Lỗi server'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@staff_member_required
def suspend_odds_for_match(request, match_id):
    """Tạm dừng tất cả odds của một match (chỉ admin)"""
    try:
        data = json.loads(request.body)
        reason = data.get('reason', 'Odds suspended')
        
        match = Match.objects.get(id=match_id)
        odds_service = OddsManagementService()
        
        suspended_count = odds_service.suspend_odds_for_match(match, reason, request.user.id)
        
        return JsonResponse({
            'success': True,
            'message': f'Đã tạm dừng {suspended_count} odds',
            'match_id': match_id,
            'suspended_count': suspended_count
        })
        
    except Match.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Match không tồn tại'
        }, status=404)
    except Exception as e:
        logger.error(f"Lỗi tạm dừng odds cho match {match_id}: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Lỗi server'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@staff_member_required
def resume_odds_for_match(request, match_id):
    """Khôi phục tất cả odds của một match (chỉ admin)"""
    try:
        match = Match.objects.get(id=match_id)
        odds_service = OddsManagementService()
        
        resumed_count = odds_service.resume_odds_for_match(match, request.user.id)
        
        return JsonResponse({
            'success': True,
            'message': f'Đã khôi phục {resumed_count} odds',
            'match_id': match_id,
            'resumed_count': resumed_count
        })
        
    except Match.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Match không tồn tại'
        }, status=404)
    except Exception as e:
        logger.error(f"Lỗi khôi phục odds cho match {match_id}: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Lỗi server'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@staff_member_required
def update_odds_for_risk(request, match_id):
    """Cập nhật odds dựa trên rủi ro (chỉ admin)"""
    try:
        match = Match.objects.get(id=match_id)
        dynamic_service = DynamicOddsService()
        
        result = dynamic_service.batch_update_odds_for_match(match)
        
        return JsonResponse({
            'success': True,
            'message': f'Đã cập nhật {result["updated"]} odds, {result["errors"]} lỗi',
            'match_id': match_id,
            'result': result
        })
        
    except Match.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Match không tồn tại'
        }, status=404)
    except Exception as e:
        logger.error(f"Lỗi cập nhật odds theo rủi ro cho match {match_id}: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Lỗi server'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_odds_analytics(request, match_id):
    """Lấy analytics về odds của một match"""
    try:
        days = int(request.GET.get('days', 7))
        
        odds_service = OddsManagementService()
        analytics = odds_service.get_odds_analytics(match_id, days)
        
        return JsonResponse({
            'success': True,
            'analytics': analytics
        })
        
    except Exception as e:
        logger.error(f"Lỗi lấy analytics odds cho match {match_id}: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Lỗi server'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_odds_snapshot(request, match_id):
    """Lấy snapshot của tất cả odds của một match"""
    try:
        match = Match.objects.get(id=match_id)
        dynamic_service = DynamicOddsService()
        
        snapshot = dynamic_service.create_odds_snapshot(match)
        
        return JsonResponse({
            'success': True,
            'snapshot': snapshot
        })
        
    except Match.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Match không tồn tại'
        }, status=404)
    except Exception as e:
        logger.error(f"Lỗi lấy snapshot odds cho match {match_id}: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Lỗi server'
        }, status=500)

# ============================================================================
# RISK INTEGRATION ENDPOINTS
# ============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def get_risk_profile_for_odds(request, odd_id):
    """Lấy thông tin risk profile cho odds"""
    try:
        odd = Odd.objects.get(id=odd_id)
        
        if not odd.risk_profile_id:
            return JsonResponse({
                'success': False,
                'error': 'Odds không có risk profile'
            })
        
        # TODO: Gọi Risk Management Service để lấy thông tin chi tiết
        risk_data = {
            'risk_profile_id': odd.risk_profile_id,
            'odds_id': odd_id,
            'odds_type': odd.odds_type,
            'current_liability': float(odd.current_liability),
            'liability_threshold': float(odd.liability_threshold) if odd.liability_threshold else None,
            'risk_multiplier': float(odd.risk_multiplier),
            'auto_adjust_enabled': odd.auto_adjust_enabled,
            'last_risk_update': odd.last_risk_update.isoformat() if odd.last_risk_update else None
        }
        
        return JsonResponse({
            'success': True,
            'risk_data': risk_data
        })
        
    except Odd.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Odds không tồn tại'
        }, status=404)
    except Exception as e:
        logger.error(f"Lỗi lấy risk profile cho odds {odd_id}: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Lỗi server'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@staff_member_required
def configure_risk_based_odds(request, odd_id):
    """Cấu hình odds dựa trên rủi ro (chỉ admin)"""
    try:
        data = json.loads(request.body)
        
        odd = Odd.objects.get(id=odd_id)
        
        # Cập nhật cấu hình risk
        if 'odds_type' in data:
            odd.odds_type = data['odds_type']
        
        if 'liability_threshold' in data:
            odd.liability_threshold = Decimal(str(data['liability_threshold']))
        
        if 'min_value' in data:
            odd.min_value = Decimal(str(data['min_value']))
        
        if 'max_value' in data:
            odd.max_value = Decimal(str(data['max_value']))
        
        if 'adjustment_step' in data:
            odd.adjustment_step = Decimal(str(data['adjustment_step']))
        
        if 'auto_adjust_enabled' in data:
            odd.auto_adjust_enabled = data['auto_adjust_enabled']
        
        if 'risk_profile_id' in data:
            odd.risk_profile_id = data['risk_profile_id']
        
        odd.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Đã cập nhật cấu hình risk-based odds',
            'odd_id': odd_id,
            'config': {
                'odds_type': odd.odds_type,
                'liability_threshold': float(odd.liability_threshold) if odd.liability_threshold else None,
                'min_value': float(odd.min_value) if odd.min_value else None,
                'max_value': float(odd.max_value) if odd.max_value else None,
                'adjustment_step': float(odd.adjustment_step),
                'auto_adjust_enabled': odd.auto_adjust_enabled,
                'risk_profile_id': odd.risk_profile_id
            }
        })
        
    except Odd.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Odds không tồn tại'
        }, status=404)
    except (KeyError, ValueError) as e:
        return JsonResponse({
            'success': False,
            'error': f'Dữ liệu không hợp lệ: {str(e)}'
        }, status=400)
    except Exception as e:
        logger.error(f"Lỗi cấu hình risk-based odds {odd_id}: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Lỗi server'
        }, status=500)


# ============================================================================
# CASH OUT VIEWSETS
# ============================================================================

class CashOutConfigurationViewSet(viewsets.ModelViewSet):
    """ViewSet cho quản lý cấu hình phí Cash Out"""
    
    queryset = CashOutConfiguration.objects.all()
    serializer_class = CashOutConfigurationSerializer
    
    def get_queryset(self):
        """Lọc theo bookmaker type và ID nếu có"""
        queryset = super().get_queryset()
        
        bookmaker_type = self.request.query_params.get('bookmaker_type')
        bookmaker_id = self.request.query_params.get('bookmaker_id')
        
        if bookmaker_type:
            queryset = queryset.filter(bookmaker_type=bookmaker_type)
        
        if bookmaker_id:
            queryset = queryset.filter(bookmaker_id=bookmaker_id)
        
        return queryset.filter(is_active=True)


class UserStatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet cho User Statistics"""
    serializer_class = UserStatisticsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Lấy thống kê của người dùng hiện tại"""
        return UserStatistics.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_statistics(self, request):
        """Lấy thống kê của người dùng hiện tại"""
        period = request.query_params.get('period', 'ALL_TIME')
        
        # Tính toán thống kê mới
        stats = StatisticsCalculationService.calculate_user_statistics(
            user=request.user,
            period=period
        )
        
        serializer = self.get_serializer(stats)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def performance_summary(self, request):
        """Lấy tổng quan hiệu suất của người dùng"""
        
        # Lấy thống kê tổng thể
        overall_stats = StatisticsCalculationService.calculate_user_statistics(
            user=request.user,
            period='ALL_TIME'
        )
        
        # Lấy thống kê theo môn thể thao
        sports_performance = []
        sports = Sport.objects.all()[:5]  # Top 5 môn thể thao
        
        for sport in sports:
            metrics = PerformanceMetricsService.calculate_performance_metrics(
                user=request.user,
                sport=sport
            )
            sports_performance.append({
                'sport_name': sport.name,
                'total_bets': metrics.total_bets,
                'win_rate': float(metrics.win_rate),
                'roi': float(metrics.roi),
                'total_stake': float(metrics.total_stake)
            })
        
        # Lấy thống kê theo loại cược
        bet_types = BetType.objects.all()[:3]  # Top 3 loại cược
        bet_type_performance = []
        
        for bet_type in bet_types:
            metrics = PerformanceMetricsService.calculate_performance_metrics(
                user=request.user,
                bet_type=bet_type
            )
            bet_type_performance.append({
                'bet_type_name': bet_type.name,
                'total_bets': metrics.total_bets,
                'win_rate': float(metrics.win_rate),
                'roi': float(metrics.roi)
            })
        
        # Tạo response
        response_data = {
            'user_id': request.user.id,
            'user_email': request.user.email,
            'username': request.user.username,
            'total_bets': overall_stats.total_bets,
            'total_wins': overall_stats.total_wins,
            'win_rate': float(overall_stats.win_rate),
            'total_profit': float(overall_stats.total_profit),
            'roi': float(overall_stats.roi),
            'current_win_streak': overall_stats.current_win_streak,
            'best_win_streak': overall_stats.best_win_streak,
            'sports_performance': sports_performance,
            'bet_type_performance': bet_type_performance,
            'last_bet_date': overall_stats.last_updated,
            'total_stake': float(overall_stats.total_stake),
            'average_bet_size': float(overall_stats.average_bet_size)
        }
        
        return Response(response_data)


class LeaderboardViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet cho Leaderboard"""
    serializer_class = LeaderboardSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Lấy bảng xếp hạng"""
        period = self.request.query_params.get('period', 'WEEKLY')
        category = self.request.query_params.get('category', 'OVERALL')
        limit = int(self.request.query_params.get('limit', 50))
        
        return LeaderboardService.get_leaderboard(period, category, limit)
    
    @action(detail=False, methods=['get'])
    def my_rank(self, request):
        """Lấy thứ hạng của người dùng hiện tại"""
        period = request.query_params.get('period', 'WEEKLY')
        category = request.query_params.get('category', 'OVERALL')
        
        rank, points = LeaderboardService.get_user_rank(
            user=request.user,
            period=period,
            category=category
        )
        
        return Response({
            'period': period,
            'category': category,
            'rank': rank,
            'points': points
        })
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Lấy tổng quan bảng xếp hạng"""
        period = request.query_params.get('period', 'WEEKLY')
        category = request.query_params.get('category', 'OVERALL')
        
        # Lấy top 3
        top_3 = LeaderboardService.get_leaderboard(period, category, 3)
        
        # Lấy thứ hạng của người dùng hiện tại
        user_rank, user_points = LeaderboardService.get_user_rank(
            user=request.user,
            period=period,
            category=category
        )
        
        # Lấy tổng số người tham gia
        period_start, period_end = StatisticsCalculationService._get_period_dates(period)
        total_participants = UserStatistics.objects.filter(
            period=period,
            period_start=period_start
        ).count()
        
        response_data = {
            'period': period,
            'category': category,
            'total_participants': total_participants,
            'top_3': self.get_serializer(top_3, many=True).data,
            'user_rank': user_rank,
            'user_points': user_points,
            'period_start': period_start,
            'period_end': period_end
        }
        
        return Response(response_data)
    
    @action(detail=False, methods=['post'])
    def refresh(self, request):
        """Làm mới bảng xếp hạng (chỉ admin)"""
        from django.contrib.auth.decorators import user_passes_test
        
        if not request.user.is_staff:
            return Response(
                {"detail": "Chỉ admin mới có thể làm mới bảng xếp hạng"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        period = request.data.get('period', 'WEEKLY')
        category = request.data.get('category', 'OVERALL')
        
        # Cập nhật bảng xếp hạng
        participants_count = LeaderboardService.update_leaderboard(period, category)
        
        return Response({
            "detail": f"Đã cập nhật bảng xếp hạng {period} - {category}",
            "participants_count": participants_count
        })


class BettingStatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet cho Betting Statistics"""
    serializer_class = BettingStatisticsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Lấy thống kê tổng hợp về cược"""
        period = self.request.query_params.get('period', 'DAILY')
        return BettingStatistics.objects.filter(period=period)
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """Lấy tổng quan thống kê"""
        period = request.query_params.get('period', 'DAILY')
        
        # Tính toán thống kê mới
        stats = BettingStatisticsService.calculate_betting_statistics(period)
        
        # Lấy thống kê người dùng
        period_start, period_end = StatisticsCalculationService._get_period_dates(period)
        
        # Đếm người dùng
        total_users = User.objects.count()
        active_users = User.objects.filter(last_login__gte=period_start).count()
        new_users = User.objects.filter(date_joined__gte=period_start).count()
        
        # Lấy top performers
        top_profit_users = UserStatistics.objects.filter(
            period=period,
            period_start=period_start
        ).order_by('-total_profit')[:5].values('user__email', 'total_profit', 'win_rate')
        
        top_win_rate_users = UserStatistics.objects.filter(
            period=period,
            period_start=period_start,
            total_bets__gte=5  # Ít nhất 5 phiếu cược
        ).order_by('-win_rate')[:5].values('user__email', 'win_rate', 'total_bets')
        
        top_volume_users = UserStatistics.objects.filter(
            period=period,
            period_start=period_start
        ).order_by('-total_stake')[:5].values('user__email', 'total_stake', 'total_bets')
        
        # Tính tỷ lệ Cash Out
        cashout_requests = CashOutHistory.objects.filter(
            requested_at__gte=period_start,
            requested_at__lte=period_end
        )
        cashout_rate = (cashout_requests.filter(status='COMPLETED').count() / cashout_requests.count() * 100) if cashout_requests.count() > 0 else 0
        
        response_data = {
            'period': period,
            'period_start': period_start,
            'period_end': period_end,
            'total_users': total_users,
            'active_users': active_users,
            'new_users': new_users,
            'total_bets': stats.total_bets_placed,
            'total_stake': float(stats.total_stake_amount),
            'total_return': float(stats.total_return_amount),
            'house_profit': float(stats.total_profit),
            'house_edge': float(stats.house_edge),
            'average_bet_size': float(stats.average_bet_size),
            'win_rate': float(stats.win_rate),
            'cashout_rate': cashout_rate,
            'top_profit_users': list(top_profit_users),
            'top_win_rate_users': list(top_win_rate_users),
            'top_volume_users': list(top_volume_users)
        }
        
        return Response(response_data)
    
    @action(detail=False, methods=['post'])
    def refresh(self, request):
        """Làm mới thống kê (chỉ admin)"""
        if not request.user.is_staff:
            return Response(
                {"detail": "Chỉ admin mới có thể làm mới thống kê"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        period = request.data.get('period', 'DAILY')
        
        # Tính toán thống kê mới
        stats = BettingStatisticsService.calculate_betting_statistics(period)
        
        return Response({
            "detail": f"Đã cập nhật thống kê {period}",
            "stats_id": stats.id
        })


class PerformanceMetricsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet cho Performance Metrics"""
    serializer_class = PerformanceMetricsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Lấy metrics hiệu suất của người dùng hiện tại"""
        return PerformanceMetrics.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_performance(self, request):
        """Lấy hiệu suất của người dùng hiện tại"""
        sport_id = request.query_params.get('sport_id')
        bet_type_id = request.query_params.get('bet_type_id')
        
        sport = None
        bet_type = None
        
        if sport_id:
            sport = Sport.objects.get(id=sport_id)
        if bet_type_id:
            bet_type = BetType.objects.get(id=bet_type_id)
        
        # Tính toán metrics mới
        metrics = PerformanceMetricsService.calculate_performance_metrics(
            user=request.user,
            sport=sport,
            bet_type=bet_type
        )
        
        serializer = self.get_serializer(metrics)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def sports_comparison(self, request):
        """So sánh hiệu suất theo môn thể thao"""
        
        sports = Sport.objects.all()
        comparison_data = []
        
        for sport in sports:
            metrics = PerformanceMetricsService.calculate_performance_metrics(
                user=request.user,
                sport=sport
            )
            
            if metrics.total_bets > 0:  # Chỉ hiển thị môn có cược
                comparison_data.append({
                    'sport_name': sport.name,
                    'total_bets': metrics.total_bets,
                    'win_rate': float(metrics.win_rate),
                    'roi': float(metrics.roi),
                    'total_stake': float(metrics.total_stake),
                    'average_odds': float(metrics.average_odds)
                })
        
        # Sắp xếp theo tỷ lệ thắng
        comparison_data.sort(key=lambda x: x['win_rate'], reverse=True)
        
        return Response(comparison_data)


class CashOutHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet cho lịch sử Cash Out"""
    
    queryset = CashOutHistory.objects.all()
    serializer_class = CashOutHistorySerializer
    
    def get_queryset(self):
        """Lọc theo user nếu có"""
        queryset = super().get_queryset()
        
        user_id = self.request.headers.get("X-User-ID")
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        return queryset


class CashOutViewSet(viewsets.ViewSet):
    """ViewSet chính cho tính năng Cash Out"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cashout_service = CashOutService()
    
    @action(detail=False, methods=["post"])
    def request_quote(self, request):
        """Yêu cầu báo giá Cash Out"""
        try:
            serializer = CashOutRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            bet_slip_id = serializer.validated_data['bet_slip_id']
            bookmaker_type = serializer.validated_data['bookmaker_type']
            bookmaker_id = serializer.validated_data['bookmaker_id']
            
            # Lấy bet slip
            try:
                bet_slip = BetSlip.objects.get(id=bet_slip_id)
            except BetSlip.DoesNotExist:
                return Response({
                    "detail": "Bet slip không tồn tại"
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Kiểm tra tính đủ điều kiện
            eligibility = self.cashout_service.get_cash_out_eligibility(bet_slip)
            if not eligibility['can_cash_out']:
                return Response({
                    "detail": "Không thể Cash Out phiếu cược này",
                    "reasons": eligibility['reasons']
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Lấy event margin (trong thực tế sẽ lấy từ Risk Management Service)
            event_margin = self._get_event_margin(bet_slip)
            
            # Kiểm tra Cash Out trước trận đấu
            if bet_slip.can_cash_out_before_match:
                # Sử dụng logic Cash Out trước trận
                cash_out_data = self.cashout_service._calculate_before_match_cash_out(bet_slip, None)
            else:
                # TODO: Lấy live odds từ Risk Management Service
                # Hiện tại sử dụng mock data
                mock_live_odds = self._get_mock_live_odds(bet_slip)
                
                # Tính toán giá trị Cash Out với event margin
                cash_out_data = self.cashout_service.calculate_cash_out_value(
                    bet_slip, mock_live_odds, bookmaker_type, bookmaker_id, event_margin
                )
            
            # Tạo báo giá với thời gian hết hạn (10 giây)
            from datetime import timedelta
            expiry_time = timezone.now() + timedelta(seconds=10)
            
            quote_data = {
                'bet_slip_id': bet_slip_id,
                'fair_value': cash_out_data['fair_value'],
                'fee_amount': cash_out_data['fee_amount'],
                'fee_percentage': cash_out_data['fee_percentage'],
                'cash_out_value': cash_out_data['cash_out_value'],
                'expiry_time': expiry_time,
                'is_before_match': cash_out_data.get('is_before_match', False),
                'event_margin': float(event_margin) if event_margin else None,
                'bookmaker_config': {
                    'type': bookmaker_type,
                    'id': bookmaker_id,
                    'fee_percentage': float(cash_out_data['fee_percentage'])
                }
            }
            
            # Lưu báo giá vào session hoặc cache để xác nhận sau
            request.session[f'cashout_quote_{bet_slip_id}'] = {
                'data': cash_out_data,
                'expiry': expiry_time.isoformat()
            }
            
            return Response(quote_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "detail": f"Lỗi yêu cầu báo giá: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def _get_event_margin(self, bet_slip):
        """
        Lấy margin của sự kiện (trong thực tế sẽ lấy từ Risk Management Service)
        Hiện tại sử dụng mock data
        """
        # TODO: Tích hợp với Risk Management Service để lấy margin thực tế
        # Mock: margin 5% cho sự kiện
        return Decimal('0.05')
    
    @action(detail=False, methods=["post"])
    def confirm_cash_out(self, request):
        """Xác nhận và thực hiện Cash Out"""
        try:
            serializer = CashOutConfirmationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            cashout_history_id = serializer.validated_data['cashout_history_id']
            user_confirmation = serializer.validated_data['user_confirmation']
            
            if not user_confirmation:
                return Response({
                    "detail": "Người dùng không xác nhận Cash Out"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Lấy cashout history
            try:
                cashout_history = CashOutHistory.objects.get(id=cashout_history_id)
            except CashOutHistory.DoesNotExist:
                return Response({
                    "detail": "Lịch sử Cash Out không tồn tại"
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Kiểm tra xem có phải của user này không
            user_id = request.headers.get("X-User-ID")
            if not user_id or str(cashout_history.user.id) != str(user_id):
                return Response({
                    "detail": "Không có quyền truy cập"
                }, status=status.HTTP_403_FORBIDDEN)
            
            # TODO: Khởi tạo Saga transaction
            # Hiện tại xử lý trực tiếp
            
            # Lấy dữ liệu báo giá từ session
            bet_slip_id = cashout_history.bet_slip.id
            quote_key = f'cashout_quote_{bet_slip_id}'
            
            if quote_key not in request.session:
                return Response({
                    "detail": "Báo giá Cash Out đã hết hạn hoặc không tồn tại"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            quote_data = request.session[quote_key]
            
            # Kiểm tra thời gian hết hạn
            expiry_time = timezone.datetime.fromisoformat(quote_data['expiry'])
            if timezone.now() > expiry_time:
                # Xóa báo giá hết hạn
                del request.session[quote_key]
                return Response({
                    "detail": "Báo giá Cash Out đã hết hạn"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Hoàn thành Cash Out
            self.cashout_service.complete_cash_out(
                cashout_history, quote_data['data']
            )
            
            # Xóa báo giá đã sử dụng
            del request.session[quote_key]
            
            return Response({
                "message": "Cash Out thành công",
                "cash_out_value": quote_data['data']['cash_out_value'],
                "transaction_id": cashout_history.id
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "detail": f"Lỗi xác nhận Cash Out: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=["get"])
    def check_eligibility(self, request):
        """Kiểm tra tính đủ điều kiện Cash Out của một phiếu cược"""
        try:
            bet_slip_id = request.query_params.get('bet_slip_id')
            if not bet_slip_id:
                return Response({
                    "detail": "bet_slip_id là bắt buộc"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                bet_slip = BetSlip.objects.get(id=bet_slip_id)
            except BetSlip.DoesNotExist:
                return Response({
                    "detail": "Bet slip không tồn tại"
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Kiểm tra tính đủ điều kiện
            eligibility = self.cashout_service.get_cash_out_eligibility(bet_slip)
            
            # Bổ sung thông tin chi tiết
            eligibility.update({
                'cash_out_enabled': bet_slip.cash_out_enabled,
                'cash_out_before_match': bet_slip.cash_out_before_match,
                'bet_status': bet_slip.bet_status,
                'bet_type': bet_slip.bet_type
            })
            
            return Response(eligibility, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "detail": f"Lỗi kiểm tra tính đủ điều kiện: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def _get_mock_live_odds(self, bet_slip):
        """Tạo mock live odds data cho testing"""
        mock_odds = []
        
        for selection in bet_slip.selections.all():
            # Mock: giảm odds 20% để simulate live betting
            live_odds = selection.odd.value * Decimal('0.8')
            
            mock_odds.append({
                'match_id': selection.odd.match.id,
                'bet_type_id': selection.odd.bet_type.id,
                'outcome': selection.odd.outcome,
                'live_odds': live_odds
            })
        
        return mock_odds


@api_view(['POST'])
@permission_classes([AllowAny])
def sports_webhook_handler(request):
    """
    Webhook endpoint để nhận sự kiện từ sports data service
    """
    try:
        webhook_service = SportsDataWebhookService()
        result = webhook_service.process_webhook_event(request.data)
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Error processing sports webhook: {str(e)}")
        return Response({
            'error': 'Internal server error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def market_suspension_status(request, match_id):
    """
    Lấy trạng thái market suspension của match
    """
    try:
        service = AutomaticMarketSuspensionService()
        status_data = service.get_market_suspension_status(match_id)
        
        if 'error' in status_data:
            return Response(status_data, status=status.HTTP_404_NOT_FOUND)
        
        return Response(status_data)
        
    except Exception as e:
        logger.error(f"Error getting market suspension status: {str(e)}")
        return Response({
            'error': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def manual_market_suspension(request, match_id):
    """
    Tạm dừng market thủ công (Admin only)
    """
    try:
        if not request.user.has_perm('betting.can_suspend_markets'):
            return Response({
                'error': 'Permission denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        data = request.data
        reason = data.get('reason', 'Manual suspension by admin')
        duration = data.get('duration', 60)  # seconds
        
        service = AutomaticMarketSuspensionService()
        result = service.suspend_market_for_event(
            match_id=match_id,
            event_type='MANUAL',
            event_description=reason,
            suspension_duration=duration
        )
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Error in manual market suspension: {str(e)}")
        return Response({
            'error': 'Internal server error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resume_market_manually(request, match_id):
    """
    Khôi phục market thủ công (Admin only)
    """
    try:
        if not request.user.has_perm('betting.can_suspend_markets'):
            return Response({
                'error': 'Permission denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        odds_service = OddsManagementService()
        resumed_count = odds_service.resume_odds_for_match(match_id, request.user.id)
        
        return Response({
            'success': True,
            'message': f'Đã khôi phục {resumed_count} odds',
            'resumed_count': resumed_count
        })
        
    except Exception as e:
        logger.error(f"Error resuming market manually: {str(e)}")
        return Response({
            'error': 'Internal server error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BetSlipOwnershipViewSet(viewsets.ModelViewSet):
    """ViewSet quản lý quyền sở hữu phân mảnh phiếu cược"""
    
    queryset = BetSlipOwnership.objects.all()
    serializer_class = BetSlipOwnershipSerializer
    
    def get_queryset(self):
        """Lọc theo user nếu có"""
        user_id = self.request.headers.get("X-User-ID")
        if user_id:
            return BetSlipOwnership.objects.filter(owner__id=user_id, is_active=True)
        return BetSlipOwnership.objects.filter(is_active=True)
    
    @action(detail=False, methods=["post"])
    def split_bet_slip(self, request):
        """Chia nhỏ phiếu cược thành nhiều phần"""
        try:
            bet_slip_id = request.data.get('bet_slip_id')
            num_fractions = request.data.get('num_fractions')
            user_id = request.headers.get("X-User-ID")
            
            if not all([bet_slip_id, num_fractions, user_id]):
                return Response(
                    {"detail": "Thiếu thông tin: bet_slip_id, num_fractions, hoặc user_id"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            fractional_service = FractionalTradingService()
            
            bet_slip = BetSlip.objects.get(id=bet_slip_id)
            user = User.objects.get(id=user_id)
            
            fractions = fractional_service.split_bet_slip(bet_slip, num_fractions, user)
            
            return Response({
                "message": f"Đã chia nhỏ phiếu cược thành {num_fractions} phần",
                "fractions": BetSlipOwnershipSerializer(fractions, many=True).data
            }, status=status.HTTP_201_CREATED)
            
        except BetSlip.DoesNotExist:
            return Response({"detail": "Không tìm thấy phiếu cược"}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({"detail": "Không tìm thấy người dùng"}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": f"Lỗi: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=["post"])
    def merge_fractions(self, request):
        """Gộp các phần sở hữu nhỏ thành một phần lớn"""
        try:
            bet_slip_id = request.data.get('bet_slip_id')
            user_id = request.headers.get("X-User-ID")
            
            if not all([bet_slip_id, user_id]):
                return Response(
                    {"detail": "Thiếu thông tin: bet_slip_id hoặc user_id"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            fractional_service = FractionalTradingService()
            
            bet_slip = BetSlip.objects.get(id=bet_slip_id)
            user = User.objects.get(id=user_id)
            
            merged_ownership = fractional_service.merge_fractions(bet_slip, user)
            
            return Response({
                "message": "Đã gộp các phần sở hữu thành công",
                "merged_ownership": BetSlipOwnershipSerializer(merged_ownership).data
            }, status=status.HTTP_200_OK)
            
        except BetSlip.DoesNotExist:
            return Response({"detail": "Không tìm thấy phiếu cược"}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({"detail": "Không tìm thấy người dùng"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": f"Lỗi: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderBookViewSet(viewsets.ModelViewSet):
    """ViewSet quản lý sổ lệnh mua/bán P2P"""
    
    queryset = OrderBook.objects.all()
    serializer_class = OrderBookSerializer
    
    def get_queryset(self):
        """Lọc theo các tham số"""
        queryset = OrderBook.objects.all()
        
        # Lọc theo loại lệnh
        order_type = self.request.query_params.get('order_type')
        if order_type:
            queryset = queryset.filter(order_type=order_type)
        
        # Lọc theo trạng thái
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Lọc theo phiếu cược
        bet_slip_id = self.request.query_params.get('bet_slip_id')
        if bet_slip_id:
            queryset = queryset.filter(bet_slip_id=bet_slip_id)
        
        # Lọc theo user
        user_id = self.request.headers.get("X-User-ID")
        if user_id:
            queryset = queryset.filter(user__id=user_id)
        
        return queryset.order_by('-created_at')
    
    @action(detail=False, methods=["post"])
    def place_buy_order(self, request):
        """Đặt lệnh mua phiếu cược"""
        try:
            user_id = request.headers.get("X-User-ID")
            if not user_id:
                return Response({"detail": "Thiếu user_id"}, status=status.HTTP_400_BAD_REQUEST)
            
            marketplace_service = P2PMarketplaceService()
            
            user = User.objects.get(id=user_id)
            bet_slip = BetSlip.objects.get(id=request.data.get('bet_slip_id'))
            price = Decimal(request.data.get('price'))
            quantity = int(request.data.get('quantity'))
            expires_in_hours = int(request.data.get('expires_in_hours', 24))
            
            buy_order = marketplace_service.create_buy_order(
                user, bet_slip, price, quantity, expires_in_hours
            )
            
            return Response({
                "message": "Đặt lệnh mua thành công",
                "order": OrderBookSerializer(buy_order).data
            }, status=status.HTTP_201_CREATED)
            
        except User.DoesNotExist:
            return Response({"detail": "Không tìm thấy người dùng"}, status=status.HTTP_404_NOT_FOUND)
        except BetSlip.DoesNotExist:
            return Response({"detail": "Không tìm thấy phiếu cược"}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": f"Lỗi: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=["post"])
    def place_sell_order(self, request):
        """Đặt lệnh bán phiếu cược"""
        try:
            user_id = request.headers.get("X-User-ID")
            if not user_id:
                return Response({"detail": "Thiếu user_id"}, status=status.HTTP_400_BAD_REQUEST)
            
            marketplace_service = P2PMarketplaceService()
            
            user = User.objects.get(id=user_id)
            bet_slip = BetSlip.objects.get(id=request.data.get('bet_slip_id'))
            price = Decimal(request.data.get('price'))
            quantity = int(request.data.get('quantity'))
            allow_fractional = request.data.get('allow_fractional', True)
            expires_in_hours = int(request.data.get('expires_in_hours', 24))
            
            sell_order = marketplace_service.create_sell_order(
                user, bet_slip, price, quantity, allow_fractional, expires_in_hours
            )
            
            return Response({
                "message": "Đặt lệnh bán thành công",
                "order": OrderBookSerializer(sell_order).data
            }, status=status.HTTP_201_CREATED)
            
        except User.DoesNotExist:
            return Response({"detail": "Không tìm thấy người dùng"}, status=status.HTTP_404_NOT_FOUND)
        except BetSlip.DoesNotExist:
            return Response({"detail": "Không tìm thấy phiếu cược"}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": f"Lỗi: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=["post"])
    def cancel_order(self, request, pk=None):
        """Hủy lệnh đã đặt"""
        try:
            order = self.get_object()
            user_id = request.headers.get("X-User-ID")
            
            if not user_id or str(order.user.id) != user_id:
                return Response({"detail": "Không có quyền hủy lệnh này"}, status=status.HTTP_403_FORBIDDEN)
            
            if order.status != 'PENDING':
                return Response({"detail": "Chỉ có thể hủy lệnh đang chờ"}, status=status.HTTP_400_BAD_REQUEST)
            
            order.status = 'CANCELLED'
            order.save()
            
            return Response({"message": "Đã hủy lệnh thành công"}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"detail": f"Lỗi: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MarketSuspensionViewSet(viewsets.ModelViewSet):
    """ViewSet quản lý tạm khóa thị trường P2P"""
    
    queryset = MarketSuspension.objects.all()
    serializer_class = MarketSuspensionSerializer
    
    def get_queryset(self):
        """Lọc theo các tham số"""
        queryset = MarketSuspension.objects.all()
        
        # Lọc theo trạng thái
        suspension_status = self.request.query_params.get('status')
        if suspension_status:
            queryset = queryset.filter(status=suspension_status)
        
        # Lọc theo loại tạm khóa
        suspension_type = self.request.query_params.get('suspension_type')
        if suspension_type:
            queryset = queryset.filter(suspension_type=suspension_type)
        
        # Lọc theo trận đấu
        match_id = self.request.query_params.get('match_id')
        if match_id:
            queryset = queryset.filter(match_id=match_id)
        
        return queryset.order_by('-suspended_at')
    
    @action(detail=True, methods=["post"])
    def resume_market(self, request, pk=None):
        """Mở lại thị trường"""
        try:
            suspension = self.get_object()
            user_id = request.headers.get("X-User-ID")
            
            if user_id:
                user = User.objects.get(id=user_id)
                resumed = suspension.resume_market(user)
            else:
                resumed = suspension.resume_market()
            
            if resumed:
                return Response({"message": "Đã mở lại thị trường thành công"}, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "Không thể mở lại thị trường"}, status=status.HTTP_400_BAD_REQUEST)
                
        except User.DoesNotExist:
            return Response({"detail": "Không tìm thấy người dùng"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": f"Lỗi: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=["post"])
    def create_suspension(self, request):
        """Tạo tạm khóa thị trường mới"""
        try:
            user_id = request.headers.get("X-User-ID")
            if not user_id:
                return Response({"detail": "Thiếu user_id"}, status=status.HTTP_400_BAD_REQUEST)
            
            user = User.objects.get(id=user_id)
            request.data['created_by'] = user.id
            
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            suspension = serializer.save()
            
            return Response({
                "message": "Tạo tạm khóa thị trường thành công",
                "suspension": MarketSuspensionSerializer(suspension).data
            }, status=status.HTTP_201_CREATED)
            
        except User.DoesNotExist:
            return Response({"detail": "Không tìm thấy người dùng"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": f"Lỗi: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TradingSessionViewSet(viewsets.ModelViewSet):
    """ViewSet quản lý phiên giao dịch P2P"""
    
    queryset = TradingSession.objects.all()
    serializer_class = TradingSessionSerializer
    
    def get_queryset(self):
        """Lọc theo các tham số"""
        queryset = TradingSession.objects.all()
        
        # Lọc theo trạng thái
        session_status = self.request.query_params.get('status')
        if session_status:
            queryset = queryset.filter(status=session_status)
        
        # Lọc theo loại phiên
        session_type = self.request.query_params.get('session_type')
        if session_type:
            queryset = queryset.filter(session_type=session_type)
        
        # Lọc theo trận đấu
        match_id = self.request.query_params.get('match_id')
        if match_id:
            queryset = queryset.filter(match_id=match_id)
        
        return queryset.order_by('-start_time')
    
    @action(detail=True, methods=["post"])
    def start_collection_phase(self, request, pk=None):
        """Bắt đầu giai đoạn thu thập lệnh"""
        try:
            session = self.get_object()
            if session.start_collection_phase():
                return Response({"message": "Đã bắt đầu giai đoạn thu thập lệnh"}, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "Không thể bắt đầu giai đoạn thu thập lệnh"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": f"Lỗi: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=["post"])
    def start_matching_phase(self, request, pk=None):
        """Bắt đầu giai đoạn khớp lệnh"""
        try:
            session = self.get_object()
            if session.start_matching_phase():
                return Response({"message": "Đã bắt đầu giai đoạn khớp lệnh"}, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "Không thể bắt đầu giai đoạn khớp lệnh"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": f"Lỗi: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=["post"])
    def close_session(self, request, pk=None):
        """Kết thúc phiên giao dịch"""
        try:
            session = self.get_object()
            if session.close_session():
                return Response({"message": "Đã kết thúc phiên giao dịch"}, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "Không thể kết thúc phiên giao dịch"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": f"Lỗi: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class P2PTransactionViewSet(viewsets.ModelViewSet):
    """ViewSet quản lý giao dịch P2P"""
    
    queryset = P2PTransaction.objects.all()
    serializer_class = P2PTransactionSerializer
    
    def get_queryset(self):
        """Lọc theo các tham số"""
        queryset = P2PTransaction.objects.all()
        
        # Lọc theo trạng thái
        transaction_status = self.request.query_params.get('status')
        if transaction_status:
            queryset = queryset.filter(status=transaction_status)
        
        # Lọc theo loại giao dịch
        transaction_type = self.request.query_params.get('transaction_type')
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
        
        # Lọc theo phiếu cược
        bet_slip_id = self.request.query_params.get('bet_slip_id')
        if bet_slip_id:
            queryset = queryset.filter(bet_slip_id=bet_slip_id)
        
        # Lọc theo user (người mua hoặc người bán)
        user_id = self.request.headers.get("X-User-ID")
        if user_id:
            queryset = queryset.filter(
                models.Q(buyer__id=user_id) | models.Q(seller__id=user_id)
            )
        
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=["post"])
    def process_transaction(self, request, pk=None):
        """Xử lý giao dịch"""
        try:
            transaction = self.get_object()
            if transaction.process_transaction():
                return Response({"message": "Đã bắt đầu xử lý giao dịch"}, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "Không thể xử lý giao dịch"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": f"Lỗi: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=["post"])
    def complete_transaction(self, request, pk=None):
        """Hoàn thành giao dịch"""
        try:
            transaction = self.get_object()
            if transaction.complete_transaction():
                return Response({"message": "Đã hoàn thành giao dịch"}, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "Không thể hoàn thành giao dịch"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": f"Lỗi: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=["post"])
    def fail_transaction(self, request, pk=None):
        """Đánh dấu giao dịch thất bại"""
        try:
            transaction = self.get_object()
            error_message = request.data.get('error_message', '')
            if transaction.fail_transaction(error_message):
                return Response({"message": "Đã đánh dấu giao dịch thất bại"}, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "Không thể đánh dấu giao dịch thất bại"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": f"Lỗi: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MatchCancellationViewSet(viewsets.ModelViewSet):
    """ViewSet quản lý hủy/hoãn trận đấu và hoàn tiền tự động"""
    
    def get_queryset(self):
        """Lấy danh sách trận đấu có thể hủy/hoãn"""
        return Match.objects.filter(
            status__in=['SCHEDULED', 'LIVE', 'POSTPONED']
        ).order_by('-start_time')
    
    @action(detail=True, methods=["post"])
    def cancel_match(self, request, pk=None):
        """Hủy trận đấu và hoàn tiền toàn bộ"""
        try:
            match = self.get_object()
            reason = request.data.get('reason', 'Không có lý do cụ thể')
            
            # Khởi tạo service
            cancellation_service = MatchCancellationService()
            
            # Xử lý hủy trận đấu
            result = cancellation_service.handle_match_cancellation(
                match.id, 
                'CANCELLED', 
                reason
            )
            
            if result['success']:
                return Response({
                    'message': result['message'],
                    'refund_count': result.get('refund_count', 0),
                    'ownership_restored': result.get('ownership_restored', 0),
                    'match_status': 'CANCELLED'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'detail': f"Lỗi hủy trận đấu: {result.get('error', 'Unknown error')}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            return Response({
                'detail': f"Lỗi: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=["post"])
    def postpone_match(self, request, pk=None):
        """Hoãn trận đấu và tạm dừng giao dịch"""
        try:
            match = self.get_object()
            reason = request.data.get('reason', 'Không có lý do cụ thể')
            
            # Khởi tạo service
            cancellation_service = MatchCancellationService()
            
            # Xử lý hoãn trận đấu
            result = cancellation_service.handle_match_cancellation(
                match.id, 
                'POSTPONED', 
                reason
            )
            
            if result['success']:
                return Response({
                    'message': result['message'],
                    'next_steps': result.get('next_steps', ''),
                    'match_status': 'POSTPONED'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'detail': f"Lỗi hoãn trận đấu: {result.get('error', 'Unknown error')}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            return Response({
                'detail': f"Lỗi: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=["post"])
    def resume_postponed_match(self, request, pk=None):
        """Khôi phục trận đấu bị hoãn với thời gian mới"""
        try:
            match = self.get_object()
            new_start_time = request.data.get('new_start_time')
            
            if not new_start_time:
                return Response({
                    'detail': 'Thời gian bắt đầu mới là bắt buộc'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Parse thời gian mới
            try:
                from django.utils.dateparse import parse_datetime
                new_start_time = parse_datetime(new_start_time)
                if not new_start_time:
                    raise ValueError("Định dạng thời gian không hợp lệ")
            except Exception as e:
                return Response({
                    'detail': f'Định dạng thời gian không hợp lệ: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Khởi tạo service
            cancellation_service = MatchCancellationService()
            
            # Khôi phục trận đấu
            result = cancellation_service.resume_postponed_match(
                match.id, 
                new_start_time
            )
            
            if result['success']:
                return Response({
                    'message': result['message'],
                    'new_start_time': result['new_start_time'],
                    'match_status': 'SCHEDULED'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'detail': f"Lỗi khôi phục trận đấu: {result.get('error', 'Unknown error')}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            return Response({
                'detail': f"Lỗi: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=["get"])
    def cancellation_status(self, request, pk=None):
        """Lấy trạng thái hủy/hoãn của trận đấu"""
        try:
            match = self.get_object()
            
            # Lấy thông tin market suspension
            active_suspensions = MarketSuspension.objects.filter(
                match=match,
                status='ACTIVE'
            )
            
            # Lấy thông tin lệnh P2P bị tạm dừng
            suspended_orders = OrderBook.objects.filter(
                bet_slip__match=match,
                status='SUSPENDED'
            ).count()
            
            # Lấy thông tin cược đã hoàn tiền
            refunded_bets = BetSlip.objects.filter(
                match=match,
                bet_status='REFUNDED'
            ).count()
            
            return Response({
                'match_id': match.id,
                'match_status': match.status,
                'is_market_suspended': match.is_market_suspended,
                'suspension_reason': match.suspension_reason,
                'suspended_at': match.suspended_at,
                'active_suspensions': active_suspensions.count(),
                'suspended_p2p_orders': suspended_orders,
                'refunded_bets': refunded_bets,
                'can_resume': match.status == 'POSTPONED'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'detail': f"Lỗi: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=["get"])
    def cancelled_matches(self, request):
        """Lấy danh sách trận đấu đã bị hủy"""
        try:
            cancelled_matches = Match.objects.filter(
                status='CANCELLED'
            ).order_by('-updated_at')
            
            # Serialize data
            from .serializers import MatchSerializer
            serializer = MatchSerializer(cancelled_matches, many=True)
            
            return Response({
                'cancelled_matches': serializer.data,
                'total_count': cancelled_matches.count()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'detail': f"Lỗi: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=["get"])
    def postponed_matches(self, request):
        """Lấy danh sách trận đấu đã bị hoãn"""
        try:
            postponed_matches = Match.objects.filter(
                status='POSTPONED'
            ).order_by('-updated_at')
            
            # Serialize data
            from .serializers import MatchSerializer
            serializer = MatchSerializer(postponed_matches, many=True)
            
            return Response({
                'postponed_matches': serializer.data,
                'total_count': postponed_matches.count()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'detail': f"Lỗi: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Auto Order Management Views (Chốt Lời & Cắt Lỗ tự động)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def setup_auto_order(request):
    """Thiết lập lệnh tự động (Chốt Lời & Cắt Lỗ) cho phiếu cược"""
    try:
        from .serializers import AutoOrderSetupSerializer
        
        serializer = AutoOrderSetupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'detail': 'Dữ liệu không hợp lệ',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        bet_slip_id = serializer.validated_data['bet_slip_id']
        take_profit_threshold = serializer.validated_data.get('take_profit_threshold')
        stop_loss_threshold = serializer.validated_data.get('stop_loss_threshold')
        
        # Kiểm tra quyền sở hữu phiếu cược
        try:
            bet_slip = BetSlip.objects.get(
                id=bet_slip_id,
                user=request.user
            )
        except BetSlip.DoesNotExist:
            return Response({
                'detail': 'Phiếu cược không tồn tại hoặc không thuộc quyền sở hữu của bạn'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Kiểm tra xem có thể thiết lập lệnh tự động không
        if not bet_slip.can_setup_auto_order:
            return Response({
                'detail': 'Phiếu cược này không thể thiết lập lệnh tự động'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Thiết lập lệnh tự động
        try:
            bet_slip.setup_auto_order(
                take_profit_threshold=take_profit_threshold,
                stop_loss_threshold=stop_loss_threshold
            )
            
            return Response({
                'success': True,
                'message': 'Lệnh tự động đã được thiết lập thành công',
                'bet_slip_id': bet_slip.id,
                'auto_order_status': bet_slip.auto_order_status,
                'take_profit_threshold': take_profit_threshold,
                'stop_loss_threshold': stop_loss_threshold
            }, status=status.HTTP_201_CREATED)
            
        except ValueError as e:
            return Response({
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Lỗi thiết lập lệnh tự động: {e}")
        return Response({
            'detail': f"Lỗi hệ thống: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_auto_order(request):
    """Hủy lệnh tự động"""
    try:
        bet_slip_id = request.data.get('bet_slip_id')
        
        if not bet_slip_id:
            return Response({
                'detail': 'Thiếu bet_slip_id'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Kiểm tra quyền sở hữu
        try:
            bet_slip = BetSlip.objects.get(
                id=bet_slip_id,
                user=request.user
            )
        except BetSlip.DoesNotExist:
            return Response({
                'detail': 'Phiếu cược không tồn tại hoặc không thuộc quyền sở hữu của bạn'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Hủy lệnh tự động
        bet_slip.cancel_auto_order()
        
        return Response({
            'success': True,
            'message': 'Lệnh tự động đã được hủy thành công',
            'bet_slip_id': bet_slip.id
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Lỗi hủy lệnh tự động: {e}")
        return Response({
            'detail': f"Lỗi hệ thống: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_auto_order_status(request, bet_slip_id):
    """Lấy trạng thái lệnh tự động của phiếu cược"""
    try:
        # Kiểm tra quyền sở hữu
        try:
            bet_slip = BetSlip.objects.get(
                id=bet_slip_id,
                user=request.user
            )
        except BetSlip.DoesNotExist:
            return Response({
                'detail': 'Phiếu cược không tồn tại hoặc không thuộc quyền sở hữu của bạn'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Lấy giá trị Cash Out hiện tại
        from .services import CashOutService
        cashout_service = CashOutService()
        
        try:
            current_cashout = cashout_service.calculate_cash_out_value(
                bet_slip=bet_slip,
                live_odds_data={},  # Sẽ được cập nhật sau
                bookmaker_type='SYSTEM',
                bookmaker_id='system'
            )
            current_cashout_value = current_cashout.get('cash_out_value')
        except:
            current_cashout_value = None
        
        # Tạo response data
        from .serializers import AutoOrderStatusSerializer
        
        status_data = {
            'bet_slip_id': bet_slip.id,
            'auto_order_status': bet_slip.auto_order_status,
            'take_profit_threshold': bet_slip.take_profit_threshold,
            'stop_loss_threshold': bet_slip.stop_loss_threshold,
            'auto_order_created_at': bet_slip.auto_order_created_at,
            'auto_order_triggered_at': bet_slip.auto_order_triggered_at,
            'auto_order_reason': bet_slip.auto_order_reason,
            'auto_order_enabled': bet_slip.auto_order_enabled,
            'current_cashout_value': current_cashout_value,
            'can_setup_auto_order': bet_slip.can_setup_auto_order,
            'has_active_auto_order': bet_slip.has_active_auto_order
        }
        
        serializer = AutoOrderStatusSerializer(data=status_data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({
                'detail': 'Lỗi serialize dữ liệu',
                'errors': serializer.errors
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Lỗi lấy trạng thái lệnh tự động: {e}")
        return Response({
            'detail': f"Lỗi hệ thống: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_auto_orders(request):
    """Lấy danh sách lệnh tự động của người dùng"""
    try:
        # Lấy tất cả phiếu cược có lệnh tự động của người dùng
        auto_orders = BetSlip.objects.filter(
            user=request.user,
            auto_order_enabled=True
        ).order_by('-auto_order_created_at')
        
        # Serialize data
        from .serializers import BetSlipSerializer
        serializer = BetSlipSerializer(auto_orders, many=True)
        
        return Response({
            'auto_orders': serializer.data,
            'total_count': auto_orders.count()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Lỗi lấy danh sách lệnh tự động: {e}")
        return Response({
            'detail': f"Lỗi hệ thống: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_auto_order_statistics(request):
    """Lấy thống kê về lệnh tự động (Admin only)"""
    try:
        # Kiểm tra quyền admin
        if not request.user.is_staff:
            return Response({
                'detail': 'Bạn không có quyền truy cập thông tin này'
            }, status=status.HTTP_403_FORBIDDEN)
        
        from .services import AutoCashoutMonitorService
        monitor_service = AutoCashoutMonitorService()
        
        stats = monitor_service.get_auto_order_statistics()
        stats['last_updated'] = timezone.now()
        
        from .serializers import AutoOrderStatisticsSerializer
        serializer = AutoOrderStatisticsSerializer(data=stats)
        
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({
                'detail': 'Lỗi serialize dữ liệu',
                'errors': serializer.errors
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Lỗi lấy thống kê lệnh tự động: {e}")
        return Response({
            'detail': f"Lỗi hệ thống: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_auto_monitoring(request):
    """Bắt đầu giám sát tự động (Admin only)"""
    try:
        # Kiểm tra quyền admin
        if not request.user.is_staff:
            return Response({
                'detail': 'Bạn không có quyền thực hiện hành động này'
            }, status=status.HTTP_403_FORBIDDEN)
        
        from .services import AutoCashoutMonitorService
        monitor_service = AutoCashoutMonitorService()
        
        result = monitor_service.start_monitoring()
        
        if result['success']:
            return Response({
                'success': True,
                'message': 'Đã bắt đầu giám sát tự động',
                'processed_count': result.get('processed', 0)
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'detail': f"Lỗi giám sát tự động: {result.get('error', 'Unknown error')}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Lỗi bắt đầu giám sát tự động: {e}")
        return Response({
            'detail': f"Lỗi hệ thống: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)