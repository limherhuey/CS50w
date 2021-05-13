from django.contrib import admin

from .models import User, Listing, Bid, Comment

# Register your models here.

class ListingAdmin(admin.ModelAdmin):
    exclude = ('current_price', 'watchers', 'closed',)
    list_display = ('user', 'name', 'price', 'category')


admin.site.register(User)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Bid)
admin.site.register(Comment)
