from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, permission_required
from django.http import Http404
from django.core.paginator import Paginator
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import os, datetime, random, string
from django.urls import reverse
from django.template.defaultfilters import slugify

from .models import Item, Lend, Place, Action, Category, Person, Feature
from .forms import LendForm


def index(request):
    if not request.user.has_perm('inventory.view_item'):
        raise Http404("Site does not exist")

    search_place = request.POST.get("place")
    search_lend = request.POST.get("lend")
    search_category = request.POST.get("category")
    search_owner = 0

    search_active=False

    itemlist = Item.objects.order_by('name')

    places = Place.objects.all()
    categories = Category.objects.all()

    if search_place == "":
        search_place = None
    if search_place is not None:
        search_active=True
        itemlist = itemlist.filter(place__pk=search_place)
        search_place = Place.objects.get(pk=search_place)
    else:
        search_place = ""

    if search_lend == "":
        search_lend = None
    if search_lend is not None:
        search_active=True
        lends = Lend.objects.filter(lend_returned=False).all()
        items = []
        for lend in lends:
            items.append(lend.item)
        itemlist_new = []
        for item in itemlist:
            if item in items and item not in itemlist_new:
                itemlist_new.append(item)
        itemlist = itemlist_new
    else:
        search_lend = ""

    if search_category == "":
        search_category = None
    if search_category is not None:
        search_active=True
        category = Category.objects.get(pk=search_category)
        itemlist = itemlist.filter(category_id=search_category)
        search_category = Category.objects.get(pk=search_category)
    else:
        search_category = ""

    context = {
        'site_title': "Inventory",
        'itemlist': itemlist,
        'search': search_active,
        'places': places,
        'search_place': search_place,
        'search_lend': search_lend,
        'categories': categories,
        'search_category': search_category
    }
    return render(request, 'items/index.html', context)

@login_required()
def singleitem(request, item_id):
    if not request.user.has_perm('inventory.view_item'):
        raise Http404("Site does not exist")
    error = False


    item = Item.objects.get(pk=item_id)
    lends = Lend.objects.filter(item=item).filter(lend_returned=False).order_by("-lend_start").all()
    actions = Action.objects.filter(item=item).order_by("-action_date").all()[:20]

    if request.POST.get("name") is not None:
        item.name = request.POST.get("name")

    if request.POST.get("notes") is not None:
        item.notes = request.POST.get("notes")

    if request.POST.get("price") is not None:
        item.price = float(request.POST.get("price"))

    if request.POST.get("item_number") is not None:
        item.item_number = request.POST.get("item_number")

    if request.POST.get("storage_position") is not None:
        item.storage_position = request.POST.get("storage_position")

    if request.POST.get("amount") is not None:
        item.amount = float(request.POST.get("amount"))

    if request.POST.get("supplier") is not None:
        item.supplier = request.POST.get("supplier")

    if "file" in request.FILES and request.FILES["file"] is not None:
        item.file = request.FILES["file"]
        filename, ext = os.path.splitext(item.file.url)
        item.file.name=filename+"_"+random.choice(string.ascii_letters)+random.choice(string.ascii_letters)+random.choice(string.ascii_letters)+random.choice(string.ascii_letters)+random.choice(string.ascii_letters)+random.choice(string.ascii_letters)+ext

    if "thumb" in request.FILES and request.FILES["thumb"] is not None:
        item.thumb = request.FILES["thumb"]
        filename, ext = os.path.splitext(item.thumb.url)
        item.thumb.name=filename+"_"+random.choice(string.ascii_letters)+random.choice(string.ascii_letters)+random.choice(string.ascii_letters)+random.choice(string.ascii_letters)+random.choice(string.ascii_letters)+random.choice(string.ascii_letters)+ext

    if request.POST.get("place") is not None:
        try:
            place = Place.objects.get(pk=request.POST.get("place"))
            item.place = place
        except:
            error = True

    if request.POST.get("category") is not None:
        try:
            category = Category.objects.get(pk=request.POST.get("category"))
            item.category = category
        except:
            error = True

    if request.POST.get("person") is not None:
        try:
            person = Person.objects.get(pk=request.POST.get("person"))
            item.owner = person
        except:
            error = True

    item.save()

    places = Place.objects.all()
    categories = Category.objects.all()
    persons = Person.objects.all()
    features = Feature.objects.filter(item=item).order_by('name').all()
    features_all = Feature.objects.order_by('name').values("name").distinct()
    feature_names = "["
    for f in features_all:
        feature_names+="'"+f["name"]+"',"
    if feature_names != "[":
        feature_names = feature_names[:-1]
    feature_names+= "]"


    context = {
        'site_title': item.name,
        'item': item,
        'actions': actions,
        'lends': lends,
        'places': places,
        'categories': categories,
        'error': error,
        'persons': persons,
        'file_name': item.file.name.split("/")[-1],
        'thumb_name': item.thumb.name.split("/")[-1],
        'features': features,
        'feature_names': feature_names
    }
    if request.method == 'POST':
        return HttpResponseRedirect(reverse('singleitem', args=(item.id,)))
    return render(request, 'items/single.html', context)

