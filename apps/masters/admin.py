from django.contrib import admin
from .models import MasterLike, MasterProfile, Workshop

admin.site.register(MasterProfile)
admin.site.register(Workshop)
admin.site.register(MasterLike)
