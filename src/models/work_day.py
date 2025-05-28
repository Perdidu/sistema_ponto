from datetime import datetime
from src.models import db

class WorkDay(db.Model):
    __tablename__ = 'work_days'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    
    # Relacionamentos
    work_periods = db.relationship('WorkPeriod', backref='work_day', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<WorkDay {self.date} - {self.employee_id}>'
