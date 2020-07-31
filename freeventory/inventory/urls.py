from django.urls import path


from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:item_id>', views.singleitem, name="singleitem"),
    path('addfeature', views.addFeature, name="addfeature"),
    path('addlend', views.addLend, name="addlend"),
    path('updatelend', views.updateLend, name="updatelend"),
    path('addaction', views.addAction, name="addaction"),
    path('lends', views.Lends, name="lends"),
    path('additem', views.addItem, name="additem"),
    path('addperson', views.addPerson, name="addperson"),
    path('addcategory', views.addCategory, name="addcategory"),
    path('addplace', views.addPlace, name="addplace"),
    path('delete', views.delete, name="delete")
    ] 
