"""
Модуль расчёта IPI (Индивидуального показателя деятельности).

Формула: IPI = Σ(Wi * Σ(Wij * Bij))
  Wi   — вес группы (по должности и году аспирантуры)
  Wij  — вес показателя: W_base × k_возраст × k_стаж × k_аспирант
  Bij  — значение показателя (сумма баллов верифицированных работ данного типа)
"""

from datetime import date

from .models import (
    Employee, KPIResult, KPIGroup, KPIGroupWeight,
    ScientificWork, OrganizationalWork, TechnicalWork,
    Rule,
)


# ============================================================
#  Поправочные коэффициенты для Wij
# ============================================================

def _evaluate_rule(rule_type: str, value: int):
    """Ищет первое подходящее правило заданного типа и возвращает коэффициент."""
    rules = list(Rule.objects.filter(rule_type=rule_type).order_by('priority'))
    if not rules:
        return None
    for rule in rules:
        if rule.min_value is not None and value < rule.min_value:
            continue
        if rule.max_value is not None and value > rule.max_value:
            continue
        return rule.coefficient
    return 1.0


def k_age(employee):
    """Возрастной коэффициент."""
    age = employee.age or 0
    coef = _evaluate_rule('k_age', age)
    if coef is not None:
        return coef
    if age <= 30:
        return 1.2
    if age <= 45:
        return 1.0
    return 0.9


def k_experience(employee):
    """Коэффициент стажа научной работы."""
    exp = employee.experience or 0
    coef = _evaluate_rule('k_experience', exp)
    if coef is not None:
        return coef
    if exp <= 5:
        return 1.2
    if exp <= 15:
        return 1.0
    return 0.9


def k_phd(employee):
    """Коэффициент обучения в аспирантуре."""
    if employee.position_type != 'phd_student':
        return 1.0
    year = employee.phd_year or 1
    coef = _evaluate_rule('k_phd', year)
    if coef is not None:
        return coef
    if year >= 4:
        return 1.3
    if year >= 2:
        return 1.2
    return 1.1


def get_employee_factors(employee):
    """Возвращает все три коэффициента + произведение."""
    ka = k_age(employee)
    ke = k_experience(employee)
    kp = k_phd(employee)
    return {
        'k_age': ka,
        'k_exp': ke,
        'k_phd': kp,
        'k_total': round(ka * ke * kp, 4),
    }


# ============================================================
#  Множитель квартиля журнала для научных статей
#  Значения берутся из правил продукционной экспертной системы.
# ============================================================

QUARTILE_MULTIPLIER_FALLBACK = {1: 1.5, 2: 1.2, 3: 1.0, 4: 0.8}


def get_quartile_multiplier(quartile):
    """Возвращает множитель за квартиль журнала."""
    if quartile is None:
        return 1.0
    coef = _evaluate_rule('quartile', quartile)
    if coef is not None:
        return coef
    return QUARTILE_MULTIPLIER_FALLBACK.get(quartile, 1.0)


def compute_scientific_work_points(base_weight, quartile=None):
    """Вычисляет итоговые баллы для научной работы с учётом квартиля журнала."""
    return base_weight * get_quartile_multiplier(quartile)


# ============================================================
#  Получение Wi (веса группы) для сотрудника
# ============================================================

def get_group_weight(group, employee):
    """Wi для группы и должности сотрудника."""
    qs = KPIGroupWeight.objects.filter(
        kpi_group=group,
        position_type=employee.position_type,
    )
    if employee.position_type == 'phd_student' and employee.phd_year:
        exact = qs.filter(phd_year=employee.phd_year).first()
        if exact:
            return exact.weight
    universal = qs.filter(phd_year__isnull=True).first()
    if universal:
        return universal.weight
    return group.group_weight


# ============================================================
#  Сбор баллов
# ============================================================

def _get_quarter(d: date) -> int:
    return (d.month - 1) // 3 + 1


def _quarter_range(year: int, quarter: int):
    q_start_month = (quarter - 1) * 3 + 1
    q_end_month = quarter * 3
    start_date = date(year, q_start_month, 1)
    if q_end_month == 12:
        end_date = date(year, 12, 31)
    else:
        end_date = date(year, q_end_month + 1, 1)
    return start_date, end_date


def _get_points_by_type(employee, start_date, end_date):
    """Собирает баллы по типам работ за период (только верифицированные)."""
    points = {}
    for work in ScientificWork.objects.filter(
        employee=employee, verified=True,
        created_at__date__gte=start_date,
        created_at__date__lt=end_date,
    ):
        key = work.work_type
        points[key] = points.get(key, 0) + work.points
    for work in OrganizationalWork.objects.filter(
        employee=employee, verified=True,
        event_date__gte=start_date,
        event_date__lt=end_date,
    ):
        key = work.work_type
        points[key] = points.get(key, 0) + work.points
    for work in TechnicalWork.objects.filter(
        employee=employee, verified=True,
        work_date__gte=start_date,
        work_date__lt=end_date,
    ):
        key = work.work_type
        points[key] = points.get(key, 0) + work.points
    return points


