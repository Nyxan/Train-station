from rest_framework import viewsets
from station.models import Station, Route, TrainType, Train, Crew, Journey, Order, Ticket
from station.serializers import StationSerializer, RouteSerializer, TrainTypeSerializer, TrainSerializer, \
    CrewSerializer, \
    JourneySerializer, OrderSerializer, TicketSerializer, JourneyListSerializer, TrainListSerializer


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer


class TrainTypeViewSet(viewsets.ModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return TrainListSerializer
        return TrainSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action == 'list':
            return queryset.prefetch_related('train_type')
        return queryset


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = Journey.objects.all()

    def get_queryset(self):
        queryset = self.queryset
        if self.action == 'list':
            return queryset.select_related()
        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return JourneyListSerializer
        return JourneySerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
