from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from station.models import Station, Route, TrainType, Train, Crew, Journey, Order, Ticket
from station.permission import IsAdminOrIfAuthenticatedReadOnly
from station.serializers import StationSerializer, RouteSerializer, TrainTypeSerializer, TrainSerializer, \
    CrewSerializer, \
    JourneySerializer, OrderSerializer, TicketSerializer, JourneyListSerializer, TrainListSerializer, \
    TrainRetrieveSerializer, JourneyRetrieveSerializer, RouteListSerializer, RouteRetrieveSerializer, \
    OrderListSerializer, TickerRetrieveSerializer, TicketListSerializer


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)
    def get_serializer_class(self):
        if self.action == 'list':
            return RouteListSerializer
        elif self.action == 'retrieve':
            return RouteRetrieveSerializer
        return RouteSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action == ('list', 'retrieve'):
            return queryset.prefetch_related('station')
        return queryset


class TrainTypeViewSet(viewsets.ModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.all()
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    @staticmethod
    def _params_to_ints(param):
        return [int(str_id) for str_id in param.split(',')]

    def get_serializer_class(self):
        if self.action == 'list':
            return TrainListSerializer
        elif self.action == 'retrieve':
            return TrainRetrieveSerializer
        return TrainSerializer

    def get_queryset(self):
        queryset = self.queryset
        facilities = self.request.query_params.get('facilities')
        if facilities:
            facilities = self._params_to_ints(facilities)
            queryset = queryset.filter(facilities__id__in=facilities)
        if self.action == ('list', 'retrieve'):
            return queryset.prefetch_related('train_type')
        return queryset


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = Journey.objects.all()
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        queryset = self.queryset
        if self.action == ('list', 'retrieve'):
            return queryset.select_related()
        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return JourneyListSerializer
        elif self.action == 'retrieve':
            return JourneyRetrieveSerializer
        return JourneySerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)

        if self.action == "list":
            queryset = queryset.prefetch_related('tickets__journey__train')
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        serializer = self.serializer_class

        if self.action == "list":
            serializer = OrderListSerializer
        return serializer


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        serializer = self.serializer_class
        if self.action == "list":
            serializer = TicketListSerializer
        elif self.action == "retrieve":
            serializer = TickerRetrieveSerializer
        return serializer
