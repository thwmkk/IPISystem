from django.db import models
from django.contrib.auth.models import User


# ============================================================
#  Справочники
# ============================================================

class Department(models.Model):
    department_name = models.CharField(max_length=300)
    department_short_name = models.CharField(max_length=50)

    class Meta:
        db_table = 'department'

    def __str__(self):
        return self.department_short_name


class UserRole(models.Model):
    role_name = models.CharField(max_length=50)

    class Meta:
        db_table = 'user_role'

    def __str__(self):
        return self.role_name


# ============================================================
#  Сотрудник
# ============================================================

class Employee(models.Model):
    POSITION_TYPE_CHOICES = [
        ('junior_researcher', 'м.н.с.'),
        ('researcher', 'н.с.'),
        ('senior_researcher', 'с.н.с.'),
        ('engineer', 'инженер'),
        ('phd_student', 'аспирант'),
        ('head', 'руководитель отдела'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee', null=True, blank=True)
    full_name = models.CharField(max_length=200)
    email = models.EmailField(max_length=120, unique=True)
    position = models.CharField(max_length=50)
    position_type = models.CharField(
        max_length=32, choices=POSITION_TYPE_CHOICES,
        default='researcher',
    )
    phd_year = models.IntegerField(null=True, blank=True)
    age = models.IntegerField()
    experience = models.IntegerField()
    academic_degree = models.CharField(max_length=50, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='employees')
    role = models.ForeignKey(UserRole, on_delete=models.PROTECT, related_name='employees')

    class Meta:
        db_table = 'employee'

    def __str__(self):
        return self.full_name


# ============================================================
#  Заявка на верификацию
# ============================================================

class VerificationRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('approved', 'Одобрена'),
        ('rejected', 'Отклонена'),
    ]
    WORK_TYPE_CHOICES = [
        ('scientific', 'Научная'),
        ('organizational', 'Организационная'),
        ('technical', 'Техническая'),
    ]

    work_type = models.CharField(max_length=50, choices=WORK_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    request_date = models.DateField(auto_now_add=True)
    comment = models.TextField(null=True, blank=True)
    requester = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='verification_requests')
    evaluator = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='evaluations')

    class Meta:
        db_table = 'verification_request'

    def __str__(self):
        return f'{self.work_type} — {self.status} ({self.requester})'


# ============================================================
#  Научные работы
# ============================================================

class ScientificWork(models.Model):
    title = models.CharField(max_length=300)
    work_type = models.CharField(max_length=50)
    points = models.FloatField(default=0)
    verified = models.BooleanField(default=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='scientific_works')
    verification_request = models.ForeignKey(VerificationRequest, on_delete=models.SET_NULL, null=True, blank=True, related_name='scientific_works')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'scientific_work'

    def __str__(self):
        return f'{self.title} ({self.work_type})'


class Publication(models.Model):
    PUB_TYPE_CHOICES = [
        ('article', 'Статья'),
        ('monograph', 'Монография'),
    ]

    title = models.CharField(max_length=300)
    year = models.IntegerField()
    pub_type = models.CharField(max_length=50, choices=PUB_TYPE_CHOICES)
    scientific_work = models.OneToOneField(ScientificWork, on_delete=models.CASCADE, related_name='publication')

    class Meta:
        db_table = 'publication'

    def __str__(self):
        return self.title


class Article(models.Model):
    publication = models.OneToOneField(Publication, on_delete=models.CASCADE, related_name='article')
    journal = models.CharField(max_length=200)
    doi = models.CharField(max_length=100, null=True, blank=True)
    quartile = models.IntegerField(null=True, blank=True)
    is_scopus = models.BooleanField(default=False)

    class Meta:
        db_table = 'article'

    def __str__(self):
        return f'{self.publication.title} — {self.journal}'


class Monograph(models.Model):
    publication = models.OneToOneField(Publication, on_delete=models.CASCADE, related_name='monograph')
    publisher = models.CharField(max_length=200)
    isbn = models.CharField(max_length=20, null=True, blank=True)
    pages_count = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'monograph'

    def __str__(self):
        return f'{self.publication.title} — {self.publisher}'


class Dissertation(models.Model):
    scientific_work = models.OneToOneField(ScientificWork, on_delete=models.CASCADE, related_name='dissertation')
    stage = models.CharField(max_length=50)
    defense_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'dissertation'

    def __str__(self):
        return f'Диссертация: {self.scientific_work.title}'


