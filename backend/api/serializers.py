from datetime import date

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Department, UserRole, Employee,
    VerificationRequest,
    ScientificWork, Publication, Article, Monograph,
    Dissertation, ProjectParticipation, Software,
    OrganizationalWork, TechnicalWork,
    KPIGroup, KPIIndicator, KPIResult,
    Project, ProjectMember,
    Task, Attachment,
    KPIGroupWeight,
)
from .ipi_calculator import compute_scientific_work_points


# ============================================================
#  Auth
# ============================================================

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


# ============================================================
#  Справочники
# ============================================================

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = '__all__'


# ============================================================
#  Сотрудник
# ============================================================

class EmployeeListSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.department_short_name', read_only=True)
    role_name = serializers.CharField(source='role.role_name', read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id', 'full_name', 'email', 'position', 'age',
            'experience', 'position_type', 'phd_year', 'academic_degree',
            'department', 'department_name', 'role', 'role_name',
        ]


class EmployeeDetailSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.department_short_name', read_only=True)
    role_name = serializers.CharField(source='role.role_name', read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id', 'full_name', 'email', 'position', 'age',
            'experience', 'position_type', 'phd_year', 'academic_degree',
            'department', 'department_name', 'role', 'role_name',
        ]


class EmployeeCreateSerializer(serializers.ModelSerializer):
    """Used by manager/admin to create employee and send credentials."""

    class Meta:
        model = Employee
        fields = [
            'full_name', 'email', 'position', 'age',
            'experience', 'position_type', 'phd_year', 'academic_degree',
            'department', 'role',
        ]

    def validate_full_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('ФИО обязательно')
        if len(value.strip()) < 3:
            raise serializers.ValidationError('ФИО слишком короткое')
        return value.strip()

    def validate_age(self, value):
        if value < 18 or value > 100:
            raise serializers.ValidationError('Возраст должен быть от 18 до 100')
        return value

    def validate_experience(self, value):
        if value < 0 or value > 80:
            raise serializers.ValidationError('Стаж должен быть от 0 до 80 лет')
        return value

    def validate_email(self, value):
        if Employee.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('Сотрудник с таким email уже существует')
        return value.lower()

    def validate(self, attrs):
        age = attrs.get('age')
        experience = attrs.get('experience')
        if age is not None and experience is not None and experience > age - 16:
            raise serializers.ValidationError({
                'experience': 'Стаж не может превышать возраст минус 16 лет',
            })
        return attrs


# ============================================================
#  Верификация
# ============================================================

class VerificationRequestSerializer(serializers.ModelSerializer):
    requester_name = serializers.CharField(source='requester.full_name', read_only=True)
    evaluator_name = serializers.CharField(source='evaluator.full_name', read_only=True)
    work_title = serializers.SerializerMethodField()
    work_details = serializers.SerializerMethodField()

    class Meta:
        model = VerificationRequest
        fields = '__all__'
        read_only_fields = ['request_date']

    def _get_work(self, obj):
        return (
            obj.scientific_works.first()
            or obj.organizational_works.first()
            or obj.technical_works.first()
        )

    def get_work_title(self, obj):
        work = self._get_work(obj)
        return work.title if work else f'Заявка #{obj.id}'

    def get_work_details(self, obj):
        work = self._get_work(obj)
        if not work:
            return None
        details = {
            'title': work.title,
            'work_type': work.work_type,
            'points': work.points,
        }
        if obj.work_type == 'scientific':
            details['created_at'] = str(work.created_at) if work.created_at else None
            pub = getattr(work, 'publication', None)
            if pub:
                details['publication'] = {'title': pub.title, 'year': pub.year, 'pub_type': pub.pub_type}
                article = getattr(pub, 'article', None)
                if article:
                    details['publication']['article'] = {
                        'journal': article.journal, 'doi': article.doi,
                        'quartile': article.quartile, 'is_scopus': article.is_scopus,
                    }
                mono = getattr(pub, 'monograph', None)
                if mono:
                    details['publication']['monograph'] = {
                        'publisher': mono.publisher, 'isbn': mono.isbn,
                        'pages_count': mono.pages_count,
                    }
            diss = getattr(work, 'dissertation', None)
            if diss:
                details['dissertation'] = {
                    'stage': diss.stage,
                    'defense_date': str(diss.defense_date) if diss.defense_date else None,
                }
            proj = getattr(work, 'project_participation', None)
            if proj:
                details['project'] = {
                    'role': proj.role, 'budget': float(proj.budget) if proj.budget else None,
                    'start_date': str(proj.start_date) if proj.start_date else None,
                    'end_date': str(proj.end_date) if proj.end_date else None,
                }
            soft = getattr(work, 'software', None)
            if soft:
                details['software'] = {'version': soft.version, 'is_commercial': soft.is_commercial}
        elif obj.work_type == 'organizational':
            details['event_date'] = str(work.event_date) if work.event_date else None
            details['participants_count'] = work.participants_count
        elif obj.work_type == 'technical':
            details['work_date'] = str(work.work_date) if work.work_date else None
            details['registration_number'] = work.registration_number
            details['metric'] = work.metric
        return details


