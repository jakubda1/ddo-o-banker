import glob
import os
import zipfile
from zipfile import ZipFile

import py7zr
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render
from rest_framework import generics

from .forms import *
from .item_analyzer.analyzer import analyze
from .serializers import ItemSerializer


def ajax_items_live_search(request):
    if request.is_ajax():
        item_name = request.POST.get("item_name")
        queryset = ItemList.objects.filter(name__icontains=item_name)
        item_set = []
        if len(queryset) > 0 and len(item_name) > 0:
            for item in queryset:
                # dct = {
                #     "item_idx": item.id,
                #     "name": item.name,
                # }
                item_set.append(item.name)
        return JsonResponse({"data": item_set})


class ItemsView(generics.ListAPIView):
    # queryset = Item.objects.all()
    queryset = Item.objects.filter(user=User.objects.get(id=1))
    serializer_class = ItemSerializer


# def ItemsListView(ListView):
#     model = Item
#     template_name = "manage.html"
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["item_json"] = json.dumps(list(Item.objects.filter(user=self.request.user)))
#         return context

def delete_item_ajax(request):
    if request.is_ajax():
        item_id = request.POST.get("item_id")
        it = Item.objects.get(id=item_id)
        print(it)
        it.delete()
        return JsonResponse({"success": "true"})


def transfer_to_ajax(request):
    if request.is_ajax():
        item_id = request.POST.get("item_id")
        character_id = request.POST.get("character")
        changed_item = Item.objects.get(id=item_id)
        print("b", changed_item.character, item_id, changed_item.id)
        changed_item.character = Character.objects.get(id=character_id)
        print("a", changed_item.character, item_id, changed_item.id)
        changed_item.save()
        return JsonResponse({"success": "true"})

    return JsonResponse({})


def search_result_ajax(request):
    if request.is_ajax():
        item_name = request.POST.get("item_name")
        queryset = Item.objects.filter(user=request.user, name__name__icontains=item_name)
        item_set = []
        if len(queryset) > 0 and len(item_name) > 0:
            for item in queryset:
                dct = {
                    "item_idx": item.id,
                    "character": item.character.name,
                    "name": item.name.name,
                    "reaper": item.reaper,
                    "mythic": item.mythic,
                }
                item_set.append(dct)

        return JsonResponse({"data": item_set})

    return JsonResponse({})


def index(request, *args, **kwargs):
    res = redirect("/login")
    return res


@login_required
def manage(request, *args, **kwargs):
    context = {}
    if request.method == "POST":
        item_form = AddItemForm(user=request.user)
        print(request.POST)
        item_form.data = request.POST
        added_item = Item()
        added_item.user = request.user
        added_item.character = Character.objects.get(id=int(item_form.data.get("character")))
        added_item.name = ItemList.objects.get(name=request.POST.get("item-name"))
        added_item.mythic = item_form.data.get("mythic")
        added_item.reaper = item_form.data.get("reaper")
        added_item.save()
        redirect("manage")

    item_form = AddItemForm(user=request.user)
    context["item_form"] = item_form

    # context["items"] = Item.objects.filter(user=request.user)
    # context["characters"] = Character.objects.filter(user=request.user)

    return render(request, "manage.html", context=context)


@login_required
def upload(request, *args, **kwargs):
    context = {}
    if request.method == "POST":
        # form = UploadFileForm(data=request.POST, files=request.FILES)
        file = request.FILES["file"]
        if file:
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, f"{request.user}"))
            fs.save(name=file.name, content=file)
            whole_file_path = os.path.join(fs.location, file.name)
            try:
                if zipfile.is_zipfile(whole_file_path):
                    with ZipFile(whole_file_path, "r") as zip_ref:
                        zip_ref.extractall(os.path.join(fs.location, "extracted"))

                elif py7zr.is_7zfile(whole_file_path):

                    with py7zr.SevenZipFile(whole_file_path, "r") as z:
                        z.extractall(os.path.join(fs.location, "extracted"))

                extracted_path = os.path.join(fs.location, "extracted")

                extracted = glob.glob(os.path.join(extracted_path, "*.png")) + \
                            glob.glob(os.path.join(extracted_path, "*.jpg")) + \
                            glob.glob(os.path.join(extracted_path, "*.jpeg"))

                if len(extracted) > 0:
                    analyzed = analyze(extracted)
                    for a in analyzed:
                        if len(a.name) > 2:
                            it = Item()
                            print(a.name)
                            it.name = ItemList.objects.get(name=a.name)
                            it.mythic = a.mythic_boost
                            it.user = request.user
                            it.character = Character.objects.get(id=request.POST.get("character"))
                            it.save()

            except Exception as e:
                print(e)
                context["errors"] = "There was an error while extracting files"
                return render(request, "upload.html", context=context)

            # finally:
            #     shutil.rmtree(fs.location, ignore_errors=True)

    if request.method == "GET":
        form = UploadFileForm(request.user)
        context["form"] = form
        return render(request, "upload.html", context=context)

    return render(request, "upload.html")


def register(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            default_shared_bank = Character(user=user, name="Shared Bank")
            default_shared_bank.save()
            messages.success(request,
                             "Task failed successfully. (JK. you are really registered. Now, go on login, little one.")
            return redirect("register")
        messages.error(request, "Unsuccessful registration. Invalid information.")

    form = NewUserForm()
    return render(request=request, template_name="register.html", context={"register_form": form})


@login_required
def create_character(request):
    context = {}
    if request.method == "POST":
        if "del_char" in request.POST:
            id = request.POST.get("name")
            ch = Character.objects.get(id=id)
            ch.delete()
            return redirect("create_char")

        elif "add_char" in request.POST:
            ch = Character()
            ch.name = request.POST.get("char_name")
            ch.user = request.user
            ch.save()
            context["success"] = "Character has been saved. Now add items to that character"
            return redirect("create_char")

    if request.method == "GET":
        add_form = CreateCharacterForm()
        del_form = DeleteCharacterForm(request.user)
        context["add_form"] = add_form
        context["del_form"] = del_form

        return render(request, template_name="add_character.html", context=context)

    return redirect("create_char")