class ProjectParticipation(models.Model):
    scientific_work = models.OneToOneField(ScientificWork, on_delete=models.CASCADE, related_name='project_participation')
    role = models.CharField(max_length=100)
    budget = models.FloatField(null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'project_participation'

    def __str__(self):
        return f'{self.scientific_work.title} — {self.role}'


class Software(models.Model):
    scientific_work = models.OneToOneField(ScientificWork, on_delete=models.CASCADE, related_name='software')
    version = models.CharField(max_length=50)
    is_commercial = models.BooleanField(default=False)

    class Meta:
        db_table = 'software'

    def __str__(self):
        return f'{self.scientific_work.title} v{self.version}'


# ============================================================
#  Организационные работы
# ============================================================

class OrganizationalWork(models.Model):
    title = models.CharField(max_length=300)
    work_type = models.CharField(max_length=50)
    event_date = models.DateField()
    participants_count = models.IntegerField(null=True, blank=True)
    points = models.FloatField(default=0)
    verified = models.BooleanField(default=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='organizational_works')
    verification_request = models.ForeignKey(VerificationRequest, on_delete=models.SET_NULL, null=True, blank=True, related_name='organizational_works')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'organizational_work'

    def __str__(self):
        return f'{self.title} ({self.work_type})'


# ============================================================
#  Технические работы
# ============================================================

class TechnicalWork(models.Model):
    title = models.CharField(max_length=300)
    work_type = models.CharField(max_length=100, default='')
    registration_number = models.CharField(max_length=50, null=True, blank=True)
    work_date = models.DateField()
    metric = models.CharField(max_length=50, null=True, blank=True)
    base_points = models.FloatField(default=0)
    points = models.FloatField(default=0)
    verified = models.BooleanField(default=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='technical_works')
    verification_request = models.ForeignKey(VerificationRequest, on_delete=models.SET_NULL, null=True, blank=True, related_name='technical_works')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'technical_work'

    def __str__(self):
        return f'{self.title}'


# ============================================================
#  KPI: группы, веса, результаты
# ============================================================

class KPIGroup(models.Model):
    """Группа показателей: Научные, Организационные, Технические."""
    name = models.CharField(max_length=100)
    group_weight = models.FloatField(default=1.0, help_text='Wi — вес группы')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='kpi_groups')

    class Meta:
        db_table = 'kpi_group'

    def __str__(self):
        return f'{self.name} (Wi={self.group_weight})'


class KPIIndicator(models.Model):
    """Показатель внутри группы. weight = W_base (базовый вес показателя).
    entity_kind задаёт, какие дополнительные поля показывать в форме создания работы.
    """
    ENTITY_KIND_CHOICES = [
        ('none', 'Без дополнительных полей'),
        ('article', 'Статья'),
        ('monograph', 'Монография'),
        ('dissertation', 'Диссертация'),
        ('software', 'ПО'),
        ('grant', 'Участие в проекте'),
    ]

    kpi_group = models.ForeignKey(KPIGroup, on_delete=models.CASCADE, related_name='indicators')
    name = models.CharField(max_length=200, help_text='Название показателя')
    work_type_key = models.CharField(max_length=100, help_text='Ключ для сопоставления с work_type работ')
    weight = models.FloatField(default=1.0, help_text='W_base — базовый вес показателя')
    entity_kind = models.CharField(
        max_length=20, choices=ENTITY_KIND_CHOICES, default='none',
        help_text='Тип сущности-подтипа научной работы (для других категорий — none)',
    )

    class Meta:
        db_table = 'kpi_indicator'

    def __str__(self):
        return f'{self.kpi_group.name} → {self.name} (W_base={self.weight})'


class KPIGroupWeight(models.Model):
    """Вес группы (Wi) для конкретной должности (и года аспирантуры)."""
    kpi_group = models.ForeignKey(KPIGroup, on_delete=models.CASCADE, related_name='position_weights')
    position_type = models.CharField(max_length=32, choices=Employee.POSITION_TYPE_CHOICES)
    phd_year = models.IntegerField(null=True, blank=True)
    weight = models.FloatField(default=1.0)

    class Meta:
        db_table = 'kpi_group_weight'
        unique_together = ['kpi_group', 'position_type', 'phd_year']

    def __str__(self):
        suffix = f', курс {self.phd_year}' if self.phd_year else ''
        return f'{self.kpi_group.name} / {self.position_type}{suffix} = {self.weight}'


