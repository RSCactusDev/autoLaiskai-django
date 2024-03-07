from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    ordering = ('email',)
    list_display = ('email','kv_nr', 'date_created', 'last_login','status', 'is_admin', 'is_staff')
    search_fields = ('email','last_login','kv_nr')
    readonly_fields = ('id', 'date_created', 'last_login')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(CustomUser, CustomUserAdmin)
