from django.utils import timezone
from decimal import Decimal
from django.conf import settings
import requests
import logging
import asyncio
import time
from typing import Dict, List, Optional, Tuple
from django.db.models import Sum
from .models import (
    Odd, Match, CashOutConfiguration, CashOutHistory,
    BetSlip, OrderBook, P2PTransaction, BetSlipOwnership, MarketSuspension
)
import os

logger = logging.getLogger(__name__)

class OddsManagementService:
    """Service quản lý odds và cập nhật tỷ lệ cược"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def suspend_odds_for_match(self, match_id, reason, user):
        """Tạm dừng tất cả odds của một match"""
        try:
            odds = Odd.objects.filter(match_id=match_id, is_active=True)
            suspended_count = odds.update(is_active=False)
            
            # Log suspension
            for odd in odds:
                self.logger.info(f"Odds {odd.id} suspended: {reason}")
            
            return suspended_count
            
        except Exception as e:
            self.logger.error(f"Error suspending odds for match {match_id}: {e}")
            return 0
    
    def resume_odds_for_match(self, match_id, user):
        """Khôi phục tất cả odds của một match"""
        try:
            odds = Odd.objects.filter(match_id=match_id, is_active=False)
            resumed_count = odds.update(is_active=True)
            
            # Log resumption
            for odd in odds:
                self.logger.info(f"Odds {odd.id} resumed")
            
            return resumed_count
            
        except Exception as e:
            self.logger.error(f"Error resuming odds for match {match_id}: {e}")
            return 0
    
    def adjust_odds_manually(self, odd, new_value, reason, user):
        """Điều chỉnh odds thủ công"""
        try:
            old_value = odd.value
            odd.value = new_value
            odd.save()
            
            self.logger.info(f"Odds {odd.id} adjusted from {old_value} to {new_value}: {reason}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adjusting odds {odd.id}: {e}")
            return False

class BetPlacementService:
    """Service xử lý logic đặt cược phức tạp"""
    
    def __init__(self):
        self.risk_check_service = RiskCheckService()
    
    @staticmethod
    def calculate_potential_payout(bet_type: str, selections: List[Dict], total_stake: Decimal) -> Decimal:
        """Tính toán potential payout theo loại bet"""
        if bet_type == 'SINGLE':
            return total_stake * selections[0]['odds']
        elif bet_type == 'MULTIPLE':
            total_odds = sum(selection['odds'] for selection in selections)
            return total_stake * (total_odds / len(selections))
        elif bet_type == 'PARLAY':
            total_odds = Decimal('1.0')
            for selection in selections:
                total_odds *= selection['odds']
            return total_stake * total_odds
        elif bet_type == 'SYSTEM':
            # System bet calculation (simplified)
            return total_stake * Decimal('2.0')  # Placeholder
        else:
            return total_stake
    
    @staticmethod
    def validate_bet_selections(selections: List[Dict]) -> Tuple[bool, str]:
        """Validate bet selections"""
        if not selections:
            return False, "Không có selection nào được chọn"
        
        for selection in selections:
            if 'odd_id' not in selection or 'stake' not in selection:
                return False, "Thiếu thông tin odd_id hoặc stake"
            
            try:
                odd = Odd.objects.get(id=selection['odd_id'])
                if not odd.is_active or odd.odds_status != 'ACTIVE':
                    return False, f"Odds {odd.id} không hoạt động"
            except Odd.DoesNotExist:
                return False, f"Không tìm thấy odds {selection['odd_id']}"
        
        return True, "Validation thành công"
    
    def validate_bet_with_risk_check(self, user, selections_data: List[Dict], total_stake: Decimal) -> Dict:
        """Validation bet với kiểm tra rủi ro từ Risk Management Service"""
        try:
            # Validation cơ bản trước
            basic_validation, message = self.validate_bet_selections(selections_data)
            if not basic_validation:
                return {
                    'valid': False,
                    'errors': [message],
                    'risk_check': None
                }
            
            # Kiểm tra rủi ro cho từng selection
            risk_results = []
            for selection in selections_data:
                risk_data = {
                    'user_id': user.id,
                    'match_id': selection['match_id'],
                    'bet_type_id': selection['bet_type_id'],
                    'outcome': selection['outcome'],
                    'stake_amount': float(selection['stake_amount']),
                    'odds_value': float(selection['odds_value'])
                }
                
                risk_result = self.risk_check_service.check_bet_risk(risk_data)
                risk_results.append(risk_result)
                
                # Nếu có lỗi kết nối, sử dụng fallback
                if risk_result.get('fallback'):
                    logger.warning(f"Using fallback risk check for selection {selection.get('odd_id')}")
                    continue
                
                # Nếu không được chấp nhận, trả về lý do
                if not risk_result.get('approved'):
                    return {
                        'valid': False,
                        'errors': [risk_result.get('rejection_reason', 'Bet bị từ chối do rủi ro')],
                        'risk_check': risk_result,
                        'recommendations': risk_result.get('recommendations', [])
                    }
            
            # Tất cả selections đều được chấp nhận
            return {
                'valid': True,
                'errors': [],
                'risk_check': {
                    'approved': True,
                    'risk_level': 'LOW',
                    'recommendations': ['Bet được chấp nhận, rủi ro trong ngưỡng cho phép']
                }
            }
            
        except Exception as e:
            logger.error(f"Error in validate_bet_with_risk_check: {str(e)}")
            return {
                'valid': False,
                'errors': [f'Lỗi kiểm tra rủi ro: {str(e)}'],
                'risk_check': None
            }

class DynamicOddsService:
    """Service quản lý odds động dựa trên risk/liability"""
    
    def __init__(self):
        from shared.base_settings import get_service_url
        self.risk_service_url = get_service_url('risk')
        self.odds_update_threshold = getattr(settings, 'ODDS_UPDATE_THRESHOLD', Decimal('0.01'))
    
    def calculate_risk_based_odds(self, odd: Odd, current_liability: Decimal) -> Optional[Decimal]:
        """Tính toán odds mới dựa trên rủi ro hiện tại"""
        try:
            if odd.odds_type != 'RISK_BASED':
                return None
            
            if not odd.liability_threshold:
                return None
            
            # Tính toán risk ratio
            risk_ratio = current_liability / odd.liability_threshold
            
            if risk_ratio <= 1.0:
                # Rủi ro trong ngưỡng cho phép, giữ nguyên odds
                return odd.value
            
            # Rủi ro vượt ngưỡng, điều chỉnh odds
            risk_multiplier = min(risk_ratio, 2.0)  # Giới hạn tối đa 2x
            new_value = odd.base_value * risk_multiplier
            
            # Áp dụng giới hạn min/max
            if odd.min_value and new_value < odd.min_value:
                new_value = odd.min_value
            if odd.max_value and new_value > odd.max_value:
                new_value = odd.max_value
            
            return new_value
            
        except Exception as e:
            logger.error(f"Lỗi tính toán risk-based odds: {e}")
            return None
    
    def update_odds_for_risk(self, odd: Odd, new_liability: Decimal) -> bool:
        """Cập nhật odds dựa trên rủi ro mới"""
        try:
            new_value = self.calculate_risk_based_odds(odd, new_liability)
            
            if new_value is None or abs(new_value - odd.value) < self.odds_update_threshold:
                return False
            
            # Cập nhật odds
            old_value = odd.value
            odd.value = new_value
            odd.save()
            
            # Ghi log thay đổi
            logger.info(f"Odds {odd.id} updated from {old_value} to {new_value} due to risk")
            
            return True
            
        except Exception as e:
            logger.error(f"Lỗi cập nhật odds: {e}")
            return False

class CashOutService:
    """Service xử lý logic Cash Out - TÍCH HỢP HOÀN CHỈNH"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Service URLs từ cấu hình tập trung
        from shared.base_settings import get_service_url
        self.risk_service_url = get_service_url('risk')
        self.wallet_service_url = get_service_url('wallet')
        self.saga_service_url = get_service_url('saga')
    
    def calculate_cash_out_value(self, bet_slip, live_odds_data, bookmaker_type='SYSTEM', bookmaker_id='system', event_margin=None):
        """
        Tính toán giá trị Cash Out dựa trên công thức:
        Giá trị Cash Out = Giá trị Công Bằng × (1 − Phí Cash Out)
        Giá trị Công Bằng = Tiền cược gốc × Tỷ lệ cược gốc / Tỷ lệ cược trực tiếp
        
        Logic phí theo mô tả:
        - Nhà cái hệ thống: sử dụng margin của sự kiện nếu không có phí cụ thể
        - Nhà cái cá nhân/nhóm: phí tối thiểu 0%
        - Cash Out trước trận: không mất phí, chỉ hoàn lại tiền gốc
        """
        try:
            # Lấy cấu hình phí Cash Out
            config = CashOutConfiguration.get_config_for_bookmaker(bookmaker_type, bookmaker_id)
            if not config or not config.is_valid:
                raise ValueError("Không tìm thấy cấu hình Cash Out hợp lệ")
            
            # Kiểm tra xem có thể Cash Out không
            if not bet_slip.can_cash_out:
                raise ValueError("Phiếu cược không thể Cash Out")
            
            # Kiểm tra Cash Out trước trận đấu
            if bet_slip.can_cash_out_before_match:
                return self._calculate_before_match_cash_out(bet_slip, config)
            
            # Tính toán giá trị công bằng
            fair_value = self._calculate_fair_value(bet_slip, live_odds_data)
            
            # Tính phí Cash Out theo logic đúng
            fee_amount = config.get_cash_out_fee(fair_value, event_margin)
            fee_percentage = config.get_fee_percentage_for_display(event_margin)
            
            # Tính giá trị Cash Out cuối cùng
            cash_out_value = fair_value - fee_amount
            
            # Kiểm tra giới hạn min/max
            if config.min_cash_out_amount and cash_out_value < config.min_cash_out_amount:
                cash_out_value = config.min_cash_out_amount
            elif config.max_cash_out_amount and cash_out_value > config.max_cash_out_amount:
                cash_out_value = config.max_cash_out_amount
            
            # Đảm bảo không âm
            if cash_out_value < 0:
                cash_out_value = Decimal('0.00')
            
            return {
                'fair_value': fair_value,
                'fee_amount': fee_amount,
                'fee_percentage': fee_percentage,
                'cash_out_value': cash_out_value,
                'config': config,
                'is_before_match': False,
                'event_margin': event_margin
            }
            
        except Exception as e:
            self.logger.error(f"Lỗi tính toán Cash Out: {e}")
            raise
    
    def _calculate_before_match_cash_out(self, bet_slip, config):
        """
        Tính toán Cash Out trước khi trận đấu bắt đầu:
        - Không mất phí
        - Chỉ hoàn lại tiền cược gốc
        - Không tính khoản thưởng chiến thắng tiềm năng
        """
        return {
            'fair_value': bet_slip.total_stake,  # Chỉ hoàn lại tiền gốc
            'fee_amount': Decimal('0.00'),      # Không mất phí
            'fee_percentage': Decimal('0.00'),  # 0%
            'cash_out_value': bet_slip.total_stake,  # = tiền gốc
            'config': config,
            'is_before_match': True,
            'event_margin': None
        }
    
    def _calculate_fair_value(self, bet_slip, live_odds_data):
        """Tính giá trị công bằng của phiếu cược"""
        if bet_slip.bet_type == 'SINGLE':
            return self._calculate_single_bet_fair_value(bet_slip, live_odds_data)
        elif bet_slip.bet_type == 'PARLAY':
            return self._calculate_parlay_fair_value(bet_slip, live_odds_data)
        else:
            # Các loại cược khác chưa hỗ trợ
            raise ValueError(f"Loại cược {bet_slip.bet_type} chưa hỗ trợ Cash Out")
    
    def _calculate_single_bet_fair_value(self, bet_slip, live_odds_data):
        """Tính giá trị công bằng cho cược đơn"""
        selection = bet_slip.selections.first()
        if not selection:
            raise ValueError("Không tìm thấy selection cho cược đơn")
        
        # Lấy odds gốc và live odds
        original_odds = selection.odds_at_placement
        live_odds = self._get_live_odds_for_selection(selection, live_odds_data)
        
        if not live_odds:
            raise ValueError("Không thể lấy live odds cho selection")
        
        # Công thức: Tiền cược gốc × Tỷ lệ cược gốc / Tỷ lệ cược trực tiếp
        fair_value = bet_slip.total_stake * (original_odds / live_odds)
        
        return fair_value
    
    def _calculate_parlay_fair_value(self, bet_slip, live_odds_data):
        """Tính giá trị công bằng cho cược xâu"""
        total_fair_value = Decimal('0.00')
        total_original_odds = Decimal('1.00')
        total_live_odds = Decimal('1.00')
        
        for selection in bet_slip.selections.all():
            # Kiểm tra xem selection có thua chưa
            if selection.is_lost:
                # Nếu đã thua thì không thể Cash Out
                raise ValueError("Cược xâu đã thua, không thể Cash Out")
            
            # Lấy odds gốc và live odds
            original_odds = selection.odds_at_placement
            live_odds = self._get_live_odds_for_selection(selection, live_odds_data)
            
            if not live_odds:
                raise ValueError(f"Không thể lấy live odds cho selection {selection.id}")
            
            # Nhân dồn odds
            total_original_odds *= original_odds
            total_live_odds *= live_odds
        
        # Công thức: Tiền cược gốc × Tỷ lệ cược gốc / Tỷ lệ cược trực tiếp
        fair_value = bet_slip.total_stake * (total_original_odds / total_live_odds)
        
        return fair_value
    
    def _get_live_odds_for_selection(self, selection, live_odds_data):
        """Lấy live odds cho một selection cụ thể"""
        # Tìm live odds trong dữ liệu từ Risk Management Service
        for odds_info in live_odds_data:
            if (odds_info.get('match_id') == selection.odd.match.id and
                odds_info.get('bet_type_id') == selection.odd.bet_type.id and
                odds_info.get('outcome') == selection.odd.outcome):
                return Decimal(str(odds_info.get('live_odds', 0)))
        
        # Nếu không tìm thấy, trả về odds hiện tại
        return selection.odd.value
    
    def get_live_odds_from_risk_service(self, bet_slip):
        """Lấy live odds từ Risk Management Service"""
        try:
            live_odds_data = []
            risk_check_service = RiskCheckService()
            
            for selection in bet_slip.selections.all():
                # Sử dụng RiskCheckService để lấy live odds
                odds_request = {
                    'match_id': selection.odd.match.id,
                    'bet_type_id': selection.odd.bet_type.id,
                    'outcome': selection.odd.outcome
                }
                
                live_odds = risk_check_service.get_live_odds(odds_request)
                
                if 'error' not in live_odds:
                    live_odds_data.append({
                        'match_id': live_odds['match_id'],
                        'bet_type_id': live_odds['bet_type_id'],
                        'outcome': live_odds['outcome'],
                        'live_odds': live_odds['live_odds'],
                        'confidence_score': live_odds['confidence_score'],
                        'is_reliable_for_cashout': live_odds['is_reliable_for_cashout']
                    })
                else:
                    self.logger.warning(f"Không thể lấy live odds cho selection {selection.id}: {live_odds.get('error')}")
                    # Sử dụng odds hiện tại nếu không thể lấy live odds
                    live_odds_data.append({
                        'match_id': selection.odd.match.id,
                        'bet_type_id': selection.odd.bet_type.id,
                        'outcome': selection.odd.outcome,
                        'live_odds': selection.odd.value,
                        'confidence_score': 0.5,
                        'is_reliable_for_cashout': False
                    })
            
            return live_odds_data
            
        except Exception as e:
            self.logger.error(f"Lỗi lấy live odds từ Risk Management Service: {e}")
            # Fallback: sử dụng odds hiện tại
            return self._get_fallback_live_odds(bet_slip)
    
    def get_event_margin_from_risk_service(self, bet_slip):
        """Lấy event margin từ Risk Management Service"""
        try:
            # Lấy match đầu tiên để xác định event
            first_selection = bet_slip.selections.first()
            if not first_selection:
                return Decimal('0.05')  # Margin mặc định
            
            match_id = first_selection.odd.match.id
            
            # Sử dụng RiskCheckService để lấy event margin
            risk_check_service = RiskCheckService()
            margin_info = risk_check_service.get_event_margin(match_id)
            
            if 'error' not in margin_info:
                return Decimal(str(margin_info['effective_margin']))
            else:
                self.logger.warning(f"Không thể lấy event margin cho match {match_id}: {margin_info.get('error')}")
                return Decimal('0.05')  # Margin mặc định
                
        except Exception as e:
            self.logger.error(f"Lỗi lấy event margin từ Risk Management Service: {e}")
            return Decimal('0.05')  # Margin mặc định
    
    def _get_fallback_live_odds(self, bet_slip):
        """Fallback: tạo mock live odds data khi không thể kết nối Risk Management Service"""
        mock_odds = []
        
        for selection in bet_slip.selections.all():
            # Mock: giảm odds 20% để simulate live betting
            live_odds = selection.odd.value * Decimal('0.8')
            
            mock_odds.append({
                'match_id': selection.odd.match.id,
                'bet_type_id': selection.odd.bet_type.id,
                'outcome': selection.odd.outcome,
                'live_odds': live_odds,
                'confidence_score': 0.5,
                'is_reliable': False
            })
        
        return mock_odds
    
    def process_cash_out_request(self, bet_slip, user_id, bookmaker_type='SYSTEM', bookmaker_id='system'):
        """Xử lý yêu cầu Cash Out - TÍCH HỢP SAGA PATTERN"""
        try:
            # Tạo record lịch sử
            cashout_history = CashOutHistory.objects.create(
                bet_slip=bet_slip,
                user_id=user_id,
                status='REQUESTED',
                requested_amount=bet_slip.total_stake,  # Tạm thời, sẽ cập nhật sau
                original_odds=bet_slip.selections.first().odds_at_placement if bet_slip.selections.exists() else Decimal('0.00')
            )
            
            # Cập nhật trạng thái bet slip thành 'CASHING_OUT'
            bet_slip.bet_status = 'CASHING_OUT'
            bet_slip.cash_out_requested_at = timezone.now()
            bet_slip.save()
            
            # Khởi tạo Saga transaction nếu có kết nối
            saga_transaction_id = self._initiate_cashout_saga(bet_slip, user_id, cashout_history.id)
            if saga_transaction_id:
                cashout_history.saga_transaction_id = saga_transaction_id
                cashout_history.save()
            
            return cashout_history
            
        except Exception as e:
            self.logger.error(f"Lỗi xử lý yêu cầu Cash Out: {e}")
            raise
    
    def _initiate_cashout_saga(self, bet_slip, user_id, cashout_history_id):
        """Khởi tạo Cash Out Saga transaction"""
        try:
            # Gọi API Saga Orchestrator để khởi tạo saga
            response = requests.post(
                f"{self.saga_service_url}/api/sagas/cashout/start/",
                json={
                    'bet_slip_id': bet_slip.id,
                    'user_id': user_id,
                    'bookmaker_type': 'SYSTEM',  # Mặc định là nhà cái hệ thống
                    'bookmaker_id': 'system'
                },
                timeout=10
            )
            
            if response.status_code == 201:  # 201 Created
                saga_info = response.json()
                return saga_info.get('saga_transaction_id')
            else:
                self.logger.warning(f"Không thể khởi tạo saga: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Lỗi khởi tạo saga: {e}")
            return None
    
    def complete_cash_out(self, cashout_history, cash_out_data, wallet_transaction_id=None):
        """Hoàn thành giao dịch Cash Out - TÍCH HỢP WALLET SERVICE"""
        try:
            # Cập nhật lịch sử
            cashout_history.final_amount = cash_out_data['cash_out_value']
            cashout_history.fair_value = cash_out_data['fair_value']
            cashout_history.fee_amount = cash_out_data['fee_amount']
            cashout_history.fee_percentage = cash_out_data['fee_percentage']
            cashout_history.live_odds = cash_out_data.get('live_odds', Decimal('0.00'))
            cashout_history.wallet_transaction_id = wallet_transaction_id
            cashout_history.mark_completed(wallet_transaction_id)
            
            # Cập nhật bet slip
            bet_slip = cashout_history.bet_slip
            bet_slip.process_cash_out(
                cash_out_data['cash_out_value'],
                cash_out_data['fair_value'],
                cash_out_data['fee_amount'],
                cash_out_data['fee_percentage']
            )
            
            # Cập nhật live odds cho các selections
            for selection in bet_slip.selections.all():
                if 'live_odds' in cash_out_data:
                    selection.update_live_odds(cash_out_data['live_odds'])
            
            # Cập nhật liability trong Risk Management Service
            self._update_liability_in_risk_service(bet_slip, cash_out_data)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Lỗi hoàn thành Cash Out: {e}")
            # Đánh dấu thất bại
            cashout_history.mark_failed(str(e))
            raise
    
    def _update_liability_in_risk_service(self, bet_slip, cash_out_data):
        """Cập nhật liability trong Risk Management Service"""
        try:
            # Gọi API Risk Management Service để cập nhật liability
            response = requests.post(
                f"{self.risk_service_url}/api/cashout/liability/update/",
                json={
                    'bet_slip_id': bet_slip.id,
                    'cashout_amount': float(cash_out_data['cash_out_value']),
                    'action': 'PROCESS_CASHOUT'
                },
                timeout=15
            )
            
            if response.status_code != 200:
                self.logger.warning(f"Không thể cập nhật liability: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Lỗi cập nhật liability: {e}")
    
    def cancel_cash_out(self, cashout_history, reason=""):
        """Hủy yêu cầu Cash Out"""
        try:
            # Cập nhật lịch sử
            cashout_history.mark_cancelled(reason)
            
            # Khôi phục bet slip
            bet_slip = cashout_history.bet_slip
            bet_slip.bet_status = 'CONFIRMED'
            bet_slip.cash_out_requested_at = None
            bet_slip.save()
            
            # Hủy saga transaction nếu có
            if cashout_history.saga_transaction_id:
                self._cancel_cashout_saga(cashout_history.saga_transaction_id)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Lỗi hủy Cash Out: {e}")
            raise
    
    def _cancel_cashout_saga(self, saga_transaction_id):
        """Hủy Cash Out Saga transaction"""
        try:
            # Gọi API Saga Orchestrator để hủy saga
            response = requests.post(
                f"{self.saga_service_url}/api/sagas/cashout/cancel/",
                json={'saga_transaction_id': saga_transaction_id},
                timeout=10
            )
            
            if response.status_code != 200:
                self.logger.warning(f"Không thể hủy saga: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Lỗi hủy saga: {e}")
    
    def get_cash_out_eligibility(self, bet_slip):
        """Kiểm tra tính đủ điều kiện Cash Out của một phiếu cược - BỔ SUNG QUY TẮC NGHIỆP VỤ"""
        eligibility = {
            'can_cash_out': bet_slip.can_cash_out,
            'reasons': []
        }
        
        if not bet_slip.cash_out_enabled:
            eligibility['reasons'].append('Tính năng Cash Out bị tắt cho phiếu cược này')
        
        if bet_slip.bet_status not in ['CONFIRMED']:
            eligibility['reasons'].append(f'Trạng thái phiếu cược không phù hợp: {bet_slip.bet_status}')
        
        if bet_slip.is_settled:
            eligibility['reasons'].append('Phiếu cược đã được thanh toán')
        
        # Kiểm tra cược xâu
        if bet_slip.bet_type == 'PARLAY':
            for selection in bet_slip.selections.all():
                if selection.is_lost:
                    eligibility['reasons'].append('Cược xâu đã thua, không thể Cash Out')
                    break
        
        # BỔ SUNG: Kiểm tra sự kiện quan trọng vừa xảy ra
        if self._has_important_event_occurred(bet_slip):
            eligibility['can_cash_out'] = False
            eligibility['reasons'].append('Sự kiện quan trọng vừa xảy ra, thị trường bị tạm khóa')
        
        # BỔ SUNG: Kiểm tra live odds có đáng tin cậy không
        if not self._are_live_odds_reliable(bet_slip):
            eligibility['can_cash_out'] = False
            eligibility['reasons'].append('Live odds không đáng tin cậy để Cash Out')
        
        return eligibility
    
    def _has_important_event_occurred(self, bet_slip):
        """Kiểm tra xem có sự kiện quan trọng vừa xảy ra không"""
        try:
            # Kiểm tra từ Risk Management Service
            for selection in bet_slip.selections.all():
                match = selection.odd.match
                
                # Gọi API để kiểm tra trạng thái thị trường
                response = requests.get(
                    f"{self.risk_service_url}/api/live-odds/?match_id={match.id}&reliable_only=true",
                    timeout=10
                )
                
                if response.status_code == 200:
                    live_odds_list = response.json()
                    for live_odds in live_odds_list:
                        if (live_odds['match_id'] == match.id and
                            live_odds['bet_type_id'] == selection.odd.bet_type.id and
                            live_odds['outcome'] == selection.odd.outcome):
                            # Kiểm tra xem thị trường có bị tạm khóa không
                            if live_odds.get('is_market_suspended', False):
                                return True
                            break
                
        except Exception as e:
            self.logger.error(f"Lỗi kiểm tra sự kiện quan trọng: {e}")
        
        return False
    
    def _are_live_odds_reliable(self, bet_slip):
        """Kiểm tra xem live odds có đáng tin cậy không"""
        try:
            # Gọi API Risk Management Service để kiểm tra độ tin cậy
            for selection in bet_slip.selections.all():
                response = requests.post(
                    f"{self.risk_service_url}/api/cashout/live-odds/",
                    json={
                        'match_id': selection.odd.match.id,
                        'bet_type_id': selection.odd.bet_type.id,
                        'outcome': selection.odd.outcome
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    odds_info = response.json()
                    if not odds_info.get('is_reliable_for_cashout', False):
                        return False
                else:
                    # Nếu không thể kết nối, coi như không đáng tin cậy
                    return False
                    
        except Exception as e:
            self.logger.error(f"Lỗi kiểm tra độ tin cậy live odds: {e}")
            return False
        
        return True

class AutomaticMarketSuspensionService:
    """Service tự động quản lý market suspension khi có sự kiện bóng đá"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def suspend_market_for_event(self, match_id, event_type, event_description, suspension_duration=60):
        """
        Tự động tạm dừng market khi có sự kiện quan trọng
        
        Args:
            match_id: ID trận đấu
            event_type: Loại sự kiện (GOAL, RED_CARD, PENALTY)
            event_description: Mô tả sự kiện
            suspension_duration: Thời gian tạm dừng (giây)
        """
        try:
            from django.utils import timezone
            import asyncio
            
            # Tạm dừng tất cả odds của match
            odds_service = OddsManagementService()
            suspended_count = odds_service.suspend_odds_for_match(
                match_id, 
                f"Tự động tạm dừng: {event_description}",
                None  # system user
            )
            
            self.logger.info(f"Automatically suspended {suspended_count} odds for match {match_id} due to {event_type}")
            
            # Lên lịch tự động khôi phục market sau suspension_duration
            asyncio.create_task(self._resume_market_after_delay(match_id, suspension_duration))
            
            return {
                'success': True,
                'suspended_count': suspended_count,
                'suspension_duration': suspension_duration,
                'resume_time': timezone.now() + timezone.timedelta(seconds=suspension_duration)
            }
            
        except Exception as e:
            self.logger.error(f"Error suspending market for event: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _resume_market_after_delay(self, match_id, delay_seconds):
        """Khôi phục market sau khi hết thời gian tạm dừng"""
        try:
            await asyncio.sleep(delay_seconds)
            
            # Khôi phục tất cả odds của match
            odds_service = OddsManagementService()
            resumed_count = odds_service.resume_odds_for_match(match_id, None)
            
            self.logger.info(f"Automatically resumed {resumed_count} odds for match {match_id} after {delay_seconds}s suspension")
            
        except Exception as e:
            self.logger.error(f"Error resuming market after delay: {str(e)}")
    
    def process_sports_event(self, event_data):
        """
        Xử lý sự kiện từ sports data service
        
        Args:
            event_data: Dữ liệu sự kiện từ webhook
        """
        try:
            event_type = event_data.get('event_type')
            match_id = event_data.get('match_id')
            description = event_data.get('description', '')
            requires_suspension = event_data.get('requires_suspension', False)
            suspension_duration = event_data.get('suspension_duration', 60)
            
            # Kiểm tra xem có cần tạm dừng market không
            if requires_suspension and event_type in ['GOAL', 'RED_CARD', 'PENALTY']:
                return self.suspend_market_for_event(
                    match_id, 
                    event_type, 
                    description, 
                    suspension_duration
                )
            
            return {
                'success': True,
                'message': 'Event processed, no market suspension required'
            }
            
        except Exception as e:
            self.logger.error(f"Error processing sports event: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_market_suspension_status(self, match_id):
        """Lấy trạng thái market suspension của match"""
        try:
            match = Match.objects.get(id=match_id)
            
            return {
                'match_id': match_id,
                'is_suspended': match.is_market_suspended,
                'suspension_reason': match.suspension_reason,
                'suspended_at': match.suspended_at,
                'resumed_at': match.resumed_at
            }
            
        except Match.DoesNotExist:
            return {
                'error': 'Match not found'
            }
        except Exception as e:
            self.logger.error(f"Error getting market suspension status: {str(e)}")
            return {
                'error': str(e)
            }

class RealtimeOddsUpdateService:
    """Service cập nhật odds realtime dựa trên sự kiện bóng đá"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.odds_service = OddsManagementService()
    
    def update_odds_for_goal(self, match_id, scoring_team, goal_minute):
        """
        Cập nhật odds sau khi có bàn thắng
        
        Args:
            match_id: ID trận đấu
            scoring_team: Đội ghi bàn (HOME/AWAY)
            goal_minute: Phút ghi bàn
        """
        try:
            # Lấy tất cả odds của match
            match_odds = Odd.objects.filter(match_id=match_id, is_active=True)
            
            updated_count = 0
            for odd in match_odds:
                # Cập nhật odds dựa trên loại bet
                if odd.bet_type.name == 'Match Winner':
                    updated_count += self._update_match_winner_odds(odd, scoring_team)
                elif odd.bet_type.name == 'Total Goals':
                    updated_count += self._update_total_goals_odds(odd, goal_minute)
                elif odd.bet_type.name == 'Both Teams Score':
                    updated_count += self._update_both_teams_score_odds(odd, scoring_team)
                elif odd.bet_type.name == 'First Goal Scorer':
                    updated_count += self._update_first_goal_scorer_odds(odd, scoring_team)
            
            self.logger.info(f"Updated {updated_count} odds for match {match_id} after goal by {scoring_team}")
            
            return {
                'success': True,
                'updated_count': updated_count
            }
            
        except Exception as e:
            self.logger.error(f"Error updating odds for goal: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _update_match_winner_odds(self, odd, scoring_team):
        """Cập nhật odds cho Match Winner"""
        try:
            if scoring_team == 'HOME':
                # Giảm odds cho đội nhà thắng
                new_value = max(odd.value * 0.8, odd.min_value or 1.01)
            elif scoring_team == 'AWAY':
                # Giảm odds cho đội khách thắng
                new_value = max(odd.value * 0.8, odd.min_value or 1.01)
            else:
                return 0
            
            if abs(new_value - odd.value) >= 0.01:
                self.odds_service.adjust_odds_manually(
                    odd, new_value, f"Tự động cập nhật sau bàn thắng của {scoring_team}", None
                )
                return 1
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Error updating match winner odds: {str(e)}")
            return 0
    
    def _update_total_goals_odds(self, odd, goal_minute):
        """Cập nhật odds cho Total Goals"""
        try:
            # Logic cập nhật odds dựa trên phút ghi bàn
            if goal_minute <= 30:
                # Bàn thắng sớm, tăng khả năng có nhiều bàn thắng
                new_value = min(odd.value * 1.2, odd.max_value or 10.0)
            else:
                # Bàn thắng muộn, giảm khả năng có nhiều bàn thắng
                new_value = max(odd.value * 0.9, odd.min_value or 1.01)
            
            if abs(new_value - odd.value) >= 0.01:
                self.odds_service.adjust_odds_manually(
                    odd, new_value, f"Tự động cập nhật sau bàn thắng phút {goal_minute}", None
                )
                return 1
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Error updating total goals odds: {str(e)}")
            return 0
    
    def _update_both_teams_score_odds(self, odd, scoring_team):
        """Cập nhật odds cho Both Teams Score"""
        try:
            # Logic cập nhật odds dựa trên đội ghi bàn
            if scoring_team == 'HOME':
                # Đội nhà đã ghi bàn, tăng khả năng đội khách cũng ghi bàn
                new_value = min(odd.value * 1.15, odd.max_value or 10.0)
            else:
                # Đội khách đã ghi bàn, tăng khả năng đội nhà cũng ghi bàn
                new_value = min(odd.value * 1.15, odd.max_value or 10.0)
            
            if abs(new_value - odd.value) >= 0.01:
                self.odds_service.adjust_odds_manually(
                    odd, new_value, f"Tự động cập nhật sau bàn thắng của {scoring_team}", None
                )
                return 1
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Error updating both teams score odds: {str(e)}")
            return 0
    
    def _update_first_goal_scorer_odds(self, odd, scoring_team):
        """Cập nhật odds cho First Goal Scorer"""
        try:
            # Nếu đây là bàn thắng đầu tiên, cập nhật odds
            if odd.outcome == scoring_team:
                # Giảm odds cho đội đã ghi bàn đầu tiên
                new_value = max(odd.value * 0.5, odd.min_value or 1.01)
            else:
                # Tăng odds cho các đội khác
                new_value = min(odd.value * 1.5, odd.max_value or 10.0)
            
            if abs(new_value - odd.value) >= 0.01:
                self.odds_service.adjust_odds_manually(
                    odd, new_value, f"Tự động cập nhật sau bàn thắng đầu tiên của {scoring_team}", None
                )
                return 1
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Error updating first goal scorer odds: {str(e)}")
            return 0

class SportsDataWebhookService:
    """Service tích hợp webhook với sports data provider"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.market_suspension_service = AutomaticMarketSuspensionService()
        self.odds_update_service = RealtimeOddsUpdateService()
    
    def handle_goal_event(self, webhook_data):
        """
        Xử lý sự kiện bàn thắng từ webhook
        
        Args:
            webhook_data: Dữ liệu webhook từ sports data provider
        """
        try:
            match_id = webhook_data.get('match_id')
            team_id = webhook_data.get('team_id')
            minute = webhook_data.get('minute', 0)
            description = webhook_data.get('description', 'Bàn thắng mới')
            
            # Xác định đội ghi bàn
            scoring_team = self._determine_scoring_team(match_id, team_id)
            
            # Tạm dừng market
            suspension_result = self.market_suspension_service.suspend_market_for_event(
                match_id=match_id,
                event_type='GOAL',
                event_description=description,
                suspension_duration=60  # Tạm dừng 60 giây
            )
            
            # Cập nhật odds
            odds_update_result = self.odds_update_service.update_odds_for_goal(
                match_id=match_id,
                scoring_team=scoring_team,
                goal_minute=minute
            )
            
            self.logger.info(f"Goal event processed: Match {match_id}, Team {scoring_team}, Minute {minute}")
            
            return {
                'success': True,
                'suspension': suspension_result,
                'odds_update': odds_update_result,
                'scoring_team': scoring_team
            }
            
        except Exception as e:
            self.logger.error(f"Error handling goal event: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def handle_red_card_event(self, webhook_data):
        """
        Xử lý sự kiện thẻ đỏ từ webhook
        
        Args:
            webhook_data: Dữ liệu webhook từ sports data provider
        """
        try:
            match_id = webhook_data.get('match_id')
            team_id = webhook_data.get('team_id')
            player_name = webhook_data.get('player_name', 'Unknown Player')
            description = f"Thẻ đỏ cho {player_name}"
            
            # Tạm dừng market
            suspension_result = self.market_suspension_service.suspend_market_for_event(
                match_id=match_id,
                event_type='RED_CARD',
                event_description=description,
                suspension_duration=45  # Tạm dừng 45 giây
            )
            
            self.logger.info(f"Red card event processed: Match {match_id}, Player {player_name}")
            
            return {
                'success': True,
                'suspension': suspension_result,
                'event_type': 'RED_CARD'
            }
            
        except Exception as e:
            self.logger.error(f"Error handling red card event: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def handle_penalty_event(self, webhook_data):
        """
        Xử lý sự kiện phạt đền từ webhook
        
        Args:
            webhook_data: Dữ liệu webhook từ sports data provider
        """
        try:
            match_id = webhook_data.get('match_id')
            team_id = webhook_data.get('team_id')
            description = "Phạt đền được thực hiện"
            
            # Tạm dừng market
            suspension_result = self.market_suspension_service.suspend_market_for_event(
                match_id=match_id,
                event_type='PENALTY',
                event_description=description,
                suspension_duration=30  # Tạm dừng 30 giây
            )
            
            self.logger.info(f"Penalty event processed: Match {match_id}")
            
            return {
                'success': True,
                'suspension': suspension_result,
                'event_type': 'PENALTY'
            }
            
        except Exception as e:
            self.logger.error(f"Error handling penalty event: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _determine_scoring_team(self, match_id, team_id):
        """
        Xác định đội ghi bàn (HOME/AWAY) dựa trên team_id
        
        Args:
            match_id: ID trận đấu
            team_id: ID đội bóng từ provider
        
        Returns:
            'HOME' hoặc 'AWAY'
        """
        try:
            # Lấy thông tin match để xác định đội nhà/khách
            match = Match.objects.get(id=match_id)
            
            # So sánh team_id với home_team và away_team
            if str(match.home_team.external_id) == str(team_id):
                return 'HOME'
            elif str(match.away_team.external_id) == str(team_id):
                return 'AWAY'
            else:
                # Fallback: sử dụng logic khác để xác định
                self.logger.warning(f"Could not determine scoring team for match {match_id}, team_id {team_id}")
                return 'UNKNOWN'
                
        except Match.DoesNotExist:
            self.logger.error(f"Match {match_id} not found")
            return 'UNKNOWN'
        except Exception as e:
            self.logger.error(f"Error determining scoring team: {str(e)}")
            return 'UNKNOWN'
    
    def process_webhook_event(self, webhook_data):
        """
        Xử lý tất cả các loại webhook events
        
        Args:
            webhook_data: Dữ liệu webhook từ sports data provider
        """
        try:
            event_type = webhook_data.get('event_type')
            
            if event_type == 'GOAL':
                return self.handle_goal_event(webhook_data)
            elif event_type == 'RED_CARD':
                return self.handle_red_card_event(webhook_data)
            elif event_type == 'PENALTY':
                return self.handle_penalty_event(webhook_data)
            else:
                self.logger.info(f"Event type {event_type} not requiring market suspension")
                return {
                    'success': True,
                    'message': f'Event type {event_type} processed, no action required'
                }
                
        except Exception as e:
            self.logger.error(f"Error processing webhook event: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

class StatisticsCalculationService:
    """Service để tính toán thống kê người dùng"""
    
    @staticmethod
    def calculate_user_statistics(user, period='ALL_TIME', period_start=None, period_end=None):
        """Tính toán thống kê cho một người dùng trong một khoảng thời gian"""
        from .models import UserStatistics, BetSlip, CashOutHistory
        from django.utils import timezone
        from decimal import Decimal
        
        # Xác định khoảng thời gian
        if period == 'ALL_TIME':
            period_start = user.date_joined
            period_end = timezone.now()
        elif not period_start or not period_end:
            period_start, period_end = StatisticsCalculationService._get_period_dates(period)
        
        # Lấy tất cả phiếu cược trong khoảng thời gian
        bets = BetSlip.objects.filter(
            user=user,
            created_at__gte=period_start,
            created_at__lte=period_end
        )
        
        # Tính toán thống kê cơ bản
        total_bets = bets.count()
        total_wins = bets.filter(bet_status='WON').count()
        total_losses = bets.filter(bet_status='LOST').count()
        total_draws = bets.filter(bet_status='DRAW').count()
        
        # Tính toán thống kê tài chính
        total_stake = sum(bet.total_stake for bet in bets)
        total_return = sum(bet.total_return for bet in bets if bet.total_return)
        total_profit = total_return - total_stake
        
        # Tính tỷ lệ thắng và ROI
        win_rate = (total_wins / total_bets * 100) if total_bets > 0 else 0
        roi = (total_profit / total_stake * 100) if total_stake > 0 else 0
        
        # Tính số tiền cược trung bình
        average_bet_size = total_stake / total_bets if total_bets > 0 else 0
        
        # Tính tỷ lệ cược trung bình
        total_odds = sum(bet.total_odds for bet in bets if bet.total_odds)
        average_odds = total_odds / total_bets if total_bets > 0 else 0
        
        # Tính chuỗi thắng/thua
        win_streak, loss_streak = StatisticsCalculationService._calculate_streaks(bets)
        
        # Thống kê theo loại cược
        single_bets = bets.filter(bet_type='SINGLE').count()
        multiple_bets = bets.filter(bet_type='MULTIPLE').count()
        system_bets = bets.filter(bet_type='SYSTEM').count()
        
        # Thống kê theo môn thể thao
        football_bets = bets.filter(selections__match__sport__name__icontains='football').distinct().count()
        basketball_bets = bets.filter(selections__match__sport__name__icontains='basketball').distinct().count()
        tennis_bets = bets.filter(selections__match__sport__name__icontains='tennis').distinct().count()
        other_sports_bets = total_bets - football_bets - basketball_bets - tennis_bets
        
        # Tạo hoặc cập nhật UserStatistics
        stats, created = UserStatistics.objects.get_or_create(
            user=user,
            period=period,
            period_start=period_start,
            defaults={
                'period_end': period_end,
                'total_bets': total_bets,
                'total_wins': total_wins,
                'total_losses': total_losses,
                'total_draws': total_draws,
                'total_stake': total_stake,
                'total_return': total_return,
                'total_profit': total_profit,
                'win_rate': win_rate,
                'roi': roi,
                'average_odds': average_odds,
                'average_bet_size': average_bet_size,
                'best_win_streak': win_streak,
                'current_win_streak': win_streak,
                'best_loss_streak': loss_streak,
                'current_loss_streak': loss_streak,
                'single_bets': single_bets,
                'multiple_bets': multiple_bets,
                'system_bets': system_bets,
                'football_bets': football_bets,
                'basketball_bets': basketball_bets,
                'tennis_bets': tennis_bets,
                'other_sports_bets': other_sports_bets,
            }
        )
        
        if not created:
            # Cập nhật thống kê hiện có
            stats.total_bets = total_bets
            stats.total_wins = total_wins
            stats.total_losses = total_losses
            stats.total_draws = total_draws
            stats.total_stake = total_stake
            stats.total_return = total_return
            stats.total_profit = total_profit
            stats.win_rate = win_rate
            stats.roi = roi
            stats.average_odds = average_odds
            stats.average_bet_size = average_bet_size
            stats.best_win_streak = max(stats.best_win_streak, win_streak)
            stats.current_win_streak = win_streak
            stats.best_loss_streak = max(stats.best_loss_streak, loss_streak)
            stats.current_loss_streak = loss_streak
            stats.single_bets = single_bets
            stats.multiple_bets = multiple_bets
            stats.system_bets = system_bets
            stats.football_bets = football_bets
            stats.basketball_bets = basketball_bets
            stats.tennis_bets = tennis_bets
            stats.other_sports_bets = other_sports_bets
            stats.period_end = period_end
            stats.save()
        
        return stats
    
    @staticmethod
    def _get_period_dates(period):
        """Lấy ngày bắt đầu và kết thúc cho một kỳ thống kê"""
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        
        if period == 'DAILY':
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
        elif period == 'WEEKLY':
            start = now - timedelta(days=now.weekday())
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(weeks=1)
        elif period == 'BIWEEKLY':
            # 2 tuần (14 ngày)
            start = now - timedelta(days=now.weekday())  # Bắt đầu từ thứ 2
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            # Lùi về 2 tuần trước
            start = start - timedelta(weeks=1)
            end = start + timedelta(weeks=2)
        elif period == 'MONTHLY':
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if now.month == 12:
                end = now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                end = now.replace(month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == 'QUARTERLY':
            # Xác định quý hiện tại
            current_quarter = (now.month - 1) // 3 + 1
            if current_quarter == 1:
                start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
                end = now.replace(month=4, day=1, hour=0, minute=0, second=0, microsecond=0)
            elif current_quarter == 2:
                start = now.replace(month=4, day=1, hour=0, minute=0, second=0, microsecond=0)
                end = now.replace(month=7, day=1, hour=0, minute=0, second=0, microsecond=0)
            elif current_quarter == 3:
                start = now.replace(month=7, day=1, hour=0, minute=0, second=0, microsecond=0)
                end = now.replace(month=10, day=1, hour=0, minute=0, second=0, microsecond=0)
            else:  # current_quarter == 4
                start = now.replace(month=10, day=1, hour=0, minute=0, second=0, microsecond=0)
                end = now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == 'YEARLY':
            start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            start = now - timedelta(days=30)  # Default to last 30 days
            end = now
        
        return start, end
    
    @staticmethod
    def _calculate_streaks(bets):
        """Tính chuỗi thắng/thua hiện tại"""
        current_win_streak = 0
        current_loss_streak = 0
        max_win_streak = 0
        max_loss_streak = 0
        
        for bet in bets.order_by('-created_at'):
            if bet.bet_status == 'WON':
                if current_loss_streak > 0:
                    max_loss_streak = max(max_loss_streak, current_loss_streak)
                    current_loss_streak = 0
                current_win_streak += 1
            elif bet.bet_status == 'LOST':
                if current_win_streak > 0:
                    max_win_streak = max(max_win_streak, current_win_streak)
                    current_win_streak = 0
                current_loss_streak += 1
            else:  # DRAW or PENDING
                break
        
        # Cập nhật max streaks
        max_win_streak = max(max_win_streak, current_win_streak)
        max_loss_streak = max(max_loss_streak, current_loss_streak)
        
        return current_win_streak, current_loss_streak


class LeaderboardService:
    """Service để quản lý bảng xếp hạng"""
    
    @staticmethod
    def update_leaderboard(period='WEEKLY', category='OVERALL'):
        """Cập nhật bảng xếp hạng cho một kỳ và danh mục cụ thể"""
        from .models import Leaderboard, UserStatistics
        from django.utils import timezone
        from decimal import Decimal
        
        # Xác định khoảng thời gian
        period_start, period_end = StatisticsCalculationService._get_period_dates(period)
        
        # Lấy thống kê người dùng trong khoảng thời gian
        user_stats = UserStatistics.objects.filter(
            period=period,
            period_start=period_start
        ).select_related('user')
        
        # Tính điểm xếp hạng dựa trên danh mục
        leaderboard_entries = []
        
        for stats in user_stats:
            if category == 'PROFIT':
                points = float(stats.total_profit)
            elif category == 'WIN_RATE':
                points = float(stats.win_rate)
            elif category == 'VOLUME':
                points = float(stats.total_stake)
            elif category == 'STREAK':
                points = stats.current_win_streak
            elif category == 'ROI':
                points = float(stats.roi)
            else:  # OVERALL
                # Tính điểm tổng hợp
                profit_score = float(stats.total_profit) / 1000  # Normalize profit
                win_rate_score = float(stats.win_rate)
                volume_score = float(stats.total_stake) / 10000  # Normalize stake
                streak_score = stats.current_win_streak * 10
                roi_score = float(stats.roi)
                
                points = profit_score + win_rate_score + volume_score + streak_score + roi_score
            
            leaderboard_entries.append({
                'user': stats.user,
                'points': points,
                'stats': stats
            })
        
        # Sắp xếp theo điểm số
        leaderboard_entries.sort(key=lambda x: x['points'], reverse=True)
        
        # Xóa bảng xếp hạng cũ
        Leaderboard.objects.filter(
            period=period,
            category=category,
            period_start=period_start
        ).delete()
        
        # Tạo bảng xếp hạng mới
        for rank, entry in enumerate(leaderboard_entries, 1):
            stats = entry['stats']
            Leaderboard.objects.create(
                period=period,
                category=category,
                period_start=period_start,
                period_end=period_end,
                user=entry['user'],
                rank=rank,
                points=int(entry['points']),
                total_profit=stats.total_profit,
                win_rate=stats.win_rate,
                total_bets=stats.total_bets,
                total_stake=stats.total_stake,
                win_streak=stats.current_win_streak,
                roi=stats.roi,
                is_featured=rank <= 3,  # Top 3 được highlight
                featured_reason=f"Top {rank} {category.lower().replace('_', ' ')}" if rank <= 3 else ""
            )
        
        return len(leaderboard_entries)
    
    @staticmethod
    def get_leaderboard(period='WEEKLY', category='OVERALL', limit=50):
        """Lấy bảng xếp hạng"""
        from .models import Leaderboard
        
        period_start, period_end = StatisticsCalculationService._get_period_dates(period)
        
        leaderboard = Leaderboard.objects.filter(
            period=period,
            category=category,
            period_start=period_start
        ).select_related('user').order_by('rank')[:limit]
        
        return leaderboard
    
    @staticmethod
    def get_user_rank(user, period='WEEKLY', category='OVERALL'):
        """Lấy thứ hạng của một người dùng cụ thể"""
        from .models import Leaderboard
        
        period_start, period_end = StatisticsCalculationService._get_period_dates(period)
        
        try:
            entry = Leaderboard.objects.get(
                user=user,
                period=period,
                category=category,
                period_start=period_start
            )
            return entry.rank, entry.points
        except Leaderboard.DoesNotExist:
            return None, None


class BettingStatisticsService:
    """Service để tính toán thống kê tổng hợp về cược"""
    
    @staticmethod
    def calculate_betting_statistics(period='DAILY'):
        """Tính toán thống kê tổng hợp về cược"""
        from .models import BettingStatistics, BetSlip, Match, CashOutHistory
        from django.utils import timezone
        from django.db.models import Count, Sum, Avg
        from decimal import Decimal
        
        # Xác định khoảng thời gian
        period_start, period_end = StatisticsCalculationService._get_period_dates(period)
        
        # Lấy tất cả phiếu cược trong khoảng thời gian
        bets = BetSlip.objects.filter(
            created_at__gte=period_start,
            created_at__lte=period_end
        )
        
        # Tính toán thống kê cơ bản
        total_bets_placed = bets.count()
        total_unique_users = bets.values('user').distinct().count()
        total_matches = bets.values('selections__match').distinct().count()
        
        # Tính toán thống kê tài chính
        total_stake_amount = bets.aggregate(total=Sum('total_stake'))['total'] or Decimal('0')
        total_return_amount = bets.filter(bet_status='WON').aggregate(total=Sum('total_return'))['total'] or Decimal('0')
        total_profit = total_stake_amount - total_return_amount
        
        # Tính biên lợi nhuận
        house_edge = (total_profit / total_stake_amount * 100) if total_stake_amount > 0 else 0
        
        # Thống kê theo loại cược
        single_bets_count = bets.filter(bet_type='SINGLE').count()
        multiple_bets_count = bets.filter(bet_type='MULTIPLE').count()
        system_bets_count = bets.filter(bet_type='SYSTEM').count()
        
        # Thống kê theo môn thể thao
        football_bets = bets.filter(selections__match__sport__name__icontains='football').distinct().count()
        basketball_bets = bets.filter(selections__match__sport__name__icontains='basketball').distinct().count()
        tennis_bets = bets.filter(selections__match__sport__name__icontains='tennis').distinct().count()
        other_sports_bets = total_bets_placed - football_bets - basketball_bets - tennis_bets
        
        # Thống kê theo loại stake
        free_stake_bets = bets.filter(selections__match__stake_type='FREE').distinct().count()
        fixed_stake_bets = bets.filter(selections__match__stake_type='FIXED').distinct().count()
        
        # Thống kê Cash Out
        cashout_requests = CashOutHistory.objects.filter(
            requested_at__gte=period_start,
            requested_at__lte=period_end
        )
        total_cashout_requests = cashout_requests.count()
        total_cashout_amount = cashout_requests.filter(status='COMPLETED').aggregate(
            total=Sum('final_amount'))['total'] or Decimal('0')
        cashout_success_rate = (cashout_requests.filter(status='COMPLETED').count() / total_cashout_requests * 100) if total_cashout_requests > 0 else 0
        
        # Tính toán các metrics hiệu suất
        average_bet_size = total_stake_amount / total_bets_placed if total_bets_placed > 0 else 0
        average_odds = bets.aggregate(avg=Avg('total_odds'))['avg'] or 0
        win_rate = (total_return_amount / total_stake_amount * 100) if total_stake_amount > 0 else 0
        
        # Tạo hoặc cập nhật BettingStatistics
        stats, created = BettingStatistics.objects.get_or_create(
            period=period,
            period_start=period_start,
            defaults={
                'period_end': period_end,
                'total_bets_placed': total_bets_placed,
                'total_unique_users': total_unique_users,
                'total_matches': total_matches,
                'total_stake_amount': total_stake_amount,
                'total_return_amount': total_return_amount,
                'total_profit': total_profit,
                'house_edge': house_edge,
                'single_bets_count': single_bets_count,
                'multiple_bets_count': multiple_bets_count,
                'system_bets_count': system_bets_count,
                'football_bets': football_bets,
                'basketball_bets': basketball_bets,
                'tennis_bets': tennis_bets,
                'other_sports_bets': other_sports_bets,
                'free_stake_bets': free_stake_bets,
                'fixed_stake_bets': fixed_stake_bets,
                'total_cashout_requests': total_cashout_requests,
                'total_cashout_amount': total_cashout_amount,
                'cashout_success_rate': cashout_success_rate,
                'average_bet_size': average_bet_size,
                'average_odds': average_odds,
                'win_rate': win_rate,
            }
        )
        
        if not created:
            # Cập nhật thống kê hiện có
            stats.period_end = period_end
            stats.total_bets_placed = total_bets_placed
            stats.total_unique_users = total_unique_users
            stats.total_matches = total_matches
            stats.total_stake_amount = total_stake_amount
            stats.total_return_amount = total_return_amount
            stats.total_profit = total_profit
            stats.house_edge = house_edge
            stats.single_bets_count = single_bets_count
            stats.multiple_bets_count = multiple_bets_count
            stats.system_bets_count = system_bets_count
            stats.football_bets = football_bets
            stats.basketball_bets = basketball_bets
            stats.tennis_bets = tennis_bets
            stats.other_sports_bets = other_sports_bets
            stats.free_stake_bets = free_stake_bets
            stats.fixed_stake_bets = fixed_stake_bets
            stats.total_cashout_requests = total_cashout_requests
            stats.total_cashout_amount = total_cashout_amount
            stats.cashout_success_rate = cashout_success_rate
            stats.average_bet_size = average_bet_size
            stats.average_odds = average_odds
            stats.win_rate = win_rate
            stats.save()
        
        return stats


class PerformanceMetricsService:
    """Service để tính toán metrics hiệu suất người chơi"""
    
    @staticmethod
    def calculate_performance_metrics(user, sport=None, bet_type=None):
        """Tính toán metrics hiệu suất cho một người dùng"""
        from .models import PerformanceMetrics, BetSlip
        from django.db.models import Avg, Min, Max
        from decimal import Decimal
        
        # Lấy tất cả phiếu cược của người dùng
        bets_query = BetSlip.objects.filter(user=user)
        
        # Lọc theo môn thể thao nếu có
        if sport:
            bets_query = bets_query.filter(selections__match__sport=sport)
        
        # Lọc theo loại cược nếu có
        if bet_type:
            bets_query = bets_query.filter(bet_type=bet_type)
        
        bets = bets_query.distinct()
        
        # Tính toán thống kê cơ bản
        total_bets = bets.count()
        total_wins = bets.filter(bet_status='WON').count()
        total_losses = bets.filter(bet_status='LOST').count()
        
        # Tính tỷ lệ thành công và thắng
        success_rate = (total_wins / total_bets * 100) if total_bets > 0 else 0
        win_rate = success_rate  # Trong trường hợp này, success_rate = win_rate
        
        # Tính toán thống kê tài chính
        total_stake = bets.aggregate(total=Sum('total_stake'))['total'] or Decimal('0')
        total_return = bets.filter(bet_status='WON').aggregate(total=Sum('total_return'))['total'] or Decimal('0')
        profit_loss = total_return - total_stake
        
        # Tính ROI
        roi = (profit_loss / total_stake * 100) if total_stake > 0 else 0
        
        # Tính toán thống kê odds
        odds_stats = bets.aggregate(
            avg=Avg('total_odds'),
            min=Min('total_odds'),
            max=Max('total_odds')
        )
        average_odds = odds_stats['avg'] or 0
        best_odds = odds_stats['max'] or 0
        worst_odds = odds_stats['min'] or 0
        
        # Lấy ngày đặt cược đầu tiên và cuối cùng
        first_bet_date = bets.order_by('created_at').first().created_at if bets.exists() else None
        last_bet_date = bets.order_by('-created_at').first().created_at if bets.exists() else None
        
        # Tạo hoặc cập nhật PerformanceMetrics
        metrics, created = PerformanceMetrics.objects.get_or_create(
            user=user,
            sport=sport,
            bet_type=bet_type,
            defaults={
                'total_bets': total_bets,
                'total_wins': total_wins,
                'total_losses': total_losses,
                'success_rate': success_rate,
                'win_rate': win_rate,
                'total_stake': total_stake,
                'total_return': total_return,
                'profit_loss': profit_loss,
                'roi': roi,
                'average_odds': average_odds,
                'best_odds': best_odds,
                'worst_odds': worst_odds,
                'first_bet_date': first_bet_date,
                'last_bet_date': last_bet_date,
            }
        )
        
        if not created:
            # Cập nhật metrics hiện có
            metrics.total_bets = total_bets
            metrics.total_wins = total_wins
            metrics.total_losses = total_losses
            metrics.success_rate = success_rate
            metrics.win_rate = win_rate
            metrics.total_stake = total_stake
            metrics.total_return = total_return
            metrics.profit_loss = profit_loss
            metrics.roi = roi
            metrics.average_odds = average_odds
            metrics.best_odds = best_odds
            metrics.worst_odds = worst_odds
            metrics.first_bet_date = first_bet_date
            metrics.last_bet_date = last_bet_date
            metrics.save()
        
        return metrics

class MatchingEngineService:
    """Service xử lý khớp lệnh mua/bán P2P"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def match_orders(self, bet_slip_id):
        """Khớp lệnh cho một phiếu cược cụ thể"""
        try:
            # Lấy tất cả lệnh mua và bán đang hoạt động
            buy_orders = OrderBook.objects.filter(
                bet_slip_id=bet_slip_id,
                order_type='BUY',
                status='PENDING'
            ).order_by('-price', 'created_at')  # Ưu tiên giá cao trước, sau đó thời gian
            
            sell_orders = OrderBook.objects.filter(
                bet_slip_id=bet_slip_id,
                order_type='SELL',
                status='PENDING'
            ).order_by('price', 'created_at')  # Ưu tiên giá thấp trước, sau đó thời gian
            
            matches = []
            
            for buy_order in buy_orders:
                if buy_order.status != 'PENDING':
                    continue
                
                for sell_order in sell_orders:
                    if sell_order.status != 'PENDING':
                        continue
                    
                    # Kiểm tra điều kiện khớp lệnh
                    if self._can_match(buy_order, sell_order):
                        match_result = self._execute_match(buy_order, sell_order)
                        if match_result:
                            matches.append(match_result)
                            
                            # Cập nhật trạng thái lệnh
                            self._update_order_status(buy_order, sell_order)
                            
                            # Nếu lệnh đã khớp hoàn toàn, thoát khỏi vòng lặp
                            if buy_order.status == 'FILLED' or sell_order.status == 'FILLED':
                                break
            
            return matches
            
        except Exception as e:
            self.logger.error(f"Lỗi khớp lệnh: {e}")
            return []
    
    def _can_match(self, buy_order, sell_order):
        """Kiểm tra có thể khớp lệnh không"""
        # Giá mua phải >= giá bán
        if buy_order.price < sell_order.price:
            return False
        
        # Cả hai lệnh phải còn hoạt động
        if not buy_order.can_fill(1) or not sell_order.can_fill(1):
            return False
        
        # Không thể khớp lệnh của cùng một người
        if buy_order.user == sell_order.user:
            return False
        
        return True
    
    def _execute_match(self, buy_order, sell_order):
        """Thực hiện khớp lệnh"""
        try:
            # Tính toán số lượng khớp
            match_quantity = min(
                buy_order.remaining_quantity,
                sell_order.remaining_quantity
            )
            
            if match_quantity <= 0:
                return None
            
            # Tạo giao dịch P2P
            transaction = P2PTransaction.objects.create(
                transaction_type='BUY' if buy_order.quantity >= sell_order.quantity else 'SELL',
                buyer=buy_order.user,
                seller=sell_order.user,
                bet_slip=buy_order.bet_slip,
                quantity=match_quantity,
                ownership_percentage=self._calculate_ownership_percentage(match_quantity, buy_order.bet_slip),
                price_per_unit=sell_order.price,  # Giá khớp theo giá bán
                buy_order=buy_order,
                sell_order=sell_order
            )
            
            # Cập nhật số lượng đã khớp
            buy_order.fill_order(match_quantity)
            sell_order.fill_order(match_quantity)
            
            # Cập nhật quyền sở hữu
            self._update_ownership(buy_order, sell_order, match_quantity, transaction)
            
            return {
                'transaction_id': transaction.transaction_id,
                'buy_order_id': buy_order.id,
                'sell_order_id': sell_order.id,
                'quantity': match_quantity,
                'price': sell_order.price,
                'total_amount': match_quantity * sell_order.price
            }
            
        except Exception as e:
            self.logger.error(f"Lỗi thực hiện khớp lệnh: {e}")
            return None
    
    def _calculate_ownership_percentage(self, quantity, bet_slip):
        """Tính toán tỷ lệ sở hữu"""
        # Giả sử mỗi phần = 1% (có thể điều chỉnh logic này)
        total_parts = 100
        return (quantity / total_parts) * 100
    
    def _update_ownership(self, buy_order, sell_order, quantity, transaction):
        """Cập nhật quyền sở hữu sau khi khớp lệnh"""
        try:
            # Giảm quyền sở hữu của người bán
            seller_ownership = BetSlipOwnership.objects.filter(
                bet_slip=sell_order.bet_slip,
                owner=sell_order.user,
                is_active=True
            ).first()
            
            if seller_ownership:
                seller_ownership.ownership_percentage -= self._calculate_ownership_percentage(quantity, sell_order.bet_slip)
                if seller_ownership.ownership_percentage <= 0:
                    seller_ownership.is_active = False
                seller_ownership.save()
            
            # Tăng quyền sở hữu của người mua
            buyer_ownership, created = BetSlipOwnership.objects.get_or_create(
                bet_slip=buy_order.bet_slip,
                owner=buy_order.user,
                defaults={
                    'ownership_percentage': 0,
                    'acquired_price': transaction.price_per_unit
                }
            )
            
            if not created:
                buyer_ownership.ownership_percentage += self._calculate_ownership_percentage(quantity, buy_order.bet_slip)
            
            buyer_ownership.acquired_price = transaction.price_per_unit
            buyer_ownership.save()
            
        except Exception as e:
            self.logger.error(f"Lỗi cập nhật quyền sở hữu: {e}")
    
    def _update_order_status(self, buy_order, sell_order):
        """Cập nhật trạng thái lệnh sau khi khớp"""
        try:
            buy_order.save()
            sell_order.save()
        except Exception as e:
            self.logger.error(f"Lỗi cập nhật trạng thái lệnh: {e}")


class FractionalTradingService:
    """Service xử lý giao dịch phân mảnh phiếu cược"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def split_bet_slip(self, bet_slip, num_fractions, user):
        """Chia nhỏ phiếu cược thành nhiều phần"""
        try:
            if num_fractions <= 1:
                raise ValueError("Số phần phải lớn hơn 1")
            
            # Kiểm tra quyền sở hữu
            ownership = BetSlipOwnership.objects.filter(
                bet_slip=bet_slip,
                owner=user,
                is_active=True
            ).first()
            
            if not ownership or ownership.ownership_percentage < 100:
                raise ValueError("Bạn phải sở hữu 100% phiếu cược để chia nhỏ")
            
            # Tính toán tỷ lệ mỗi phần
            fraction_percentage = Decimal('100.0') / num_fractions
            
            # Kiểm tra tính chia hết (tuân thủ quy tắc 2^n * 5^m)
            if not self._is_valid_fraction(fraction_percentage):
                raise ValueError("Số phần không hợp lệ, phải tuân thủ quy tắc chia hết")
            
            # Tạo các phần sở hữu mới
            fractions = []
            for i in range(num_fractions):
                fraction = BetSlipOwnership.objects.create(
                    bet_slip=bet_slip,
                    owner=user,
                    ownership_percentage=fraction_percentage,
                    acquired_price=bet_slip.total_stake * fraction_percentage / 100
                )
                fractions.append(fraction)
            
            # Cập nhật quyền sở hữu gốc
            ownership.ownership_percentage = 0
            ownership.is_active = False
            ownership.save()
            
            return fractions
            
        except Exception as e:
            self.logger.error(f"Lỗi chia nhỏ phiếu cược: {e}")
            raise
    
    def _is_valid_fraction(self, fraction_percentage):
        """Kiểm tra tỷ lệ phần có hợp lệ không"""
        # Chuyển đổi thành phân số và kiểm tra mẫu số
        # Ví dụ: 10% = 0.1 = 1/10, mẫu số = 10 = 2 * 5 (hợp lệ)
        # 33.33% = 0.333... = 1/3, mẫu số = 3 (không hợp lệ)
        
        # Logic đơn giản: kiểm tra xem có thể biểu diễn dưới dạng thập phân hữu hạn
        try:
            str(fraction_percentage).split('.')[1]  # Phần thập phân
            return True
        except:
            return False
    
    def merge_fractions(self, bet_slip, user):
        """Gộp các phần sở hữu nhỏ thành một phần lớn"""
        try:
            # Lấy tất cả phần sở hữu của user cho bet_slip này
            fractions = BetSlipOwnership.objects.filter(
                bet_slip=bet_slip,
                owner=user,
                is_active=True
            )
            
            if fractions.count() <= 1:
                return fractions.first()
            
            # Tính tổng tỷ lệ sở hữu
            total_percentage = sum(f.ownership_percentage for f in fractions)
            total_value = sum(f.ownership_value for f in fractions)
            
            # Tạo phần sở hữu mới
            merged_ownership = BetSlipOwnership.objects.create(
                bet_slip=bet_slip,
                owner=user,
                ownership_percentage=total_percentage,
                acquired_price=total_value
            )
            
            # Vô hiệu hóa các phần cũ
            fractions.update(is_active=False)
            
            return merged_ownership
            
        except Exception as e:
            self.logger.error(f"Lỗi gộp phần sở hữu: {e}")
            raise


class P2PMarketplaceService:
    """Service quản lý P2P Marketplace"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.matching_engine = MatchingEngineService()
        self.fractional_service = FractionalTradingService()
    
    def create_sell_order(self, user, bet_slip, price, quantity, allow_fractional=True, expires_in_hours=24):
        """Tạo lệnh bán phiếu cược"""
        try:
            # Kiểm tra quyền sở hữu
            ownership = BetSlipOwnership.objects.filter(
                bet_slip=bet_slip,
                owner=user,
                is_active=True
            ).first()
            
            if not ownership:
                raise ValueError("Bạn không sở hữu phiếu cược này")
            
            if ownership.ownership_percentage < quantity:
                raise ValueError("Bạn không đủ quyền sở hữu để bán")
            
            # Kiểm tra user có bị blacklist không
            if self._is_user_blacklisted(user.id):
                raise ValueError("Tài khoản của bạn đã bị hạn chế giao dịch")
            
            # Tạo lệnh bán
            expires_at = timezone.now() + timezone.timedelta(hours=expires_in_hours)
            
            sell_order = OrderBook.objects.create(
                order_type='SELL',
                bet_slip=bet_slip,
                user=user,
                price=price,
                quantity=quantity,
                allow_partial_fill=allow_fractional,
                is_fractional=allow_fractional,
                expires_at=expires_at
            )
            
            return sell_order
            
        except Exception as e:
            self.logger.error(f"Lỗi tạo lệnh bán: {e}")
            raise
    
    def _is_user_blacklisted(self, user_id):
        """Kiểm tra user có bị blacklist không"""
        try:
            import requests
            
            # Gọi User Rating Service để kiểm tra blacklist
            blacklist_url = f"http://user_rating_service:8000/api/blacklist/check_user/{user_id}/"
            
            response = requests.get(blacklist_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get('is_blacklisted', False)
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking user blacklist: {e}")
            return False
    
    def _get_user_trust_score(self, user_id):
        """Lấy trust score của user"""
        try:
            import requests
            
            # Gọi User Rating Service để lấy trust score
            trust_score_url = f"http://user_rating_service:8000/api/user-summary/{user_id}/"
            
            response = requests.get(trust_score_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get('overall_score', 0)
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Error getting user trust score: {e}")
            return 0
    
    def create_buy_order(self, user, bet_slip, price, quantity, expires_in_hours=24):
        """Tạo lệnh mua phiếu cược"""
        try:
            # Kiểm tra user có bị blacklist không
            if self._is_user_blacklisted(user.id):
                raise ValueError("Tài khoản của bạn đã bị hạn chế giao dịch")
            
            # Kiểm tra phiếu cược có đang được bán không
            active_sell_orders = OrderBook.objects.filter(
                bet_slip=bet_slip,
                order_type='SELL',
                status='PENDING'
            )
            
            if not active_sell_orders.exists():
                raise ValueError("Phiếu cược này không có lệnh bán nào")
            
            # Tạo lệnh mua
            expires_at = timezone.now() + timezone.timedelta(hours=expires_in_hours)
            
            buy_order = OrderBook.objects.create(
                order_type='BUY',
                bet_slip=bet_slip,
                user=user,
                price=price,
                quantity=quantity,
                allow_partial_fill=True,
                is_fractional=False,
                expires_at=expires_at
            )
            
            # Thử khớp lệnh ngay lập tức
            self.matching_engine.match_orders(bet_slip.id)
            
            return buy_order
            
        except Exception as e:
            self.logger.error(f"Lỗi tạo lệnh mua: {e}")
            raise
    
    def get_market_overview(self, bet_slip_id=None):
        """Lấy tổng quan thị trường P2P"""
        try:
            if bet_slip_id:
                # Tổng quan cho một phiếu cược cụ thể
                buy_orders = OrderBook.objects.filter(
                    bet_slip_id=bet_slip_id,
                    order_type='BUY',
                    status='PENDING'
                ).order_by('-price')
                
                sell_orders = OrderBook.objects.filter(
                    bet_slip_id=bet_slip_id,
                    order_type='SELL',
                    status='PENDING'
                ).order_by('price')
                
                return {
                    'bet_slip_id': bet_slip_id,
                    'buy_orders': buy_orders.count(),
                    'sell_orders': sell_orders.count(),
                    'best_buy_price': buy_orders.first().price if buy_orders.exists() else None,
                    'best_sell_price': sell_orders.first().price if sell_orders.exists() else None,
                    'total_volume': sum(o.total_value for o in buy_orders) + sum(o.total_value for o in sell_orders)
                }
            else:
                # Tổng quan toàn bộ thị trường
                total_buy_orders = OrderBook.objects.filter(order_type='BUY', status='PENDING').count()
                total_sell_orders = OrderBook.objects.filter(order_type='SELL', status='PENDING').count()
                total_transactions = P2PTransaction.objects.filter(status='COMPLETED').count()
                
                return {
                    'total_buy_orders': total_buy_orders,
                    'total_sell_orders': total_sell_orders,
                    'total_transactions': total_transactions,
                    'active_markets': BetSlip.objects.filter(orders__status='PENDING').distinct().count()
                }
                
        except Exception as e:
            self.logger.error(f"Lỗi lấy tổng quan thị trường: {e}")
            return {}

class MatchCancellationService:
    """Service xử lý các trường hợp trận đấu bị hủy/hoãn và hoàn tiền tự động"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        from shared.base_settings import get_service_url
        self.payment_service_url = get_service_url('payment')
        self.saga_service_url = get_service_url('saga')
    
    def handle_match_cancellation(self, match_id, cancellation_type, reason=""):
        """
        Xử lý trận đấu bị hủy/hoãn
        
        Args:
            match_id: ID trận đấu
            cancellation_type: 'CANCELLED' hoặc 'POSTPONED'
            reason: Lý do hủy/hoãn
        """
        try:
            from django.utils import timezone
            
            # Lấy thông tin trận đấu
            match = Match.objects.get(id=match_id)
            
            # Cập nhật trạng thái trận đấu
            match.status = cancellation_type
            match.updated_at = timezone.now()
            match.save()
            
            # Xử lý theo loại hủy/hoãn
            if cancellation_type == 'CANCELLED':
                return self._handle_cancelled_match(match, reason)
            elif cancellation_type == 'POSTPONED':
                return self._handle_postponed_match(match, reason)
            else:
                raise ValueError(f"Loại hủy/hoãn không hợp lệ: {cancellation_type}")
                
        except Match.DoesNotExist:
            self.logger.error(f"Match {match_id} không tồn tại")
            return {'success': False, 'error': 'Match không tồn tại'}
        except Exception as e:
            self.logger.error(f"Lỗi xử lý hủy/hoãn trận đấu: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _handle_cancelled_match(self, match, reason):
        """Xử lý trận đấu bị hủy - hoàn tiền toàn bộ"""
        try:
            # 1. Tạm dừng tất cả giao dịch P2P liên quan
            self._suspend_p2p_trading(match)
            
            # 2. Hoàn tiền tất cả cược đã đặt
            refund_result = self._refund_all_bets(match)
            
            # 3. Hoàn trả quyền sở hữu P2P
            ownership_result = self._restore_p2p_ownership(match)
            
            # 4. Ghi log và thông báo
            self._log_cancellation_actions(match, reason, refund_result, ownership_result)
            
            return {
                'success': True,
                'match_id': match.id,
                'action': 'CANCELLED',
                'refund_count': refund_result.get('refund_count', 0),
                'ownership_restored': ownership_result.get('restored_count', 0),
                'message': f'Trận đấu {match} đã được hủy và hoàn tiền hoàn tất'
            }
            
        except Exception as e:
            self.logger.error(f"Lỗi xử lý trận đấu bị hủy: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _handle_postponed_match(self, match, reason):
        """Xử lý trận đấu bị hoãn - tạm dừng giao dịch, chờ thông báo mới"""
        try:
            # 1. Tạm dừng tất cả giao dịch P2P
            self._suspend_p2p_trading(match)
            
            # 2. Tạm dừng đặt cược mới
            self._suspend_new_bets(match)
            
            # 3. Ghi log và thông báo
            self._log_postponement_actions(match, reason)
            
            return {
                'success': True,
                'match_id': match.id,
                'action': 'POSTPONED',
                'message': f'Trận đấu {match} đã được hoãn, giao dịch tạm dừng',
                'next_steps': 'Chờ thông báo lịch thi đấu mới'
            }
            
        except Exception as e:
            self.logger.error(f"Lỗi xử lý trận đấu bị hoãn: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _suspend_p2p_trading(self, match):
        """Tạm dừng giao dịch P2P cho trận đấu"""
        try:
            # Tạo market suspension
            suspension = MarketSuspension.objects.create(
                match=match,
                suspension_type='MANUAL',
                status='ACTIVE',
                duration_minutes=1440,  # 24 giờ
                p2p_orders_suspended=True,
                new_bets_suspended=True,
                cash_out_suspended=True,
                reason=f"Trận đấu bị hủy/hoãn - {match.status}"
            )
            
            # Tạm dừng tất cả lệnh P2P đang hoạt động
            active_orders = OrderBook.objects.filter(
                bet_slip__match=match,
                status='PENDING'
            )
            
            for order in active_orders:
                order.status = 'SUSPENDED'
                order.suspension_reason = f"Trận đấu bị {match.status.lower()}"
                order.save()
            
            self.logger.info(f"Đã tạm dừng {active_orders.count()} lệnh P2P cho match {match.id}")
            
        except Exception as e:
            self.logger.error(f"Lỗi tạm dừng P2P trading: {str(e)}")
            raise
    
    def _refund_all_bets(self, match):
        """Hoàn tiền tất cả cược đã đặt cho trận đấu"""
        try:
            # Lấy tất cả cược đã xác nhận
            confirmed_bets = BetSlip.objects.filter(
                match=match,
                bet_status='CONFIRMED',
                is_settled=False
            )
            
            refund_count = 0
            total_refund_amount = 0
            
            for bet in confirmed_bets:
                try:
                    # Tạo refund request
                    refund_result = self._create_refund_request(bet)
                    if refund_result['success']:
                        refund_count += 1
                        total_refund_amount += bet.stake_amount
                        
                        # Cập nhật trạng thái bet
                        bet.bet_status = 'REFUNDED'
                        bet.refunded_at = timezone.now()
                        bet.refund_reason = f"Trận đấu bị hủy: {match.status}"
                        bet.save()
                        
                except Exception as e:
                    self.logger.error(f"Lỗi hoàn tiền bet {bet.id}: {str(e)}")
                    continue
            
            return {
                'refund_count': refund_count,
                'total_amount': total_refund_amount,
                'failed_count': confirmed_bets.count() - refund_count
            }
            
        except Exception as e:
            self.logger.error(f"Lỗi hoàn tiền bets: {str(e)}")
            raise
    
    def _restore_p2p_ownership(self, match):
        """Khôi phục quyền sở hữu P2P về người bán ban đầu"""
        try:
            # Lấy tất cả giao dịch P2P đã hoàn thành
            completed_transactions = P2PTransaction.objects.filter(
                bet_slip__match=match,
                status='COMPLETED'
            )
            
            restored_count = 0
            
            for transaction in completed_transactions:
                try:
                    # Khôi phục quyền sở hữu về seller
                    self._restore_ownership_to_seller(transaction)
                    
                    # Cập nhật trạng thái transaction
                    transaction.status = 'REFUNDED'
                    transaction.refund_reason = f"Trận đấu bị hủy: {match.status}"
                    transaction.save()
                    
                    restored_count += 1
                    
                except Exception as e:
                    self.logger.error(f"Lỗi khôi phục ownership cho transaction {transaction.id}: {str(e)}")
                    continue
            
            return {
                'restored_count': restored_count,
                'total_transactions': completed_transactions.count()
            }
            
        except Exception as e:
            self.logger.error(f"Lỗi khôi phục P2P ownership: {str(e)}")
            raise
    
    def _restore_ownership_to_seller(self, transaction):
        """Khôi phục quyền sở hữu về người bán"""
        try:
            # Lấy thông tin ownership hiện tại
            current_ownership = BetSlipOwnership.objects.filter(
                bet_slip=transaction.bet_slip,
                user=transaction.buyer
            ).first()
            
            if current_ownership:
                # Chuyển ownership về seller
                seller_ownership, created = BetSlipOwnership.objects.get_or_create(
                    bet_slip=transaction.bet_slip,
                    user=transaction.seller,
                    defaults={
                        'ownership_percentage': transaction.ownership_percentage,
                        'acquired_at': timezone.now(),
                        'acquisition_method': 'REFUND_RESTORATION'
                    }
                )
                
                if not created:
                    # Cập nhật ownership percentage
                    seller_ownership.ownership_percentage += transaction.ownership_percentage
                    seller_ownership.save()
                
                # Xóa ownership của buyer
                current_ownership.delete()
                
                # Hoàn tiền cho buyer
                self._refund_p2p_payment(transaction)
                
        except Exception as e:
            self.logger.error(f"Lỗi khôi phục ownership: {str(e)}")
            raise
    
    def _refund_p2p_payment(self, transaction):
        """Hoàn tiền giao dịch P2P"""
        try:
            # Tạo refund request cho giao dịch P2P
            refund_data = {
                'transaction_id': str(transaction.id),
                'amount': transaction.total_amount,
                'currency': 'USD',  # Mặc định
                'reason': 'service_not_provided',
                'description': f'Hoàn tiền P2P do trận đấu bị hủy'
            }
            
            # Gọi payment service để tạo refund
            response = requests.post(
                f"{self.payment_service_url}/api/refund-requests/",
                json=refund_data,
                timeout=10
            )
            
            if response.status_code == 201:
                self.logger.info(f"Đã tạo refund request cho P2P transaction {transaction.id}")
            else:
                self.logger.warning(f"Không thể tạo refund request: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Lỗi tạo refund P2P: {str(e)}")
    
    def _create_refund_request(self, bet):
        """Tạo refund request cho bet"""
        try:
            # Tạo refund request
            refund_data = {
                'transaction_id': str(bet.id),  # Sử dụng bet ID làm transaction ID
                'amount': float(bet.stake_amount),
                'currency': 'USD',  # Mặc định
                'reason': 'service_not_provided',
                'description': f'Hoàn tiền do trận đấu bị hủy'
            }
            
            # Gọi payment service
            response = requests.post(
                f"{self.payment_service_url}/api/refund-requests/",
                json=refund_data,
                timeout=10
            )
            
            if response.status_code == 201:
                return {'success': True, 'refund_id': response.json().get('id')}
            else:
                return {'success': False, 'error': f'HTTP {response.status_code}'}
                
        except Exception as e:
            self.logger.error(f"Lỗi tạo refund request: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _suspend_new_bets(self, match):
        """Tạm dừng đặt cược mới cho trận đấu"""
        try:
            # Cập nhật trạng thái match để ngăn đặt cược mới
            match.is_market_suspended = True
            match.suspension_reason = f"Trận đấu bị hoãn - {match.status}"
            match.suspended_at = timezone.now()
            match.save()
            
            self.logger.info(f"Đã tạm dừng đặt cược mới cho match {match.id}")
            
        except Exception as e:
            self.logger.error(f"Lỗi tạm dừng đặt cược mới: {str(e)}")
            raise
    
    def _log_cancellation_actions(self, match, reason, refund_result, ownership_result):
        """Ghi log các hành động hủy trận đấu"""
        try:
            log_data = {
                'match_id': match.id,
                'action': 'MATCH_CANCELLED',
                'reason': reason,
                'refund_summary': refund_result,
                'ownership_summary': ownership_result,
                'timestamp': timezone.now().isoformat()
            }
            
            self.logger.info(f"Match cancellation completed: {log_data}")
            
        except Exception as e:
            self.logger.error(f"Lỗi ghi log cancellation: {str(e)}")
    
    def _log_postponement_actions(self, match, reason):
        """Ghi log các hành động hoãn trận đấu"""
        try:
            log_data = {
                'match_id': match.id,
                'action': 'MATCH_POSTPONED',
                'reason': reason,
                'timestamp': timezone.now().isoformat()
            }
            
            self.logger.info(f"Match postponement completed: {log_data}")
            
        except Exception as e:
            self.logger.error(f"Lỗi ghi log postponement: {str(e)}")
    
    def resume_postponed_match(self, match_id, new_start_time):
        """Khôi phục trận đấu bị hoãn với thời gian mới"""
        try:
            match = Match.objects.get(id=match_id)
            
            if match.status != 'POSTPONED':
                return {'success': False, 'error': 'Trận đấu không ở trạng thái hoãn'}
            
            # Cập nhật thời gian mới
            match.start_time = new_start_time
            match.status = 'SCHEDULED'
            match.is_market_suspended = False
            match.suspension_reason = ""
            match.suspended_at = None
            match.save()
            
            # Mở lại giao dịch P2P
            self._resume_p2p_trading(match)
            
            return {
                'success': True,
                'match_id': match.id,
                'new_start_time': new_start_time,
                'message': 'Trận đấu đã được khôi phục và mở lại giao dịch'
            }
            
        except Match.DoesNotExist:
            return {'success': False, 'error': 'Match không tồn tại'}
        except Exception as e:
            self.logger.error(f"Lỗi khôi phục trận đấu: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _resume_p2p_trading(self, match):
        """Mở lại giao dịch P2P cho trận đấu"""
        try:
            # Kết thúc market suspension
            active_suspensions = MarketSuspension.objects.filter(
                match=match,
                status='ACTIVE'
            )
            
            for suspension in active_suspensions:
                suspension.status = 'RESUMED'
                suspension.resumed_at = timezone.now()
                suspension.save()
            
            # Mở lại các lệnh P2P bị tạm dừng
            suspended_orders = OrderBook.objects.filter(
                bet_slip__match=match,
                status='SUSPENDED'
            )
            
            for order in suspended_orders:
                order.status = 'PENDING'
                order.suspension_reason = ""
                order.save()
            
            self.logger.info(f"Đã mở lại {suspended_orders.count()} lệnh P2P cho match {match.id}")
            
        except Exception as e:
            self.logger.error(f"Lỗi mở lại P2P trading: {str(e)}")
            raise


class AutoCashoutMonitorService:
    """Service tự động giám sát và thực hiện lệnh Chốt Lời & Cắt Lỗ"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        from shared.base_settings import get_service_url
        self.betting_service_url = get_service_url('betting')
        self.risk_service_url = get_service_url('risk')
        self.saga_service_url = get_service_url('saga')
        self.cashout_service = CashOutService()
        
        # Cấu hình monitoring
        self.monitoring_interval = int(os.getenv('AUTO_CASHOUT_MONITORING_INTERVAL', '10'))  # giây
        self.max_batch_size = int(os.getenv('AUTO_CASHOUT_MAX_BATCH_SIZE', '100'))
        
    def start_monitoring(self):
        """Bắt đầu giám sát tự động - được gọi bởi Celery Beat hoặc Cron"""
        try:
            self.logger.info("Bắt đầu giám sát lệnh tự động Chốt Lời & Cắt Lỗ")
            
            # Lấy danh sách phiếu cược có lệnh tự động đang hoạt động
            active_auto_orders = self._get_active_auto_orders()
            
            if not active_auto_orders:
                self.logger.info("Không có lệnh tự động nào đang hoạt động")
                return {'success': True, 'processed': 0}
            
            # Xử lý từng batch để tránh quá tải
            processed_count = 0
            for i in range(0, len(active_auto_orders), self.max_batch_size):
                batch = active_auto_orders[i:i + self.max_batch_size]
                batch_result = self._process_batch(batch)
                processed_count += batch_result.get('processed', 0)
                
                # Tạm dừng giữa các batch để tránh quá tải
                time.sleep(1)
            
            self.logger.info(f"Hoàn thành giám sát: {processed_count} phiếu cược đã được xử lý")
            return {'success': True, 'processed': processed_count}
            
        except Exception as e:
            self.logger.error(f"Lỗi trong quá trình giám sát tự động: {e}")
            return {'success': False, 'error': str(e)}
    
    def _get_active_auto_orders(self):
        """Lấy danh sách phiếu cược có lệnh tự động đang hoạt động"""
        try:
            from .models import BetSlip
            
            active_orders = BetSlip.objects.filter(
                auto_order_enabled=True,
                auto_order_status__in=['ACTIVE', 'SUSPENDED'],
                bet_status='CONFIRMED',
                is_settled=False
            ).select_related('user').prefetch_related('selections__odd__match')
            
            return list(active_orders)
            
        except Exception as e:
            self.logger.error(f"Lỗi lấy danh sách lệnh tự động: {e}")
            return []
    
    def _process_batch(self, bet_slips):
        """Xử lý một batch phiếu cược"""
        try:
            processed_count = 0
            triggered_count = 0
            
            for bet_slip in bet_slips:
                try:
                    # Kiểm tra xem có chạm ngưỡng không
                    threshold_check = self._check_thresholds(bet_slip)
                    
                    if threshold_check['should_trigger']:
                        # Kích hoạt lệnh tự động
                        trigger_result = self._trigger_auto_order(bet_slip, threshold_check['reason'])
                        
                        if trigger_result['success']:
                            triggered_count += 1
                            self.logger.info(f"Đã kích hoạt lệnh tự động cho BetSlip #{bet_slip.id}: {threshold_check['reason']}")
                    
                    processed_count += 1
                    
                except Exception as e:
                    self.logger.error(f"Lỗi xử lý BetSlip #{bet_slip.id}: {e}")
                    continue
            
            return {
                'success': True,
                'processed': processed_count,
                'triggered': triggered_count
            }
            
        except Exception as e:
            self.logger.error(f"Lỗi xử lý batch: {e}")
            return {'success': False, 'error': str(e)}
    
    def _check_thresholds(self, bet_slip):
        """Kiểm tra xem phiếu cược có chạm ngưỡng chốt lời/cắt lỗ không"""
        try:
            # Lấy giá trị Cash Out hiện tại
            current_cashout_value = self._get_current_cashout_value(bet_slip)
            
            if current_cashout_value is None:
                return {'should_trigger': False, 'reason': None}
            
            # Kiểm tra ngưỡng chốt lời
            if (bet_slip.take_profit_threshold and 
                current_cashout_value >= bet_slip.take_profit_threshold):
                return {
                    'should_trigger': True,
                    'reason': 'TAKE_PROFIT',
                    'current_value': current_cashout_value,
                    'threshold': bet_slip.take_profit_threshold
                }
            
            # Kiểm tra ngưỡng cắt lỗ
            if (bet_slip.stop_loss_threshold and 
                current_cashout_value <= bet_slip.stop_loss_threshold):
                return {
                    'should_trigger': True,
                    'reason': 'STOP_LOSS',
                    'current_value': current_cashout_value,
                    'threshold': bet_slip.stop_loss_threshold
                }
            
            return {'should_trigger': False, 'reason': None}
            
        except Exception as e:
            self.logger.error(f"Lỗi kiểm tra ngưỡng cho BetSlip #{bet_slip.id}: {e}")
            return {'should_trigger': False, 'reason': None}
    
    def _get_current_cashout_value(self, bet_slip):
        """Lấy giá trị Cash Out hiện tại của phiếu cược"""
        try:
            # Gọi đến CashOutService để tính toán giá trị hiện tại
            live_odds_data = self._get_live_odds_data(bet_slip)
            
            if not live_odds_data:
                return None
            
            # Tính toán giá trị Cash Out hiện tại
            cashout_calculation = self.cashout_service.calculate_cash_out_value(
                bet_slip=bet_slip,
                live_odds_data=live_odds_data,
                bookmaker_type='SYSTEM',
                bookmaker_id='system'
            )
            
            return cashout_calculation.get('cash_out_value')
            
        except Exception as e:
            self.logger.error(f"Lỗi lấy giá trị Cash Out hiện tại cho BetSlip #{bet_slip.id}: {e}")
            return None
    
    def _get_live_odds_data(self, bet_slip):
        """Lấy dữ liệu live odds từ Risk Management Service"""
        try:
            import requests
            
            # Lấy thông tin về các selection trong phiếu cược
            selections_info = []
            for selection in bet_slip.selections.all():
                match = selection.odd.match
                selections_info.append({
                    'match_id': match.id,
                    'selection_id': selection.id,
                    'bet_type': selection.odd.bet_type.name,
                    'outcome': selection.odd.outcome
                })
            
            # Gọi API Risk Management Service để lấy live odds
            response = requests.post(
                f"{self.risk_service_url}/api/cashout/live-odds/",
                json={
                    'selections': selections_info,
                    'bet_slip_id': bet_slip.id,
                    'user_id': bet_slip.user.id
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.warning(f"Không thể lấy live odds từ Risk Service: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Lỗi lấy live odds data: {e}")
            return None
    
    def _trigger_auto_order(self, bet_slip, reason):
        """Kích hoạt lệnh tự động và thực hiện Cash Out"""
        try:
            # 1. Cập nhật trạng thái lệnh tự động
            bet_slip.trigger_auto_order(reason)
            
            # 2. Khởi tạo quy trình Saga Cash Out tự động
            saga_result = self._initiate_auto_cashout_saga(bet_slip, reason)
            
            if saga_result['success']:
                # 3. Hoàn thành lệnh tự động
                bet_slip.complete_auto_order()
                
                self.logger.info(f"Hoàn thành lệnh tự động {reason} cho BetSlip #{bet_slip.id}")
                
                return {
                    'success': True,
                    'bet_slip_id': bet_slip.id,
                    'reason': reason,
                    'saga_id': saga_result.get('saga_id')
                }
            else:
                # Nếu Saga thất bại, khôi phục trạng thái
                bet_slip.auto_order_status = 'ACTIVE'
                bet_slip.save()
                
                return {
                    'success': False,
                    'error': saga_result.get('error', 'Saga thất bại')
                }
                
        except Exception as e:
            self.logger.error(f"Lỗi kích hoạt lệnh tự động cho BetSlip #{bet_slip.id}: {e}")
            return {'success': False, 'error': str(e)}
    
    def _initiate_auto_cashout_saga(self, bet_slip, reason):
        """Khởi tạo Saga transaction cho Cash Out tự động"""
        try:
            import requests
            
            # Gọi API Saga Service để khởi tạo transaction
            response = requests.post(
                f"{self.saga_service_url}/api/sagas/auto-cashout/start/",
                json={
                    'bet_slip_id': bet_slip.id,
                    'user_id': bet_slip.user.id,
                    'reason': reason,
                    'auto_order_id': f"auto_{bet_slip.id}_{int(time.time())}",
                    'cashout_data': {
                        'bet_slip_id': bet_slip.id,
                        'user_id': bet_slip.user.id,
                        'reason': f"Auto {reason}",
                        'is_auto_order': True
                    }
                },
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'saga_id': result.get('saga_id'),
                    'message': 'Saga transaction đã được khởi tạo'
                }
            else:
                return {
                    'success': False,
                    'error': f"Saga service trả về lỗi: {response.status_code}"
                }
                
        except Exception as e:
            self.logger.error(f"Lỗi khởi tạo Saga auto cashout: {e}")
            return {'success': False, 'error': str(e)}
    
    def suspend_auto_orders_for_market(self, match_id, reason="Market suspended"):
        """Tạm dừng tất cả lệnh tự động cho một trận đấu"""
        try:
            from .models import BetSlip
            
            suspended_count = BetSlip.objects.filter(
                selections__odd__match_id=match_id,
                auto_order_status='ACTIVE'
            ).update(auto_order_status='SUSPENDED')
            
            self.logger.info(f"Đã tạm dừng {suspended_count} lệnh tự động cho match {match_id}")
            
            return {
                'success': True,
                'suspended_count': suspended_count,
                'match_id': match_id
            }
            
        except Exception as e:
            self.logger.error(f"Lỗi tạm dừng lệnh tự động cho match {match_id}: {e}")
            return {'success': False, 'error': str(e)}
    
    def resume_auto_orders_for_market(self, match_id):
        """Khôi phục tất cả lệnh tự động cho một trận đấu"""
        try:
            from .models import BetSlip
            
            resumed_count = BetSlip.objects.filter(
                selections__odd__match_id=match_id,
                auto_order_status='SUSPENDED'
            ).update(auto_order_status='ACTIVE')
            
            self.logger.info(f"Đã khôi phục {resumed_count} lệnh tự động cho match {match_id}")
            
            return {
                'success': True,
                'resumed_count': resumed_count,
                'match_id': match_id
            }
            
        except Exception as e:
            self.logger.error(f"Lỗi khôi phục lệnh tự động cho match {match_id}: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_auto_order_statistics(self):
        """Lấy thống kê về lệnh tự động"""
        try:
            from .models import BetSlip
            from django.db.models import Count, Q
            
            stats = {
                'total_active': BetSlip.objects.filter(
                    auto_order_enabled=True,
                    auto_order_status='ACTIVE'
                ).count(),
                'total_suspended': BetSlip.objects.filter(
                    auto_order_enabled=True,
                    auto_order_status='SUSPENDED'
                ).count(),
                'total_triggered_today': BetSlip.objects.filter(
                    auto_order_status='TRIGGERED',
                    auto_order_triggered_at__date=timezone.now().date()
                ).count(),
                'take_profit_count': BetSlip.objects.filter(
                    auto_order_reason='TAKE_PROFIT'
                ).count(),
                'stop_loss_count': BetSlip.objects.filter(
                    auto_order_reason='STOP_LOSS'
                ).count()
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Lỗi lấy thống kê lệnh tự động: {e}")
            return {}

class RiskCheckService:
    """Service tích hợp với Risk Management Service để kiểm tra rủi ro"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        from shared.base_settings import get_service_url
        self.risk_service_url = get_service_url('risk')
    
    def check_bet_risk(self, bet_data: Dict) -> Dict:
        """Kiểm tra rủi ro của một bet thông qua Risk Management Service"""
        try:
            # Chuẩn bị dữ liệu để gửi đến Risk Management Service
            risk_check_payload = {
                'user_id': bet_data['user_id'],
                'match_id': bet_data['match_id'],
                'bet_type_id': bet_data['bet_type_id'],
                'outcome': bet_data['outcome'],
                'stake_amount': float(bet_data['stake_amount']),
                'odds_value': float(bet_data['odds_value'])
            }
            
            # Gọi API Risk Management Service
            response = requests.post(
                f"{self.risk_service_url}/api/v1/risk/risk-check/check_bet/",
                json=risk_check_payload,
                timeout=15
            )
            
            if response.status_code == 200:
                risk_result = response.json()
                self.logger.info(f"Risk check completed for bet: {bet_data.get('user_id')} - {risk_result.get('approved')}")
                return risk_result
            else:
                self.logger.error(f"Risk check failed: {response.status_code} - {response.text}")
                return {
                    'approved': False,
                    'error': f'Risk service error: {response.status_code}',
                    'fallback': True
                }
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to connect to risk service: {str(e)}")
            return {
                'approved': False,
                'error': 'Risk service unavailable',
                'fallback': True
            }
        except Exception as e:
            self.logger.error(f"Error in risk check: {str(e)}")
            return {
                'approved': False,
                'error': 'Internal error during risk check',
                'fallback': True
            }
    
    def get_live_odds(self, odds_request: Dict) -> Dict:
        """Lấy live odds từ Risk Management Service"""
        try:
            response = requests.post(
                f"{self.risk_service_url}/api/v1/risk/risk-check/get_live_odds/",
                json=odds_request,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.warning(f"Failed to get live odds: {response.status_code}")
                return self._get_fallback_live_odds(odds_request)
                
        except Exception as e:
            self.logger.error(f"Error getting live odds: {str(e)}")
            return self._get_fallback_live_odds(odds_request)
    
    def get_event_margin(self, match_id: str) -> Dict:
        """Lấy event margin từ Risk Management Service"""
        try:
            response = requests.post(
                f"{self.risk_service_url}/api/v1/risk/risk-check/get_event_margin/",
                json={'match_id': match_id},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.warning(f"Failed to get event margin: {response.status_code}")
                return {'effective_margin': 0.05}  # Default 5%
                
        except Exception as e:
            self.logger.error(f"Error getting event margin: {str(e)}")
            return {'effective_margin': 0.05}  # Default 5%
    
    def _get_fallback_live_odds(self, odds_request: Dict) -> Dict:
        """Fallback live odds khi không thể kết nối Risk Management Service"""
        return {
            'match_id': odds_request.get('match_id'),
            'bet_type_id': odds_request.get('bet_type_id'),
            'outcome': odds_request.get('outcome'),
            'live_odds': 1.50,  # Default odds
            'confidence_score': 0.5,
            'is_reliable_for_cashout': False,
            'fallback': True
        }