"""
Conflict Resolution Manager cho Sports Data Service
Xử lý xung đột dữ liệu từ các providers khác nhau
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from django.utils import timezone
from django.core.cache import cache
from enum import Enum

from ..alerting.alert_manager import alert_manager, AlertLevel

logger = logging.getLogger(__name__)

class ConflictType(Enum):
    """Loại xung đột dữ liệu"""
    SCORE_MISMATCH = "score_mismatch"
    EVENT_TIMING = "event_timing"
    TEAM_INFO = "team_info"
    MATCH_STATUS = "match_status"
    ODDS_DISCREPANCY = "odds_discrepancy"
    STATISTICS_DIFFERENCE = "statistics_difference"

class SourceTier(Enum):
    """Phân cấp độ tin cậy của nguồn dữ liệu"""
    TIER_1 = "TIER_1"  # Trang web chính thức của giải đấu
    TIER_2 = "TIER_2"  # Kênh truyền hình lớn (ESPN, Sky Sports)
    TIER_3 = "TIER_3"  # Các API dữ liệu trả phí
    TIER_4 = "TIER_4"  # Các nguồn dữ liệu miễn phí

class ConflictStatus(Enum):
    """Trạng thái xử lý xung đột"""
    DETECTED = "detected"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    IGNORED = "ignored"

class DataConflict:
    """Đối tượng xung đột dữ liệu"""
    
    def __init__(
        self,
        conflict_type: ConflictType,
        match_id: str,
        sport: str,
        description: str,
        sources: List[Dict[str, Any]],
        detected_at: datetime = None
    ):
        self.conflict_type = conflict_type
        self.match_id = match_id
        self.sport = sport
        self.description = description
        self.sources = sources
        self.detected_at = detected_at or timezone.now()
        self.status = ConflictStatus.DETECTED
        self.resolution = None
        self.resolved_by = None
        self.resolved_at = None
        self.confidence_score = self._calculate_confidence_score()
        
        # Tạo ID duy nhất
        self.id = f"conflict_{self.conflict_type.value}_{self.match_id}_{self.detected_at.strftime('%Y%m%d_%H%M%S')}"
    
    def _calculate_confidence_score(self) -> float:
        """Tính điểm tin cậy dựa trên source tiers"""
        if not self.sources:
            return 0.0
        
        total_score = 0
        for source in self.sources:
            tier = source.get('tier', SourceTier.TIER_4)
            if tier == SourceTier.TIER_1:
                total_score += 1.0
            elif tier == SourceTier.TIER_2:
                total_score += 0.8
            elif tier == SourceTier.TIER_3:
                total_score += 0.6
            else:
                total_score += 0.3
        
        return total_score / len(self.sources)
    
    def to_dict(self) -> Dict[str, Any]:
        """Chuyển đổi thành dictionary"""
        return {
            'id': self.id,
            'conflict_type': self.conflict_type.value,
            'match_id': self.match_id,
            'sport': self.sport,
            'description': self.description,
            'sources': self.sources,
            'detected_at': self.detected_at.isoformat(),
            'status': self.status.value,
            'resolution': self.resolution,
            'resolved_by': self.resolved_by,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'confidence_score': self.confidence_score
        }

class ConflictResolutionManager:
    """
    Quản lý xử lý xung đột dữ liệu
    """
    
    def __init__(self):
        self.active_conflicts: Dict[str, DataConflict] = {}
        self.resolved_conflicts: List[DataConflict] = []
        self.source_tier_mapping = self._initialize_source_tier_mapping()
        self.conflict_rules = self._initialize_conflict_rules()
        
        # Metrics
        self.total_conflicts_detected = 0
        self.total_conflicts_resolved = 0
        self.auto_resolution_count = 0
        self.manual_resolution_count = 0
    
    def _initialize_source_tier_mapping(self) -> Dict[str, SourceTier]:
        """Khởi tạo mapping source tiers"""
        return {
            # Tier 1: Trang web chính thức
            'premierleague.com': SourceTier.TIER_1,
            'laliga.com': SourceTier.TIER_1,
            'bundesliga.com': SourceTier.TIER_1,
            'seriea.it': SourceTier.TIER_1,
            'nba.com': SourceTier.TIER_1,
            'nfl.com': SourceTier.TIER_1,
            'mlb.com': SourceTier.TIER_1,
            
            # Tier 2: Kênh truyền hình lớn
            'espn.com': SourceTier.TIER_2,
            'skysports.com': SourceTier.TIER_2,
            'bbc.com/sport': SourceTier.TIER_2,
            'sportingnews.com': SourceTier.TIER_2,
            
            # Tier 3: API dữ liệu trả phí
            'api-sports.io': SourceTier.TIER_3,
            'the-odds-api.com': SourceTier.TIER_3,
            'sportradar.com': SourceTier.TIER_3,
            
            # Tier 4: Nguồn miễn phí
            'openligadb.de': SourceTier.TIER_4,
            'thesportsdb.com': SourceTier.TIER_4,
            'football-data.org': SourceTier.TIER_4
        }
    
    def _initialize_conflict_rules(self) -> Dict[str, Dict[str, Any]]:
        """Khởi tạo quy tắc xử lý xung đột"""
        return {
            ConflictType.SCORE_MISMATCH.value: {
                'auto_resolution_threshold': 0.8,  # Tự động giải quyết nếu confidence > 80%
                'escalation_threshold': 0.3,       # Escalate nếu confidence < 30%
                'timeout_minutes': 30,             # Timeout để xử lý
                'requires_admin_review': True
            },
            ConflictType.EVENT_TIMING.value: {
                'auto_resolution_threshold': 0.7,
                'escalation_threshold': 0.4,
                'timeout_minutes': 15,
                'requires_admin_review': False
            },
            ConflictType.TEAM_INFO.value: {
                'auto_resolution_threshold': 0.9,
                'escalation_threshold': 0.2,
                'timeout_minutes': 60,
                'requires_admin_review': False
            },
            ConflictType.MATCH_STATUS.value: {
                'auto_resolution_threshold': 0.6,
                'escalation_threshold': 0.5,
                'timeout_minutes': 10,
                'requires_admin_review': True
            },
            ConflictType.ODDS_DISCREPANCY.value: {
                'auto_resolution_threshold': 0.8,
                'escalation_threshold': 0.3,
                'timeout_minutes': 5,
                'requires_admin_review': True
            },
            ConflictType.STATISTICS_DIFFERENCE.value: {
                'auto_resolution_threshold': 0.7,
                'escalation_threshold': 0.4,
                'timeout_minutes': 20,
                'requires_admin_review': False
            }
        }
    
    def detect_conflict(
        self,
        conflict_type: ConflictType,
        match_id: str,
        sport: str,
        description: str,
        data_sources: List[Dict[str, Any]]
    ) -> Optional[DataConflict]:
        """
        Phát hiện xung đột dữ liệu
        """
        try:
            # Phân tích sources và gán tiers
            analyzed_sources = self._analyze_data_sources(data_sources)
            
            # Kiểm tra xem có thực sự là xung đột không
            if not self._is_actual_conflict(analyzed_sources):
                logger.info(f"No actual conflict detected for {conflict_type.value} in match {match_id}")
                return None
            
            # Tạo conflict object
            conflict = DataConflict(
                conflict_type=conflict_type,
                match_id=match_id,
                sport=sport,
                description=description,
                sources=analyzed_sources
            )
            
            # Thêm vào active conflicts
            self.active_conflicts[conflict.id] = conflict
            self.total_conflicts_detected += 1
            
            # Gửi cảnh báo
            alert_manager.send_alert(
                alert_type='data_conflict',
                message=f"Data conflict detected: {description}",
                level=AlertLevel.WARNING,
                metadata={
                    'conflict_id': conflict.id,
                    'conflict_type': conflict_type.value,
                    'match_id': match_id,
                    'sport': sport,
                    'confidence_score': conflict.confidence_score
                }
            )
            
            logger.info(f"Conflict detected: {conflict.id} - {conflict_type.value} - {description}")
            
            # Thử tự động giải quyết
            if self._should_auto_resolve(conflict):
                self._attempt_auto_resolution(conflict)
            
            return conflict
            
        except Exception as e:
            logger.error(f"Error detecting conflict: {str(e)}")
            return None
    
    def _analyze_data_sources(self, data_sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Phân tích và gán tiers cho data sources"""
        analyzed_sources = []
        
        for source in data_sources:
            source_url = source.get('url', '')
            source_name = source.get('name', '')
            
            # Xác định tier dựa trên URL hoặc tên
            tier = SourceTier.TIER_4  # Default tier
            
            for pattern, source_tier in self.source_tier_mapping.items():
                if pattern in source_url.lower() or pattern in source_name.lower():
                    tier = source_tier
                    break
            
            analyzed_source = {
                **source,
                'tier': tier.value,
                'tier_priority': self._get_tier_priority(tier),
                'analyzed_at': timezone.now().isoformat()
            }
            
            analyzed_sources.append(analyzed_source)
        
        # Sắp xếp theo priority (cao nhất trước)
        analyzed_sources.sort(key=lambda x: x['tier_priority'], reverse=True)
        
        return analyzed_sources
    
    def _get_tier_priority(self, tier: SourceTier) -> int:
        """Lấy priority của tier"""
        priorities = {
            SourceTier.TIER_1: 4,
            SourceTier.TIER_2: 3,
            SourceTier.TIER_3: 2,
            SourceTier.TIER_4: 1
        }
        return priorities.get(tier, 1)
    
    def _is_actual_conflict(self, analyzed_sources: List[Dict[str, Any]]) -> bool:
        """Kiểm tra xem có thực sự là xung đột không"""
        if len(analyzed_sources) < 2:
            return False
        
        # So sánh dữ liệu từ các sources
        first_source_data = analyzed_sources[0].get('data', {})
        
        for source in analyzed_sources[1:]:
            current_data = source.get('data', {})
            if self._data_differs_significantly(first_source_data, current_data):
                return True
        
        return False
    
    def _data_differs_significantly(self, data1: Dict, data2: Dict) -> bool:
        """Kiểm tra xem dữ liệu có khác biệt đáng kể không"""
        # Implement logic so sánh dữ liệu cụ thể
        # Ví dụ: so sánh score, timing, status
        return True  # Placeholder
    
    def _should_auto_resolve(self, conflict: DataConflict) -> bool:
        """Kiểm tra xem có nên tự động giải quyết không"""
        rule = self.conflict_rules.get(conflict.conflict_type.value, {})
        threshold = rule.get('auto_resolution_threshold', 0.8)
        
        return conflict.confidence_score >= threshold
    
    def _attempt_auto_resolution(self, conflict: DataConflict):
        """Thử tự động giải quyết xung đột"""
        try:
            # Lấy source có tier cao nhất
            best_source = conflict.sources[0]
            
            # Tự động giải quyết
            resolution = {
                'method': 'auto_resolution',
                'selected_source': best_source,
                'reason': f"Auto-resolved based on highest tier source ({best_source['tier']})",
                'confidence_score': conflict.confidence_score,
                'resolved_at': timezone.now().isoformat()
            }
            
            conflict.resolution = resolution
            conflict.status = ConflictStatus.RESOLVED
            conflict.resolved_at = timezone.now()
            
            # Chuyển từ active sang resolved
            del self.active_conflicts[conflict.id]
            self.resolved_conflicts.append(conflict)
            self.total_conflicts_resolved += 1
            self.auto_resolution_count += 1
            
            logger.info(f"Conflict {conflict.id} auto-resolved")
            
            # Gửi cảnh báo thành công
            alert_manager.send_alert(
                alert_type='conflict_resolved',
                message=f"Conflict auto-resolved: {conflict.description}",
                level=AlertLevel.INFO,
                metadata={'conflict_id': conflict.id, 'method': 'auto'}
            )
            
        except Exception as e:
            logger.error(f"Error in auto-resolution: {str(e)}")
    
    def manual_resolve_conflict(
        self,
        conflict_id: str,
        resolution: Dict[str, Any],
        resolved_by: str
    ) -> bool:
        """
        Giải quyết xung đột thủ công
        """
        try:
            if conflict_id not in self.active_conflicts:
                logger.warning(f"Conflict {conflict_id} not found in active conflicts")
                return False
            
            conflict = self.active_conflicts[conflict_id]
            
            # Cập nhật conflict
            conflict.resolution = resolution
            conflict.status = ConflictStatus.RESOLVED
            conflict.resolved_by = resolved_by
            conflict.resolved_at = timezone.now()
            
            # Chuyển từ active sang resolved
            del self.active_conflicts[conflict_id]
            self.resolved_conflicts.append(conflict)
            self.total_conflicts_resolved += 1
            self.manual_resolution_count += 1
            
            logger.info(f"Conflict {conflict_id} manually resolved by {resolved_by}")
            
            # Gửi cảnh báo thành công
            alert_manager.send_alert(
                alert_type='conflict_resolved',
                message=f"Conflict manually resolved: {conflict.description}",
                level=AlertLevel.INFO,
                metadata={'conflict_id': conflict_id, 'method': 'manual', 'resolved_by': resolved_by}
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error in manual resolution: {str(e)}")
            return False
    
    def escalate_conflict(self, conflict_id: str, reason: str) -> bool:
        """
        Escalate conflict lên admin
        """
        try:
            if conflict_id not in self.active_conflicts:
                return False
            
            conflict = self.active_conflicts[conflict_id]
            conflict.status = ConflictStatus.ESCALATED
            
            # Gửi cảnh báo escalation
            alert_manager.send_alert(
                alert_type='conflict_escalated',
                message=f"Conflict escalated: {conflict.description}",
                level=AlertLevel.ERROR,
                metadata={
                    'conflict_id': conflict_id,
                    'reason': reason,
                    'escalated_at': timezone.now().isoformat()
                }
            )
            
            logger.info(f"Conflict {conflict_id} escalated: {reason}")
            return True
            
        except Exception as e:
            logger.error(f"Error escalating conflict: {str(e)}")
            return False
    
    def get_active_conflicts(self) -> List[Dict[str, Any]]:
        """Lấy danh sách xung đột đang hoạt động"""
        return [conflict.to_dict() for conflict in self.active_conflicts.values()]
    
    def get_resolved_conflicts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Lấy danh sách xung đột đã giải quyết trong N giờ gần đây"""
        cutoff_time = timezone.now() - timedelta(hours=hours)
        
        recent_conflicts = [
            conflict.to_dict() for conflict in self.resolved_conflicts
            if conflict.resolved_at and conflict.resolved_at >= cutoff_time
        ]
        
        return sorted(recent_conflicts, key=lambda x: x['resolved_at'], reverse=True)
    
    def get_conflict_statistics(self) -> Dict[str, Any]:
        """Lấy thống kê xung đột"""
        return {
            'total_detected': self.total_conflicts_detected,
            'total_resolved': self.total_conflicts_resolved,
            'active_count': len(self.active_conflicts),
            'auto_resolution_count': self.auto_resolution_count,
            'manual_resolution_count': self.manual_resolution_count,
            'resolution_rate': (self.total_conflicts_resolved / self.total_conflicts_detected * 100) if self.total_conflicts_detected > 0 else 0,
            'auto_resolution_rate': (self.auto_resolution_count / self.total_conflicts_resolved * 100) if self.total_conflicts_resolved > 0 else 0
        }
    
    def cleanup_old_conflicts(self, days: int = 7):
        """Dọn dẹp xung đột cũ"""
        cutoff_time = timezone.now() - timedelta(days=days)
        
        # Xóa resolved conflicts cũ
        self.resolved_conflicts = [
            conflict for conflict in self.resolved_conflicts
            if conflict.resolved_at and conflict.resolved_at >= cutoff_time
        ]
        
        logger.info(f"Cleaned up conflicts older than {days} days")

# Global Conflict Resolution Manager instance
conflict_resolution_manager = ConflictResolutionManager()
