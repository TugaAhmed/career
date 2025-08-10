# users/serializers.py
import re
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class SignupSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'full_name', 'email', 'password', 'role')

    def validate_full_name(self, value):
        # Must contain only alphabets with exactly one space
        if not re.match(r'^[A-Za-z]+ [A-Za-z]+$', value):
            raise serializers.ValidationError("Full name must be two words with alphabets only and one space between")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already in use")
        return value

    def validate_password(self, value):
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*\W).{8,}$'
        if not re.match(pattern, value):
            raise serializers.ValidationError("Password must be 8+ chars with upper, lower, digit and special char")
        return value

    def validate_role(self, value):
        if value not in ('applicant', 'company'):
            raise serializers.ValidationError("Role must be 'applicant' or 'company'")
        return value

    def create(self, validated_data):
        full_name = validated_data.pop('full_name')
        first_name, last_name = full_name.split(' ', 1)
        validated_data['first_name'] = first_name
        validated_data['last_name'] = last_name
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.is_active = False  # User inactive until email verified
        user.save()
        return user





# import re
# from django.contrib.auth import get_user_model
# from rest_framework import serializers

# User = get_user_model()

# class SignupSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True)

#     class Meta:
#         model = User
#         fields = ('id', 'first_name', 'last_name', 'email', 'password', 'role')

#     def validate_email(self, value):
#         if User.objects.filter(email=value).exists():
#             raise serializers.ValidationError("Email already in use")
#         return value

#     def validate_first_name(self, v):
#         if not re.match(r'^[A-Za-z]+$', v):
#             raise serializers.ValidationError("First name must contain only alphabets")
#         return v

#     def validate_last_name(self, v):
#         if not re.match(r'^[A-Za-z]+$', v):
#             raise serializers.ValidationError("Last name must contain only alphabets")
#         return v

#     def validate_password(self, value):
#         pattern = r'(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*\W).{8,}'
#         if not re.match(pattern, value):
#             raise serializers.ValidationError("Password must be 8+ chars with upper, lower, digit and special char")
#         return value

#     def create(self, validated_data):
#         password = validated_data.pop('password')
#         user = User(**validated_data)
#         user.set_password(password)
#         user.save()
#         return user


# class LoginSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     password = serializers.CharField()
