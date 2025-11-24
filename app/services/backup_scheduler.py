import asyncio
from datetime import datetime, time, timedelta  
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.services.backup_service import backup_service
from app.database import get_db
from app.config import settings

class BackupScheduler:
    def __init__(self):
        self.schedule = {}
        self.is_running = False
    
    def set_schedule(self, frequency: str, time_of_day: str = "02:00") -> Dict[str, Any]:
        """Set backup schedule"""
        valid_frequencies = ['daily', 'weekly', 'monthly', 'manual']
        
        if frequency not in valid_frequencies:
            return {'success': False, 'error': f'Invalid frequency. Must be one of: {valid_frequencies}'}
        
        if frequency == 'manual':
            self.schedule = {}
            return {'success': True, 'message': 'Manual backup mode set'}
        
        try:
            # Validate time format
            backup_time = datetime.strptime(time_of_day, "%H:%M").time()
            self.schedule = {
                'frequency': frequency,
                'time': backup_time,
                'last_run': None,
                'next_run': self._calculate_next_run(frequency, backup_time)
            }
            
            return {
                'success': True, 
                'message': f'Backup schedule set to {frequency} at {time_of_day}',
                'next_run': self.schedule['next_run'].isoformat() if self.schedule['next_run'] else None
            }
            
        except ValueError:
            return {'success': False, 'error': 'Invalid time format. Use HH:MM (24-hour format)'}
    
    def _calculate_next_run(self, frequency: str, backup_time: time) -> datetime:
        """Calculate next run time based on frequency"""
        now = datetime.now()
        today = now.date()
        
        if frequency == 'daily':
            next_run = datetime.combine(today, backup_time)
            if next_run <= now:
                next_run = datetime.combine(today, backup_time) + timedelta(days=1)
        
        elif frequency == 'weekly':
            # Run every Monday
            days_until_monday = (7 - now.weekday()) % 7
            if days_until_monday == 0 and now.time() < backup_time:
                days_until_monday = 0
            else:
                days_until_monday = (7 - now.weekday()) % 7
                if days_until_monday == 0:
                    days_until_monday = 7
            
            next_run = datetime.combine(today, backup_time) + timedelta(days=days_until_monday)
        
        elif frequency == 'monthly':
            # Run on 1st of each month
            if now.day == 1 and now.time() < backup_time:
                next_run = datetime.combine(today, backup_time)
            else:
                next_month = today.replace(day=28) + timedelta(days=4) 
                next_month = next_month.replace(day=1)
                next_run = datetime.combine(next_month, backup_time)
        
        return next_run
    
    async def start(self):
        """Start the backup scheduler"""
        if self.is_running:
            return
        
        self.is_running = True
        print("Backup scheduler started")
        
        while self.is_running:
            await self._check_schedule()
            await asyncio.sleep(60)
    
    async def stop(self):
        """Stop the backup scheduler"""
        self.is_running = False
        print("Backup scheduler stopped")
    
    async def _check_schedule(self):
        """Check if it's time to run scheduled backup"""
        if not self.schedule or self.schedule['frequency'] == 'manual':
            return
        
        now = datetime.now()
        
        if self.schedule['next_run'] and now >= self.schedule['next_run']:
            print(f"Running scheduled {self.schedule['frequency']} backup...")
            
            # Perform backup 
            try:
                db = next(get_db())
                result = backup_service.perform_backup(db, admin_id=1, backup_type='auto')
                
                if result['success']:
                    print(f"Automated backup completed successfully: {result['backup_id']}")
                else:
                    print(f"Automated backup failed: {result['error']}")
                
                # Update schedule
                self.schedule['last_run'] = now
                self.schedule['next_run'] = self._calculate_next_run(
                    self.schedule['frequency'], 
                    self.schedule['time']
                )
                
            except Exception as e:
                print(f"Error during automated backup: {e}")
    
    def get_schedule_status(self) -> Dict[str, Any]:
        """Get current schedule status"""
        if not self.schedule:
            return {
                'active': False,
                'message': 'No backup schedule set (manual mode)'
            }
        
        return {
            'active': True,
            'frequency': self.schedule['frequency'],
            'scheduled_time': self.schedule['time'].strftime("%H:%M"),
            'last_run': self.schedule['last_run'].isoformat() if self.schedule['last_run'] else 'Never',
            'next_run': self.schedule['next_run'].isoformat() if self.schedule['next_run'] else 'Not scheduled'
        }

backup_scheduler = BackupScheduler()