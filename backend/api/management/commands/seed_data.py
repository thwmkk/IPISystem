"""Очистка БД и заполнение тестовыми данными."""

import random
from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from api.ipi_calculator import calculate_ipi, compute_scientific_work_points
from api.models import (
    Article, Attachment, Department, Dissertation, Employee,
    KPIGroup, KPIGroupWeight, KPIIndicator, KPIResult,
    Monograph, OrganizationalWork, Project, ProjectMember,
    ProjectParticipation, Publication, Rule, ScientificWork, Software,
    Task, TechnicalWork, UserRole, VerificationRequest,
)


PASSWORD = 'test1234'


# Показатели: (название, work_type_key, W_base, форма-сущность)
# entity_kind: article | monograph | dissertation | software | grant | none
SCI_INDICATORS = [
    ('Публикационная активность (статьи SCOPUS и WoS)', 'article_scopus_wos', 8.0, 'article'),
    ('Публикационная активность (статьи ВАК)', 'article_vak', 3.0, 'article'),
    ('Патенты', 'patent', 8.0, 'none'),
    ('Регистрация ПО и БД', 'software_registration', 3.0, 'software'),
    ('Участие, разработка конечного продукта (практическая реализация)', 'product_dev', 5.0, 'none'),
    ('Монографии', 'monograph', 10.0, 'monograph'),
    ('Защита диссертации', 'dissertation_defense', 15.0, 'dissertation'),
    ('Руководство аспирантами, докторантами', 'phd_supervision', 4.0, 'none'),
    ('Доведение до защиты соискателя к.н.', 'bring_to_phd_defense', 6.0, 'none'),
    ('Доведение до защиты соискателя д.н.', 'bring_to_doctorate_defense', 10.0, 'none'),
    ('Участие в грантах', 'grant_participation', 4.0, 'grant'),
    ('Руководство грантом', 'grant_leadership', 7.0, 'grant'),
    ('Подготовка заявки на грант', 'grant_application', 2.0, 'none'),
    ('Внешнее научное взаимодействие', 'external_collaboration', 1.5, 'none'),
    ('Экспертизы, оппонирование, рецензии, отзывы', 'reviews_oppositions', 1.5, 'none'),
]
ORG_INDICATORS = [
    ('Работа в организационном комитете конференции', 'conf_committee', 2.0),
    ('Руководство организационным комитетом конференции', 'conf_committee_chair', 4.0),
    ('Работа в ВУЗе', 'university_work', 2.0),
    ('Работа техническим редактором в журнале', 'tech_editor', 2.0),
    ('Работа научным редактором в журнале', 'sci_editor', 3.0),
    ('Руководство журналом', 'journal_leadership', 5.0),
    ('Продвижение журнала', 'journal_promotion', 2.0),
    ('Общение с участниками конференций, авторами журнала, рецензентами', 'participant_communication', 1.0),
]
TECH_INDICATORS = [
    ('Сопровождение конференций', 'conf_support', 2.0),
    ('Поддержка наполнения контентом информационных систем', 'content_support', 2.0),
    ('Заключение договоров с участниками конференций, местами проведения', 'contracts', 1.5),
]

WI_TABLE = [
    # (position_type, phd_year, sci, tech, org)
    ('head', None, 0.5, 0.2, 0.3),
    ('senior_researcher', None, 0.55, 0.25, 0.2),
    ('researcher', None, 0.5, 0.3, 0.2),
    ('junior_researcher', None, 0.6, 0.3, 0.1),
    ('engineer', None, 0.2, 0.7, 0.1),
    ('phd_student', 1, 0.7, 0.2, 0.1),
    ('phd_student', 2, 0.7, 0.2, 0.1),
    ('phd_student', 3, 0.7, 0.2, 0.1),
    ('phd_student', 4, 0.8, 0.15, 0.05),
]

