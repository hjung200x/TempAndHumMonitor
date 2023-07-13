from unittest.util import _MAX_LENGTH
from django.db import models

class ConfigTbl(models.Model):
    key = models.CharField(max_length=64, primary_key=True)
    value = models.CharField(max_length=64)
    
    def __str__(self):
        return f'{self.key} {self.value}'
