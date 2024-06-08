from django.contrib import admin

from station.models import Route, Ticket, Train, TrainType, Station, Crew, Order, Journey

admin.site.register(Route)
admin.site.register(Train)
admin.site.register(TrainType)
admin.site.register(Station)
admin.site.register(Crew)
admin.site.register(Order)
admin.site.register(Journey)
admin.site.register(Ticket)