class KPIResult(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='kpi_results')
    year = models.IntegerField()
    quarter = models.IntegerField()
    scientific_score = models.FloatField(default=0)
    organizational_score = models.FloatField(default=0)
    technical_score = models.FloatField(default=0)
    total_ipi = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'kpi_result'
        unique_together = ['employee', 'year', 'quarter']

    def __str__(self):
        return f'{self.employee} — {self.year} Q{self.quarter}: IPI={self.total_ipi}'


# ============================================================
#  Проекты
# ============================================================

class Project(models.Model):
    name = models.CharField(max_length=300)
    description = models.TextField(null=True, blank=True)
    budget = models.FloatField(null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    creator = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='created_projects')
    completed_at = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'project'

    def __str__(self):
        return self.name


class ProjectMember(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='members')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='project_memberships')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'project_member'
        unique_together = ['project', 'employee']

    def __str__(self):
        return f'{self.project.name} — {self.employee.full_name}'


# ============================================================
#  Задачи
# ============================================================

class Task(models.Model):
    STATUS_CHOICES = [
        ('assigned', 'Назначена'),
        ('in_progress', 'В работе'),
        ('completed', 'Выполнена'),
        ('overdue', 'Просрочена'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий'),
    ]

    title = models.CharField(max_length=300)
    description = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    deadline = models.DateField()
    kpi_group = models.ForeignKey(KPIGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    work_type_key = models.CharField(max_length=100, null=True, blank=True)
    points = models.FloatField(default=0)
    project = models.ForeignKey('Project', on_delete=models.CASCADE, null=True, blank=True, related_name='tasks')
    assigned_to = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True, related_name='assigned_tasks')
    created_by = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='created_tasks')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'task'

    def __str__(self):
        return f'{self.title} ({self.status})'


# ============================================================
#  Вложения (файлы к работам и задачам)
# ============================================================

class Attachment(models.Model):
    file = models.FileField(upload_to='attachments/%Y/%m/')
    original_name = models.CharField(max_length=255)
    size = models.IntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='uploaded_attachments')

    # К чему прикреплено — ровно одно из:
    scientific_work = models.ForeignKey(ScientificWork, on_delete=models.CASCADE, null=True, blank=True, related_name='attachments')
    organizational_work = models.ForeignKey(OrganizationalWork, on_delete=models.CASCADE, null=True, blank=True, related_name='attachments')
    technical_work = models.ForeignKey(TechnicalWork, on_delete=models.CASCADE, null=True, blank=True, related_name='attachments')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True, related_name='attachments')

    class Meta:
        db_table = 'attachment'

    def __str__(self):
        return self.original_name


# ============================================================
#  Правила продукционной экспертной системы
# ============================================================

class Rule(models.Model):
    """Правило экспертной системы для определения поправочного коэффициента
    или множителя по характеристикам сотрудника или работы."""

    RULE_TYPE_CHOICES = [
        ('k_age', 'Поправка по возрасту'),
        ('k_experience', 'Поправка по стажу научной работы'),
        ('k_phd', 'Поправка по году обучения в аспирантуре'),
        ('quartile', 'Множитель квартиля журнала'),
    ]

    rule_type = models.CharField(max_length=20, choices=RULE_TYPE_CHOICES)
    description = models.CharField(max_length=300, help_text='Текстовое описание правила')
    min_value = models.IntegerField(null=True, blank=True,
                                    help_text='Нижняя граница диапазона (включительно), либо NULL')
    max_value = models.IntegerField(null=True, blank=True,
                                    help_text='Верхняя граница диапазона (включительно), либо NULL')
    coefficient = models.FloatField(default=1.0, help_text='Итоговый коэффициент / множитель')
    priority = models.IntegerField(default=100,
                                   help_text='Порядок проверки (меньше — раньше)')

    class Meta:
        db_table = 'rule'
        ordering = ['rule_type', 'priority']

    def __str__(self):
        return f'[{self.get_rule_type_display()}] {self.description} → {self.coefficient}'
