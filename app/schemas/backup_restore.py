from pydantic import BaseModel, validator
from datetime import datetime, date
from typing import List, Optional, Dict, Any

class BackupBase(BaseModel):
    file_name: str
    type: str  # manual, auto
    data_list: Dict[str, Any]

class BackupResponse(BackupBase):
    backup_id: int
    admin_id: int
    path: str
    date: date
    message: Optional[str] = None

    class Config:
        from_attributes = True

class RestoreBase(BaseModel):
    file_name: str
    type: str
    data_list: Dict[str, Any]

class RestoreResponse(RestoreBase):
    restore_id: int
    admin_id: int
    path: str
    date: date
    message: Optional[str] = None

    class Config:
        from_attributes = True

class ScheduleRequest(BaseModel):
    frequency: str  # daily, weekly, monthly, manual
    time_of_day: Optional[str] = "02:00"  # HH:MM format

    @validator('frequency')
    def validate_frequency(cls, v):
        valid_frequencies = ['daily', 'weekly', 'monthly', 'manual']
        if v not in valid_frequencies:
            raise ValueError(f'Frequency must be one of: {valid_frequencies}')
        return v

    @validator('time_of_day')
    def validate_time_format(cls, v):
        if v:
            try:
                from datetime import datetime
                datetime.strptime(v, "%H:%M")
            except ValueError:
                raise ValueError('Time must be in HH:MM format (24-hour)')
        return v

class ScheduleResponse(BaseModel):
    success: bool
    message: str
    next_run: Optional[str] = None

class ScheduleStatusResponse(BaseModel):
    active: bool
    frequency: Optional[str] = None
    scheduled_time: Optional[str] = None
    last_run: Optional[str] = None
    next_run: Optional[str] = None
    message: Optional[str] = None

class ScheduleOption(BaseModel):
    description: str
    recommended: bool
    retention_days: int

class ScheduleOptionsResponse(BaseModel):
    options: Dict[str, ScheduleOption]

class BackupValidationResponse(BaseModel):
    valid: bool
    backup_timestamp: Optional[str] = None
    data_version: Optional[str] = None
    record_counts: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class BackupStatsResponse(BaseModel):
    total_backups: int
    manual_backups: int
    auto_backups: int
    recent_backups: int  # last 7 days
    total_restores: int