@login_required()
def addFeature(request):
    name = request.POST.get("fname")
    value = request.POST.get("fvalue")
    itemid = request.POST.get("itemid")
    deleteid = request.POST.get("deleteid")

    if itemid is None or int(itemid) <= 0 or not request.user.has_perm('inventory.add_feature'):
        return HttpResponseRedirect(reverse('index'))
    if name is None or value is None:
        if deleteid is not None:
            fd = Feature.objects.get(pk=deleteid)
            fd.delete()
        return HttpResponseRedirect(reverse('singleitem', args=(int(itemid),)))

    if deleteid is not None:
        fd = Feature.objects.get(pk=deleteid)
        fd.delete()

    f = Feature()
    f.name = name
    f.value = value

    item = Item.objects.get(pk=itemid)

    f.item = item
    f.save()

    return HttpResponseRedirect(reverse('singleitem', args=(int(itemid),)))

@login_required()
def addLend(request):
    itemid = request.POST.get("itemid")
    isindex = request.POST.get("isindex")
    islend = request.POST.get("islend")

    if not request.user.has_perm('inventory.add_lend'):
        return HttpResponseRedirect(reverse('index'))
    
    if isindex is not None:
        isindex = True
    else:
        isindex = False

    if islend is not None:
        islend = True
    else:
        islend = False

    lend_start = request.POST.get('lend_start')
    lend_end = request.POST.get('lend_end')
    notes = request.POST.get("notes")
    amount = request.POST.get('amount')
    person = request.POST.get('person')

    if amount is not None and notes is not None and lend_end is not None and lend_start is not None and person is not None and itemid is not None:
        l = Lend()
        l.amount = amount
        l.notes = notes
        l.lend_end = lend_end
        l.lend_start = lend_start
        p = Person.objects.get(pk=person)
        l.responsible = p
        
        item = Item.objects.get(pk=itemid)
        l.item=item
        l.save()
        if itemid is not None and islend is False and isindex is False:
            return HttpResponseRedirect(reverse('singleitem', args=(int(itemid),)))
        elif islend:
            return HttpResponseRedirect(reverse('lends'))
        else:
            return HttpResponseRedirect(reverse('index'))

    #return HttpResponseRedirect(reverse('singleitem', args=(int(itemid),)))
    items=Item.objects.all()
    if itemid is not None:
        item = Item.objects.get(pk=itemid)
    else:
        item = None
    persons = Person.objects.all()
    context = {
        'site_title': "add Lend",
        'isindex': isindex,
        'islend': islend,
        'item': item,
        'items': items,
        'persons': persons,
    }
    return render(request, 'items/addlend.html', context)



@login_required()
def updateLend(request):
    deleteid = request.POST.get("deleteid")
    itemid = request.POST.get("itemid")
    lendid = request.POST.get("lendid")

    if itemid is None or not request.user.has_perm('inventory.delete_lend'):
        return HttpResponseRedirect(reverse('index'))
    if deleteid is not None:
        l = Lend.objects.get(pk=deleteid)
        l.delete()
        if itemid == "index":
            return HttpResponseRedirect(reverse('index'))
        elif itemid == "lends":
            return HttpResponseRedirect(reverse('lends'))
        else:
            return HttpResponseRedirect(reverse('singleitem', args=(int(itemid),)))

    if lendid is not None:
        l = Lend.objects.get(pk=lendid)
        l.lend_returned = True
        l.save()

    if itemid == "index":
            return HttpResponseRedirect(reverse('index'))
    elif itemid == "lends":
            return HttpResponseRedirect(reverse('lends'))
    else:
        return HttpResponseRedirect(reverse('singleitem', args=(int(itemid),)))

