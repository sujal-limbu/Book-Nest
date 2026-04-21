from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Carousel)
admin.site.register(New_Arrivals)
admin.site.register(Best_Sellers)
admin.site.register(Non_Fiction)
admin.site.register(Fiction)
admin.site.register(Nepali)




admin.site.site_title= 'Book Nest'
admin.site.index_title= 'Book E-commerce'
admin.site.site_header= 'Book Nest'