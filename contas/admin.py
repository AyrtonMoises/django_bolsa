from django.contrib import admin
from django.db import models

from .models import User

admin.site.register(User)
