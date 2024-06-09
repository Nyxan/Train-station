import os
import uuid

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.db.models import UniqueConstraint
from django.utils.text import slugify
from rest_framework.exceptions import ValidationError


class Station(models.Model):
    name = models.CharField(max_length=100, unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name

    class Meta:
        unique_together = (('latitude', 'longitude'),)
        ordering = ('name',)
        verbose_name = 'Station'
        verbose_name_plural = 'Stations'


class Route(models.Model):
    source = models.ForeignKey(Station, related_name='source_routes', on_delete=models.CASCADE)
    destination = models.ForeignKey(Station, related_name='destination_routes', on_delete=models.CASCADE)
    distance = models.IntegerField()

    def __str__(self):
        return f'{self.source} to {self.destination}'

    class Meta:
        unique_together = (('source', 'destination'),)
        ordering = ('source', 'destination')
        verbose_name = 'Route'
        verbose_name_plural = 'Routes'


class TrainType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


def train_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.name)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/movies/", filename)


class Train(models.Model):
    name = models.CharField(max_length=100, unique=True)
    cargo_num = models.IntegerField()
    places_in_cargo = models.IntegerField()
    train_type = models.ForeignKey(TrainType, on_delete=models.CASCADE)
    image = models.ImageField(null=True, upload_to=train_image_file_path)

    @property
    def total_capacity(self):
        return self.cargo_num * self.places_in_cargo

    def __str__(self):
        return self.name


class Crew(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f'{self.full_name}'

    class Meta:
        unique_together = (('first_name', 'last_name'),)


class Journey(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    train = models.ForeignKey(Train, on_delete=models.CASCADE)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew, related_name='journeys')

    @property
    def travel_duration(self):
        duration = self.arrival_time - self.departure_time
        days = duration.days
        hours, remainder = divmod(duration.seconds, 3600)
        return f"{days} days, {hours} hours"

    def __str__(self):
        return f'Journey on {self.departure_time} from {self.route}'

    class Meta:
        indexes = [
            models.Index(fields=['route', 'train']),
            models.Index(fields=['departure_time', 'arrival_time']),
        ]


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user} {self.created_at}'

    class Meta:
        ordering = ['-created_at']


class Ticket(models.Model):
    cargo = models.IntegerField()
    seat = models.IntegerField()
    journey = models.ForeignKey(Journey, on_delete=models.CASCADE, related_name="tickets")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="tickets")

    class Meta:
        constraints = [
            UniqueConstraint(fields=['journey', 'cargo', 'seat'], name='journey_seat_unique'),
        ]

    @staticmethod
    def validate_ticket(cargo, seat, train, error_to_raise):
        for ticket_attr_value, ticket_attr_name, train_attr_name in [
            (cargo, "cargo", "cargo_num"),
            (seat, "seat", "places_in_cargo"),
        ]:
            count_attrs = getattr(train, train_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name} "
                        f"number must be in available range: "
                        f"(1, {train_attr_name}): "
                        f"(1, {count_attrs})"
                    }
                )

    def clean(self):
        Ticket.validate_ticket(
            self.cargo,
            self.seat,
            self.journey.train,
            ValidationError,
        )

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert, force_update, using, update_fields
        )

    def __str__(self):
        return f'{self.journey} {self.cargo} {self.seat}'

