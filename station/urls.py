from django.urls import path, include
from rest_framework.routers import DefaultRouter
from station.views import (
    StationViewSet,
    RouteViewSet,
    TrainTypeViewSet,
    TrainViewSet,
    CrewViewSet,
    JourneyViewSet,
    OrderViewSet,
    TicketViewSet,
)

router = DefaultRouter()
router.register(r"stations", StationViewSet)
router.register(r"routes", RouteViewSet)
router.register(r"train_types", TrainTypeViewSet)
router.register(r"trains", TrainViewSet)
router.register(r"crews", CrewViewSet)
router.register(r"journeys", JourneyViewSet)
router.register(r"orders", OrderViewSet)
router.register(r"tickets", TicketViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "station"
