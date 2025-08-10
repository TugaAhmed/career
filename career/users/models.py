# users/models.py
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_APPLICANT = "applicant"
    ROLE_COMPANY = "company"
    ROLE_CHOICES = [
        (ROLE_APPLICANT, "Applicant"),
        (ROLE_COMPANY, "Company"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
   
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    email_verified = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"] 
    
    def __str__(self):
        return f"{self.email} ({self.role})"
