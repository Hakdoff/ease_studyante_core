from datetime import datetime, timedelta

from class_information.models import Section
from registration.models import Registration
from .models import AcademicYear, Attendance, Schedule


def perform_end_of_day_tasks():
    current_academic_year = AcademicYear.get_current_academic_year()
    sections = Section.objects.all()

    # perform student absent
    if current_academic_year:
        current_date = datetime.now()
        schedules = Schedule.objects.filter(
            section__in=sections, academic_year=current_academic_year)
        registered_students = Registration.objects.filter(
            academic_year=current_academic_year)
        if schedules.exists():
            for registered_student in registered_students:
                for schedule in schedules:
                    # validate student if he/she already have attendance
                    attendances = Attendance.objects.filter(
                        student__pk=registered_student.student.pk, time_in__date=current_date, schedule=schedule)
                    if not attendances.exists():
                        # perform creation of student absent
                        Attendance.objects.create(
                            student=registered_student.student, schedule=schedule, is_present=False, time_in=None)
