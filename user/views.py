# create a model view sets for the user model

from rest_framework import viewsets, status
from rest_framework.decorators import action

from user.permissions import IsAdmin, IsProjectManager
from user.tokens import create_jwt_pair_for_user
from .models import User
from .serializers import (
    UpdateUserRoleSerializer,
    UpdateUserSerializer,
    UserSerializer,
    LoginUserSerializer,
)
from rest_framework import mixins
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

class UserViewSets(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['role']
    search_fields = ['email', 'username', 'fullname']

    def get_serializer_class(self):
        if self.action == 'register_user':
            return UserSerializer
        if self.action in ['update', 'partial_update']:
            self.parser_classes = [MultiPartParser]
            return UpdateUserSerializer
        return self.serializer_class

    def get_permissions(self):
        permission_classes = self.permission_classes
        if self.action in ['register_user', 'login_user']:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    @action(
        methods=['POST'],
        detail=False,
        url_path='register-user',
        serializer_class=UserSerializer,
        parser_classes=[MultiPartParser],
    )
    def register_user(self, request, pk=None):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['POST'],
        detail=False,
        serializer_class=LoginUserSerializer,
        url_path='login-user',
    )
    def login_user(self, request, pk=None):
        serializer = LoginUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        user = authenticate(email=email, password=password)
        if user is not None:
            tokens = create_jwt_pair_for_user(user)

            response = {
                "message": "Login Successful",
                "tokens": tokens,
                **UserSerializer(instance=user).data,
            }
            return Response(data=response, status=status.HTTP_200_OK)

        else:
            return Response(
                data={"message": "Invalid email or password"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    @action(
        methods=['POST'],
        detail=True,
        serializer_class=UpdateUserRoleSerializer,
        url_path='update-user-role',
        permission_classes=[IsAdmin],
    )
    def update_user_role(self, request, pk=None):
        """update user role"""
        user = self.get_object()
        serializer = UpdateUserRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user.role = serializer.validated_data['role']
        user.save()
        return Response(data=UserSerializer(instance=user).data, status=status.HTTP_200_OK)
