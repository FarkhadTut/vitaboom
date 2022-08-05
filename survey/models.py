from asyncore import poll
from pyexpat import model
from statistics import mode
from django.db import models
from datetime import datetime
# from products.models import *
# Create your models here.
from database.connector import con
import pandas as pd

models_list = pd.read_sql(sql="SELECT * FROM sqlite_sequence", con=con)
products_mask = models_list['name'].str.startswith('products_')
models_list = models_list[products_mask]

PRODUCTS_MODELS = (
    ('products_type', 'Products type'),
    ('products_product', 'Product name'),
    ('products_identifier', 'Products identifier'),
    (None, 'None'),
)

SHOW_USERS = (
    ('show_all_users', 'Show all users'),
    ('show_confirmed_users', 'Show confirmed users'),
    ('show_not_confirmed_users', 'Show not confirmed users'),
    (None, 'None'),
)




class Poll(models.Model):
    name = models.TextField(max_length=512, blank=False, default='Test poll', unique=True)
    status = models.BooleanField(default=False, blank=False)
    date = models.DateTimeField(blank=False, default=datetime.now())
    update_db = models.BooleanField(blank=False, null=False)

    def __str__(self):
        return self.name

class Question(models.Model):
    TYPES = (
        ('single', 'Single choice'),
        ('multiple', 'Multiple choice'),
        ('open', 'Open question'),
        ('location', 'Location'),
        ('integer', 'Integer'),
        ('image', 'Image'),
        ('password', 'Password'),
        ('action', 'Action'),
        ('price', 'Price'),
        ('payment', 'Payment'),
        ('unit', 'Unit'),
        ('product', 'Product'),
        ('quantity', 'Quantity'),
        ('volume', 'Volume'),
        ('contact', 'Contact'),
        ('success', 'Success'),
        ('daterange', 'Daterange')

    )

    uz = models.TextField(max_length=4096, blank=False)
    ru = models.TextField(max_length=4096, blank=True)
    finish = models.BooleanField()
    poll = models.ForeignKey(to=Poll, on_delete=models.SET_NULL, null=True)
    num = models.IntegerField()
    type = models.CharField(choices=TYPES, max_length=128)

    def __str__(self):
        return self.uz

class Answer(models.Model):
    ru = models.TextField(max_length=4096, blank=True, null=True)
    uz = models.TextField(max_length=4096, blank=True, null=True)
    product = models.CharField(max_length=512, choices=PRODUCTS_MODELS, blank=True, null=True)
    show_users = models.CharField(default=None, max_length=512, choices=SHOW_USERS, blank=True, null=True)
    question = models.ForeignKey(to=Question, on_delete=models.SET_NULL, null=True)
    next_question = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.uz

class Response(models.Model):
    # answer = models.ForeignKey(to=Answer, on_delete=models.SET_NULL, null=True)
    poll = models.ForeignKey(to=Poll, on_delete=models.SET_NULL, null=True)
    

    
    question = models.ForeignKey(to=Question, on_delete=models.SET_NULL, null=True)
    answer_type = models.CharField(max_length=512, null=False, blank=False)
    answer_id_source = models.CharField(max_length=512, null=False, blank=True)
    date = models.DateTimeField(default=datetime.now())
    user_id = models.IntegerField()
    answer_id = models.IntegerField(null=False, blank=False)
    record_id = models.CharField(max_length=256, blank=False, null=False)


class OpenAnswer(models.Model):
    answer = models.TextField(max_length=4096, blank=False, null=True)
    question = models.ForeignKey(to=Question, on_delete=models.SET_NULL, null=True)


