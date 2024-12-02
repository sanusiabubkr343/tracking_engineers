from django.urls import path, include

from rest_framework import routers

from . import views

app_name = "tracker"
router = routers.DefaultRouter()

router.register("projects", viewset=views.ProjectViewSet)


urlpatterns = [
    path("", include(router.urls)),
]
