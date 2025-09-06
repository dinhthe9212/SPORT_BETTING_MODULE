import os
import uuid
import logging
import requests
from datetime import datetime

logger = logging.getLogger(__name__)

class MatchCancellationSagaService:
    """Saga Service xử lý việc hủy/hoãn trận đấu với rollback và compensation"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        from shared.base_settings import get_service_url
        self.betting_service_url = get_service_url('betting')
        self.payment_service_url = get_service_url('payment')
        self.notification_service_url = get_service_url('notification')
    
    def execute_match_cancellation_saga(self, match_id, cancellation_type, reason=""):
        """
        Thực hiện saga cho việc hủy/hoãn trận đấu
        
        Args:
            match_id: ID trận đấu
            cancellation_type: 'CANCELLED' hoặc 'POSTPONED'
            reason: Lý do hủy/hoãn
        """
        saga_id = str(uuid.uuid4())
        
        try:
            self.logger.info(f"Bắt đầu Match Cancellation Saga {saga_id} cho match {match_id}")
            
            # Bước 1: Tạm dừng thị trường
            step1_result = self._step1_suspend_market(saga_id, match_id, cancellation_type, reason)
            if not step1_result['success']:
                return self._rollback_saga(saga_id, match_id, 1, step1_result['error'])
            
            # Bước 2: Xử lý hoàn tiền (chỉ khi hủy)
            if cancellation_type == 'CANCELLED':
                step2_result = self._step2_process_refunds(saga_id, match_id)
                if not step2_result['success']:
                    return self._rollback_saga(saga_id, match_id, 2, step2_result['error'])
            
            # Bước 3: Khôi phục quyền sở hữu P2P (chỉ khi hủy)
            if cancellation_type == 'CANCELLED':
                step3_result = self._step3_restore_ownership(saga_id, match_id)
                if not step3_result['success']:
                    return self._rollback_saga(saga_id, match_id, 3, step3_result['error'])
            
            # Bước 4: Gửi thông báo
            step4_result = self._step4_send_notifications(saga_id, match_id, cancellation_type, reason)
            if not step4_result['success']:
                self.logger.warning(f"Không thể gửi thông báo: {step4_result['error']}")
            
            # Bước 5: Cập nhật trạng thái cuối cùng
            step5_result = self._step5_finalize_cancellation(saga_id, match_id, cancellation_type, reason)
            if not step5_result['success']:
                return self._rollback_saga(saga_id, match_id, 5, step5_result['error'])
            
            # Saga hoàn thành thành công
            self.logger.info(f"Match Cancellation Saga {saga_id} hoàn thành thành công")
            
            return {
                'saga_id': saga_id,
                'success': True,
                'match_id': match_id,
                'cancellation_type': cancellation_type,
                'message': f'Saga hoàn thành thành công cho match {match_id}',
                'steps_completed': 5,
                'final_status': cancellation_type
            }
            
        except Exception as e:
            self.logger.error(f"Lỗi trong Match Cancellation Saga {saga_id}: {str(e)}")
            return self._rollback_saga(saga_id, match_id, 0, str(e))
    
    def _step1_suspend_market(self, saga_id, match_id, cancellation_type, reason):
        """Bước 1: Tạm dừng thị trường"""
        try:
            self.logger.info(f"Saga {saga_id}: Bước 1 - Tạm dừng thị trường")
            
            # Gọi betting service để tạm dừng thị trường
            response = requests.post(
                f"{self.betting_service_url}/api/matches/{match_id}/market-suspension/suspend/",
                json={
                    'suspension_type': 'MANUAL',
                    'reason': f"Trận đấu bị {cancellation_type.lower()}: {reason}",
                    'duration_minutes': 1440,  # 24 giờ
                    'p2p_orders_suspended': True,
                    'new_bets_suspended': True,
                    'cash_out_suspended': True
                },
                timeout=30
            )
            
            if response.status_code == 200:
                self.logger.info(f"Saga {saga_id}: Bước 1 hoàn thành")
                return {'success': True, 'data': response.json()}
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                self.logger.error(f"Saga {saga_id}: Bước 1 thất bại - {error_msg}")
                return {'success': False, 'error': error_msg}
                
        except Exception as e:
            self.logger.error(f"Saga {saga_id}: Lỗi Bước 1 - {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _step2_process_refunds(self, saga_id, match_id):
        """Bước 2: Xử lý hoàn tiền"""
        try:
            self.logger.info(f"Saga {saga_id}: Bước 2 - Xử lý hoàn tiền")
            
            # Gọi betting service để xử lý hoàn tiền
            response = requests.post(
                f"{self.betting_service_url}/api/match-cancellations/{match_id}/cancel_match/",
                json={'reason': 'Trận đấu bị hủy - xử lý tự động'},
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                self.logger.info(f"Saga {saga_id}: Bước 2 hoàn thành - {result.get('refund_count', 0)} refunds")
                return {'success': True, 'data': result}
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                self.logger.error(f"Saga {saga_id}: Bước 2 thất bại - {error_msg}")
                return {'success': False, 'error': error_msg}
                
        except Exception as e:
            self.logger.error(f"Saga {saga_id}: Lỗi Bước 2 - {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _step3_restore_ownership(self, saga_id, match_id):
        """Bước 3: Khôi phục quyền sở hữu P2P"""
        try:
            self.logger.info(f"Saga {saga_id}: Bước 3 - Khôi phục quyền sở hữu P2P")
            
            # Gọi betting service để khôi phục ownership
            response = requests.get(
                f"{self.betting_service_url}/api/match-cancellations/{match_id}/cancellation_status/",
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ownership_restored = result.get('ownership_restored', 0)
                self.logger.info(f"Saga {saga_id}: Bước 3 hoàn thành - {ownership_restored} ownerships restored")
                return {'success': True, 'data': result}
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                self.logger.error(f"Saga {saga_id}: Bước 3 thất bại - {error_msg}")
                return {'success': False, 'error': error_msg}
                
        except Exception as e:
            self.logger.error(f"Saga {saga_id}: Lỗi Bước 3 - {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _step4_send_notifications(self, saga_id, match_id, cancellation_type, reason):
        """Bước 4: Gửi thông báo"""
        try:
            self.logger.info(f"Saga {saga_id}: Bước 4 - Gửi thông báo")
            
            # Gửi thông báo cho tất cả người dùng liên quan
            notification_data = {
                'type': 'MATCH_CANCELLATION',
                'match_id': match_id,
                'cancellation_type': cancellation_type,
                'reason': reason,
                'timestamp': datetime.now().isoformat(),
                'priority': 'HIGH'
            }
            
            response = requests.post(
                f"{self.notification_service_url}/api/notifications/broadcast/",
                json=notification_data,
                timeout=30
            )
            
            if response.status_code == 200:
                self.logger.info(f"Saga {saga_id}: Bước 5 hoàn thành")
                return {'success': True, 'data': response.json()}
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                self.logger.warning(f"Saga {saga_id}: Bước 4 thất bại - {error_msg}")
                return {'success': False, 'error': error_msg}
                
        except Exception as e:
            self.logger.warning(f"Saga {saga_id}: Lỗi Bước 4 - {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _step5_finalize_cancellation(self, saga_id, match_id, cancellation_type, reason):
        """Bước 5: Hoàn tất việc hủy/hoãn"""
        try:
            self.logger.info(f"Saga {saga_id}: Bước 5 - Hoàn tất hủy/hoãn")
            
            # Cập nhật trạng thái cuối cùng của match
            response = requests.patch(
                f"{self.betting_service_url}/api/matches/{match_id}/",
                json={
                    'status': cancellation_type,
                    'cancellation_reason': reason,
                    'cancelled_at': datetime.now().isoformat()
                },
                timeout=30
            )
            
            if response.status_code == 200:
                self.logger.info(f"Saga {saga_id}: Bước 5 hoàn thành")
                return {'success': True, 'data': response.json()}
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                self.logger.error(f"Saga {saga_id}: Bước 5 thất bại - {error_msg}")
                return {'success': False, 'error': error_msg}
                
        except Exception as e:
            self.logger.error(f"Saga {saga_id}: Lỗi Bước 5 - {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _rollback_saga(self, saga_id, match_id, failed_step, error_message):
        """Rollback saga khi có lỗi"""
        try:
            self.logger.warning(f"Saga {saga_id}: Rollback từ bước {failed_step} - {error_message}")
            
            # Thực hiện rollback theo từng bước
            if failed_step >= 1:
                self._rollback_step1(saga_id, match_id)
            
            if failed_step >= 2:
                self._rollback_step2(saga_id, match_id)
            
            if failed_step >= 3:
                self._rollback_step3(saga_id, match_id)
            
            if failed_step >= 4:
                self._rollback_step4(saga_id, match_id)
            
            if failed_step >= 5:
                self._rollback_step5(saga_id, match_id)
            
            self.logger.info(f"Saga {saga_id}: Rollback hoàn tất")
            
            return {
                'saga_id': saga_id,
                'success': False,
                'match_id': match_id,
                'error': f'Saga thất bại ở bước {failed_step}: {error_message}',
                'rollback_completed': True
            }
            
        except Exception as e:
            self.logger.error(f"Saga {saga_id}: Lỗi rollback - {str(e)}")
            return {
                'saga_id': saga_id,
                'success': False,
                'match_id': match_id,
                'error': f'Rollback thất bại: {str(e)}',
                'rollback_completed': False
            }
    
    def _rollback_step1(self, saga_id, match_id):
        """Rollback bước 1: Mở lại thị trường"""
        try:
            response = requests.post(
                f"{self.betting_service_url}/api/matches/{match_id}/market-suspension/resume/",
                timeout=30
            )
            self.logger.info(f"Saga {saga_id}: Rollback bước 1 hoàn tất")
        except Exception as e:
            self.logger.error(f"Saga {saga_id}: Lỗi rollback bước 1 - {str(e)}")
    
    def _rollback_step2(self, saga_id, match_id):
        """Rollback bước 2: Khôi phục trạng thái cược"""
        try:
            # Khôi phục trạng thái cược về CONFIRMED
            response = requests.patch(
                f"{self.betting_service_url}/api/matches/{match_id}/restore_bets/",
                timeout=30
            )
            self.logger.info(f"Saga {saga_id}: Rollback bước 2 hoàn tất")
        except Exception as e:
            self.logger.error(f"Saga {saga_id}: Lỗi rollback bước 2 - {str(e)}")
    
    def _rollback_step3(self, saga_id, match_id):
        """Rollback bước 3: Khôi phục quyền sở hữu P2P"""
        try:
            # Khôi phục quyền sở hữu về trạng thái ban đầu
            response = requests.post(
                f"{self.betting_service_url}/api/matches/{match_id}/restore_ownership/",
                timeout=30
            )
            self.logger.info(f"Saga {saga_id}: Rollback bước 3 hoàn tất")
        except Exception as e:
            self.logger.error(f"Saga {saga_id}: Lỗi rollback bước 3 - {str(e)}")
    
    def _rollback_step4(self, saga_id, match_id):
        """Rollback bước 4: Gửi thông báo rollback"""
        try:
            notification_data = {
                'type': 'SAGA_ROLLBACK',
                'message': 'Saga rollback - trận đấu đã được khôi phục',
                'priority': 'HIGH'
            }
            
            response = requests.post(
                f"{self.notification_service_url}/api/notifications/broadcast/",
                json=notification_data,
                timeout=30
            )
            self.logger.info(f"Saga {saga_id}: Rollback bước 4 hoàn tất")
        except Exception as e:
            self.logger.error(f"Saga {saga_id}: Lỗi rollback bước 4 - {str(e)}")
    
    def _rollback_step5(self, saga_id, match_id):
        """Rollback bước 5: Khôi phục trạng thái match"""
        try:
            response = requests.patch(
                f"{self.betting_service_url}/api/matches/{match_id}/",
                json={'status': 'SCHEDULED'},
                timeout=30
            )
            self.logger.info(f"Saga {saga_id}: Rollback bước 5 hoàn tất")
        except Exception as e:
            self.logger.error(f"Saga {saga_id}: Lỗi rollback bước 5 - {str(e)}")
    
    def get_saga_status(self, saga_id):
        """Lấy trạng thái của saga"""
        try:
            # Lấy thông tin saga từ database hoặc cache
            # (Cần implement database model cho saga tracking)
            
            return {
                'saga_id': saga_id,
                'status': 'COMPLETED',  # Placeholder
                'current_step': 5,
                'total_steps': 5,
                'started_at': datetime.now().isoformat(),
                'completed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Lỗi lấy trạng thái saga {saga_id}: {str(e)}")
            return {'error': str(e)}



