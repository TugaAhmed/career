from rest_framework import generics, permissions, status , filters
from rest_framework.response import Response
from .models import Application, Job
from .serializers import ApplicationSerializer , ApplicationListSerializer , ApplicationStatusUpdateSerializer
from django.utils import timezone
from django.core.mail import send_mail
from rest_framework.parsers import MultiPartParser, FormParser
import cloudinary.uploader
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from django.core.exceptions import PermissionDenied
from users.permissions import IsCompany 
from rest_framework.permissions import IsAuthenticated

class IsApplicant(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'applicant'

class IsCompanyUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "company"
    
    
class ApplyJobView(generics.CreateAPIView):
    permission_classes = [IsApplicant]
    serializer_class = ApplicationSerializer
    parser_classes = [MultiPartParser, FormParser]  # For file upload

    def post(self, request, *args, **kwargs):
        user = request.user
        job_id = request.data.get('job_id')
        cover_letter = request.data.get('cover_letter', '')
        resume_file = request.FILES.get('resume')

        # Validate job existence
        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            return Response({
                "success": False,
                "message": "Job not found.",
                "object": None,
                "errors": ["Invalid job_id"]
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if user already applied
        if Application.objects.filter(applicant=user, job=job).exists():
            return Response({
                "success": False,
                "message": "You have already applied for this job.",
                "object": None,
                "errors": ["Duplicate application"]
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate resume file type
        if not resume_file:
            return Response({
                "success": False,
                "message": "Resume file is required.",
                "object": None,
                "errors": ["Resume file missing"]
            }, status=status.HTTP_400_BAD_REQUEST)

        valid_extensions = ['pdf', 'docx']
        ext = resume_file.name.split('.')[-1].lower()
        if ext not in valid_extensions:
            return Response({
                "success": False,
                "message": "Unsupported resume file format. Only PDF and DOCX allowed.",
                "object": None,
                "errors": ["Invalid file format"]
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate cover letter length
        if len(cover_letter) > 200:
            return Response({
                "success": False,
                "message": "Cover letter must be under 200 characters.",
                "object": None,
                "errors": ["Cover letter too long"]
            }, status=status.HTTP_400_BAD_REQUEST)

        # Upload resume to Cloudinary
        try:
            upload_result = cloudinary.uploader.upload(resume_file, resource_type="auto")
            resume_url = upload_result.get('secure_url')
        except Exception as e:
            return Response({
                "success": False,
                "message": "Failed to upload resume.",
                "object": None,
                "errors": [str(e)]
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Create application
        application = Application.objects.create(
            applicant=user,
            job=job,
            resume_link=resume_url,
            cover_letter=cover_letter,
            status="Applied",
            applied_at=timezone.now()
        )

        # Send notification email to company
        send_mail(
            subject="New Job Application",
            message=f"Applicant {user.name} has applied to your job '{job.title}'.",
            from_email="no-reply@example.com",
            recipient_list=[job.created_by.email],
            fail_silently=True
        )

        serializer = ApplicationSerializer(application)
        return Response({
            "success": True,
            "message": "Application submitted successfully.",
            "object": serializer.data,
            "errors": None
        }, status=status.HTTP_201_CREATED)



class TrackApplicationsView(generics.ListAPIView):
    permission_classes = [IsApplicant]
    serializer_class = ApplicationListSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    
    # Define filter fields for DjangoFilterBackend
    filterset_fields = {
        'job__created_by__name': ['icontains'],  # company name filter
        'job__status': ['exact'],                # job status filter (Closed, Open)
        'status': ['in'],                        # application status filter (Applied, Interview, etc.)
    }

    # Define ordering fields
    ordering_fields = ['applied_at', 'job__created_by__name', 'status', 'job__title']
    ordering = ['-applied_at']  # default ordering desc by applied_at

    def get_queryset(self):
        # Filter applications to current user only
        return Application.objects.filter(applicant=self.request.user).select_related('job', 'job__created_by')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                "success": True,
                "message": "Applications retrieved successfully",
                "object": serializer.data,
                "page_number": request.query_params.get('page', 1),
                "page_size": self.paginator.page_size,
                "total_size": self.paginator.page.paginator.count,
                "errors": None
            })

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "message": "Applications retrieved successfully",
            "object": serializer.data,
            "page_number": 1,
            "page_size": len(serializer.data),
            "total_size": len(serializer.data),
            "errors": None
        })


class JobApplicationsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class JobApplicationsView(generics.ListAPIView):
    permission_classes = [IsCompanyUser]
    serializer_class = ApplicationListSerializer
    pagination_class = JobApplicationsPagination

    def get_queryset(self):
        job_id = self.kwargs['job_id']
        user = self.request.user

        # Check job ownership
        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            return Application.objects.none()  # No applications, job does not exist

        if job.created_by != user:
            raise PermissionDenied("Unauthorized access")

        queryset = Application.objects.filter(job=job)

        # Filter by status if provided
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status__iexact=status_filter)

        return queryset

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
        except PermissionDenied:
            return Response({
                "success": False,
                "message": "Unauthorized access",
                "object": None,
                "errors": ["You do not have permission to view applications for this job."]
            }, status=status.HTTP_403_FORBIDDEN)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                "success": True,
                "message": "Applications retrieved successfully.",
                "object": serializer.data,
                "page_number": request.query_params.get('page', 1),
                "page_size": self.paginator.page_size,
                "total_size": queryset.count(),
                "errors": None
            })

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "message": "Applications retrieved successfully.",
            "object": serializer.data,
            "errors": None
        })
    


class UpdateApplicationStatusView(generics.UpdateAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationStatusUpdateSerializer
    permission_classes = [IsAuthenticated, IsCompany]  # only companies

    def get_object(self):
        application = super().get_object()
        user = self.request.user
        # Check ownership: job created by this company user
        if application.job.created_by != user:
            return None
        return application

    def update(self, request, *args, **kwargs):
        application = self.get_object()
        if not application:
            return Response({
                "success": False,
                "message": "Unauthorized",
                "object": None,
                "errors": ["You do not own this job's application."]
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(application, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        old_status = application.status
        new_status = serializer.validated_data.get('status')

        if old_status == new_status:
            # No change - just return current data
            return Response({
                "success": True,
                "message": "Status unchanged.",
                "object": serializer.data,
                "errors": None
            })

        serializer.save()

        # Email notifications only for certain statuses
        email_messages = {
            "Interview": "You’ve been selected for an interview!",
            "Rejected": "We regret to inform you...",
            "Hired": "Congratulations! You’ve been hired."
        }
        if new_status in email_messages:
            subject = f"Update on your application for {application.job.title}"
            message = (
                f"Dear {application.applicant.name},\n\n"
                f"Your application status for the job '{application.job.title}' has been updated to '{new_status}'.\n\n"
                f"{email_messages[new_status]}\n\n"
                "Best regards,\n"
                f"{application.job.created_by.name} Team"
            )
            recipient = [application.applicant.email]
            send_mail(subject, message, None, recipient)

        return Response({
            "success": True,
            "message": "Application status updated successfully.",
            "object": serializer.data,
            "errors": None
        })