from rest_framework import serializers

from .models import Station, Route, TrainType, Train, Crew, Journey, Order, Ticket


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = '__all__'


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = '__all__'


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
    train_type = TrainTypeSerializer(read_only=True)


class JourneySerializer(serializers.ModelSerializer):
    travel_duration = serializers.ReadOnlyField()
    available_seats = serializers.ReadOnlyField()

    class Meta:
        model = Journey
        fields = '__all__'


class JourneyListSerializer(JourneySerializer):
    train = TrainSerializer()
    crew = CrewSerializer(many=True, read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'
