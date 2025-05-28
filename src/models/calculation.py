from datetime import datetime
from src.models import db

class Calculation(db.Model):
    __tablename__ = 'calculations'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    regular_hours = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    overtime_50 = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    overtime_100 = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    night_hours = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    interjournada_hours = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    dsr_value = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    overtime_50_value = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    overtime_100_value = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    night_hours_value = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    interjournada_value = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    total_value = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f'<Calculation {self.period_start} to {self.period_end} - {self.employee_id}>'
