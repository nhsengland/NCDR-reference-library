# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from . import models

admin.site.register(models.Database)
admin.site.register(models.Table)
admin.site.register(models.Row)
admin.site.register(models.SiteDescription)
