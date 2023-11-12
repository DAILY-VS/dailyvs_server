from django.contrib import admin
from .models import *

admin.site.register(Poll)
admin.site.register(Choice)
admin.site.register(UserVote)
admin.site.register(Comment)
admin.site.register(Poll_Result)
admin.site.register(Category)
admin.site.register(Today_Poll)
admin.site.register(Report)