from rest_framework import serializers
from .models import Job

class JobCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ['title', 'description', 'location', 'status']

    def validate_title(self, value):
        if not (1 <= len(value) <= 100):
            raise serializers.ValidationError("Title must be between 1 and 100 characters.")
        return value

    def validate_description(self, value):
        if not (20 <= len(value) <= 2000):
            raise serializers.ValidationError("Description must be between 20 and 2000 characters.")
        return value

# jobs/serializers.py
class JobUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ['title', 'description', 'location', 'status']
        extra_kwargs = {
            'title': {'required': False},
            'description': {'required': False},
            'location': {'required': False},
            'status': {'required': False},
        }

    def validate_title(self, value):
        if not (1 <= len(value) <= 100):
            raise serializers.ValidationError("Title must be between 1 and 100 characters.")
        return value

    def validate_description(self, value):
        if not (20 <= len(value) <= 2000):
            raise serializers.ValidationError("Description must be between 20 and 2000 characters.")
        return value

    def validate_status(self, value):
        # Validate forward-only status transition
        old_status = self.instance.status if self.instance else None
        valid_transitions = {
            'Draft': ['Open', 'Draft'],
            'Open': ['Closed', 'Open'],
            'Closed': ['Closed'],
        }

        if old_status and value not in valid_transitions.get(old_status, []):
            raise serializers.ValidationError(
                f"Invalid status transition from {old_status} to {value}."
            )
        return value


class JobListSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='created_by.name', read_only=True)

    class Meta:
        model = Job
        fields = ['id', 'title', 'description', 'location', 'status', 'company_name', 'created_at']

        


class CompanyJobListSerializer(serializers.ModelSerializer):
    num_applications = serializers.IntegerField(read_only=True)
    description = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = ['id', 'title', 'description', 'location', 'status', 'created_at', 'num_applications']

    def get_description(self, obj):
        max_length = 200
        if obj.description and len(obj.description) > max_length:
            return obj.description[:max_length] + "..."
        return obj.description


class JobDetailSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.name', read_only=True)

    class Meta:
        model = Job
        fields = ['id', 'title', 'description', 'location', 'status', 'created_at', 'created_by_name']