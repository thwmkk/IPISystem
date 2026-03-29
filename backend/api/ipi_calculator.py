"""
Модуль расчёта IPI (Индивидуального показателя деятельности).

Формула: IPI = Σ(Wi * Σ(Wij * Bij))
  Wi  — вес группы показателей
  Wij — вес показателя
  Bij — значение показателя (баллы)
"""

from datetime import date
from .models import (
    Employee, KPIResult,
    ScientificWork, OrganizationalWork, TechnicalWork,
    KPIWeight,
)


def _get_quarter(d: date) -> int:
    return (d.month - 1) // 3 + 1


def calculate_ipi(employee: Employee, year: int, quarter: int) -> KPIResult:
    """
    Рассчитывает IPI сотрудника за указанный год и квартал.
    Учитываются только верифицированные работы.
    """

    # Определяем диапазон дат квартала
    q_start_month = (quarter - 1) * 3 + 1
    q_end_month = quarter * 3
    start_date = date(year, q_start_month, 1)
    if q_end_month == 12:
        end_date = date(year, 12, 31)
    else:
        end_date = date(year, q_end_month + 1, 1)

    # Считаем баллы по верифицированным работам
    scientific_score = sum(
        w.points for w in ScientificWork.objects.filter(
            employee=employee, verified=True,
            created_at__date__gte=start_date,
            created_at__date__lt=end_date,
        )
    )

    organizational_score = sum(
        w.points for w in OrganizationalWork.objects.filter(
            employee=employee, verified=True,
            event_date__gte=start_date,
            event_date__lt=end_date,
        )
    )

    technical_score = sum(
        w.points for w in TechnicalWork.objects.filter(
            employee=employee, verified=True,
            work_date__gte=start_date,
            work_date__lt=end_date,
        )
    )

    # Ищем веса для должности сотрудника
    weights = KPIWeight.objects.filter(
        kpi_group__department=employee.department,
        position=employee.position,
    )

    # Группируем веса по группе KPI
    group_weights = {}
    for w in weights:
        group_name = w.kpi_group.name.lower()
        group_weights[group_name] = {
            'group_weight': w.group_weight,
            'weight': w.weight,
        }

    # Рассчитываем IPI по формуле
    # Если веса не настроены — считаем с единичными весами
    w_sci = group_weights.get('научные', {})
    w_org = group_weights.get('организационные', {})
    w_tech = group_weights.get('технические', {})

    total_ipi = (
        w_sci.get('group_weight', 1.0) * w_sci.get('weight', 1.0) * scientific_score +
        w_org.get('group_weight', 1.0) * w_org.get('weight', 1.0) * organizational_score +
        w_tech.get('group_weight', 1.0) * w_tech.get('weight', 1.0) * technical_score
    )

    # Сохраняем или обновляем результат
    result, _ = KPIResult.objects.update_or_create(
        employee=employee,
        year=year,
        quarter=quarter,
        defaults={
            'scientific_score': scientific_score,
            'organizational_score': organizational_score,
            'technical_score': technical_score,
            'total_ipi': round(total_ipi, 2),
        }
    )

    return result


def recalculate_all(year: int = None, quarter: int = None):
    """Пересчитывает IPI для всех сотрудников за указанный период."""
    if year is None:
        year = date.today().year
    if quarter is None:
        quarter = _get_quarter(date.today())

    results = []
    for employee in Employee.objects.all():
        result = calculate_ipi(employee, year, quarter)
        results.append(result)
    return results