@login_required()
def addAction(request):
    itemid = request.POST.get("itemid")
    isindex = request.POST.get("isindex")
    deleteid = request.POST.get("deleteid")
    if isindex is not None:
        isindex = True
    else:
        isindex = False

    if itemid is None or int(itemid) <= 0 or not request.user.has_perm('inventory.add_action'):
        return HttpResponseRedirect(reverse('index'))
    if deleteid is not None:
        a = Action.objects.get(pk=deleteid)
        a.delete()
        if isindex:
            return HttpResponseRedirect(reverse('index'))
        else:
            return HttpResponseRedirect(reverse('singleitem', args=(int(itemid),)))

    notes = request.POST.get("notes")
    amount = request.POST.get('amount')

    if amount is not None and notes is not None:
        a = Action()
        a.amount = amount
        a.notes = notes
        item = Item.objects.get(pk=itemid)
        a.item=item
        a.save()
        if isindex:
            return HttpResponseRedirect(reverse('index'))
        else:
            return HttpResponseRedirect(reverse('singleitem', args=(int(itemid),)))

    item = Item.objects.get(pk=itemid)
    items=Item.objects.all()
    context = {
        'site_title': "add Action",
        'isindex': isindex,
        'item': item,
        'items': items,
    }
    return render(request, 'items/addaction.html', context)

@login_required()
def Lends(request):
    search = False
    search_item = None
    search_person = None
    itemid = request.POST.get("item")
    personid = request.POST.get("person")

    lends = Lend.objects.filter(lend_returned=False).all()
    if itemid is not None and itemid is not "":
        lends = lends.filter(item__id=itemid)
        search = True
        search_item = Item.objects.get(pk=itemid)
    if personid is not None and personid is not "":
        lends = lends.filter(responsible__id=personid)
        search = True
        search_person = Person.objects.get(pk=personid)
    persons = Person.objects.all()
    items = Item.objects.all()
    context = {
        "site_title": "Lends",
        "lends": lends,
        'items': items,
        'persons': persons,
        'search': search,
        'search_item': search_item,
        'search_person': search_person
    }
    return render(request, 'lends.html', context)

@login_required()
def addItem(request):
    item = Item()
    name = request.POST.get("name")
    supplier = request.POST.get("supplier")
    category_id = request.POST.get("category")
    owner_id = request.POST.get("owner")
    place_id = request.POST.get("place")
    amount = request.POST.get("amount")
    price = request.POST.get("price")
    number = request.POST.get("number")
    storage = request.POST.get("storage")
    notes = request.POST.get("notes")

    if name is not None and category_id is not None and owner_id is not None and place_id is not None and amount is not None:
        item.name = name
        item.slug=slugify(name)
        item.category = Category.objects.get(pk=category_id)
        item.owner = Person.objects.get(pk=owner_id)
        item.place = Place.objects.get(pk=place_id)
        item.amount = amount

        if supplier is not None and supplier is not "":
            item.supplier = supplier
        if price is not None and price is not "":
            item.price = price
        if number is not None and number is not "":
            item.item_number = number
        if storage is not None and storage is not "":
            item.storage_position = storage
        if notes is not None and notes is not "":
            item.notes = notes

        if "file" in request.FILES and request.FILES["file"] is not None:
            item.file = request.FILES["file"]
            filename, ext = os.path.splitext(item.file.url)
            item.file.name=filename+"_"+random.choice(string.ascii_letters)+random.choice(string.ascii_letters)+random.choice(string.ascii_letters)+random.choice(string.ascii_letters)+random.choice(string.ascii_letters)+random.choice(string.ascii_letters)+ext

        if "thumb" in request.FILES and request.FILES["thumb"] is not None:
            item.thumb = request.FILES["thumb"]
            filename, ext = os.path.splitext(item.thumb.url)
            item.thumb.name=filename+"_"+random.choice(string.ascii_letters)+random.choice(string.ascii_letters)+random.choice(string.ascii_letters)+random.choice(string.ascii_letters)+random.choice(string.ascii_letters)+random.choice(string.ascii_letters)+ext

        item.save()

        return HttpResponseRedirect(reverse('index'))

    lends = Lend.objects.filter(lend_returned=False).all()
    persons = Person.objects.all()
    items = Item.objects.all()
    categories = Category.objects.all()
    persons = Person.objects.all()
    places = Place.objects.all()

    context = {
        "site_title": "add Item",
        "categories": categories,
        "persons": persons,
        "places": places,
    }
    return render(request, 'items/additem.html', context)


@login_required()
def addPerson(request):
    person = Person()
    name = request.POST.get("name")
    address = request.POST.get("address")
    mail = request.POST.get("mail")
    phone = request.POST.get("phone")
    notes = request.POST.get("notes")

    if name is not None:
        person.name=name

        if address is not None and address is not "":
            person.address=address
        if mail is not None and mail is not "":
            person.mail=mail
        if phone is not None and phone is not "":
            person.phone = phone
        if notes is not None and notes is not "":
            person.notes=notes

        person.save()

        return HttpResponseRedirect(reverse('index'))

    context = {
        "site_title": "add Person",
    }
    return render(request, 'items/addperson.html', context)

