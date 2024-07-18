from drf_spectacular.utils import OpenApiParameter, OpenApiExample, extend_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from station.models import (
    Station,
    Route,
    TrainType,
    Train,
    Crew,
    Journey,
    Order,
    Ticket,
)
from station.serializers import (
    StationSerializer,
    RouteSerializer,
    TrainTypeSerializer,
    TrainSerializer,
    CrewSerializer,
    JourneySerializer,
    OrderSerializer,
    TicketSerializer,
    JourneyListSerializer,
    TrainListSerializer,
    TrainRetrieveSerializer,
    JourneyRetrieveSerializer,
    RouteListSerializer,
    RouteRetrieveSerializer,
    OrderListSerializer,
    TickerRetrieveSerializer,
    TicketListSerializer,
    TrainImageSerializer,
)


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        elif self.action == "retrieve":
            return RouteRetrieveSerializer
        return RouteSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action == ("list", "retrieve"):
            return queryset.prefetch_related("station")
        return queryset


class TrainTypeViewSet(viewsets.ModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.all()

    @staticmethod
    def _params_to_ints(param):
        return [int(str_id) for str_id in param.split(",")]

    def get_serializer_class(self):
        if self.action == "list":
            return TrainListSerializer
        elif self.action == "retrieve":
            return TrainRetrieveSerializer
        elif self.action == "upload_image":
            return TrainImageSerializer
        return TrainSerializer

    def get_queryset(self):
        queryset = self.queryset
        facilities = self.request.query_params.get("facilities")
        if facilities:
            facilities = self._params_to_ints(facilities)
            queryset = queryset.filter(facilities__id__in=facilities)
        if self.action == ("list", "retrieve"):
            return queryset.prefetch_related("train_type")
        return queryset

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None):
        train = self.get_object()
        serializer = self.get_serializer(train, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "name",
                description="Filtering by name (ex. ?name='train1')",
                required=False,
                type=str,
                examples=[
                    OpenApiExample(name="Example 1", value="train2"),
                    OpenApiExample(name="Example 2", value="train3"),
                ],
            ),
            OpenApiParameter(
                "train_types",
                description="Filtering by train_types id (ex. ?train_type=1,2)",
                type={"type": "array", "items": {"type": "number"}},
                examples=[
                    OpenApiExample(name="Example 1", value="1"),
                    OpenApiExample(name="Example 2", value="2"),
                ],
            ),
            OpenApiParameter(
                "crews",
                description="Filtering by crew id (ex. ?crews=1,2)",
                type={"type": "array", "items": {"type": "number"}},
                examples=[
                    OpenApiExample(name="Example 1", value="3"),
                    OpenApiExample(name="Example 2", value="2"),
                ],
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """Endpoint for listing movies"""
        return super().list(request, *args, **kwargs)


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = Journey.objects.all()

    def get_queryset(self):
        queryset = self.queryset
        if self.action == ("list", "retrieve"):
            return queryset.select_related()
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return JourneyListSerializer
        elif self.action == "retrieve":
            return JourneyRetrieveSerializer
        return JourneySerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)

        if self.action == "list":
            queryset = queryset.prefetch_related("tickets__journey__train")
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
