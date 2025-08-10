# job_portal/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from jobs.views import JobViewSet

router = routers.DefaultRouter()
router.register(r'jobs', JobViewSet, basename='jobs')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/', include('users.urls')),
    path('api/', include('applications.urls')),

    path('api/users/', include('users.urls')),
    path('api/jobs/', include('jobs.urls')),
    path('api/applications/', include('applications.urls')),

]
