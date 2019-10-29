from django.contrib import admin

from . import models

admin.site.register(models.Metric)
admin.site.register(models.Operand)
admin.site.register(models.Organisation)
admin.site.register(models.Report)
admin.site.register(models.TeamLead)
admin.site.register(models.MetricLead)
admin.site.register(models.Topic)
