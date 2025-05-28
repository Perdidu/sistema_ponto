from src.routes.main import main_bp
from src.routes.employee import employee_bp
from src.routes.time_record import time_record_bp
from src.routes.holiday import holiday_bp
from src.routes.calculation import calculation_bp
from src.routes.import_xlsx import import_xlsx_bp

__all__ = [
    'main_bp',
    'employee_bp',
    'time_record_bp',
    'holiday_bp',
    'calculation_bp',
    'import_xlsx_bp'
]
