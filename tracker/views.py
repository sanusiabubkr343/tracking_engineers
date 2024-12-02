from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import action
from tracker.models import Project
from tracker.serializers import CreateProjectSerializer, ProjectSerializer, AssignEngineerSerializer
from user.permissions import IsAdmin, IsProjectManager
from user.models import User
from .task import send_profile_update_mail
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


        return Response(data={"message":"Engineer assigned successfully",**ProjectSerializer(instance=project).data}, status=status.HTTP_200_OK,)
