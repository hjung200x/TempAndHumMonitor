from django.db import models

class Monitor(models.Model):
    date = models.CharField(max_length=21, null=False, blank=False)
    temperature = models.IntegerField(null=False, blank=False)
    hummidity = models.IntegerField(null=False, blank=False)
    
    def __str__(self):
        return f'{self.date} {self.temperature} {self.hummidity}'


class Event(models.Model):
    date = models.CharField(max_length=21, null=False, blank=False)
    humidifier_event = models.BooleanField(default=False)
    fan_event = models.BooleanField(default=False)
    pump_event = models.BooleanField(default=False)
    water_level_event = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.date} {self.humidifier_event} {self.fan_event} {self.pump_event} {self.water_level_event}'


