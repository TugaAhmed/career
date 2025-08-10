# jobs/views.py
from rest_framework import viewsets, filters, status , permissions , generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Job
from .serializers import  JobListSerializer , JobDetailSerializer , JobUpdateSerializer
from users.permissions import IsCompany
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import RetrieveUpdateDestroyAPIView

from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from .serializers import JobCreateSerializer , CompanyJobListSerializer
from django.db.models import Count


class IsCompanyUser:
    """Custom permission: user must have role 'company'"""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'company'


class IsAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

class JobCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Check role
        if request.user.role != 'company':
            return Response({
                "success": False,
                "message": "Only companies can create jobs",
                "object": None,
                "errors": ["Permission denied"]
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = JobCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Save job with current user as creator
            job = serializer.save(created_by=request.user)
            return Response({
                "success": True,
                "message": "Job created successfully",
                "object": {
                    "id": job.id,
                    "title": job.title,
                    "description": job.description,
                    "location": job.location,
                    "status": job.status,
                    "created_by": job.created_by.id,
                    "created_at": job.created_at,
                },
                "errors": None
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "success": False,
                "message": "Invalid data",
                "object": None,
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        

class JobUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Job.objects.all()
    serializer_class = JobUpdateSerializer
    lookup_field = 'id'  # or 'pk'

    def get_object(self):
        job = super().get_object()
        # Only allow if current user is the creator and role is company
        if self.request.user.role != 'company' or job.created_by != self.request.user:
            return None
        return job

    def retrieve(self, request, *args, **kwargs):
        job = self.get_object()
        if not job:
            return Response({
                "success": False,
                "message": "Unauthorized access",
                "object": None,
                "errors": ["You do not own this job or lack permissions."]
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(job)
        return Response({
            "success": True,
            "message": "Job retrieved successfully",
            "object": serializer.data,
            "errors": None
        })

    def update(self, request, *args, **kwargs):
        job = self.get_object()
        if not job:
            return Response({
                "success": False,
                "message": "Unauthorized access",
                "object": None,
                "errors": ["You do not own this job or lack permissions."]
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(job, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Job updated successfully",
                "object": serializer.data,
                "errors": None
            })
        else:
            return Response({
                "success": False,
                "message": "Invalid data",
                "object": None,
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        job = self.get_object()
        if not job:
            return Response({
                "success": False,
                "message": "Unauthorized access",
                "object": None,
                "errors": ["You do not own this job or lack permissions."]
            }, status=status.HTTP_403_FORBIDDEN)

        job.delete()
        return Response({
            "success": True,
            "message": "Job deleted successfully",
            "object": None,
            "errors": None
        }, status=status.HTTP_200_OK)


class JobPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class BrowseJobsView(generics.ListAPIView):
    queryset = Job.objects.filter(status='Open')
    serializer_class = JobListSerializer
    permission_classes = [permissions.IsAuthenticated]  # all authenticated users allowed
    filter_backends = [DjangoFilterBackend]
    pagination_class = JobPagination

    filterset_fields = {
        'title': ['icontains'],
        'location': ['icontains'],
        'created_by__name': ['icontains'],  # company name filter (case-insensitive)
    }



class MyPostedJobsView(generics.ListAPIView):
    permission_classes = [IsCompany]
    serializer_class = CompanyJobListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']  # Filter by JobStatus

    def get_queryset(self):
        # Get jobs created by current user, annotate with count of applications
        return Job.objects.filter(created_by=self.request.user) \
                          .annotate(num_applications=Count('application'))

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                "success": True,
                "message": "Jobs retrieved successfully",
                "object": serializer.data,
                "page_number": request.query_params.get('page', 1),
                "page_size": self.paginator.page_size,
                "total_size": self.paginator.page.paginator.count,
                "errors": None
            })

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "message": "Jobs retrieved successfully",
            "object": serializer.data,
            "page_number": 1,
            "page_size": len(serializer.data),
            "total_size": len(serializer.data),
            "errors": None
        })
    

class JobDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Job.objects.all()
    serializer_class = JobDetailSerializer
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        try:
            job = self.get_object()
            serializer = self.get_serializer(job)
            return Response({
                "success": True,
                "message": "Job details retrieved successfully.",
                "object": serializer.data,
                "errors": None
            })
        except:
            return Response({
                "success": False,
                "message": "Job not found.",
                "object": None,
                "errors": ["Job with the given ID does not exist."]
            }, status=status.HTTP_404_NOT_FOUND)