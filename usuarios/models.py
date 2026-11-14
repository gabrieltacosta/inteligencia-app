from django.db import models
from core.utils import generate_cuid

class usuarios(models.Model):
    id = models.CharField(primary_key=True, default=generate_cuid, editable=False, max_length=50)
    