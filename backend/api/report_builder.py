"""Сбор данных для отчёта по сотрудникам отдела за период."""
from datetime import date, timedelta

from .models import (
    Department, Employee,
    ScientificWork, OrganizationalWork, TechnicalWork,
    Task, Project, ProjectMember,
)
from .ipi_calculator import calculate_breakdown


PERIOD_LABELS = {
    'month': 'месяц',
    'quarter': 'квартал',
    'year': 'год',
}

POSITION_LABELS = {
    'head': 'Руководитель отдела',
    'senior_researcher': 'Старший научный сотрудник',
    'researcher': 'Научный сотрудник',
    'junior_researcher': 'Младший научный сотрудник',
    'engineer': 'Инженер',
    'phd_student': 'Аспирант',
}


def resolve_period(period, year, month=None, quarter=None):
    """Возвращает (start_date, end_date_exclusive, label) для указанного периода."""
    if period == 'month':
        if not month:
            month = date.today().month
        start = date(year, month, 1)
        if month == 12:
            end = date(year + 1, 1, 1)
        else:
            end = date(year, month + 1, 1)
        label = f'{_month_name(month)} {year} г.'
        return start, end, label
    if period == 'quarter':
        if not quarter:
            quarter = (date.today().month - 1) // 3 + 1
        q_start_month = (quarter - 1) * 3 + 1
        q_end_month = quarter * 3
        start = date(year, q_start_month, 1)
        if q_end_month == 12:
            end = date(year + 1, 1, 1)
        else:
            end = date(year, q_end_month + 1, 1)
        label = f'{quarter} квартал {year} г.'
        return start, end, label
    if period == 'year':
        start = date(year, 1, 1)
        end = date(year + 1, 1, 1)
        label = f'{year} г.'
        return start, end, label
    raise ValueError(f'Unknown period: {period}')


def _month_name(month):
    names = ['', 'январь', 'февраль', 'март', 'апрель', 'май', 'июнь',
             'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь']
    return names[month]


def _position_label(employee):
    label = POSITION_LABELS.get(employee.position_type, employee.position or '')
    if employee.position_type == 'phd_student' and employee.phd_year:
        label += f' ({employee.phd_year} год обучения)'
    return label


def build_employee_report(employee, start, end, period, year, quarter=None, month=None):
    """Собирает данные для отчёта по одному сотруднику за период."""
    # Работы
    sci_works = list(ScientificWork.objects.filter(
        employee=employee,
        created_at__date__gte=start,
        created_at__date__lt=end,
    ).order_by('created_at'))

    org_works = list(OrganizationalWork.objects.filter(
        employee=employee,
        event_date__gte=start,
        event_date__lt=end,
    ).order_by('event_date'))

    tech_works = list(TechnicalWork.objects.filter(
        employee=employee,
        work_date__gte=start,
        work_date__lt=end,
    ).order_by('work_date'))

    # Задачи
    tasks_done = list(Task.objects.filter(
        assigned_to=employee,
        status='completed',
        deadline__gte=start,
        deadline__lt=end,
    ).order_by('deadline'))

    tasks_pending = list(Task.objects.filter(
        assigned_to=employee,
        deadline__gte=start,
        deadline__lt=end,
    ).exclude(status='completed').order_by('deadline'))

    # Проекты, в которых сотрудник участник
    projects = list(Project.objects.filter(
        members__employee=employee,
    ).filter(
        start_date__lt=end,
    ).distinct().order_by('start_date'))

    # IPI breakdown
    if period == 'quarter' and quarter:
        breakdown = calculate_breakdown(employee, year, quarter)
    elif period == 'month' and month:
        breakdown = calculate_breakdown(employee, year, (month - 1) // 3 + 1)
    else:
        breakdown = calculate_breakdown(employee, year, (date.today().month - 1) // 3 + 1)

    return {
        'employee': {
            'full_name': employee.full_name,
            'position': _position_label(employee),
            'department': employee.department.department_short_name,
            'age': employee.age,
            'experience': employee.experience,
            'academic_degree': employee.academic_degree or '—',
            'email': employee.email,
        },
        'scientific_works': [
            {
                'title': w.title,
                'work_type': w.work_type,
                'date': w.created_at.date(),
                'points': w.points,
                'verified': w.verified,
            } for w in sci_works
        ],
        'organizational_works': [
            {
                'title': w.title,
                'work_type': w.work_type,
                'date': w.event_date,
                'points': w.points,
                'verified': w.verified,
            } for w in org_works
        ],
        'technical_works': [
            {
                'title': w.title,
                'work_type': w.work_type,
                'date': w.work_date,
                'points': w.points,
                'verified': w.verified,
            } for w in tech_works
        ],
        'tasks_done': [
            {
                'title': t.title,
                'deadline': t.deadline,
                'priority': t.get_priority_display(),
                'project': t.project.name if t.project else '—',
                'points': t.points,
            } for t in tasks_done
        ],
        'tasks_pending': [
            {
                'title': t.title,
                'status': t.get_status_display(),
                'deadline': t.deadline,
                'priority': t.get_priority_display(),
                'project': t.project.name if t.project else '—',
            } for t in tasks_pending
        ],
        'projects': [
            {
                'name': p.name,
                'start_date': p.start_date,
                'end_date': p.end_date,
                'completed': p.completed_at is not None,
                'is_creator': p.creator_id == employee.id,
            } for p in projects
        ],
        'ipi': {
            'total': breakdown['total_ipi'],
            'scientific': breakdown['scientific_score'],
            'organizational': breakdown['organizational_score'],
            'technical': breakdown['technical_score'],
            'factors': breakdown['factors'],
        },
    }


def build_department_report(department, period, year, month=None, quarter=None):
    """Собирает данные для отчёта по всему отделу."""
    start, end, period_label = resolve_period(period, year, month=month, quarter=quarter)

    employees = Employee.objects.filter(
        department=department,
    ).order_by('position_type', 'full_name')

    employees_data = []
    for emp in employees:
        emp_data = build_employee_report(emp, start, end, period, year,
                                          quarter=quarter, month=month)
        employees_data.append(emp_data)

    return {
        'department': {
            'name': department.department_name,
            'short_name': department.department_short_name,
        },
        'period': {
            'type': period,
            'type_label': PERIOD_LABELS[period],
            'label': period_label,
            'start': start,
            'end': end - timedelta(days=1),
        },
        'employees': employees_data,
        'generated_at': date.today(),
    }