# ============================================================
#  Научные работы
# ============================================================

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        exclude = ['id', 'publication']


class MonographSerializer(serializers.ModelSerializer):
    class Meta:
        model = Monograph
        exclude = ['id', 'publication']


class PublicationSerializer(serializers.ModelSerializer):
    article = ArticleSerializer(required=False)
    monograph = MonographSerializer(required=False)

    class Meta:
        model = Publication
        exclude = ['scientific_work']


class DissertationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dissertation
        exclude = ['scientific_work']


class ProjectParticipationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectParticipation
        exclude = ['scientific_work']


class SoftwareSerializer(serializers.ModelSerializer):
    class Meta:
        model = Software
        exclude = ['scientific_work']


class ScientificWorkSerializer(serializers.ModelSerializer):
    publication = PublicationSerializer(required=False)
    dissertation = DissertationSerializer(required=False)
    project_participation = ProjectParticipationSerializer(required=False)
    software = SoftwareSerializer(required=False)
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    attachments = serializers.SerializerMethodField()

    class Meta:
        model = ScientificWork
        fields = '__all__'
        read_only_fields = ['verified', 'verification_request', 'created_at']

    def get_attachments(self, obj):
        return AttachmentSerializer(obj.attachments.all(), many=True, context=self.context).data

    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('Название не может быть пустым')
        return value.strip()

    def validate_points(self, value):
        if value is None or value < 0:
            raise serializers.ValidationError('Баллы не могут быть отрицательными')
        if value > 1000:
            raise serializers.ValidationError('Значение баллов слишком велико')
        return value

    def validate(self, attrs):
        is_partial = self.partial  # True for PATCH

        pub = attrs.get('publication')
        if pub:
            if not is_partial and not pub.get('pub_type'):
                raise serializers.ValidationError({'publication': 'Укажите тип публикации'})
            year = pub.get('year')
            if year and (year < 1900 or year > date.today().year + 1):
                raise serializers.ValidationError({'publication': {'year': 'Недопустимый год'}})
            pub_type = pub.get('pub_type')
            if pub_type == 'article' or (is_partial and pub.get('article') is not None):
                art = pub.get('article') or {}
                if not is_partial and not (art.get('journal') or '').strip():
                    raise serializers.ValidationError({'publication': {'article': {'journal': 'Укажите журнал'}}})
                q = art.get('quartile')
                if q is not None and q not in (1, 2, 3, 4):
                    raise serializers.ValidationError({'publication': {'article': {'quartile': 'Квартиль должен быть 1–4'}}})
            elif pub_type == 'monograph' or (is_partial and pub.get('monograph') is not None):
                mono = pub.get('monograph') or {}
                if not is_partial and not (mono.get('publisher') or '').strip():
                    raise serializers.ValidationError({'publication': {'monograph': {'publisher': 'Укажите издательство'}}})
                pages = mono.get('pages_count')
                if pages is not None and pages <= 0:
                    raise serializers.ValidationError({'publication': {'monograph': {'pages_count': 'Количество страниц должно быть положительным'}}})

        proj = attrs.get('project_participation')
        if proj:
            if not is_partial and not (proj.get('role') or '').strip():
                raise serializers.ValidationError({'project_participation': {'role': 'Укажите роль в проекте'}})
            start = proj.get('start_date')
            end = proj.get('end_date')
            if start and end and end < start:
                raise serializers.ValidationError({'project_participation': 'Дата окончания раньше даты начала'})
            if proj.get('budget') is not None and proj['budget'] < 0:
                raise serializers.ValidationError({'project_participation': {'budget': 'Бюджет не может быть отрицательным'}})

        diss = attrs.get('dissertation')
        if diss:
            if not is_partial and not (diss.get('stage') or '').strip():
                raise serializers.ValidationError({'dissertation': {'stage': 'Укажите этап диссертации'}})
            d_date = diss.get('defense_date')
            if d_date and d_date > date.today():
                raise serializers.ValidationError({'dissertation': {'defense_date': 'Дата защиты не может быть в будущем'}})

        soft = attrs.get('software')
        if soft and not is_partial and not (soft.get('version') or '').strip():
            raise serializers.ValidationError({'software': {'version': 'Укажите версию ПО'}})

        return attrs

    def create(self, validated_data):
        pub_data = validated_data.pop('publication', None)
        diss_data = validated_data.pop('dissertation', None)
        proj_data = validated_data.pop('project_participation', None)
        soft_data = validated_data.pop('software', None)

        work = ScientificWork.objects.create(**validated_data)

        if pub_data:
            article_data = pub_data.pop('article', None)
            monograph_data = pub_data.pop('monograph', None)
            pub = Publication.objects.create(scientific_work=work, **pub_data)
            if article_data:
                article = Article.objects.create(publication=pub, **article_data)
                # Учёт квартиля журнала в баллах
                if article.quartile:
                    work.points = compute_scientific_work_points(
                        work.points, quartile=article.quartile
                    )
                    work.save(update_fields=['points'])
            if monograph_data:
                Monograph.objects.create(publication=pub, **monograph_data)
        if diss_data:
            Dissertation.objects.create(scientific_work=work, **diss_data)
        if proj_data:
            ProjectParticipation.objects.create(scientific_work=work, **proj_data)
        if soft_data:
            Software.objects.create(scientific_work=work, **soft_data)

        return work

    def update(self, instance, validated_data):
        pub_data = validated_data.pop('publication', None)
        diss_data = validated_data.pop('dissertation', None)
        proj_data = validated_data.pop('project_participation', None)
        soft_data = validated_data.pop('software', None)

        # Update top-level scientific work fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update / replace nested subtype data
        if pub_data is not None:
            article_data = pub_data.pop('article', None)
            monograph_data = pub_data.pop('monograph', None)
            pub = getattr(instance, 'publication', None)
            if pub is None:
                pub = Publication.objects.create(scientific_work=instance, **pub_data)
            else:
                for attr, value in pub_data.items():
                    setattr(pub, attr, value)
                pub.save()
            if article_data is not None:
                article = getattr(pub, 'article', None)
                if article is None:
                    article = Article.objects.create(publication=pub, **article_data)
                    # Только для нового article-подтипа применяем множитель квартиля
                    if article.quartile:
                        instance.points = compute_scientific_work_points(
                            instance.points, quartile=article.quartile
                        )
                        instance.save(update_fields=['points'])
                else:
                    for attr, value in article_data.items():
                        setattr(article, attr, value)
                    article.save()
            if monograph_data is not None:
                monograph = getattr(pub, 'monograph', None)
                if monograph is None:
                    Monograph.objects.create(publication=pub, **monograph_data)
                else:
                    for attr, value in monograph_data.items():
                        setattr(monograph, attr, value)
                    monograph.save()

        if diss_data is not None:
            diss = getattr(instance, 'dissertation', None)
            if diss is None:
                Dissertation.objects.create(scientific_work=instance, **diss_data)
            else:
                for attr, value in diss_data.items():
                    setattr(diss, attr, value)
                diss.save()

        if proj_data is not None:
            proj = getattr(instance, 'project_participation', None)
            if proj is None:
                ProjectParticipation.objects.create(scientific_work=instance, **proj_data)
            else:
                for attr, value in proj_data.items():
                    setattr(proj, attr, value)
                proj.save()

        if soft_data is not None:
            soft = getattr(instance, 'software', None)
            if soft is None:
                Software.objects.create(scientific_work=instance, **soft_data)
            else:
                for attr, value in soft_data.items():
                    setattr(soft, attr, value)
                soft.save()

        return instance