JOURNALS_SCOPUS = [
    'Energy', 'Applied Energy', 'IEEE Transactions on Power Systems',
    'Renewable and Sustainable Energy Reviews',
    'International Journal of Electrical Power & Energy Systems',
]
JOURNALS_VAK = [
    'Известия РАН. Энергетика',
    'Электричество',
    'Энергетик',
    'Промышленная энергетика',
    'Известия высших учебных заведений. Электромеханика',
]
PUBLISHERS = [
    'Наука', 'Энергоатомиздат', 'Издательство СО РАН',
    'Лань', 'ИНФРА-М',
]

WORK_THEMES_SCI = [
    'нейросетевые модели прогнозирования режимов',
    'анализ надёжности энергосистем',
    'оптимизация топологии распределительной сети',
    'моделирование возобновляемых источников энергии',
    'устойчивость электроэнергетической системы',
    'декомпозиция задач большого масштаба',
    'учёт неопределённостей при планировании режимов',
    'управление спросом в энергосистеме',
]

PROJECT_TASK_TITLES = [
    'Анализ требований к системе',
    'Разработка архитектуры приложения',
    'Реализация ядра расчётов',
    'Покрытие модульными тестами',
    'Подготовка технической документации',
    'Внедрение пилотной версии',
    'Интеграция с базой данных',
    'Настройка CI/CD',
]

# Шаблоны свободных задач (привязаны к показателю)
FREE_TASK_TEMPLATES = [
    ('Подготовить и опубликовать статью в журнале ВАК', 'sci', 'article_vak', 'high'),
    ('Подготовить статью для журнала SCOPUS/WoS', 'sci', 'article_scopus_wos', 'high'),
    ('Подать заявку на грант', 'sci', 'grant_application', 'medium'),
    ('Подготовить экспертное заключение', 'sci', 'reviews_oppositions', 'medium'),
    ('Зарегистрировать программу для ЭВМ', 'sci', 'software_registration', 'medium'),
    ('Сопровождение конференции', 'tech', 'conf_support', 'medium'),
    ('Наполнение информационной системы контентом', 'tech', 'content_support', 'low'),
    ('Подготовка договоров с участниками конференции', 'tech', 'contracts', 'medium'),
    ('Работа в организационном комитете конференции', 'org', 'conf_committee', 'medium'),
    ('Подготовка материалов журнала', 'org', 'tech_editor', 'low'),
]


