from django.contrib.auth.models import User
from django.db import models


class Character(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(default="", max_length=128)

    def __str__(self):
        return self.name


class ItemList(models.Model):
    name = models.CharField(default=None, max_length=64)

    def __str__(self):
        return self.name


class Item(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    character = models.ForeignKey(Character, default=None, null=True, blank=True, on_delete=models.CASCADE)
    name = models.ForeignKey(ItemList, default=None, null=True, blank=True, on_delete=models.CASCADE)
    mythic = models.IntegerField(default=0)
    reaper = models.IntegerField(default=0)
