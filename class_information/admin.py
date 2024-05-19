from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest

from academic_record.models import AcademicYear, Schedule
from base.admin import BaseAdmin
from base.models import User
from user_profile.models import Teacher
from registration.models import Registration
from .models import Subject, Department, Section, GradeEncode
from django.db.models import Q
from django import forms
from dal import autocomplete
from django.urls import path

class SubjectAdminForm(forms.ModelForm):

    class Meta:
        model = Subject
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        instance = getattr(self, 'instance', None)
        subjectcode = cleaned_data.get('code')
        written_work = cleaned_data.get("written_work")
        performance_task = cleaned_data.get("performance_task")
        quartery_assessment = cleaned_data.get("quartery_assessment")
        
        if instance and instance.pk:  # Check if instance exists and has a primary key
            if Subject.objects.filter(code=subjectcode).exclude(pk=instance.pk).exists():
                self.add_error('code', 'Subject Code already exists')
        else:
            if Subject.objects.filter(code=subjectcode).exists():
                self.add_error('code', 'Subject Code already exists')
                
        if written_work <= 1:
            self.add_error('written_work', "Written work must be greater than 1.")
        if performance_task <= 1:
            self.add_error('performance_task', "Performance task must be greater than 1.")
        if quartery_assessment <= 1:
            self.add_error('quartery_assessment', "Quarterly assessment must be greater than 1.")

        total = written_work + performance_task + quartery_assessment

        if total != 100:
            self.add_error('written_work', "The sum of the subject components must be 100.")
        if total != 100:
            self.add_error('performance_task',"The sum of the subject components must be 100.")
        if total != 100:
            self.add_error('quartery_assessment', "The sum of the subject components must be 100.")
        


        return cleaned_data
    
class SectionAdviserHeadChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f'{obj.last_name} - {obj.first_name}'

    def filter_queryset(self, value, queryset):
        if value:
            queryset = queryset.filter(Q(first_name__icontains=value) | Q(
                last_name__icontains=value))
        return queryset

class SectionAdminForm(forms.ModelForm):
    adviser = SectionAdviserHeadChoiceField(
        queryset=User.objects.all(),
        widget=autocomplete.ModelSelect2(
            url='teacher-autocomplete',
            attrs={
                'data-placeholder': 'Search for a teacher...',
                'data-minimum-input-length': 2,
            }
        ),
        required=False
    )
    class Meta:
        model = Section
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        instance = getattr(self, 'instance', None)
        section_name = cleaned_data.get('name')
        year_level = cleaned_data.get('year_level')
        adviser = cleaned_data.get('adviser')
        
        if instance and instance.pk:  # Check if instance exists and has a primary key
            if Section.objects.filter(name=section_name, year_level=year_level).exclude(pk=instance.pk).exists():
                self.add_error('name', 'A section with this name already exists in this year level')
            if Section.objects.filter(adviser=adviser).exclude(pk=instance.pk).exists():
                self.add_error('adviser', 'Adviser already exists')
        else:
            if Section.objects.filter(name=section_name, year_level=year_level).exists():
                self.add_error('name', 'A section with this name already exists in this year level')
            if Section.objects.filter(adviser=adviser).exists():
                self.add_error('adviser', 'Adviser already exists')

        return cleaned_data

@admin.register(GradeEncode)
class GradeEncodeAdminView(BaseAdmin):
    list_fields = ('grading_period', 'is_enable',)
    search_fields = ('grading_period',)
    list_filter = ['grading_period', 'is_enable']
    edit_fields = (
        ('Grade Encoding', {
            'fields': [
                'grading_period',
                'is_enable',
            ]
        }),
    )


class ScheduleTabularInline(admin.TabularInline):
    verbose_name = "Schedule"
    verbose_name_plural = "Schedules"
    model = Schedule
    fields = ('section',)
    readonly_fields = ('section',)

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        academic_years = AcademicYear.objects.all()
        qs = super(ScheduleTabularInline, self).get_queryset(request)
        if academic_years.exists():
            academic_year = academic_years.first()
            return qs.filter(academic_year=academic_year)

        return qs


@admin.register(Subject)
class SubjectAdminView(admin.ModelAdmin):
    # change_list_template = 'admin/class_information/subject/change_list.html'
    list_display = ['name', 'code', 'department', 'year_level']
    search_fields = ['name', 'year_level', 'code',]
    list_filter = ('name', 'year_level',)
    form = SubjectAdminForm
    inlines = [ScheduleTabularInline,]
    autocomplete_fields = ['department',]


class TeachersTabularInline(admin.TabularInline):
    verbose_name = "Teacher"
    verbose_name_plural = "Teachers"
    model = Teacher
    fields = ('user', 'department',)
    readonly_fields = ('user',)

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        departments = Department.objects.all()
        qs = super(TeachersTabularInline, self).get_queryset(request)
        if departments.exists():
            return qs.filter(department__in=departments)

        return qs

class TeacherDepartmentHeadChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f'{obj.last_name} - {obj.first_name}'

    def filter_queryset(self, value, queryset):
        if value:
            queryset = queryset.filter(Q(first_name__icontains=value) | Q(
                last_name__icontains=value))
        return queryset


class DepartmentAdminForm(forms.ModelForm):
    department_head = TeacherDepartmentHeadChoiceField(
        queryset=User.objects.all(),
        widget=autocomplete.ModelSelect2(
            url='teacher-autocomplete',
            attrs={
                'data-placeholder': 'Search for a teacher...',
                'data-minimum-input-length': 2,
            }
        ),
        required=False
    )

    class Meta:
        model = Department
        fields = '__all__'
        
    def clean(self):
        cleaned_data = super().clean()
        instance = getattr(self, 'instance', None)
        departmentcode = cleaned_data.get('code')
        department_head = cleaned_data.get('department_head')
        
        if instance and instance.pk:  # Check if instance exists and has a primary key
            if Department.objects.filter(code=departmentcode).exclude(pk=instance.pk).exists():
                self.add_error('code', 'Department Code already exists')
            if Department.objects.filter(department_head=department_head).exclude(pk=instance.pk).exists():
                self.add_error('department_head', 'Department Head already exists')
        else:
            if Department.objects.filter(code=departmentcode).exists():
                self.add_error('code', 'Department Code already exists')
            if Department.objects.filter(department_head=department_head).exists():
                self.add_error('department_head', 'Department Head already exists')

        return cleaned_data


from django.contrib import admin
from django.http import HttpRequest
from django.forms.models import BaseInlineFormSet
from django.db.models import QuerySet

class ReadOnlyInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.can_add = True  # Allow adding new objects

class SubjectsTabularInline(admin.TabularInline):
    verbose_name = "Subject"
    verbose_name_plural = "Subjects"
    model = Subject
    fields = ('name', 'code', 'year_level', 'written_work', 'performance_task', 'quartery_assessment',)
    show_change_link = True  # Corrected syntax for show_change_link
    formset = ReadOnlyInlineFormSet
    extra = 1
    classes = ['collapse']

    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if obj:
            formset.can_add = True
        return formset

    def has_add_permission(self, request: HttpRequest, obj=None) -> bool:
        return True  # Allow adding new subjects

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        departments = Department.objects.all()
        qs = super().get_queryset(request)
        if departments.exists():
            return qs.filter(department__in=departments)
        return qs

@admin.register(Department)
class DepartmentAdminView(admin.ModelAdmin):
    list_display = ['code', 'name', 'department_head']
    search_fields = ['code', 'department_head__user__first_name', 'department_head__user__last_name']
    list_filter = ('code',)
    inlines = [SubjectsTabularInline,]
    form = DepartmentAdminForm

    def get_formsets_with_inlines(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            if obj is None and isinstance(inline, SubjectsTabularInline):
                continue  # Skip this inline when adding new object
            yield inline.get_formset(request, obj), inline

    def get_inline_instances(self, request, obj=None):
        inline_instances = []
        for inline_class in self.inlines:
            inline = inline_class(self.model, self.admin_site)
            if obj:
                inline.has_change_permission = lambda request, obj=None: False  # Disable editing for existing objects
            inline_instances.append(inline)
        return inline_instances

    class Media:
        css = {
            'all': ('https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.13/css/select2.min.css',)
        }
        js = (
            'https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.13/js/select2.full.min.js',)


class RegistrationTabularInline(admin.TabularInline):
    verbose_name = "Student"
    verbose_name_plural = "Students"
    model = Registration
    fields = ('student', 'academic_year')
    readonly_fields = ('student', 'academic_year')

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        academic_years = AcademicYear.objects.all()
        qs = super(RegistrationTabularInline, self).get_queryset(request)
        if academic_years.exists():
            academic_year = academic_years.first()
            return qs.filter(academic_year=academic_year)

        return qs


class SubjectTabularInline(admin.TabularInline):
    verbose_name = "Subject"
    verbose_name_plural = "Subjects"
    model = Schedule
    fields = ('subject', 'academic_year',)
    readonly_fields = ('subject', 'academic_year',)

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        academic_years = AcademicYear.objects.all()
        qs = super(SubjectTabularInline, self).get_queryset(request)
        if academic_years.exists():
            academic_year = academic_years.first()
            return qs.filter(academic_year=academic_year)

        return qs

@admin.register(Section)
class SectionAdminView(admin.ModelAdmin):
    list_display = ['name', 'year_level']
    search_fields = ['name', 'year_level']
    list_filter = ('name', 'year_level')
    form = SectionAdminForm
    inlines = [RegistrationTabularInline,]
    edit_fields = (
        ('Section Information', {
            'fields': [
                'name',
                'year_level',
            ]
        }),
    )
    form = SectionAdminForm
    class Media:
        css = {
            'all': ('https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.13/css/select2.min.css',)
        }
        js = (
            'https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.13/js/select2.full.min.js',)