class Command(BaseCommand):
    help = 'Очищает БД и заполняет тестовыми данными.'

    @transaction.atomic
    def handle(self, *args, **options):
        random.seed(42)
        self._clear()
        self._create_directories()
        self._create_rules()
        self._create_kpi_groups_and_indicators()
        self._create_kpi_weights()
        employees = self._create_employees()
        projects = self._create_projects(employees)
        self._create_tasks(employees, projects)
        self._create_works(employees)
        self._recalculate_ipi(employees)
        self._print_summary()

    # ------------------------------------------------------------
    # Очистка
    # ------------------------------------------------------------

    def _clear(self):
        self.stdout.write('Очистка БД...')
        Rule.objects.all().delete()
        Attachment.objects.all().delete()
        Task.objects.all().delete()
        ProjectMember.objects.all().delete()
        Project.objects.all().delete()
        VerificationRequest.objects.all().delete()
        Article.objects.all().delete()
        Monograph.objects.all().delete()
        Publication.objects.all().delete()
        Dissertation.objects.all().delete()
        ProjectParticipation.objects.all().delete()
        Software.objects.all().delete()
        ScientificWork.objects.all().delete()
        OrganizationalWork.objects.all().delete()
        TechnicalWork.objects.all().delete()
        KPIResult.objects.all().delete()
        KPIGroupWeight.objects.all().delete()
        KPIIndicator.objects.all().delete()
        KPIGroup.objects.all().delete()
        Employee.objects.all().delete()
        Department.objects.all().delete()
        UserRole.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

    # ------------------------------------------------------------
    # Справочники
    # ------------------------------------------------------------

    def _create_directories(self):
        self.dept_ivt = Department.objects.create(
            department_name='Отдел информационно-вычислительных технологий',
            department_short_name='ОИВТ',
        )
        self.dept_ies = Department.objects.create(
            department_name='Отдел иерархического моделирования энергосистем',
            department_short_name='ОИЭС',
        )
        self.role_admin = UserRole.objects.create(role_name='администратор')
        self.role_manager = UserRole.objects.create(role_name='руководитель')
        self.role_employee = UserRole.objects.create(role_name='сотрудник')

    # ------------------------------------------------------------
    # Правила продукционной экспертной системы
    # ------------------------------------------------------------

    def _create_rules(self):
        """Заполняет базу правил для расчёта поправочных коэффициентов IPI."""
        rules_data = [
            # k_возраст
            ('k_age', 'Возраст до 30 лет включительно',         None, 30,   1.2, 10),
            ('k_age', 'Возраст 31–45 лет',                       31,   45,   1.0, 20),
            ('k_age', 'Возраст более 45 лет',                    46,   None, 0.9, 30),
            # k_стаж
            ('k_experience', 'Стаж научной работы до 5 лет',     None, 5,    1.2, 10),
            ('k_experience', 'Стаж научной работы 6–15 лет',     6,    15,   1.0, 20),
            ('k_experience', 'Стаж научной работы более 15 лет', 16,   None, 0.9, 30),
            # k_аспирант
            ('k_phd', '1 год обучения в аспирантуре',            1,    1,    1.1, 10),
            ('k_phd', '2–3 год обучения в аспирантуре',          2,    3,    1.2, 20),
            ('k_phd', '4 год обучения в аспирантуре',            4,    4,    1.3, 30),
            # Квартиль журнала
            ('quartile', 'Журнал первого квартиля (Q1)',         1, 1, 1.5, 10),
            ('quartile', 'Журнал второго квартиля (Q2)',         2, 2, 1.2, 20),
            ('quartile', 'Журнал третьего квартиля (Q3)',        3, 3, 1.0, 30),
            ('quartile', 'Журнал четвёртого квартиля (Q4)',      4, 4, 0.8, 40),
        ]
        for rule_type, desc, mn, mx, coef, prio in rules_data:
            Rule.objects.create(
                rule_type=rule_type, description=desc,
                min_value=mn, max_value=mx,
                coefficient=coef, priority=prio,
            )

    # ------------------------------------------------------------
    # KPI
    # ------------------------------------------------------------

    def _create_kpi_groups_and_indicators(self):
        self.groups = {'sci': {}, 'tech': {}, 'org': {}}
        for dept_key, dept in (('ivt', self.dept_ivt), ('ies', self.dept_ies)):
            self.groups['sci'][dept_key] = KPIGroup.objects.create(
                name='Научные', group_weight=0.5, department=dept,
            )
            self.groups['tech'][dept_key] = KPIGroup.objects.create(
                name='Технические', group_weight=0.3, department=dept,
            )
            self.groups['org'][dept_key] = KPIGroup.objects.create(
                name='Организационные', group_weight=0.2, department=dept,
            )

            for name, key, weight, ekind in SCI_INDICATORS:
                KPIIndicator.objects.create(
                    kpi_group=self.groups['sci'][dept_key],
                    name=name, work_type_key=key, weight=weight,
                    entity_kind=ekind,
                )
            for name, key, weight in TECH_INDICATORS:
                KPIIndicator.objects.create(
                    kpi_group=self.groups['tech'][dept_key],
                    name=name, work_type_key=key, weight=weight,
                )
            for name, key, weight in ORG_INDICATORS:
                KPIIndicator.objects.create(
                    kpi_group=self.groups['org'][dept_key],
                    name=name, work_type_key=key, weight=weight,
                )

    def _create_kpi_weights(self):
        for ptype, phd, sci, tech, org in WI_TABLE:
            for dept_key in ('ivt', 'ies'):
                KPIGroupWeight.objects.create(
                    kpi_group=self.groups['sci'][dept_key],
                    position_type=ptype, phd_year=phd, weight=sci,
                )
                KPIGroupWeight.objects.create(
                    kpi_group=self.groups['tech'][dept_key],
                    position_type=ptype, phd_year=phd, weight=tech,
                )
                KPIGroupWeight.objects.create(
                    kpi_group=self.groups['org'][dept_key],
                    position_type=ptype, phd_year=phd, weight=org,
                )

    # ------------------------------------------------------------
    # Сотрудники
    # ------------------------------------------------------------

    def _create_employee(self, *, name, login, position, position_type, phd_year,
                         age, experience, degree, dept, role):
        user = User.objects.create_user(username=login, email=login, password=PASSWORD)
        return Employee.objects.create(
            user=user, full_name=name, email=login, position=position,
            position_type=position_type, phd_year=phd_year,
            age=age, experience=experience, academic_degree=degree,
            department=dept, role=role,
        )

    def _create_employees(self):
        employees = []

        admin = self._create_employee(
            name='Иванов Иван Иванович', login='admin@gmail.com',
            position='Администратор системы',
            position_type='senior_researcher', phd_year=None,
            age=45, experience=20, degree='к.т.н.',
            dept=self.dept_ivt, role=self.role_admin,
        )
        employees.append(admin)

        ivt_head = self._create_employee(
            name='Петров Алексей Сергеевич', login='petrov@gmail.com',
            position='Руководитель отдела',
            position_type='head', phd_year=None,
            age=52, experience=25, degree='д.т.н.',
            dept=self.dept_ivt, role=self.role_manager,
        )
        ies_head = self._create_employee(
            name='Смирнова Елена Михайловна', login='smirnova@gmail.com',
            position='Руководитель отдела',
            position_type='head', phd_year=None,
            age=48, experience=22, degree='д.т.н.',
            dept=self.dept_ies, role=self.role_manager,
        )
        employees += [ivt_head, ies_head]

        sample = [
            ('ivt', 'Кузнецов Артём Викторович', 'kuznetsov@gmail.com', 'с.н.с.', 'senior_researcher', None, 42, 18, 'к.т.н.'),
            ('ivt', 'Васильева Анна Дмитриевна', 'vasileva@gmail.com', 'н.с.', 'researcher', None, 35, 10, 'к.т.н.'),
            ('ivt', 'Соколов Михаил Андреевич', 'sokolov@gmail.com', 'м.н.с.', 'junior_researcher', None, 28, 4, None),
            ('ivt', 'Морозова Ксения Игоревна', 'morozova@gmail.com', 'Аспирант', 'phd_student', 2, 25, 2, None),
            ('ivt', 'Новиков Денис Олегович', 'novikov@gmail.com', 'Аспирант', 'phd_student', 4, 27, 4, None),
            ('ivt', 'Фёдоров Игорь Васильевич', 'fedorov@gmail.com', 'Инженер', 'engineer', None, 38, 12, None),
            ('ies', 'Лебедев Антон Павлович', 'lebedev@gmail.com', 'с.н.с.', 'senior_researcher', None, 50, 24, 'д.т.н.'),
            ('ies', 'Орлова Мария Сергеевна', 'orlova@gmail.com', 'н.с.', 'researcher', None, 32, 7, 'к.т.н.'),
            ('ies', 'Семёнов Павел Юрьевич', 'semenov@gmail.com', 'м.н.с.', 'junior_researcher', None, 30, 5, None),
            ('ies', 'Григорьева Ольга Александровна', 'grigorieva@gmail.com', 'Аспирант', 'phd_student', 1, 24, 1, None),
            ('ies', 'Тарасов Сергей Николаевич', 'tarasov@gmail.com', 'Аспирант', 'phd_student', 3, 26, 3, None),
            ('ies', 'Захаров Виктор Алексеевич', 'zakharov@gmail.com', 'Инженер', 'engineer', None, 40, 15, None),
        ]

        for dept_key, name, login, pos, ptype, phd_year, age, exp, degree in sample:
            dept = self.dept_ivt if dept_key == 'ivt' else self.dept_ies
            employees.append(self._create_employee(
                name=name, login=login, position=pos,
                position_type=ptype, phd_year=phd_year,
                age=age, experience=exp, degree=degree,
                dept=dept, role=self.role_employee,
            ))

        return employees

    # ------------------------------------------------------------
    # Проекты
    # ------------------------------------------------------------

    def _create_projects(self, employees):
        ivt_emps = [e for e in employees if e.department.department_short_name == 'ОИВТ']
        ies_emps = [e for e in employees if e.department.department_short_name == 'ОИЭС']
        ivt_head = next(e for e in ivt_emps if e.position_type == 'head')
        ies_head = next(e for e in ies_emps if e.position_type == 'head')

        projects = []

        p1 = Project.objects.create(
            name='Система поддержки принятия решений в энергетике',
            description='Веб-система для оценки энергоэффективности и планирования режимов.',
            budget=2_500_000, start_date=date(2025, 9, 1),
            end_date=date(2026, 6, 30), creator=ivt_head,
        )
        ProjectMember.objects.create(project=p1, employee=ivt_head)
        for emp in random.sample([e for e in ivt_emps if e != ivt_head], 4):
            ProjectMember.objects.get_or_create(project=p1, employee=emp)
        projects.append(p1)

        p2 = Project.objects.create(
            name='Моделирование надёжности электроэнергетических систем',
            description='Иерархическое моделирование надёжности с учётом ВИЭ.',
            budget=3_800_000, start_date=date(2025, 7, 15),
            end_date=date(2026, 12, 31), creator=ies_head,
        )
        ProjectMember.objects.create(project=p2, employee=ies_head)
        for emp in random.sample([e for e in ies_emps if e != ies_head], 4):
            ProjectMember.objects.get_or_create(project=p2, employee=emp)
        projects.append(p2)

        p3 = Project.objects.create(
            name='Анализ режимов работы энергосистемы Сибири',
            description='Исследование оптимальных режимов в рамках госбюджетной темы.',
            budget=1_500_000, start_date=date(2025, 1, 15),
            end_date=date(2025, 12, 31), completed_at=date(2025, 12, 28),
            creator=ies_head,
        )
        ProjectMember.objects.create(project=p3, employee=ies_head)
        for emp in random.sample([e for e in ies_emps if e != ies_head], 3):
            ProjectMember.objects.get_or_create(project=p3, employee=emp)
        projects.append(p3)

        return projects

    # ------------------------------------------------------------
    # Задачи
    # ------------------------------------------------------------

    def _create_tasks(self, employees, projects):
        for project in projects[:2]:
            members = list(project.members.all())
            for i, title in enumerate(random.sample(PROJECT_TASK_TITLES, 5)):
                assignee = random.choice(members).employee if members else None
                if random.random() < 0.2:
                    assignee = None
                Task.objects.create(
                    title=title,
                    description=f'Задача №{i + 1} проекта «{project.name}».',
                    status=random.choice(['assigned', 'in_progress', 'completed']),
                    priority=random.choice(['low', 'medium', 'high']),
                    deadline=date.today() + timedelta(days=random.randint(-10, 60)),
                    project=project, assigned_to=assignee,
                    created_by=project.creator,
                )

        managers = [e for e in employees if e.role.role_name == 'руководитель']
        regular = [e for e in employees if e.role.role_name == 'сотрудник']

        for emp in regular[:6]:
            title, gkey, key, prio = random.choice(FREE_TASK_TEMPLATES)
            mgr = next(m for m in managers if m.department == emp.department)
            dept_key = 'ivt' if emp.department == self.dept_ivt else 'ies'
            indicator = KPIIndicator.objects.get(
                kpi_group=self.groups[gkey][dept_key], work_type_key=key,
            )
            Task.objects.create(
                title=title, description=f'Свободная задача: {emp.full_name}.',
                status=random.choice(['assigned', 'in_progress']), priority=prio,
                deadline=date.today() + timedelta(days=random.randint(7, 45)),
                kpi_group=self.groups[gkey][dept_key],
                work_type_key=key, points=indicator.weight,
                project=None, assigned_to=emp, created_by=mgr,
            )

        for _ in range(3):
            mgr = random.choice(managers)
            title, gkey, key, prio = random.choice(FREE_TASK_TEMPLATES)
            dept_key = 'ivt' if mgr.department == self.dept_ivt else 'ies'
            indicator = KPIIndicator.objects.get(
                kpi_group=self.groups[gkey][dept_key], work_type_key=key,
            )
            Task.objects.create(
                title=title + ' (в общий пул)',
                description='Задача доступна для взятия из пула.',
                status='assigned', priority=prio,
                deadline=date.today() + timedelta(days=30),
                kpi_group=self.groups[gkey][dept_key],
                work_type_key=key, points=indicator.weight,
                project=None, assigned_to=None, created_by=mgr,
            )

    # ------------------------------------------------------------
    # Работы
    # ------------------------------------------------------------

    def _make_sci_work(self, emp, indicator_def):
        name, key, points, kind = indicator_def
        title = self._title_for_indicator(name, key, kind)
        verified = random.random() > 0.3
        work = ScientificWork.objects.create(
            employee=emp, title=title, work_type=key,
            points=points, verified=verified,
        )
        if not verified:
            vr = VerificationRequest.objects.create(
                work_type='scientific', requester=emp,
            )
            work.verification_request = vr
            work.save(update_fields=['verification_request'])

        if kind == 'article_scopus':
            quartile = random.randint(1, 4)
            pub = Publication.objects.create(
                scientific_work=work, title=title, year=2025, pub_type='article',
            )
            Article.objects.create(
                publication=pub, journal=random.choice(JOURNALS_SCOPUS),
                doi=f'10.1016/j.energy.{random.randint(2024, 2025)}.{random.randint(100000, 999999)}',
                quartile=quartile, is_scopus=True,
            )
            # Учёт квартиля в баллах
            work.points = compute_scientific_work_points(points, quartile=quartile)
            work.save(update_fields=['points'])
        elif kind == 'article_vak':
            pub = Publication.objects.create(
                scientific_work=work, title=title, year=2025, pub_type='article',
            )
            Article.objects.create(
                publication=pub, journal=random.choice(JOURNALS_VAK),
                doi=None, quartile=None, is_scopus=False,
            )
        elif kind == 'monograph':
            pub = Publication.objects.create(
                scientific_work=work, title=title, year=2025, pub_type='monograph',
            )
            Monograph.objects.create(
                publication=pub, publisher=random.choice(PUBLISHERS),
                isbn=f'978-5-{random.randint(1000, 9999)}-{random.randint(100, 999)}-{random.randint(0, 9)}',
                pages_count=random.randint(120, 320),
            )
        elif kind == 'dissertation':
            Dissertation.objects.create(
                scientific_work=work,
                stage=random.choice(['Защита к.т.н.', 'Защита д.т.н.']),
                defense_date=date.today() - timedelta(days=random.randint(30, 365)),
            )
        elif kind == 'software':
            Software.objects.create(
                scientific_work=work,
                version=f'{random.randint(1, 4)}.{random.randint(0, 9)}',
                is_commercial=random.random() > 0.7,
            )
        elif kind == 'grant':
            role = 'Руководитель' if key == 'grant_leadership' else 'Участник'
            ProjectParticipation.objects.create(
                scientific_work=work, role=role,
                budget=random.randint(500_000, 5_000_000),
                start_date=date(2024, random.randint(1, 12), 1),
                end_date=date(2026, random.randint(1, 12), 28),
            )

    def _title_for_indicator(self, name, key, kind):
        theme = random.choice(WORK_THEMES_SCI)
        if kind == 'article_scopus':
            return f'Статья: {theme}'
        if kind == 'article_vak':
            return f'Статья (ВАК): {theme}'
        if kind == 'monograph':
            return f'Монография: {theme}'
        if kind == 'dissertation':
            return f'Диссертация: {theme}'
        if kind == 'software':
            return f'Программа для ЭВМ: расчёт {theme}'
        if kind == 'grant':
            return f'Грант: «{theme}»'
        if key == 'patent':
            return f'Патент на изобретение: способ {theme}'
        if key == 'product_dev':
            return f'Конечный продукт: {theme}'
        if key == 'phd_supervision':
            return 'Руководство аспирантом'
        if key == 'bring_to_phd_defense':
            return 'Доведение соискателя к.н. до защиты'
        if key == 'bring_to_doctorate_defense':
            return 'Доведение соискателя д.н. до защиты'
        if key == 'grant_application':
            return f'Заявка на грант: {theme}'
        if key == 'external_collaboration':
            return f'Внешнее научное взаимодействие: {theme}'
        if key == 'reviews_oppositions':
            return 'Рецензия на статью / экспертное заключение'
        return name

    def _make_org_work(self, emp, indicator_def):
        name, key, points = indicator_def
        verified = random.random() > 0.4
        work = OrganizationalWork.objects.create(
            employee=emp, title=name, work_type=key,
            event_date=date.today() - timedelta(days=random.randint(5, 90)),
            points=points, verified=verified,
            participants_count=random.randint(20, 100) if 'conf' in key else None,
        )
        if not verified:
            vr = VerificationRequest.objects.create(
                work_type='organizational', requester=emp,
            )
            work.verification_request = vr
            work.save(update_fields=['verification_request'])

    def _make_tech_work(self, emp, indicator_def):
        name, key, points = indicator_def
        verified = random.random() > 0.4
        work = TechnicalWork.objects.create(
            employee=emp, title=name, work_type=key,
            work_date=date.today() - timedelta(days=random.randint(5, 60)),
            base_points=points, points=points, verified=verified,
            registration_number=f'РФ-{random.randint(1000, 9999)}'
            if key == 'contracts' else None,
        )
        if not verified:
            vr = VerificationRequest.objects.create(
                work_type='technical', requester=emp,
            )
            work.verification_request = vr
            work.save(update_fields=['verification_request'])

    def _create_works(self, employees):
        for emp in employees:
            if emp.role.role_name == 'администратор':
                continue
            for _ in range(random.randint(2, 5)):
                self._make_sci_work(emp, random.choice(SCI_INDICATORS))
            for _ in range(random.randint(0, 2)):
                self._make_tech_work(emp, random.choice(TECH_INDICATORS))
            for _ in range(random.randint(0, 2)):
                self._make_org_work(emp, random.choice(ORG_INDICATORS))

    # ------------------------------------------------------------
    # IPI
    # ------------------------------------------------------------

    def _recalculate_ipi(self, employees):
        today = date.today()
        year = today.year
        quarter = (today.month - 1) // 3 + 1
        for emp in employees:
            calculate_ipi(emp, year, quarter)

    # ------------------------------------------------------------
    # Сводка
    # ------------------------------------------------------------

    def _print_summary(self):
        self.stdout.write(self.style.SUCCESS('=' * 64))
        self.stdout.write(self.style.SUCCESS('Тестовые данные загружены.'))
        self.stdout.write('')
        self.stdout.write(f'Пароль для всех учётных записей: {PASSWORD}')
        self.stdout.write('')
        self.stdout.write('Учётные записи:')
        for e in Employee.objects.select_related('role', 'department').order_by('role__role_name', 'full_name'):
            self.stdout.write(
                f'  {e.email:<28} {e.role.role_name:<16} '
                f'{e.position_type:<20} {e.department.department_short_name}'
            )
        self.stdout.write('')
        self.stdout.write(f'Сотрудников: {Employee.objects.count()}')
        self.stdout.write(f'Проектов: {Project.objects.count()}')
        self.stdout.write(f'Задач: {Task.objects.count()}')
        works_total = (
            ScientificWork.objects.count()
            + OrganizationalWork.objects.count()
            + TechnicalWork.objects.count()
        )
        self.stdout.write(f'Работ: {works_total}')
        self.stdout.write(f'Заявок на верификацию: {VerificationRequest.objects.count()}')
        self.stdout.write(self.style.SUCCESS('=' * 64))