# ============================================================
#  Организационные работы
# ============================================================

class OrganizationalWorkSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    attachments = serializers.SerializerMethodField()

    class Meta:
        model = OrganizationalWork
        fields = '__all__'
        read_only_fields = ['verified', 'verification_request', 'created_at']

    def get_attachments(self, obj):
        return AttachmentSerializer(obj.attachments.all(), many=True, context=self.context).data

    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('Название не может быть пустым')
        return value.strip()

    def validate_points(self, value):
        if value is None or value < 0:
            raise serializers.ValidationError('Баллы не могут быть отрицательными')
        if value > 1000:
            raise serializers.ValidationError('Значение баллов слишком велико')
        return value

    def validate_event_date(self, value):
        if value is None:
            raise serializers.ValidationError('Дата мероприятия обязательна')
        if value > date.today():
            raise serializers.ValidationError('Дата мероприятия не может быть в будущем')
        return value

    def validate_participants_count(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError('Количество участников не может быть отрицательным')
        return value


# ============================================================
#  Технические работы
# ============================================================

class TechnicalWorkSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    attachments = serializers.SerializerMethodField()

    class Meta:
        model = TechnicalWork
        fields = '__all__'
        read_only_fields = ['verified', 'verification_request', 'created_at']

    def get_attachments(self, obj):
        return AttachmentSerializer(obj.attachments.all(), many=True, context=self.context).data

    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('Название не может быть пустым')
        return value.strip()

    def validate_points(self, value):
        if value is None or value < 0:
            raise serializers.ValidationError('Баллы не могут быть отрицательными')
        if value > 1000:
            raise serializers.ValidationError('Значение баллов слишком велико')
        return value

    def validate_work_date(self, value):
        if value is None:
            raise serializers.ValidationError('Дата работы обязательна')
        if value > date.today():
            raise serializers.ValidationError('Дата работы не может быть в будущем')
        return value


# ============================================================
#  KPI
# ============================================================

class KPIIndicatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = KPIIndicator
        fields = '__all__'


class KPIGroupSerializer(serializers.ModelSerializer):
    indicators = KPIIndicatorSerializer(many=True, read_only=True)

    class Meta:
        model = KPIGroup
        fields = '__all__'


class KPIGroupWeightSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source='kpi_group.name', read_only=True)

    class Meta:
        model = KPIGroupWeight
        fields = ['id', 'kpi_group', 'group_name', 'position_type', 'phd_year', 'weight']


class KPIResultSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)

    class Meta:
        model = KPIResult
        fields = '__all__'
        read_only_fields = ['created_at']


# ============================================================
#  Проекты
# ============================================================

class ProjectMemberSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)

    class Meta:
        model = ProjectMember
        fields = ['id', 'project', 'employee', 'employee_name', 'joined_at']
        read_only_fields = ['joined_at']


class ProjectListSerializer(serializers.ModelSerializer):
    creator_name = serializers.CharField(source='creator.full_name', read_only=True)
    members_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'budget',
            'start_date', 'end_date', 'completed_at',
            'creator', 'creator_name', 'members_count', 'created_at',
        ]
        read_only_fields = ['created_at', 'creator', 'completed_at']

    def get_members_count(self, obj):
        return obj.members.count()

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('Название проекта обязательно')
        if len(value.strip()) < 3:
            raise serializers.ValidationError('Название слишком короткое')
        return value.strip()

    def validate_budget(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError('Бюджет не может быть отрицательным')
        return value

    def validate(self, attrs):
        start = attrs.get('start_date')
        end = attrs.get('end_date')
        if start and end and end < start:
            raise serializers.ValidationError({'end_date': 'Дата окончания не может быть раньше даты начала'})
        return attrs


class ProjectDetailSerializer(serializers.ModelSerializer):
    creator_name = serializers.CharField(source='creator.full_name', read_only=True)
    members = ProjectMemberSerializer(many=True, read_only=True)
    tasks_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'budget',
            'start_date', 'end_date', 'completed_at',
            'creator', 'creator_name', 'members', 'tasks_count', 'created_at',
        ]
        read_only_fields = ['created_at', 'creator', 'completed_at']

    def get_tasks_count(self, obj):
        return obj.tasks.count()