@login_required()
def addCategory(request):
    cat = Category()
    name = request.POST.get("name")

    if name is not None:
        cat.name=name
        cat.slug = slugify(name)

        cat.save()

        return HttpResponseRedirect(reverse('index'))

    context = {
        "site_title": "add Category",
    }
    return render(request, 'items/addcategory.html', context)

@login_required()
def addPlace(request):
    place = Place()
    name = request.POST.get("name")
    address = request.POST.get("address")
    owner_id = request.POST.get("person")
    notes = request.POST.get("notes")

    if name is not None and owner_id is not None:
        place.name=name
        place.slug = slugify(name)
        place.owner = Person.objects.get(pk=owner_id)
        
        if address is not None and address is not "":
            place.address = address
        if notes is not None and notes is not "":
            place.notes = notes

        place.save()

        return HttpResponseRedirect(reverse('index'))
    
    persons = Person.objects.all()

    context = {
        "site_title": "add Place",
        'persons': persons 
    }
    return render(request, 'items/addplace.html', context)

@login_required()
def delete(request):
    item = request.POST.get("item")
    item_id = request.POST.get("itemid")

    notification_type=""
    notification = ""
    notification_enabled = False

    if item is not None and item_id is not None:
        notification_enabled = True
        if item == "Person" and request.user.has_perm('inventory.delete_person'):
            # handle models that require a person
            try:
                placeholder = Person.objects.get(name="Deleted Account")
            except:
                placeholder = Person()
                placeholder.name="Deleted Account"
                placeholder.save()
            try:
                a = Place.objects.filter(owner__id=item_id)
                for i in a:
                    i.owner=placeholder
                    i.save()
                a = Item.objects.filter(owner__id=item_id)
                for i in a:
                    i.owner=placeholder
                    i.save()
                a = Lend.objects.filter(responsible__id=item_id)
                for i in a:
                    i.responsible=placeholder
                    i.save()

                p = Person.objects.get(pk=item_id)
                p.delete()
                notification_type="success"
                notification = "Successfully deleted person."
            except:
                notification_type="danger"
                notification = "There are some dependecies that can not be deleted. Or the item is already deleted."
        elif item == "Category" and request.user.has_perm('inventory.delete_category'):
            try:
                placeholder = Category.objects.get(name="Uncategorized")
            except:
                placeholder = Category()
                placeholder.name="Uncategorized"
                placeholder.slug="uncategorized"
                placeholder.save()
            try:
                a = Item.objects.filter(category__id=item_id)
                for i in a:
                    i.category=placeholder
                    i.save()

                p = Category.objects.get(pk=item_id)
                p.delete()
                notification_type="success"
                notification = "Successfully deleted category."
            except:
                notification_type="danger"
                notification = "There are some dependecies that can not be deleted. Or the item is already deleted."
        elif item == "Place" and request.user.has_perm('inventory.delete_place'):
            try:
                p = Place.objects.get(pk=item_id)
                p.delete()
                notification_type="success"
                notification = "Successfully deleted place."
            except:
                notification_type="danger"
                notification = "There are some dependecies that can not be deleted. Or the item is already deleted. Make sure there is no item left in this place."
        elif item == "Item" and request.user.has_perm('inventory.delete_item'):
            try:
                a = Feature.objects.filter(item__id=item_id)
                a.delete()
                a = Lend.objects.filter(item__id=item_id)
                a.delete()
                a = Action.objects.filter(item__id=item_id)
                a.delete()
                p = Item.objects.get(pk=item_id)
                p.delete()
                notification_type="success"
                notification = "Successfully deleted item."
            except:
                notification_type="danger"
                notification = "There are some dependecies that can not be deleted. Or the item is already deleted."
        else:
            notification_type="danger"
            notification = "You did not provide all Information needed."
    else:
        notification_type=True
        notification = ""
        notification_enabled = False
            
    persons = Person.objects.all().exclude(name="Deleted Account")
    categories = Category.objects.all().exclude(name="Uncategorized")
    places = Place.objects.all()
    items = Item.objects.all()


    context = {
        "site_title": "Deletion",
        'notification_type': notification_type,
        'notification': notification,
        'persons': persons,
        'categories': categories,
        'places': places,
        'items': items,
        'notification_enabled': notification_enabled

    }
    return render(request, 'items/delete.html', context)