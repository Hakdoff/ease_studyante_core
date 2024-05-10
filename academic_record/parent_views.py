
from rest_framework import generics, permissions, response, status, exceptions

from core.paginate import ExtraSmallResultsSetPagination
from .serializers import ParentStudentListSerializers
from .models import Schedule, AcademicYear
from registration.models import Registration


class ParentStudentListView(generics.RetrieveAPIView):
    serializer_class = ParentStudentListSerializers
    queryset = Schedule.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ExtraSmallResultsSetPagination

    def get_queryset(self):
        current_academic_year = AcademicYear.get_current_academic_year()

        if current_academic_year:
            user = self.request.user
            register_users = Registration.objects.filter(
                academic_year=current_academic_year, student__user__pk=user.pk)

            if register_users.exists():
                # check the user wether is register to current academic or not
                register_user = register_users.first()
                return Schedule.objects.filter(academic_year=current_academic_year, section__pk=register_user.section.pk).order_by('time_start')

        return []
