import requests
import json
import time
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from django.db import transaction, F
from celery import shared_task
import logging

from .models import SagaTransaction, SagaStep, SagaEvent, SagaDefinition
from .kafka_producer import KafkaProducer

logger = logging.getLogger(__name__)

class SagaOrchestrator:
    """Main saga orchestrator class"""
    
    def __init__(self):
        self.kafka_producer = KafkaProducer()
    
    def start_saga(self, saga_type, user_id, input_data, correlation_id=None):
        """Start a new saga transaction"""
        if not correlation_id:
            correlation_id = f"saga_{saga_type}_{int(time.time())}_{user_id}"
        
        try:
            with transaction.atomic():
                # Get saga definition
                saga_definition = SagaDefinition.objects.get(
                    saga_type=saga_type, 
                    is_active=True
                )
                
                # Create saga transaction
                saga_transaction = SagaTransaction.objects.create(
                    saga_type=saga_type,
                    user_id=user_id,
                    correlation_id=correlation_id,
                    input_data=input_data,
                    timeout_at=timezone.now() + timedelta(seconds=saga_definition.timeout_seconds),
                    max_retries=saga_definition.max_retries
                )
                
                # Create saga steps from definition
                self._create_saga_steps(saga_transaction, saga_definition)
                
                # Log saga started event
                SagaEvent.objects.create(
                    saga_transaction=saga_transaction,
                    event_type='saga_started',
                    message=f"Saga {saga_type} started for user {user_id}"
                )
                
                # Start execution asynchronously
                execute_saga.delay(str(saga_transaction.id))
                
                return saga_transaction
                
        except SagaDefinition.DoesNotExist:
            logger.error(f"Saga definition not found for type: {saga_type}")
            raise Exception(f"Saga definition not found for type: {saga_type}")
        except Exception as e:
            logger.error(f"Failed to start saga: {e}")
            raise
    
    def start_cashout_saga(self, bet_slip_id, user_id, bookmaker_type='SYSTEM', bookmaker_id='system'):
        """Khởi tạo Cash Out Saga transaction"""
        try:
            input_data = {
                'bet_slip_id': bet_slip_id,
                'user_id': user_id,
                'bookmaker_type': bookmaker_type,
                'bookmaker_id': bookmaker_id,
                'saga_type': 'cashout_flow',
                'timestamp': timezone.now().isoformat()
            }
            
            return self.start_saga('cashout_flow', user_id, input_data)
            
        except Exception as e:
            logger.error(f"Failed to start cashout saga: {e}")
            raise

    def process_cashout_step(self, step, cashout_data):
        """Xử lý step Cash Out cụ thể"""
        try:
            step_name = step.step_name
            
            if step_name == 'cashout_validation':
                return self._execute_cashout_validation(step, cashout_data)
            elif step_name == 'live_odds_fetch':
                return self._execute_live_odds_fetch(step, cashout_data)
            elif step_name == 'cashout_quote':
                return self._execute_cashout_quote(step, cashout_data)
            elif step_name == 'wallet_credit':
                return self._execute_wallet_credit(step, cashout_data)
            elif step_name == 'liability_update':
                return self._execute_liability_update(step, cashout_data)
            elif step_name == 'cashout_completion':
                return self._execute_cashout_completion(step, cashout_data)
            else:
                # Fallback to generic step execution
                return self._execute_step(step)
                
        except Exception as e:
            logger.error(f"Cashout step processing failed: {e}")
            self._fail_step(step, str(e))
            return False

    def _execute_cashout_validation(self, step, cashout_data):
        """Thực hiện validation Cash Out"""
        try:
            # Gọi Betting Service để kiểm tra tính đủ điều kiện
            service_url = settings.MICROSERVICES.get('betting_service')
            if not service_url:
                raise Exception("Betting service URL not found")
            
            response = requests.post(
                f"{service_url}/api/cashout/check-eligibility/",
                json={'bet_slip_id': cashout_data['bet_slip_id']},
                headers={'X-Correlation-ID': step.saga_transaction.correlation_id},
                timeout=15
            )
            
            if response.status_code == 200:
                eligibility_data = response.json()
                if eligibility_data.get('can_cash_out'):
                    step.status = 'completed'
                    step.completed_at = timezone.now()
                    step.response_data = eligibility_data
                    step.save()
                    
                    # Cập nhật context
                    self._update_saga_context(step.saga_transaction, eligibility_data)
                    
                    # Log event
                    SagaEvent.objects.create(
                        saga_transaction=step.saga_transaction,
                        saga_step=step,
                        event_type='cashout_validation_passed',
                        message="Cash Out validation passed"
                    )
                    
                    return True
                else:
                    raise Exception(f"Cash Out not eligible: {eligibility_data.get('reasons', [])}")
            else:
                raise Exception(f"Validation service call failed: {response.status_code}")
                
        except Exception as e:
            self._fail_step(step, f"Cash Out validation failed: {str(e)}")
            return False

    def _execute_live_odds_fetch(self, step, cashout_data):
        """Lấy live odds từ Risk Management Service"""
        try:
            # Gọi Risk Management Service để lấy live odds
            service_url = settings.MICROSERVICES.get('risk_management_service')
            if not service_url:
                raise Exception("Risk Management service URL not found")
            
            response = requests.post(
                f"{service_url}/api/cashout/live-odds/",
                json={'bet_slip_id': cashout_data['bet_slip_id']},
                headers={'X-Correlation-ID': step.saga_transaction.correlation_id},
                timeout=15
            )
            
            if response.status_code == 200:
                odds_data = response.json()
                step.status = 'completed'
                step.completed_at = timezone.now()
                step.response_data = odds_data
                step.save()
                
                # Cập nhật context
                self._update_saga_context(step.saga_transaction, odds_data)
                
                # Log event
                SagaEvent.objects.create(
                    saga_transaction=step.saga_transaction,
                    saga_step=step,
                    event_type='live_odds_fetched',
                    message="Live odds fetched successfully"
                )
                
                return True
            else:
                raise Exception(f"Live odds service call failed: {response.status_code}")
                
        except Exception as e:
            self._fail_step(step, f"Live odds fetch failed: {str(e)}")
            return False

    def _execute_cashout_quote(self, step, cashout_data):
        """Tính toán báo giá Cash Out"""
        try:
            # Gọi Betting Service để tính toán báo giá
            service_url = settings.MICROSERVICES.get('betting_service')
            if not service_url:
                raise Exception("Betting service URL not found")
            
            response = requests.post(
                f"{service_url}/api/cashout/request-quote/",
                json={
                    'bet_slip_id': cashout_data['bet_slip_id'],
                    'bookmaker_type': cashout_data.get('bookmaker_type', 'SYSTEM'),
                    'bookmaker_id': cashout_data.get('bookmaker_id', 'system')
                },
                headers={'X-Correlation-ID': step.saga_transaction.correlation_id},
                timeout=15
            )
            
            if response.status_code == 200:
                quote_data = response.json()
                step.status = 'completed'
                step.completed_at = timezone.now()
                step.response_data = quote_data
                step.save()
                
                # Cập nhật context
                self._update_saga_context(step.saga_transaction, quote_data)
                
                # Log event
                SagaEvent.objects.create(
                    saga_transaction=step.saga_transaction,
                    saga_step=step,
                    event_type='cashout_quote_received',
                    message="Cash Out quote received"
                )
                
                return True
            else:
                raise Exception(f"Quote service call failed: {response.status_code}")
                
        except Exception as e:
            self._fail_step(step, f"Cash Out quote failed: {str(e)}")
            return False

    def _execute_wallet_credit(self, step, cashout_data):
        """Thực hiện cộng tiền vào ví"""
        try:
            # Gọi Wallet Service để cộng tiền
            service_url = settings.MICROSERVICES.get('wallet_service')
            if not service_url:
                raise Exception("Wallet service URL not found")
            
            response = requests.post(
                f"{service_url}/api/cashout/process/",
                json={
                    'bet_slip_id': cashout_data['bet_slip_id'],
                    'user_id': cashout_data['user_id'],
                    'cashout_amount': cashout_data.get('cash_out_value'),
                    'saga_transaction_id': str(step.saga_transaction.id)
                },
                headers={'X-Correlation-ID': step.saga_transaction.correlation_id},
                timeout=15
            )
            
            if response.status_code == 200:
                wallet_data = response.json()
                step.status = 'completed'
                step.completed_at = timezone.now()
                step.response_data = wallet_data
                step.save()
                
                # Cập nhật context
                self._update_saga_context(step.saga_transaction, wallet_data)
                
                # Log event
                SagaEvent.objects.create(
                    saga_transaction=step.saga_transaction,
                    saga_step=step,
                    event_type='cashout_funds_credited',
                    message="Cash Out funds credited to wallet"
                )
                
                return True
            else:
                raise Exception(f"Wallet service call failed: {response.status_code}")
                
        except Exception as e:
            self._fail_step(step, f"Wallet credit failed: {str(e)}")
            return False

    def _execute_liability_update(self, step, cashout_data):
        """Cập nhật liability trong Risk Management Service"""
        try:
            # Gọi Risk Management Service để cập nhật liability
            service_url = settings.MICROSERVICES.get('risk_management_service')
            if not service_url:
                raise Exception("Risk Management service URL not found")
            
            response = requests.post(
                f"{service_url}/api/cashout/liability/update/",
                json={
                    'bet_slip_id': cashout_data['bet_slip_id'],
                    'cashout_amount': cashout_data.get('cash_out_value'),
                    'action': 'PROCESS_CASHOUT'
                },
                headers={'X-Correlation-ID': step.saga_transaction.correlation_id},
                timeout=15
            )
            
            if response.status_code == 200:
                liability_data = response.json()
                step.status = 'completed'
                step.completed_at = timezone.now()
                step.response_data = liability_data
                step.save()
                
                # Cập nhật context
                self._update_saga_context(step.saga_transaction, liability_data)
                
                # Log event
                SagaEvent.objects.create(
                    saga_transaction=step.saga_transaction,
                    saga_step=step,
                    event_type='cashout_liability_updated',
                    message="Cash Out liability updated"
                )
                
                return True
            else:
                raise Exception(f"Liability update service call failed: {response.status_code}")
                
        except Exception as e:
            self._fail_step(step, f"Liability update failed: {str(e)}")
            return False

    def _execute_cashout_completion(self, step, cashout_data):
        """Hoàn thành giao dịch Cash Out"""
        try:
            # Gọi Betting Service để hoàn thành
            service_url = settings.MICROSERVICES.get('betting_service')
            if not service_url:
                raise Exception("Betting service URL not found")
            
            response = requests.post(
                f"{service_url}/api/cashout/complete/",
                json={
                    'bet_slip_id': cashout_data['bet_slip_id'],
                    'cashout_history_id': cashout_data.get('cashout_history_id'),
                    'saga_transaction_id': str(step.saga_transaction.id)
                },
                headers={'X-Correlation-ID': step.saga_transaction.correlation_id},
                timeout=15
            )
            
            if response.status_code == 200:
                completion_data = response.json()
                step.status = 'completed'
                step.completed_at = timezone.now()
                step.response_data = completion_data
                step.save()
                
                # Cập nhật context
                self._update_saga_context(step.saga_transaction, completion_data)
                
                # Log event
                SagaEvent.objects.create(
                    saga_transaction=step.saga_transaction,
                    saga_step=step,
                    event_type='cashout_completed',
                    message="Cash Out completed successfully"
                )
                
                return True
            else:
                raise Exception(f"Completion service call failed: {response.status_code}")
                
        except Exception as e:
            self._fail_step(step, f"Cash Out completion failed: {str(e)}")
            return False

    def rollback_cashout_saga(self, saga_transaction_id, reason=""):
        """Rollback Cash Out Saga transaction"""
        try:
            saga_transaction = SagaTransaction.objects.get(id=saga_transaction_id)
            
            # Cập nhật trạng thái
            saga_transaction.status = 'rollback_initiated'
            saga_transaction.save()
            
            # Log rollback event
            SagaEvent.objects.create(
                saga_transaction=saga_transaction,
                event_type='cashout_rollback_initiated',
                message=f"Cash Out rollback initiated: {reason}"
            )
            
            # Thực hiện rollback các bước đã hoàn thành
            completed_steps = saga_transaction.steps.filter(
                status='completed'
            ).order_by('-step_order')
            
            for step in completed_steps:
                self._rollback_cashout_step(step, reason)
            
            # Đánh dấu rollback hoàn thành
            saga_transaction.status = 'rolled_back'
            saga_transaction.completed_at = timezone.now()
            saga_transaction.save()
            
            # Log rollback completed
            SagaEvent.objects.create(
                saga_transaction=saga_transaction,
                event_type='cashout_rollback_completed',
                message="Cash Out rollback completed"
            )
            
            return True
            
        except SagaTransaction.DoesNotExist:
            logger.error(f"Saga transaction not found: {saga_transaction_id}")
            return False
        except Exception as e:
            logger.error(f"Cash Out rollback failed: {e}")
            return False

    def _rollback_cashout_step(self, step, reason):
        """Rollback một bước Cash Out cụ thể"""
        try:
            step_name = step.step_name
            
            if step_name == 'wallet_credit':
                self._rollback_wallet_credit(step, reason)
            elif step_name == 'liability_update':
                self._rollback_liability_update(step, reason)
            elif step_name == 'cashout_completion':
                self._rollback_cashout_completion(step, reason)
            else:
                # Các bước khác không cần rollback
                step.status = 'rolled_back'
                step.save()
                
        except Exception as e:
            logger.error(f"Rollback step {step_name} failed: {e}")
            step.status = 'rollback_failed'
            step.error_message = str(e)
            step.save()

    def _rollback_wallet_credit(self, step, reason):
        """Rollback việc cộng tiền vào ví"""
        try:
            service_url = settings.MICROSERVICES.get('wallet_service')
            if not service_url:
                raise Exception("Wallet service URL not found")
            
            response = requests.post(
                f"{service_url}/api/cashout/rollback/",
                json={
                    'bet_slip_id': step.saga_transaction.input_data.get('bet_slip_id'),
                    'user_id': step.saga_transaction.user_id,
                    'saga_transaction_id': str(step.saga_transaction.id),
                    'reason': reason
                },
                headers={'X-Correlation-ID': step.saga_transaction.correlation_id},
                timeout=15
            )
            
            if response.status_code == 200:
                step.status = 'rolled_back'
                step.save()
                
                SagaEvent.objects.create(
                    saga_transaction=step.saga_transaction,
                    saga_step=step,
                    event_type='wallet_credit_rolled_back',
                    message="Wallet credit rolled back"
                )
            else:
                raise Exception(f"Wallet rollback failed: {response.status_code}")
                
        except Exception as e:
            step.status = 'rollback_failed'
            step.error_message = str(e)
            step.save()
            logger.error(f"Wallet credit rollback failed: {e}")

    def _rollback_liability_update(self, step, reason):
        """Rollback việc cập nhật liability"""
        try:
            service_url = settings.MICROSERVICES.get('risk_management_service')
            if not service_url:
                raise Exception("Risk Management service URL not found")
            
            response = requests.post(
                f"{service_url}/api/cashout/liability/rollback/",
                json={
                    'bet_slip_id': step.saga_transaction.input_data.get('bet_slip_id'),
                    'action': 'ROLLBACK_CASHOUT',
                    'reason': reason
                },
                headers={'X-Correlation-ID': step.saga_transaction.correlation_id},
                timeout=15
            )
            
            if response.status_code == 200:
                step.status = 'rolled_back'
                step.save()
                
                SagaEvent.objects.create(
                    saga_transaction=step.saga_transaction,
                    saga_step=step,
                    event_type='liability_update_rolled_back',
                    message="Liability update rolled back"
                )
            else:
                raise Exception(f"Liability rollback failed: {response.status_code}")
                
        except Exception as e:
            step.status = 'rollback_failed'
            step.error_message = str(e)
            step.save()
            logger.error(f"Liability update rollback failed: {e}")

    def _rollback_cashout_completion(self, step, reason):
        """Rollback việc hoàn thành Cash Out"""
        try:
            service_url = settings.MICROSERVICES.get('betting_service')
            if not service_url:
                raise Exception("Betting service URL not found")
            
            response = requests.post(
                f"{service_url}/api/cashout/cancel/",
                json={
                    'bet_slip_id': step.saga_transaction.input_data.get('bet_slip_id'),
                    'reason': reason
                },
                headers={'X-Correlation-ID': step.saga_transaction.correlation_id},
                timeout=15
            )
            
            if response.status_code == 200:
                step.status = 'rolled_back'
                step.save()
                
                SagaEvent.objects.create(
                    saga_transaction=step.saga_transaction,
                    saga_step=step,
                    event_type='cashout_completion_rolled_back',
                    message="Cash Out completion rolled back"
                )
            else:
                raise Exception(f"Completion rollback failed: {response.status_code}")
                
        except Exception as e:
            step.status = 'rollback_failed'
            step.error_message = str(e)
            step.save()
            logger.error(f"Cash Out completion rollback failed: {e}")
    
    def _create_saga_steps(self, saga_transaction, saga_definition):
        """Create saga steps from workflow definition"""
        workflow = saga_definition.workflow_definition
        steps = workflow.get('steps', [])
        
        for i, step_def in enumerate(steps):
            SagaStep.objects.create(
                saga_transaction=saga_transaction,
                step_name=step_def['name'],
                step_type=step_def.get('type', 'service_call'),
                step_order=i + 1,
                service_name=step_def['service'],
                service_endpoint=step_def['endpoint'],
                http_method=step_def.get('method', 'POST'),
                request_data=step_def.get('request_template', {}),
                compensation_service=step_def.get('compensation', {}).get('service'),
                compensation_endpoint=step_def.get('compensation', {}).get('endpoint'),
                compensation_method=step_def.get('compensation', {}).get('method', 'POST'),
                compensation_data=step_def.get('compensation', {}).get('data', {}),
                max_retries=step_def.get('max_retries', saga_definition.max_retries)
            )
    
    def execute_saga(self, saga_transaction_id):
        """Execute saga transaction"""
        try:
            saga_transaction = SagaTransaction.objects.get(id=saga_transaction_id)
            
            if saga_transaction.status != 'pending':
                logger.warning(f"Saga {saga_transaction_id} is not in pending status")
                return
            
            # Update status to in_progress
            saga_transaction.status = 'in_progress'
            saga_transaction.started_at = timezone.now()
            saga_transaction.save()
            
            # Execute steps in order
            steps = saga_transaction.steps.order_by('step_order')
            
            for step in steps:
                success = self._execute_step(step)
                if not success:
                    # Step failed, start compensation
                    self._start_compensation(saga_transaction)
                    return
            
            # All steps completed successfully
            self._complete_saga(saga_transaction)
            
        except SagaTransaction.DoesNotExist:
            logger.error(f"Saga transaction not found: {saga_transaction_id}")
        except Exception as e:
            logger.error(f"Error executing saga {saga_transaction_id}: {e}")
            try:
                saga_transaction = SagaTransaction.objects.get(id=saga_transaction_id)
                self._fail_saga(saga_transaction, str(e))
            except:
                pass
    
    def _execute_step(self, step):
        """Execute a single saga step"""
        try:
            step.status = 'in_progress'
            step.started_at = timezone.now()
            step.save()
            
            # Log step started
            SagaEvent.objects.create(
                saga_transaction=step.saga_transaction,
                saga_step=step,
                event_type='step_started',
                message=f"Step {step.step_name} started"
            )
            
            # Kiểm tra nếu là Cash Out saga, sử dụng logic xử lý riêng
            if step.saga_transaction.saga_type == 'cashout_flow':
                cashout_data = step.saga_transaction.input_data
                return self.process_cashout_step(step, cashout_data)
            
            # Prepare request data
            request_data = self._prepare_request_data(step)
            
            # Get service URL
            service_url = settings.MICROSERVICES.get(step.service_name)
            if not service_url:
                raise Exception(f"Service URL not found for {step.service_name}")
            
            full_url = f"{service_url}{step.service_endpoint}"
            
            # Prepare headers
            headers = {
                'Content-Type': 'application/json',
                'X-Correlation-ID': step.saga_transaction.correlation_id,
                'X-User-ID': str(step.saga_transaction.user_id)
            }
            headers.update(step.headers)
            
            # Make service call
            response = self._make_service_call(
                step.http_method,
                full_url,
                request_data,
                headers
            )
            
            # Process response
            if response.status_code in [200, 201, 202]:
                step.status = 'completed'
                step.completed_at = timezone.now()
                step.response_data = response.json() if response.content else {}
                step.save()
                
                # Update saga context with response data
                self._update_saga_context(step.saga_transaction, step.response_data)
                
                # Log step completed
                SagaEvent.objects.create(
                    saga_transaction=step.saga_transaction,
                    saga_step=step,
                    event_type='step_completed',
                    message=f"Step {step.step_name} completed successfully"
                )
                
                return True
            else:
                # Step failed
                error_msg = f"Service call failed with status {response.status_code}: {response.text}"
                self._fail_step(step, error_msg)
                return False
                
        except Exception as e:
            error_msg = f"Step execution failed: {str(e)}"
            self._fail_step(step, error_msg)
            return False
    
    def _prepare_request_data(self, step):
        """Prepare request data using template and saga context"""
        request_template = step.request_data
        saga_context = step.saga_transaction.context_data
        input_data = step.saga_transaction.input_data
        
        # Simple template substitution (in production, use a proper template engine)
        request_data = json.loads(json.dumps(request_template))
        
        # Replace placeholders with actual values
        def replace_placeholders(obj):
            if isinstance(obj, dict):
                return {k: replace_placeholders(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [replace_placeholders(item) for item in obj]
            elif isinstance(obj, str):
                if obj.startswith('${context.'):
                    key = obj[10:-1]  # Remove ${context. and }
                    return saga_context.get(key, obj)
                elif obj.startswith('${input.'):
                    key = obj[8:-1]  # Remove ${input. and }
                    return input_data.get(key, obj)
                return obj
            else:
                return obj
        
        return replace_placeholders(request_data)
    
    def _make_service_call(self, method, url, data, headers):
        """Make HTTP service call"""
        timeout = 30
        
        if method.upper() == 'GET':
            return requests.get(url, params=data, headers=headers, timeout=timeout)
        elif method.upper() == 'POST':
            return requests.post(url, json=data, headers=headers, timeout=timeout)
        elif method.upper() == 'PUT':
            return requests.put(url, json=data, headers=headers, timeout=timeout)
        elif method.upper() == 'PATCH':
            return requests.patch(url, json=data, headers=headers, timeout=timeout)
        elif method.upper() == 'DELETE':
            return requests.delete(url, headers=headers, timeout=timeout)
        else:
            raise Exception(f"Unsupported HTTP method: {method}")
    
    def _update_saga_context(self, saga_transaction, response_data):
        """Update saga context with response data"""
        saga_transaction.context_data.update(response_data)
        saga_transaction.save()
    
    def _fail_step(self, step, error_message):
        """Mark step as failed"""
        step.status = 'failed'
        step.error_message = error_message
        step.save()
        
        # Log step failed
        SagaEvent.objects.create(
            saga_transaction=step.saga_transaction,
            saga_step=step,
            event_type='step_failed',
            message=f"Step {step.step_name} failed: {error_message}"
        )
        
        logger.error(f"Step {step.step_name} failed: {error_message}")
    
    def _start_compensation(self, saga_transaction):
        """Start compensation process"""
        try:
            saga_transaction.status = 'compensating'
            saga_transaction.save()
            
            # Log compensation started
            SagaEvent.objects.create(
                saga_transaction=saga_transaction,
                event_type='compensation_started',
                message="Compensation process started"
            )
            
            # Compensate completed steps in reverse order
            completed_steps = saga_transaction.steps.filter(
                status='completed'
            ).order_by('-step_order')
            
            for step in completed_steps:
                self._compensate_step(step)
            
            # Mark saga as compensated
            saga_transaction.status = 'compensated'
            saga_transaction.completed_at = timezone.now()
            saga_transaction.save()
            
            # Log compensation completed
            SagaEvent.objects.create(
                saga_transaction=saga_transaction,
                event_type='compensation_completed',
                message="Compensation process completed"
            )
            
        except Exception as e:
            logger.error(f"Compensation failed for saga {saga_transaction.id}: {e}")
            saga_transaction.status = 'failed'
            saga_transaction.error_message = f"Compensation failed: {str(e)}"
            saga_transaction.save()
    
    def _compensate_step(self, step):
        """Compensate a single step"""
        if not step.compensation_service or not step.compensation_endpoint:
            logger.info(f"No compensation defined for step {step.step_name}")
            return
        
        try:
            step.status = 'compensating'
            step.save()
            
            # Prepare compensation data
            compensation_data = self._prepare_compensation_data(step)
            
            # Get service URL
            service_url = settings.MICROSERVICES.get(step.compensation_service)
            if not service_url:
                raise Exception(f"Compensation service URL not found for {step.compensation_service}")
            
            full_url = f"{service_url}{step.compensation_endpoint}"
            
            # Prepare headers
            headers = {
                'Content-Type': 'application/json',
                'X-Correlation-ID': step.saga_transaction.correlation_id,
                'X-User-ID': str(step.saga_transaction.user_id)
            }
            
            # Make compensation call
            response = self._make_service_call(
                step.compensation_method,
                full_url,
                compensation_data,
                headers
            )
            
            if response.status_code in [200, 201, 202]:
                step.status = 'compensated'
                step.save()
                logger.info(f"Step {step.step_name} compensated successfully")
            else:
                raise Exception(f"Compensation call failed with status {response.status_code}")
                
        except Exception as e:
            step.status = 'failed'
            step.error_message = f"Compensation failed: {str(e)}"
            step.save()
            logger.error(f"Compensation failed for step {step.step_name}: {e}")
    
    def _prepare_compensation_data(self, step):
        """Prepare compensation data"""
        compensation_template = step.compensation_data
        response_data = step.response_data
        
        # Use response data to prepare compensation
        compensation_data = json.loads(json.dumps(compensation_template))
        
        # Replace placeholders with response data
        def replace_placeholders(obj):
            if isinstance(obj, dict):
                return {k: replace_placeholders(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [replace_placeholders(item) for item in obj]
            elif isinstance(obj, str):
                if obj.startswith('${response.'):
                    key = obj[11:-1]  # Remove ${response. and }
                    return response_data.get(key, obj)
                return obj
            else:
                return obj
        
        return replace_placeholders(compensation_data)
    
    def _complete_saga(self, saga_transaction):
        """Mark saga as completed"""
        saga_transaction.status = 'completed'
        saga_transaction.completed_at = timezone.now()
        saga_transaction.save()
        
        # Log saga completed
        SagaEvent.objects.create(
            saga_transaction=saga_transaction,
            event_type='saga_completed',
            message="Saga completed successfully"
        )
        
        # Publish completion event to Kafka
        self.kafka_producer.publish_event(
            'saga_completed',
            {
                'saga_id': str(saga_transaction.id),
                'saga_type': saga_transaction.saga_type,
                'user_id': saga_transaction.user_id,
                'correlation_id': saga_transaction.correlation_id,
                'result_data': saga_transaction.result_data
            }
        )
        
        logger.info(f"Saga {saga_transaction.id} completed successfully")
    
    def _fail_saga(self, saga_transaction, error_message):
        """Mark saga as failed"""
        saga_transaction.status = 'failed'
        saga_transaction.error_message = error_message
        saga_transaction.completed_at = timezone.now()
        saga_transaction.save()
        
        # Log saga failed
        SagaEvent.objects.create(
            saga_transaction=saga_transaction,
            event_type='saga_failed',
            message=f"Saga failed: {error_message}"
        )
        
        logger.error(f"Saga {saga_transaction.id} failed: {error_message}")

# Celery tasks
@shared_task
def execute_saga(saga_transaction_id):
    """Celery task to execute saga"""
    orchestrator = SagaOrchestrator()
    orchestrator.execute_saga(saga_transaction_id)

@shared_task
def check_saga_timeouts():
    """Check for timed out sagas"""
    timeout_sagas = SagaTransaction.objects.filter(
        status__in=['pending', 'in_progress'],
        timeout_at__lt=timezone.now()
    )
    
    for saga in timeout_sagas:
        saga.status = 'timeout'
        saga.completed_at = timezone.now()
        saga.save()
        
        SagaEvent.objects.create(
            saga_transaction=saga,
            event_type='saga_timeout',
            message="Saga timed out"
        )
        
        logger.warning(f"Saga {saga.id} timed out")

@shared_task
def retry_failed_steps():
    """Retry failed steps that haven't exceeded max retries"""
    failed_steps = SagaStep.objects.filter(
        status='failed',
        retry_count__lt=F('max_retries'),
        saga_transaction__status='in_progress'
    )
    
    for step in failed_steps:
        step.retry_count += 1
        step.status = 'pending'
        step.save()
        
        SagaEvent.objects.create(
            saga_transaction=step.saga_transaction,
            saga_step=step,
            event_type='retry_attempted',
            message=f"Retry attempt {step.retry_count} for step {step.step_name}"
        )
        
        # Re-execute the step
        orchestrator = SagaOrchestrator()
        orchestrator._execute_step(step)

