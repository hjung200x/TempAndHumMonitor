from django.db import models

class Status(models.Model):
    name = models.CharField(max_length=64, primary_key=True)
    value = models.CharField(max_length=64)
    
    def __str__(self):
        return f'{self.name} {self.value}'