def _get_works_by_type(employee, start_date, end_date):
    """Возвращает dict: work_type_key → [{id, title, points, kind}, ...]."""
    works = {}
    for w in ScientificWork.objects.filter(
        employee=employee, verified=True,
        created_at__date__gte=start_date,
        created_at__date__lt=end_date,
    ):
        works.setdefault(w.work_type, []).append({
            'id': w.id, 'title': w.title, 'points': w.points, 'kind': 'scientific',
        })
    for w in OrganizationalWork.objects.filter(
        employee=employee, verified=True,
        event_date__gte=start_date,
        event_date__lt=end_date,
    ):
        works.setdefault(w.work_type, []).append({
            'id': w.id, 'title': w.title, 'points': w.points, 'kind': 'organizational',
        })
    for w in TechnicalWork.objects.filter(
        employee=employee, verified=True,
        work_date__gte=start_date,
        work_date__lt=end_date,
    ):
        works.setdefault(w.work_type, []).append({
            'id': w.id, 'title': w.title, 'points': w.points, 'kind': 'technical',
        })
    return works


# ============================================================
#  Подробная разбивка
# ============================================================

def calculate_breakdown(employee: Employee, year: int, quarter: int) -> dict:
    """Полная разбивка IPI по формуле для интерфейса."""
    start_date, end_date = _quarter_range(year, quarter)
    points_by_type = _get_points_by_type(employee, start_date, end_date)
    works_by_type = _get_works_by_type(employee, start_date, end_date)
    factors = get_employee_factors(employee)

    groups_qs = KPIGroup.objects.filter(
        department=employee.department
    ).prefetch_related('indicators')

    groups_data = []
    total_ipi = 0.0
    scientific_score = 0.0
    organizational_score = 0.0
    technical_score = 0.0

    for group in groups_qs:
        wi = get_group_weight(group, employee)
        indicators_data = []
        sum_inner = 0.0

        for ind in group.indicators.all():
            w_base = ind.weight
            wij = w_base * factors['k_total']
            bij = points_by_type.get(ind.work_type_key, 0)
            contribution = wij * bij
            indicators_data.append({
                'name': ind.name,
                'work_type_key': ind.work_type_key,
                'w_base': round(w_base, 3),
                'k_age': factors['k_age'],
                'k_exp': factors['k_exp'],
                'k_phd': factors['k_phd'],
                'wij': round(wij, 3),
                'bij': round(bij, 3),
                'contribution': round(contribution, 3),
                'works': works_by_type.get(ind.work_type_key, []),
            })
            sum_inner += contribution

        group_contribution = wi * sum_inner
        total_ipi += group_contribution

        name_lower = group.name.lower()
        if 'науч' in name_lower:
            scientific_score += group_contribution
        elif 'организ' in name_lower:
            organizational_score += group_contribution
        elif 'техн' in name_lower:
            technical_score += group_contribution

        groups_data.append({
            'group_id': group.id,
            'name': group.name,
            'wi': round(wi, 3),
            'sum_inner': round(sum_inner, 3),
            'contribution': round(group_contribution, 3),
            'indicators': indicators_data,
        })

    return {
        'employee_id': employee.id,
        'employee_name': employee.full_name,
        'position_type': employee.position_type,
        'phd_year': employee.phd_year,
        'year': year,
        'quarter': quarter,
        'factors': factors,
        'groups': groups_data,
        'scientific_score': round(scientific_score, 2),
        'organizational_score': round(organizational_score, 2),
        'technical_score': round(technical_score, 2),
        'total_ipi': round(total_ipi, 2),
    }


# ============================================================
#  Расчёт и сохранение KPIResult
# ============================================================

def calculate_ipi(employee: Employee, year: int, quarter: int) -> KPIResult:
    """Считает IPI и сохраняет/обновляет KPIResult."""
    breakdown = calculate_breakdown(employee, year, quarter)
    result, _ = KPIResult.objects.update_or_create(
        employee=employee,
        year=year,
        quarter=quarter,
        defaults={
            'scientific_score': breakdown['scientific_score'],
            'organizational_score': breakdown['organizational_score'],
            'technical_score': breakdown['technical_score'],
            'total_ipi': breakdown['total_ipi'],
        }
    )
    return result


def recalculate_all(year: int = None, quarter: int = None):
    if year is None:
        year = date.today().year
    if quarter is None:
        quarter = _get_quarter(date.today())
    results = []
    for employee in Employee.objects.all():
        result = calculate_ipi(employee, year, quarter)
        results.append(result)
    return results
