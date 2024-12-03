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
    queryset = (
        Project.objects.select_related('project_manager')
        .prefetch_related('engineers')
        .filter()
        .all()
    )

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateProjectSerializer
        return self.serializer_class

    @action(
        methods=['POST'],
        detail=True,
        url_path='assign-engineer',
        serializer_class=AssignEngineerSerializer,
    )
    def assign_engineer(self, request, pk=None):
        """Assign an engineer to a project"""
        serializer = AssignEngineerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        project = self.get_object()
        user = User.objects.get(email=email)
        project.engineers.add(user)

        profile_completetion_url = f"https://base_url/auth//?update_profile={user.id}"

        email_data = {
            "email": user.email,
            "fullname": user.fullname or user.username,
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
    )
    def log_time(self, request, pk=None):
        """Log time spent on a project by an engineer: time_spent in format( "00:30:00") HH:MM:SS"""
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
                'time_spent': time_spent,
                'is_active': is_active,
            },
        )

        if not created:
            time_entry.time_spent += time_spent
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
        """View project details with time entries"""
        project = self.get_object()

        engineers = project.engineers.all()
        json_objects = []
        for engineer in engineers:
            try:
                time_entry_instance = TimeEntry.objects.get(project=project, user=engineer)
                json_objects.append(TimeEntrySerializerDetail(instance=time_entry_instance).data)
            except TimeEntry.DoesNotExist:
                json_objects.append(
                    TimeEntrySerializerDetail(
                        instance=TimeEntry(
                            project=project,
                            user=engineer,
                            time_spent=timezone.timedelta(minutes=0),
                            is_active=False,
                        )
                    ).data
                )
        print(json_objects)
        return Response(
            data={
                "Project_name": project.name,
                "project_id": project.id,
                "time_entries_detials": json_objects,
            },
            status=status.HTTP_200_OK,
        )
