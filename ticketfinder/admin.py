from django.contrib import admin

# Register your models here.
from .models import TrainStation, TrainFare, UserQuery, TrainJourney

admin.site.register(TrainStation)
admin.site.register(TrainFare)
admin.site.register(UserQuery)
class UserQueryAdmin(admin.ModelAdmin):
    list_display = ('query_text', 'timestamp', 'processed')

admin.site.register(TrainJourney)
class TrainJourneyAdmin(admin.ModelAdmin):
    list_display = ('rid', 'tpl', 'pta', 'ptd', 'arr_at', 'dep_at')
    list_filter = ('tpl', 'arr_at', 'dep_at')
    search_fields = ('rid', 'tpl')