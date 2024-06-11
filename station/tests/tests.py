import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from station.models import Ticket, Journey, Route, Station, Train, TrainType, Order

ORDER_URL = reverse("station:order-list")
TRAIN_URL = reverse("station:train-list")
JOURNEY_URL = reverse("station:journey-list")
TICKET_URL = reverse("station:ticket-list")
JOURNEY_URL = reverse("station:journey-list")


class UnethenticatedTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(TRAIN_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # New tests
    def test_unauthenticated_cannot_list_trains(self):
        response = self.client.get(TRAIN_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_cannot_retrieve_train(self):
        train = Train.objects.create(
            name="Express Train",
            cargo_num=5,
            places_in_cargo=50,
            train_type=TrainType.objects.create(name="Type A"),
        )
        url = reverse("station:train-detail", args=[train.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com", password="password123"
        )
        self.client.force_authenticate(user=self.user)

    def test_authenticated_can_list_trains(self):
        Train.objects.create(
            name="Express Train",
            cargo_num=5,
            places_in_cargo=50,
            train_type=TrainType.objects.create(name="Type A"),
        )
        response = self.client.get(TRAIN_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_can_retrieve_train(self):
        train = Train.objects.create(
            name="Express Train",
            cargo_num=5,
            places_in_cargo=50,
            train_type=TrainType.objects.create(name="Type A"),
        )
        url = reverse("station:train-detail", args=[train.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], train.name)


class UnauthenticatedTicketApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TICKET_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTicketApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com", password="password123"
        )
        self.client.force_authenticate(self.user)
        self.train_type = TrainType.objects.create(name="Type A")
        self.train = Train.objects.create(
            name="Train 1", cargo_num=5, places_in_cargo=50, train_type=self.train_type
        )
        self.source = Station.objects.create(
            name="Source", latitude=10.0, longitude=20.0
        )
        self.destination = Station.objects.create(
            name="Destination", latitude=30.0, longitude=40.0
        )
        self.route = Route.objects.create(
            source=self.source, destination=self.destination, distance=100
        )
        self.journey = Journey.objects.create(
            route=self.route,
            train=self.train,
            departure_time=datetime.datetime.now(),
            arrival_time=datetime.datetime.now() + datetime.timedelta(hours=2),
        )
        self.order = Order.objects.create(user=self.user)
        self.ticket = Ticket.objects.create(
            cargo=1, seat=1, journey=self.journey, order=self.order
        )

    def test_retrieve_tickets(self):
        res = self.client.get(TICKET_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_ticket(self):
        payload = {
            "cargo": 2,
            "seat": 2,
            "journey": self.journey.id,
            "order": self.order.id,
        }
        res = self.client.post(TICKET_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_update_ticket(self):
        payload = {
            "cargo": 3,
            "seat": 3,
            "journey": self.journey.id,
            "order": self.order.id,
        }
        url = reverse("station:ticket-detail", args=[self.ticket.id])
        res = self.client.put(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_ticket(self):
        url = reverse("station:ticket-detail", args=[self.ticket.id])
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)


class UnauthenticatedOrderApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(ORDER_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedOrderApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com", password="password123"
        )
        self.client.force_authenticate(self.user)
        self.train_type = TrainType.objects.create(name="Type A")
        self.train = Train.objects.create(
            name="Train 1", cargo_num=5, places_in_cargo=50, train_type=self.train_type
        )
        self.source = Station.objects.create(
            name="Source", latitude=10.0, longitude=20.0
        )
        self.destination = Station.objects.create(
            name="Destination", latitude=30.0, longitude=40.0
        )
        self.route = Route.objects.create(
            source=self.source, destination=self.destination, distance=100
        )
        self.journey = Journey.objects.create(
            route=self.route,
            train=self.train,
            departure_time=datetime.datetime.now(),
            arrival_time=datetime.datetime.now() + datetime.timedelta(hours=2),
        )
        self.order = Order.objects.create(user=self.user)
        self.ticket = Ticket.objects.create(
            cargo=1, seat=1, journey=self.journey, order=self.order
        )

    def test_retrieve_orders(self):
        res = self.client.get(ORDER_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_order(self):
        payload = {
            "tickets": [
                {
                    "cargo": 1,
                    "seat": 1,
                    "journey": self.journey.id,  # Assume there's a journey with ID 1
                }
            ]
        }
        res = self.client.post(ORDER_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_update_order(self):
        payload = {
            "tickets": [
                {
                    "cargo": 1,
                    "seat": 2,
                    "journey": self.journey.id,  # Assume there's a journey with ID 1
                }
            ]
        }
        url = reverse("station:order-detail", args=[self.order.id])
        res = self.client.put(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_order(self):
        url = reverse("station:order-detail", args=[self.order.id])
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)


class UnauthenticatedJourneyApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(JOURNEY_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedJourneyApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com", password="password123"
        )
        self.client.force_authenticate(self.user)
        self.train_type = TrainType.objects.create(name="Type A")
        self.train = Train.objects.create(
            name="Train 1", cargo_num=5, places_in_cargo=50, train_type=self.train_type
        )
        self.source = Station.objects.create(
            name="Source", latitude=10.0, longitude=20.0
        )
        self.destination = Station.objects.create(
            name="Destination", latitude=30.0, longitude=40.0
        )
        self.route = Route.objects.create(
            source=self.source, destination=self.destination, distance=100
        )
        self.journey = Journey.objects.create(
            route=self.route,
            train=self.train,
            departure_time=datetime.datetime.now(),
            arrival_time=datetime.datetime.now() + datetime.timedelta(hours=2),
        )

    def test_retrieve_journeys(self):
        res = self.client.get(JOURNEY_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_journey(self):
        payload = {
            "route": self.route.id,
            "train": self.train.id,
            "departure_time": datetime.datetime.now().isoformat(),
            "arrival_time": (
                datetime.datetime.now() + datetime.timedelta(hours=2)
            ).isoformat(),
        }
        res = self.client.post(JOURNEY_URL, payload, format="json")
        print(res.data)  # Debugging information
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_update_journey(self):
        payload = {
            "route": self.route.id,
            "train": self.train.id,
            "departure_time": datetime.datetime.now().isoformat(),
            "arrival_time": (
                datetime.datetime.now() + datetime.timedelta(hours=3)
            ).isoformat(),
        }
        url = reverse("station:journey-detail", args=[self.journey.id])
        res = self.client.put(url, payload, format="json")
        print(res.data)  # Debugging information
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_journey(self):
        url = reverse("station:journey-detail", args=[self.journey.id])
        res = self.client.delete(url)
        print(res.data)  # Debugging information
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
