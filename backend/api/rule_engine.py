"""
Продукционная экспертная система для назначения весов показателей.

Структура правил: ЕСЛИ (условие) ТО (назначение весов).
Условия основаны на характеристиках сотрудника:
  - должность
  - стаж научной работы
  - наличие научной степени
  - обучение в аспирантуре
  - возраст
"""

from .models import Employee, KPIGroup, KPIWeight


# ============================================================
#  Правила (продукционная база знаний)
# ============================================================

# Каждое правило — словарь:
#   condition: функция (employee) -> bool
#   weights: {group_name: (group_weight, indicator_weight)}

RULES = [
    # --- Научные сотрудники ---
    {
        'name': 'Научный сотрудник с учёной степенью',
        'condition': lambda e: 'научный' in e.position.lower() and e.academic_degree is not None,
        'weights': {
            'научные': (0.6, 1.0),
            'организационные': (0.25, 1.0),
            'технические': (0.15, 1.0),
        },
    },
    {
        'name': 'Научный сотрудник без степени',
        'condition': lambda e: 'научный' in e.position.lower() and e.academic_degree is None,
        'weights': {
            'научные': (0.5, 1.0),
            'организационные': (0.25, 1.0),
            'технические': (0.25, 1.0),
        },
    },

    # --- Инженеры ---
    {
        'name': 'Инженер',
        'condition': lambda e: 'инженер' in e.position.lower(),
        'weights': {
            'научные': (0.2, 1.0),
            'организационные': (0.2, 1.0),
            'технические': (0.6, 1.0),
        },
    },

    # --- Аспиранты ---
    {
        'name': 'Аспирант 1-го года',
        'condition': lambda e: e.is_phd_student and e.experience <= 1,
        'weights': {
            'научные': (0.7, 0.5),
            'организационные': (0.15, 0.5),
            'технические': (0.15, 0.5),
        },
    },
    {
        'name': 'Аспирант 2+ года',
        'condition': lambda e: e.is_phd_student and e.experience > 1,
        'weights': {
            'научные': (0.65, 0.8),
            'организационные': (0.2, 0.8),
            'технические': (0.15, 0.8),
        },
    },

    # --- Опытные сотрудники (стаж > 10 лет) ---
    {
        'name': 'Опытный сотрудник (стаж > 10)',
        'condition': lambda e: e.experience > 10,
        'weights': {
            'научные': (0.5, 1.2),
            'организационные': (0.3, 1.1),
            'технические': (0.2, 1.0),
        },
    },

    # --- Правило по умолчанию (должно быть последним) ---
    {
        'name': 'По умолчанию',
        'condition': lambda e: True,
        'weights': {
            'научные': (0.4, 1.0),
            'организационные': (0.3, 1.0),
            'технические': (0.3, 1.0),
        },
    },
]


def apply_rules(employee: Employee) -> dict:
    """
    Применяет первое подходящее правило к сотруднику.
    Возвращает словарь назначенных весов.
    """
    for rule in RULES:
        if rule['condition'](employee):
            return {
                'rule_name': rule['name'],
                'weights': rule['weights'],
            }
    return {'rule_name': 'По умолчанию', 'weights': RULES[-1]['weights']}


def assign_weights(employee: Employee) -> list:
    """
    Применяет правила и сохраняет/обновляет веса в БД (KPIWeight).
    Возвращает список созданных/обновлённых KPIWeight.
    """
    result = apply_rules(employee)
    weights_data = result['weights']
    created = []

    for group_name, (group_weight, weight) in weights_data.items():
        # Ищем KPI-группу по имени и подразделению
        kpi_group = KPIGroup.objects.filter(
            name__iexact=group_name,
            department=employee.department,
        ).first()

        if kpi_group is None:
            # Создаём группу, если не существует
            kpi_group = KPIGroup.objects.create(
                name=group_name.capitalize(),
                department=employee.department,
                base_points=0,
            )

        kpi_weight, _ = KPIWeight.objects.update_or_create(
            kpi_group=kpi_group,
            position=employee.position,
            defaults={
                'group_weight': group_weight,
                'weight': weight,
            },
        )
        created.append(kpi_weight)

    return created


def assign_weights_all():
    """Назначает веса всем сотрудникам."""
    results = {}
    for employee in Employee.objects.all():
        rule_result = apply_rules(employee)
        assign_weights(employee)
        results[employee.full_name] = rule_result['rule_name']
    return results
