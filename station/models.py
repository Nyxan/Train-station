from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.db.models import UniqueConstraint


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


class Train(models.Model):
    name = models.CharField(max_length=100, unique=True)
    cargo_num = models.IntegerField()
    places_in_cargo = models.IntegerField()
    train_type = models.ForeignKey(TrainType, on_delete=models.CASCADE)

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

    @property
    def available_seats(self):
        booked_seats = Ticket.objects.filter(journey=self).aggregate(models.Sum('seat'))['seat__sum'] or 0
        return self.train.total_capacity - booked_seats

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
    journey = models.ForeignKey(Journey, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['journey', 'cargo', 'seat'], name='journey_seat__unique'),
        ]

    def clean(self):
        if not (1 <= self.seat <= self.journey.train.places_in_cargo):
            raise ValueError({
                "seat": f"seat must be in range [1, self.trip.bus.num_seats"
            })
        if not (1 <= self.cargo <= self.journey.train.cargo_num):
            raise ValueError({
                "seat": f"cargo must be in range [1, self.trip.bus.num_seats"
            })

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

