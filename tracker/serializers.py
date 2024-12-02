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





class LogTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeEntry
        fields = ['time_spent', 'is_active']

class TimeEntrySerializerDetail(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name',read_only=True)
    user_details = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TimeEntry
        fields = "__all__"

    def get_user_details(self, obj):
        return {
            "email": obj.user.email,
            "fullname": obj.user.fullname,
            "username": obj.user.username,
            "role": obj.user.role,
            "image": obj.user.image,
        }
