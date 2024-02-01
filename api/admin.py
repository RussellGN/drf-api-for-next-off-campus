from django.contrib import admin
from .models import Listing, Image, Lister

# Register your models here.
admin.site.register(Listing)
admin.site.register(Lister)
admin.site.register(Image)