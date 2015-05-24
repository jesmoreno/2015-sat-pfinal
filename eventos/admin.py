from django.contrib import admin
from eventos.models import Events
from eventos.models import upDate
from eventos.models import tabUserEvent
from eventos.models import miPagina
# Register your models here.

admin.site.register(Events)
admin.site.register(upDate)
admin.site.register(tabUserEvent)
admin.site.register(miPagina)
