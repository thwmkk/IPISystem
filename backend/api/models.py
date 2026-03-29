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
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee', null=True, blank=True)
    full_name = models.CharField(max_length=200)
    email = models.EmailField(max_length=120, unique=True)
    position = models.CharField(max_length=50)
    age = models.IntegerField()
    experience = models.IntegerField()
    is_phd_student = models.BooleanField(default=False)
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
    name = models.CharField(max_length=100)
    metric_group = models.CharField(max_length=50, null=True, blank=True)
    base_points = models.FloatField(default=0)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='kpi_groups')

    class Meta:
        db_table = 'kpi_group'

    def __str__(self):
        return self.name


class KPIWeight(models.Model):
    kpi_group = models.ForeignKey(KPIGroup, on_delete=models.CASCADE, related_name='weights')
    position = models.CharField(max_length=50)
    group_weight = models.FloatField()
    weight = models.FloatField()

    class Meta:
        db_table = 'kpi_weight'

    def __str__(self):
        return f'{self.kpi_group.name} — {self.position}: W={self.group_weight}, w={self.weight}'


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
    assigned_to = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True, related_name='assigned_tasks')
    created_by = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='created_tasks')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'task'

    def __str__(self):
        return f'{self.title} ({self.status})'
