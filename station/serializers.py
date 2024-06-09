from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Station, Route, TrainType, Train, Crew, Journey, Order, Ticket


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = '__all__'


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = '__all__'


class RouteListSerializer(RouteSerializer):
    source = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name',
    )
    destination = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name',
    )


class RouteRetrieveSerializer(RouteSerializer):
    source = StationSerializer()
    destination = StationSerializer()


class TrainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = '__all__'


class CrewSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Crew
        fields = ["id", "full_name"]


class TrainSerializer(serializers.ModelSerializer):
    total_capacity = serializers.ReadOnlyField()


    class Meta:
        model = Train
        fields = '__all__'


class TrainListSerializer(TrainSerializer):
    train_type = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'
    )


class TrainRetrieveSerializer(TrainSerializer):
    train_type = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'
    )


class JourneySerializer(serializers.ModelSerializer):
    travel_duration = serializers.ReadOnlyField()

    class Meta:
        model = Journey
        fields = '__all__'


class JourneyListSerializer(serializers.ModelSerializer):
    train_name = serializers.CharField(source='train.name', read_only=True)
    source = serializers.CharField(source='route.source.name', read_only=True)
    destination = serializers.CharField(source='route.destination.name', read_only=True)
    available_tickets = serializers.SerializerMethodField()

    class Meta:
        model = Journey
        fields = ['id', 'train_name', 'source', 'destination', 'departure_time', 'arrival_time', 'travel_duration', 'available_tickets']

    def get_available_tickets(self, obj):
        booked_tickets = Ticket.objects.filter(journey=obj).count()
        return obj.train.total_capacity - booked_tickets


class JourneyRetrieveSerializer(JourneySerializer):
    train = TrainSerializer()
    crew = CrewSerializer(many=True, read_only=True)
    routes = RouteListSerializer(many=True, read_only=True)


class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = ("id", "cargo", "seat", "journey", "order")

    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs=attrs)
        Ticket.validate_ticket(
            attrs["cargo"],
            attrs["seat"],
            attrs["journey"].train,
            ValidationError,
        )
        return data


class TicketListSerializer(TicketSerializer):
    journey = serializers.SerializerMethodField()
    order = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = ("id", "cargo", "seat", "journey", "order")

    def get_journey(self, obj):
        return str(obj.journey)

    def get_order(self, obj):
        return str(obj.order)


class TickerRetrieveSerializer(TicketSerializer):
    journey = serializers.SerializerMethodField()
    order = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = ("id", "cargo", "seat", "journey", "order", "ticket_taken")

    def get_journey(self, obj):
        return str(obj.journey)

    def get_order(self, obj):
        return str(obj.order)


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "tickets", "created_at")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)

