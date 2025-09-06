"""
Conflict Resolution Module - Xử lý xung đột dữ liệu

Module này cung cấp:
- Data conflict detection
- Automatic conflict resolution
- Manual conflict resolution
- Conflict history tracking

Classes:
- ConflictResolutionManager: Quản lý xung đột dữ liệu
- DataConflict: Đại diện cho một xung đột dữ liệu
- ConflictType: Các loại xung đột
- SourceTier: Độ tin cậy của nguồn dữ liệu
- ConflictStatus: Trạng thái xung đột
"""

from .conflict_manager import conflict_resolution_manager, ConflictResolutionManager, DataConflict, ConflictType, SourceTier, ConflictStatus

__all__ = [
    'conflict_resolution_manager',
    'ConflictResolutionManager',
    'DataConflict',
    'ConflictType',
    'SourceTier',
    'ConflictStatus'
]
