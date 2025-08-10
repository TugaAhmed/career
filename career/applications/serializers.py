# applications/serializers.py
from rest_framework import serializers
from .models import Application

class ApplicationSerializer(serializers.ModelSerializer):
    applicant_name = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = ('id','applicant','applicant_name','job','resume_link','cover_letter','status','applied_at')
        read_only_fields = ('status','applied_at','applicant')

    def get_applicant_name(self, obj):
        return f"{obj.applicant.first_name} {obj.applicant.last_name}"


class ApplicationListSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source='job.title', read_only=True)
    company_name = serializers.CharField(source='job.created_by.name', read_only=True)
    applicant_name = serializers.CharField(source='applicant.name', read_only=True)
    
    class Meta:
        model = Application
        fields = ['id', 'job_title', 'company_name', 'status', 'applied_at'
                   'applicant_name', 'resume_link', 'cover_letter', 'status', 'applied_at']



class ApplicationStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['status']

    def validate_status(self, value):
        allowed_statuses = ["Applied", "Reviewed", "Interview", "Rejected", "Hired"]
        if value not in allowed_statuses:
            raise serializers.ValidationError("Invalid status value.")
        return value