# ============================================================
#  Задачи
# ============================================================

class AttachmentSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    uploaded_by_name = serializers.CharField(source='uploaded_by.full_name', read_only=True, default=None)

    class Meta:
        model = Attachment
        fields = [
            'id', 'file', 'url', 'original_name', 'size',
            'uploaded_at', 'uploaded_by', 'uploaded_by_name',
            'scientific_work', 'organizational_work', 'technical_work', 'task',
        ]
        read_only_fields = ['uploaded_at', 'uploaded_by', 'size', 'original_name']

    def get_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url if obj.file else None


class TaskSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.full_name', read_only=True, default=None)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['created_at', 'created_by']

    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('Название задачи обязательно')
        if len(value.strip()) < 3:
            raise serializers.ValidationError('Название слишком короткое')
        return value.strip()

    def validate_deadline(self, value):
        if value is None:
            raise serializers.ValidationError('Дедлайн обязателен')
        # При создании (нет instance) дедлайн должен быть сегодня или позже
        if self.instance is None and value < date.today():
            raise serializers.ValidationError('Дедлайн не может быть в прошлом')
        return value

    def validate_points(self, value):
        if value is None:
            return 0
        if value < 0:
            raise serializers.ValidationError('Баллы не могут быть отрицательными')
        if value > 1000:
            raise serializers.ValidationError('Значение баллов слишком велико')
        return value

    def validate(self, attrs):
        project = attrs.get('project') or (self.instance.project if self.instance else None)
        assigned = attrs.get('assigned_to')
        # Задача в проекте — исполнитель должен быть участником
        if project and assigned and not project.members.filter(employee=assigned).exists():
            raise serializers.ValidationError({
                'assigned_to': 'Исполнитель должен быть участником проекта',
            })
        # Дедлайн не должен выходить за срок проекта
        deadline = attrs.get('deadline')
        if project and deadline and project.end_date and deadline > project.end_date:
            raise serializers.ValidationError({
                'deadline': 'Дедлайн задачи не может быть позже даты окончания проекта',
            })

        # Свободные задачи: при создании должны быть заполнены KPI-поля и баллы
        if self.instance is None and project is None:
            kpi_group = attrs.get('kpi_group')
            work_type_key = attrs.get('work_type_key')
            points = attrs.get('points')
            if not kpi_group:
                raise serializers.ValidationError({
                    'kpi_group': 'Для свободной задачи укажите группу показателей',
                })
            if not work_type_key:
                raise serializers.ValidationError({
                    'work_type_key': 'Для свободной задачи укажите тип работы',
                })
            if not points or points <= 0:
                raise serializers.ValidationError({
                    'points': 'Для свободной задачи укажите баллы',
                })
        return attrs
