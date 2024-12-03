from rest_framework import serializers

from user.models import User
from .models import Project, TimeEntry


class ProjectSerializer(serializers.ModelSerializer):
    project_manager_details = serializers.SerializerMethodField(read_only=True)
    engineers_details = serializers.SerializerMethodField(
        read_only=True, method_name='get_engineers_details'
    )

    class Meta:
        model = Project
        fields = "__all__"

    def get_project_manager_details(self, obj):
        return {
            "email": obj.project_manager.email,
            "fullname": obj.project_manager.fullname,
            "username": obj.project_manager.username,
            "role": obj.project_manager.role,
            "image": obj.project_manager.image.url if obj.project_manager.image else None,
        }

    def get_engineers_details(self, obj):
        if obj.engineers.all().count() == 0:
            return []
        return [
            {
                "email": engineer.email,
                "fullname": engineer.fullname,
                "username": engineer.username,
                "role": engineer.role,
                "image": engineer.image.url if engineer.image else None,
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
    time_spent = serializers.DurationField()
    class Meta:
        model = TimeEntry
        fields = ['time_spent', 'is_active']

class TimeEntrySerializerDetail(serializers.ModelSerializer):
    engineers_engaged = serializers.SerializerMethodField(
        read_only=True, method_name='get_user_details'
    )

    class Meta:
        model = TimeEntry
        fields = "__all__"

    def get_user_details(self, obj):

        if not obj.user:
            return None
        return {
            "email": obj.user.email,
            "fullname": obj.user.fullname,
            "username": obj.user.username,
            "role": obj.user.role,
            "image": obj.user.image.url if obj.user.image else None,
        }
