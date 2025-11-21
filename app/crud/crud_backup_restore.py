from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import json
import os
import zipfile
from app.models.models import Backup, Restore, Admin, Customer, Transaction, Subscription, Plan, Category
from app.config import settings

class CRUDBackupRestore:
    def create_backup(self, db: Session, admin_id: int, backup_type: str, data_list: Dict[str, Any]):
        """Create a backup record"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"backup_{timestamp}.json"
        path = f"backups/{file_name}"
        
        # Ensure data_list is JSON serializable
        serializable_data_list = {
            'tables_backed_up': data_list.get('tables_backed_up', []),
            'record_counts': data_list.get('record_counts', {})
        }
        
        backup = Backup(
            admin_id=admin_id,
            file_name=file_name,
            path=path,
            type=backup_type,
            data_list=serializable_data_list,
            date=datetime.utcnow().date()  # Explicitly set the date
        )
        
        db.add(backup)
        db.commit()
        db.refresh(backup)
        return backup
    
    def create_restore(self, db: Session, admin_id: int, backup_id: int, file_name: str, data_list: Dict[str, Any]):
        """Create a restore record"""
        path = f"restores/restore_from_{file_name}"
        
        # Ensure data_list is JSON serializable
        serializable_data_list = {
            'tables_restored': data_list.get('tables_restored', []),
            'record_counts': data_list.get('record_counts', {}),
            'backup_source_id': backup_id
        }
        
        restore = Restore(
            admin_id=admin_id,
            file_name=file_name,
            path=path,
            type="manual",
            data_list=serializable_data_list,
            date=datetime.utcnow().date()  # Explicitly set the date
        )
        
        db.add(restore)
        db.commit()
        db.refresh(restore)
        return restore
    
    def get_backup(self, db: Session, backup_id: int):
        return db.query(Backup).filter(Backup.backup_id == backup_id).first()
    
    def get_all_backups(self, db: Session, skip: int = 0, limit: int = 100, backup_type: str = None):
        query = db.query(Backup)
        if backup_type:
            query = query.filter(Backup.type == backup_type)
        return query.order_by(Backup.date.desc()).offset(skip).limit(limit).all()
    
    def get_restore(self, db: Session, restore_id: int):
        return db.query(Restore).filter(Restore.restore_id == restore_id).first()
    
    def get_all_restores(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(Restore).order_by(Restore.date.desc()).offset(skip).limit(limit).all()
    
    def get_essential_data(self, db: Session) -> Dict[str, Any]:
        """Get only essential data for backup (excluding logs, temporary data, etc.)"""
        
        # Essential tables and their data
        essential_data = {}
        
        # 1. Customers (essential info only)
        customers = db.query(Customer).filter(Customer.deleted_at.is_(None)).all()
        essential_data['customers'] = [
            {
                'customer_id': c.customer_id,
                'phone_number': c.phone_number,
                'full_name': c.full_name,
                'account_status': c.account_status.value if c.account_status else None,
                'created_at': c.created_at.isoformat() if c.created_at else None
            }
            for c in customers
        ]
        
        # 2. Plans (active plans only)
        plans = db.query(Plan).filter(
            Plan.deleted_at.is_(None),
            Plan.status == 'active'
        ).all()
        essential_data['plans'] = [
            {
                'plan_id': p.plan_id,
                'plan_name': p.plan_name,
                'plan_type': p.plan_type.value if p.plan_type else None,
                'price': float(p.price) if p.price else 0.0,
                'validity_days': p.validity_days,
                'data_allowance_gb': float(p.data_allowance_gb) if p.data_allowance_gb else None,
                'is_featured': p.is_featured,
                'created_at': p.created_at.isoformat() if p.created_at else None
            }
            for p in plans
        ]
        
        # 3. Categories
        categories = db.query(Category).all()
        essential_data['categories'] = [
            {
                'category_id': c.category_id,
                'category_name': c.category_name,
                'created_at': c.created_at.isoformat() if c.created_at else None
            }
            for c in categories
        ]
        
        # 4. Recent transactions (last 90 days only)
        ninety_days_ago = datetime.utcnow() - timedelta(days=90)
        transactions = db.query(Transaction).filter(
            Transaction.transaction_date >= ninety_days_ago
        ).all()
        essential_data['transactions'] = [
            {
                'transaction_id': t.transaction_id,
                'customer_id': t.customer_id,
                'plan_id': t.plan_id,
                'final_amount': float(t.final_amount) if t.final_amount else 0.0,
                'payment_status': t.payment_status.value if t.payment_status else None,
                'transaction_type': t.transaction_type.value if t.transaction_type else None,
                'transaction_date': t.transaction_date.isoformat() if t.transaction_date else None
            }
            for t in transactions
        ]
        
        # 5. Active subscriptions
        active_subscriptions = db.query(Subscription).filter(
            Subscription.expiry_date > datetime.utcnow()
        ).all()
        essential_data['subscriptions'] = [
            {
                'subscription_id': s.subscription_id,
                'customer_id': s.customer_id,
                'plan_id': s.plan_id,
                'phone_number': s.phone_number,
                'activation_date': s.activation_date.isoformat() if s.activation_date else None,
                'expiry_date': s.expiry_date.isoformat() if s.expiry_date else None
            }
            for s in active_subscriptions
        ]
        
        # Add metadata
        essential_data['metadata'] = {
            'backup_timestamp': datetime.utcnow().isoformat(),
            'total_customers': len(essential_data['customers']),
            'total_plans': len(essential_data['plans']),
            'total_transactions': len(essential_data['transactions']),
            'total_active_subscriptions': len(essential_data['subscriptions']),
            'data_version': '1.0'
        }
        
        return essential_data
    
    def save_backup_file(self, data: Dict[str, Any], file_path: str) -> bool:
        """Save backup data to file"""
        try:
            # Create backups directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Save as JSON with custom serializer for any remaining datetime objects
            def default_serializer(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=default_serializer)
            
            # Create compressed version
            zip_path = file_path.replace('.json', '.zip')
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(file_path, os.path.basename(file_path))
            
            return True
        except Exception as e:
            print(f"Error saving backup file: {e}")
            return False
    
    def load_backup_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Load backup data from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading backup file: {e}")
            return None
    
    def get_backup_stats(self, db: Session):
        """Get backup statistics"""
        total_backups = db.query(Backup).count()
        manual_backups = db.query(Backup).filter(Backup.type == 'manual').count()
        auto_backups = db.query(Backup).filter(Backup.type == 'auto').count()
        
        # Recent backups (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_backups = db.query(Backup).filter(Backup.date >= week_ago.date()).count()
        
        # Total restores
        total_restores = db.query(Restore).count()
        
        return {
            'total_backups': total_backups,
            'manual_backups': manual_backups,
            'auto_backups': auto_backups,
            'recent_backups': recent_backups,
            'total_restores': total_restores
        }

crud_backup_restore = CRUDBackupRestore()