from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.subscription_activation_queue import SubscriptionActivationQueue
from datetime import datetime

class SubscriptionActivationQueueCRUD:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, queue_id: int) -> SubscriptionActivationQueue:
        return self.db.query(SubscriptionActivationQueue).filter(SubscriptionActivationQueue.queue_id == queue_id).first()
    
    def get_by_subscription_id(self, subscription_id: int) -> SubscriptionActivationQueue:
        return self.db.query(SubscriptionActivationQueue).filter(
            SubscriptionActivationQueue.subscription_id == subscription_id
        ).first()
    
    def get_by_customer_id(self, customer_id: int):
        return self.db.query(SubscriptionActivationQueue).filter(
            SubscriptionActivationQueue.customer_id == customer_id
        ).all()
    
    def get_pending_queues(self):
        return self.db.query(SubscriptionActivationQueue).filter(
            SubscriptionActivationQueue.processed_at.is_(None)
        ).order_by(SubscriptionActivationQueue.queue_position).all()
    
    def get_next_in_queue(self, phone_number: str):
        return self.db.query(SubscriptionActivationQueue).filter(
            and_(
                SubscriptionActivationQueue.phone_number == phone_number,
                SubscriptionActivationQueue.processed_at.is_(None),
                SubscriptionActivationQueue.queue_position == 1
            )
        ).first()
    
    def create(self, queue_data: dict) -> SubscriptionActivationQueue:
        queue = SubscriptionActivationQueue(**queue_data)
        self.db.add(queue)
        self.db.commit()
        self.db.refresh(queue)
        return queue
    
    def mark_processed(self, queue_id: int) -> SubscriptionActivationQueue:
        queue = self.get_by_id(queue_id)
        if queue:
            queue.processed_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(queue)
        return queue
    
    def update_queue_position(self, queue_id: int, new_position: int) -> SubscriptionActivationQueue:
        queue = self.get_by_id(queue_id)
        if queue:
            queue.queue_position = new_position
            self.db.commit()
            self.db.refresh(queue)
        return queue
    
    def delete(self, queue_id: int) -> bool:
        queue = self.get_by_id(queue_id)
        if queue:
            self.db.delete(queue)
            self.db.commit()
            return True
        return False