from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Importar modelos após definir db para evitar circular imports
from src.models.employee import Employee
from src.models.work_day import WorkDay
from src.models.work_period import WorkPeriod
from src.models.holiday import Holiday
from src.models.calculation import Calculation

__all__ = ['db', 'Employee', 'WorkDay', 'WorkPeriod', 'Holiday', 'Calculation']
