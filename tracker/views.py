from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import action
from tracker.models import Project
from tracker.serializers import (
    CreateProjectSerializer,
    LogTimeSerializer,
    ProjectSerializer,
    AssignEngineerSerializer,
)
from user.permissions import IsAdmin, IsProjectManager, IsEngineer
from user.models import User
from .task import send_profile_update_mail
from tracker.serializers import LogTimeSerializer, TimeEntrySerializerDetail
from tracker.models import TimeEntry
from django.utils import timezone
from rest_framework.parsers import MultiPartParser

class ProjectViewSet(
 viewsets.ModelViewSet
):
    serializer_class = ProjectSerializer
    permission_classes = [IsProjectManager | IsAdmin]
    queryset = Project.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateProjectSerializer
        return ProjectSerializer

    @action(
        methods=['POST'],
        detail=True,
        url_path='assign-engineer'
    )
    def assign_engineer(self, request):
        serializer = AssignEngineerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        project = self.get_object()
        user = User.objects.get(email=email)
        project.engineers.add(user)

        profile_completetion_url = f"https://base_url/auth//?update_profile={user.id}"

        email_data = {
                "email": user.email,
                "full_name": user.full_name or user.username,
                "link": profile_completetion_url,
                "project_name": project.name,
                "project_id": project.id,
          }
        send_profile_update_mail(email_data)

        return Response(
            data={
                "message": "Engineer assigned successfully",
                **ProjectSerializer(instance=project).data,
            },
            status=status.HTTP_200_OK,
        )

    @action(
        methods=['POST'],
        detail=True,
        url_path='log-time',
        serializer_class=LogTimeSerializer,
        permission_classes=[IsEngineer],
        parser_classes=[MultiPartParser],
    )
    def log_time(self, request, pk=None):
        project = self.get_object()
        user = request.user
        serializer = LogTimeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        time_spent = serializer.validated_data['time_spent']
        is_active = serializer.validated_data.get('is_active', True)

        time_entry, created = TimeEntry.objects.get_or_create(
            project=project,
            user=user,
            defaults={
                'time_spent': timezone.timedelta(minutes=int(time_spent)),
                'is_active': is_active,
            },
        )

        if not created:
            time_entry.time_spent += timezone.timedelta(minutes=int(time_spent))
            time_entry.is_active = is_active
            time_entry.save()

        return Response(
            data={
                "message": "Time logged successfully",
                **TimeEntrySerializerDetail(instance=time_entry).data,
            },
            status=status.HTTP_200_OK,
        )

    @action(
        methods=['GET'],
        detail=True,
        url_path='view-project-details-with-time-entries',
        permission_classes=[IsProjectManager | IsAdmin],
        serializer_class=TimeEntrySerializerDetail,
    )
    def view_project_details(self, request, pk=None):
        project = self.get_object()

        engineers = project.engineers.all()
        data = []
        for engineer in engineers:
            time_entry = TimeEntry.objects.filter(project=project, user=engineer)
            engineer_data=TimeEntrySerializerDetail(time_entry).data
            data.append(engineer_data)

        return Response(data, status=status.HTTP_200_OK)
