# jobs/urls.py
from django.urls import path
from .views import JobCreateView , JobUpdateDeleteView, JobCreateView , BrowseJobsView , MyPostedJobsView , JobDetailView

urlpatterns = [
    path('create/', JobCreateView.as_view(), name='job-create'),
    path('create/', JobCreateView.as_view(), name='job-create'),
    path('<int:id>/', JobUpdateDeleteView.as_view(), name='job-update-delete'),
    path('browse/', BrowseJobsView.as_view(), name='browse-jobs'),
    path('my-jobs/', MyPostedJobsView.as_view(), name='my-posted-jobs'),
    path('jobs/<int:id>/', JobDetailView.as_view(), name='job-detail'),
]
