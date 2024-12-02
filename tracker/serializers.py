from rest_framework import serializers

from user.models import User
from .models import Project, TimeEntry


class ProjectSerializer(serializers.ModelSerializer):
    project_manager_details = serializers.SerializerMethodField(read_only=True)
    engineers_details = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Project
        fields = "__all__"

    def get_project_manager_details(self, obj):
        return {
            "email": obj.project_manager.email,
            "fullname": obj.project_manager.fullname,
            "username": obj.project_manager.username,
            "role": obj.project_manager.role,
            "image": obj.project_manager.image,
        }

    def get_engineers_details(self, obj):
        return [
            {
                "email": engineer.email,
                "fullname": engineer.fullname,
                "username": engineer.username,
                "role": engineer.role,
                "image": engineer.image,
            }
            for engineer in obj.engineers.all()
        ]


class CreateProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        exclude = [
            'engineers',
        ]


class AssignEngineerSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist")
        return value


class TimeEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeEntry
        fields = ['id', 'project', 'user', 'time_spent', 'is_active']
        read_only_fields = ['id', 'is_active']
