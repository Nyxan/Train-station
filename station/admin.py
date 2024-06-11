from django.contrib import admin

from station.models import (
    Route,
    Ticket,
    Train,
    TrainType,
    Station,
    Crew,
    Order,
    Journey,
)


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [TicketInline]


admin.site.register(Route)
admin.site.register(Train)
admin.site.register(TrainType)
admin.site.register(Station)
admin.site.register(Crew)
admin.site.register(Journey)
admin.site.register(Ticket)
