from django.db import models
from django.conf import settings
from careerapp.models import Job, Application as CareerApplication

User = settings.AUTH_USER_MODEL