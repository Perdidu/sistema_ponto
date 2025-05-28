from datetime import datetime, date, timedelta
from decimal import Decimal
import sys
import os

# Adicionar o diretório raiz ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar a função de cálculo
from src.utils.calculation_utils import calculate_period_hours, calculate_multiple_periods

# Criar uma classe mock para simular períodos de trabalho
class MockPeriod:
    def __init__(self, period_type, entry_time=None, lunch_start=None, lunch_end=None, exit_time=None):
        self.period_type = period_type
        self.entry_time = entry_time
        self.lunch_start = lunch_start
        self.lunch_end = lunch_end
        self.exit_time = exit_time

# Criar uma classe mock para simular funcionário
class MockEmployee:
    def __init__(self, salary):
        self.salary = Decimal(str(salary))

# Função para converter string para time
def str_to_time(time_str):
    if not time_str:
        return None
    return datetime.strptime(time_str, '%H:%M').time()

# Teste 1: Dia normal com 10 horas trabalhadas (8 regulares + 2 extras)
def test_normal_day_with_2_overtime():
    periods = [
        MockPeriod(
            'regular',
            str_to_time('09:00'),
            str_to_time('12:00'),
            str_to_time('13:00'),
            str_to_time('20:00')
        )
    ]
    
    employee = MockEmployee(2200.00)  # R$ 2.200,00 de salário
    test_date = date(2025, 5, 21)  # Uma quarta-feira
    
    regular, overtime, night = calculate_period_hours(periods, test_date, employee)
    
    print("=== Teste 1: Dia normal com 10 horas trabalhadas ===")
    print(f"Horas regulares: {regular}")
    print(f"Horas extras: {overtime}")
    print(f"Horas noturnas: {night}")
    print("Esperado: 8 horas regulares, 2 horas extras")
    print()

# Teste 2: Dia normal com 12 horas trabalhadas (8 regulares + 4 extras)
def test_normal_day_with_4_overtime():
    periods = [
        MockPeriod(
            'regular',
            str_to_time('09:00'),
            str_to_time('12:00'),
            str_to_time('13:00'),
            str_to_time('22:00')
        )
    ]
    
    employee = MockEmployee(2200.00)
    test_date = date(2025, 5, 22)  # Uma quinta-feira
    
    regular, overtime, night = calculate_period_hours(periods, test_date, employee)
    
    print("=== Teste 2: Dia normal com 12 horas trabalhadas ===")
    print(f"Horas regulares: {regular}")
    print(f"Horas extras: {overtime}")
    print(f"Horas noturnas: {night}")
    print("Esperado: 8 horas regulares, 4 horas extras")
    print()

# Teste 3: Fim de semana com 6 horas trabalhadas (todas extras)
def test_weekend_day():
    periods = [
        MockPeriod(
            'regular',
            str_to_time('10:00'),
            str_to_time('13:00'),
            str_to_time('14:00'),
            str_to_time('17:00')
        )
    ]
    
    employee = MockEmployee(2200.00)
    test_date = date(2025, 5, 24)  # Um sábado
    
    regular, overtime, night = calculate_period_hours(periods, test_date, employee)
    
    print("=== Teste 3: Fim de semana com 6 horas trabalhadas ===")
    print(f"Horas regulares: {regular}")
    print(f"Horas extras: {overtime}")
    print(f"Horas noturnas: {night}")
    print("Esperado: 0 horas regulares, 6 horas extras")
    print()

# Teste 4: Dia com múltiplos períodos
def test_multiple_periods():
    periods = [
        MockPeriod(
            'regular',
            str_to_time('09:00'),
            str_to_time('12:00'),
            str_to_time('13:00'),
            str_to_time('18:00')
        ),
        MockPeriod(
            'additional',
            str_to_time('20:00'),
            None,
            None,
            str_to_time('23:00')
        )
    ]
    
    employee = MockEmployee(2200.00)
    test_date = date(2025, 5, 23)  # Uma sexta-feira
    
    regular, overtime, night = calculate_period_hours(periods, test_date, employee)
    
    print("=== Teste 4: Dia com múltiplos períodos ===")
    print(f"Horas regulares: {regular}")
    print(f"Horas extras: {overtime}")
    print(f"Horas noturnas: {night}")
    print("Esperado: 8 horas regulares, 3 horas extras, 1 hora noturna")
    print()

# Teste 5: Simulação de cálculo completo com interjornada
def test_full_calculation_with_interjornada():
    print("=== Teste 5: Simulação de cálculo completo com interjornada ===")
    print("Este teste requer acesso ao banco de dados e não pode ser executado diretamente.")
    print("Cenário: Funcionário trabalha das 09:00 às 18:00 em um dia e das 02:00 às 03:00 no dia seguinte.")
    print("Esperado: Violação de interjornada de 5 horas (11h requeridas - 6h concedidas).")
    print("As 5 horas de interjornada devem ser somadas às horas extras do dia.")
    print("Se o total de horas extras do dia for <= 2h, todas são pagas a 50%.")
    print("Se o total for > 2h, as 2 primeiras são pagas a 50% e as demais a 100%.")
    print()

# Executar todos os testes
if __name__ == "__main__":
    print("Iniciando testes de cálculo de horas trabalhadas...")
    print("Nota: Estes testes validam a nova regra da convenção coletiva:")
    print("- As 2 primeiras horas extras do dia são pagas a 50%")
    print("- As demais horas extras são pagas a 100%")
    print("- Horas de interjornada são somadas às horas extras do dia")
    print()
    
    test_normal_day_with_2_overtime()
    test_normal_day_with_4_overtime()
    test_weekend_day()
    test_multiple_periods()
    test_full_calculation_with_interjornada()
    
    print("Testes concluídos!")
