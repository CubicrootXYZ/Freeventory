from django.contrib import admin

# Register your models here.
from .models import Item, Place, Person, Lend, Category

admin.site.register(Item)
admin.site.register(Place)
admin.site.register(Person)
admin.site.register(Lend)
admin.site.register(Category)