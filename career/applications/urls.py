from django.urls import path
from .views import ApplyJobView , TrackApplicationsView, JobApplicationsView , UpdateApplicationStatusView

urlpatterns = [
    path('apply/', ApplyJobView.as_view(), name='apply-job'),
    path('my-applications/', TrackApplicationsView.as_view(), name='track-applications'),
    path('jobs/<int:job_id>/applications/', JobApplicationsView.as_view(), name='job-applications'),
    path('applications/<int:pk>/status/', UpdateApplicationStatusView.as_view(), name='update-application-status'),
]
