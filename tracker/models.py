from django.contrib.auth.models import AbstractUser
from django.db import models
from user.models import User
from time_tracking.models import AuditableModel


class Project(AuditableModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    project_manager = models.ForeignKey(User, related_name="projects", on_delete=models.CASCADE)
    engineers = models.ManyToManyField(User, related_name="assigned_projects")

    class Meta:
        ordering = ("-created_at",)


class TimeEntry(AuditableModel):
    project = models.ForeignKey(Project, related_name="time_entries", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="time_entries", on_delete=models.CASCADE)
    time_spent = models.DurationField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("-created_at",)
