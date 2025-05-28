from datetime import datetime
from src.models import db

class WorkPeriod(db.Model):
    __tablename__ = 'work_periods'
    
    id = db.Column(db.Integer, primary_key=True)
    work_day_id = db.Column(db.Integer, db.ForeignKey('work_days.id'), nullable=False)
    period_type = db.Column(db.String(20), nullable=False, default='regular')  # 'regular', 'extra'
    entry_time = db.Column(db.Time, nullable=True)
    exit_time = db.Column(db.Time, nullable=True)
    is_lunch_break = db.Column(db.Boolean, nullable=False, default=False)
    lunch_start = db.Column(db.Time, nullable=True)
    lunch_end = db.Column(db.Time, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f'<WorkPeriod {self.id} - {self.period_type}>'
