from datetime import datetime
from src.models import db

class Employee(db.Model):
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    salary = db.Column(db.Numeric(10, 2), nullable=False)
    workday_start = db.Column(db.Time, nullable=False, default='09:00:00')
    workday_end = db.Column(db.Time, nullable=False, default='18:00:00')
    lunch_duration = db.Column(db.Integer, nullable=False, default=60)  # em minutos
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    
    # Relacionamentos
    work_days = db.relationship('WorkDay', backref='employee', lazy=True)
    calculations = db.relationship('Calculation', backref='employee', lazy=True)
    
    def __repr__(self):
        return f'<Employee {self.name}>'
