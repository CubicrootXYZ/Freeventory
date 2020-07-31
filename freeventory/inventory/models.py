from django.db import models
from django.utils import timezone
from django.db.models import Sum, Count
from django.db.models.functions import Coalesce

# Create your models here.

# describtors for items and items itself
class Category(models.Model):
    name = models.CharField(max_length=200, default="unnamed")
    slug = models.SlugField(max_length=100)
    def __str__(self):
        return self.name

class Person(models.Model):
    name = models.CharField(max_length=200, default="unnamed")
    address = models.CharField(max_length=200, blank=True)
    mail = models.CharField(max_length=100, blank=True, default="")
    phone = models.CharField(max_length=50, blank=True, default="0")
    notes = models.TextField(blank=True)
    def __str__(self):
        return self.name

class Place(models.Model):
    name = models.CharField(max_length=200, default="unnamed")
    address = models.TextField(blank=True)
    owner = models.ForeignKey(Person, on_delete=models.PROTECT)
    notes = models.TextField(blank=True)
    slug = models.SlugField(max_length=100)
    def __str__(self):
        return self.name

class Item(models.Model):
    name = models.CharField(max_length=200, default="unnamed")
    supplier = models.CharField(max_length=200, blank=True, default="no supplier")
    file = models.FileField(upload_to="static/uploads/%Y/%m/%d", blank=True)
    thumb = models.FileField(upload_to="static/uploads/%Y/%m/%d", blank=True)
    slug = models.SlugField(max_length=100)
    category = models.ForeignKey(Category, blank=True, on_delete=models.PROTECT)
    owner = models.ForeignKey(Person, on_delete=models.PROTECT)
    place = models.ForeignKey(Place, on_delete=models.PROTECT)
    amount = models.PositiveIntegerField()
    price = models.FloatField(default=0)
    notes = models.TextField(blank=True)
    item_number = models.CharField(max_length=20, default="0")
    storage_position = models.CharField(max_length=100, default="-")
    def __str__(self):
        return self.name
    def calcLends(self):
        return Lend.objects.filter(item=self, lend_returned=False).all().aggregate(amount__sum=Coalesce(Sum('amount'), 0))["amount__sum"]
    lends = property(calcLends)
    def calcLendsAmount(self):
        return Lend.objects.filter(item=self, lend_returned=False).all().aggregate(amount__count=Coalesce(Count('amount'), 0))["amount__count"]
    lends_amount = property(calcLendsAmount)
    def calcAmount(self):
        act = Action.objects.filter(item=self).all().aggregate(amount__sum=Coalesce(Sum('amount'),0))["amount__sum"]
        return int(self.amount)-int(self.lends)+int(act)
    amount_fixed = property(calcAmount)

class Feature(models.Model):
    name = models.CharField(max_length=200, default="unnamed")
    value = models.TextField()
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    def __str__(self):
        return self.name

# actions to perform on items
class Lend(models.Model):
    responsible = models.ForeignKey(Person,on_delete=models.PROTECT)
    lend_start = models.DateField(default=timezone.now)
    lend_end = models.DateField(blank=True, null=True)
    lend_returned = models.BooleanField(blank=True, default=False)
    lend_finish = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True)
    amount = models.PositiveIntegerField()
    item = models.ForeignKey(Item,on_delete=models.PROTECT)
    def __str__(self):
        return "Lend by "+self.responsible.name

class Action(models.Model):
    action_date = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)
    amount = models.IntegerField(default=0)
    item = models.ForeignKey(Item,on_delete=models.PROTECT)
    def __str__(self):
        if self.amount < 0:
            return "Checkin"
        else:
            return "Checkout"


