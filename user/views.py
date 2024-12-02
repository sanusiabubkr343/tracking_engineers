# create a model view sets for the user model

from rest_framework import viewsets, status
from rest_framework.decorators import action

from user.permissions import IsAdmin, IsProjectManager
from user.tokens import create_jwt_pair_for_user
from .models import User
from .serializers import UserSerializer, LoginUserSerializer
from rest_framework import mixins
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from django.contrib.auth import authenticate


class UserViewSets(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    queryset = User.objects.all()

    @action(
        methods=['POST'],
        detail=False,
        url_path='register-user',
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
