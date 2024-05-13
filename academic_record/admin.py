from django.contrib import admin
from django import forms

from base.admin import BaseAdmin
from class_information.models import Section, Subject
from user_profile.models import Student, Teacher

from .models import DAYS_OF_THE_WEEK, Assessment, Attendance, Schedule, StudentAssessment, AcademicYear

class AcademicYearForm(forms.ModelForm):

    class Meta:
        model = AcademicYear
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if name and start_date and end_date:
            # Check if an AcademicYear with the same name and date range already exists
            if AcademicYear.objects.filter(
                name=name,
                start_date=start_date,
                end_date=end_date
            ).exclude(pk=self.instance.pk if self.instance else None).exists():
                raise forms.ValidationError("An Academic Year with the same name and date range already exists.")

        return cleaned_data

@admin.register(AcademicYear)
class AcademicYearView(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date']
    search_fields = ['name', 'start_date', 'end_date']
    list_filter = ('name',)
    form = AcademicYearForm
    edit_fields = (
        ('Department', {
            'fields': [
                'code',
                'name',
            ]
        }),
    )

class ScheduleAdminForm(forms.ModelForm):
    day = forms.ChoiceField(choices=DAYS_OF_THE_WEEK)  
    class Meta:
        model = Schedule
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        teacher = cleaned_data.get('teacher')
        day = cleaned_data.get('day')
        time_start = cleaned_data.get('time_start')
        time_end = cleaned_data.get('time_end')

        # Ensure `time_end` is not less than `time_start`
        if time_start and time_end:
            if time_end < time_start:
                self.add_error('time_end', 'End time cannot be earlier than start time.')
                raise forms.ValidationError('End time must be after start time.')

        # Check for schedule conflicts with other schedules
        if teacher and day and time_start and time_end:
            overlapping_schedules = Schedule.objects.filter(
                teacher=teacher,
                day=day,
                time_start__lte=time_end,
                time_end__gte=time_start
            )

            # Exclude the current instance from the check if it exists
            if self.instance and self.instance.pk:
                overlapping_schedules = overlapping_schedules.exclude(pk=self.instance.pk)

            if overlapping_schedules.exists():
                self.add_error('time_start', 'Schedule conflict detected.')
                raise forms.ValidationError('This teacher has a conflicting schedule at this time and day.')

        return cleaned_data

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'day', 'time_start', 'time_end',
                    'section', 'subject']
    search_fields = ('teacher__user__first_name',
                     'teacher__user__last_name', 'section__name', 'subject__name')
    form = ScheduleAdminForm
    list_filter = ('teacher__user__teacher', 'section__name', 'subject', )
    formfield_querysets = {
        'subject': lambda: Subject.objects.all(),
        'teacher': lambda: Teacher.objects.all(),
        'section': lambda: Section.objects.all(),
        'academic_year': lambda: AcademicYear.objects.all(),
    }
    autocomplete_fields = ['subject', 'teacher', 'section', 'academic_year']
    edit_fields = (
        ('Schedule Information', {
            'fields': [
                'academic_year',
                'subject',
                'teacher',
                'section',
                'day',
                'is_view_grade',
                'time_start',
                'time_end'
            ]
        }),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "teacher":
            # Get the selected subject ID from the form data
            subject_id = request.GET.get('subject', None)
            if subject_id:
                try:
                    # Fetch the subject instance
                    subject = Subject.objects.get(pk=subject_id)
                    # Filter the queryset of teachers based on the subject's department
                    kwargs["queryset"] = subject.department.teacher_set.all()
                except Subject.DoesNotExist:
                    pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def add_view(self, request, *args, **kwargs):
        # This method is called when the admin page for adding a new Schedule is requested
        # We include the subject field in the form to ensure its value is available in the form data
        self.fields = ('academic_year', 'subject', 'teacher', 'section', 'is_view_grade',
                       'day', 'time_start', 'time_end')
        return super().add_view(request, *args, **kwargs)


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'schedule',  'is_present', 'attendance_date']
    search_fields = ['student__user__last_name', 'student__user__first_name',]
    list_filter = ('student', 'schedule__day',)
    formfield_querysets = {
        'student': lambda: Student.objects.all(),
        'schedule': lambda: Schedule.objects.all(),
    }
    autocomplete_fields = ['student', 'schedule',]
    edit_fields = (
        ('Attendance', {
            'fields': [
                'schedule',
                'student',
                'time_in',
                'time_out',
                'is_present',
                'attendance_date',
            ]
        }),
    )


class StudentAssessmentTabularInLine(admin.TabularInline):
    model = StudentAssessment
    autocomplete_fields = ['student', ]
    fields = ('assessment', 'student', 'obtained_marks')


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_fields = ('name', 'teacher', 'subject', 'academic_year')
    search_fields = ('name', 'subject__name',)
    ordering = ('name',)
    list_filter = ('assessment_type', 'subject', 'teacher__user__teacher')
    autocomplete_fields = ['subject', 'teacher',]
    inlines = [StudentAssessmentTabularInLine,]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "academic_year":
            kwargs["queryset"] = AcademicYear.get_academic_years()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:  # Check if the user is an admin
            return qs  # Return the default queryset
        else:
            user = request.user
            teachers = Teacher.objects.filter(user=user)
            if teachers.exists():
                teacher = teachers.first()
                # Apply filtering based on your condition
                return qs.filter(teacher=teacher)
        return qs

    def get_list_filter(self, request):
        default_list_filter = ('assessment_type', 'subject', 'teacher__user__teacher')
        qs = super().get_queryset(request)
        if request.user.is_superuser:  # Check if the user is an admin
            return default_list_filter
        else:
            user = request.user
            teachers = Teacher.objects.filter(user=user)
            if teachers.exists():
                return ('assessment_type', 'subject',)
        return default_list_filter
    
    def save_model(self, request, obj, form, change):
        if request.user.is_staff:
            user = request.user
            teachers = Teacher.objects.filter(user=user)
            if teachers.exists():
                teacher = teachers.first()
                obj.teacher = teacher
        obj.save()
    
    def get_exclude(self, request, obj=None):
        excludes = super().get_exclude(request, obj=obj) or ()
        if request.user.is_staff:
            excludes += ('teacher',)
        return excludes


@admin.register(StudentAssessment)
class StudentAssessmentAdmin(admin.ModelAdmin):
    search_fields = ['assessment__name',
                     'student__user__last_name', 'student__user__first_name',]
    list_display = ['assessment', 'student', 'obtained_marks']
    list_filter = ['assessment', 'student',]
    autocomplete_fields = ['student', 'assessment']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:  # Check if the user is an admin
            return qs  # Return the default queryset
        else:
            user = request.user
            teachers = Teacher.objects.filter(user=user)
            if teachers.exists():
                teacher = teachers.first()
                # Apply filtering based on your condition
                return qs.filter(assessment__teacher=teacher)
        return qs

