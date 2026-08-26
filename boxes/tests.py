from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APIClient

from .models import Box, Order, OrderItem, Product
from .services import (
    NoSuitableBoxError,
    PackBox,
    PackItem,
    recommend_box_for_order,
    select_box,
)


def make_item(l=10, w=10, h=10, weight=1, qty=1, name="item"):
    return PackItem(
        name=name,
        length_cm=Decimal(l),
        width_cm=Decimal(w),
        height_cm=Decimal(h),
        weight_kg=Decimal(weight),
        quantity=qty,
    )


def make_box(l=20, w=20, h=20, max_weight=10, cost=5, name="box"):
    return PackBox(
        name=name,
        internal_length_cm=Decimal(l),
        internal_width_cm=Decimal(w),
        internal_height_cm=Decimal(h),
        max_weight_kg=Decimal(max_weight),
        cost=Decimal(cost),
    )


class SelectBoxUnitTests(TestCase):
    """Tests against the pure select_box() function -- no database needed."""

    def test_picks_the_only_box_that_fits(self):
        item = make_item(l=15, w=15, h=15, weight=2)
        small_box = make_box(l=10, w=10, h=10, cost=1, name="small")
        big_box = make_box(l=20, w=20, h=20, cost=5, name="big")

        result = select_box([item], [small_box, big_box])

        self.assertEqual(result.name, "big")

    def test_picks_cheapest_among_multiple_fitting_boxes(self):
        item = make_item(l=5, w=5, h=5, weight=1)
        cheap_box = make_box(l=20, w=20, h=20, cost=2, name="cheap")
        pricey_box = make_box(l=20, w=20, h=20, cost=8, name="pricey")

        result = select_box([item], [cheap_box, pricey_box])

        self.assertEqual(result.name, "cheap")

    def test_ties_on_cost_broken_by_smaller_volume(self):
        item = make_item(l=5, w=5, h=5, weight=1)
        roomy = make_box(l=30, w=30, h=30, cost=5, name="roomy")
        snug = make_box(l=10, w=10, h=10, cost=5, name="snug")

        result = select_box([item], [roomy, snug])

        self.assertEqual(result.name, "snug")

    def test_allows_rotation_to_fit_item(self):
        # Item is long and thin: 25 x 4 x 4. It should still fit a box
        # that is 5 x 5 x 30 once rotated, even though it would not fit
        # if compared axis-for-axis without rotation.
        item = make_item(l=25, w=4, h=4, weight=1)
        rotated_fit_box = make_box(l=5, w=5, h=30, cost=3, name="tall-thin")

        result = select_box([item], [rotated_fit_box])

        self.assertEqual(result.name, "tall-thin")

    def test_raises_when_item_too_heavy_for_every_box(self):
        heavy_item = make_item(weight=50)
        light_box = make_box(max_weight=10)

        with self.assertRaises(NoSuitableBoxError):
            select_box([heavy_item], [light_box])

    def test_raises_when_item_too_large_for_every_box(self):
        huge_item = make_item(l=100, w=100, h=100, weight=1)
        small_box = make_box(l=10, w=10, h=10)

        with self.assertRaises(NoSuitableBoxError):
            select_box([huge_item], [small_box])

    def test_raises_on_empty_order(self):
        with self.assertRaises(NoSuitableBoxError):
            select_box([], [make_box()])

    def test_raises_when_no_boxes_available(self):
        with self.assertRaises(NoSuitableBoxError):
            select_box([make_item()], [])

    def test_accounts_for_combined_volume_of_multiple_items(self):
        # Two items which individually fit easily, but together exceed
        # the small box's volume, must bump the order up to the big box.
        item_a = make_item(l=15, w=15, h=15, weight=1, name="a")
        item_b = make_item(l=15, w=15, h=15, weight=1, name="b")
        small_box = make_box(l=16, w=16, h=16, cost=1, name="small")
        big_box = make_box(l=30, w=30, h=30, cost=5, name="big")

        result = select_box([item_a, item_b], [small_box, big_box])

        self.assertEqual(result.name, "big")

    def test_quantity_multiplies_weight_and_volume(self):
        # 5 units of a 3kg item exceed a 10kg-capacity box on weight
        # alone, even though a single unit would not.
        item = make_item(weight=3, qty=5)
        box = make_box(max_weight=10)

        with self.assertRaises(NoSuitableBoxError):
            select_box([item], [box])


class RecommendBoxForOrderModelTests(TestCase):
    """Tests exercising the Django ORM-backed convenience wrapper."""

    def setUp(self):
        self.small_box = Box.objects.create(
            name="Small",
            internal_length_cm=Decimal("20"),
            internal_width_cm=Decimal("20"),
            internal_height_cm=Decimal("20"),
            max_weight_kg=Decimal("5"),
            cost=Decimal("2.00"),
        )
        self.large_box = Box.objects.create(
            name="Large",
            internal_length_cm=Decimal("50"),
            internal_width_cm=Decimal("50"),
            internal_height_cm=Decimal("50"),
            max_weight_kg=Decimal("25"),
            cost=Decimal("6.00"),
        )
        self.product = Product.objects.create(
            name="Widget",
            length_cm=Decimal("10"),
            width_cm=Decimal("10"),
            height_cm=Decimal("10"),
            weight_kg=Decimal("1"),
        )

    def test_recommends_small_box_for_single_widget(self):
        order = Order.objects.create()
        OrderItem.objects.create(order=order, product=self.product, quantity=1)

        recommended = recommend_box_for_order(order)

        self.assertEqual(recommended, self.small_box)

    def test_recommends_large_box_when_quantity_is_high(self):
        order = Order.objects.create()
        # 20 widgets: total volume 20,000 cm3 exceeds the small box's
        # 8,000 cm3, so it must escalate to the large box.
        OrderItem.objects.create(order=order, product=self.product, quantity=20)

        recommended = recommend_box_for_order(order)

        self.assertEqual(recommended, self.large_box)


class RecommendBoxAPITests(TestCase):
    """Integration tests against the /api/recommend-box/ endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.box = Box.objects.create(
            name="Standard",
            internal_length_cm=Decimal("30"),
            internal_width_cm=Decimal("30"),
            internal_height_cm=Decimal("30"),
            max_weight_kg=Decimal("10"),
            cost=Decimal("3.50"),
        )
        self.product = Product.objects.create(
            name="Gadget",
            length_cm=Decimal("10"),
            width_cm=Decimal("10"),
            height_cm=Decimal("10"),
            weight_kg=Decimal("2"),
        )

    def test_recommend_with_existing_product_id(self):
        response = self.client.post(
            "/api/recommend-box/",
            {"items": [{"product_id": self.product.id, "quantity": 1}]},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["recommended_box"]["name"], "Standard")

    def test_recommend_with_inline_item_dimensions(self):
        response = self.client.post(
            "/api/recommend-box/",
            {
                "items": [
                    {
                        "name": "One-off item",
                        "length_cm": "5",
                        "width_cm": "5",
                        "height_cm": "5",
                        "weight_kg": "0.5",
                        "quantity": 1,
                    }
                ]
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["recommended_box"]["name"], "Standard")

    def test_recommend_returns_422_when_nothing_fits(self):
        response = self.client.post(
            "/api/recommend-box/",
            {
                "items": [
                    {
                        "name": "Boulder",
                        "length_cm": "500",
                        "width_cm": "500",
                        "height_cm": "500",
                        "weight_kg": "9999",
                        "quantity": 1,
                    }
                ]
            },
            format="json",
        )

        self.assertEqual(response.status_code, 422)

    def test_recommend_returns_400_for_empty_items(self):
        response = self.client.post("/api/recommend-box/", {"items": []}, format="json")

        self.assertEqual(response.status_code, 400)

    def test_recommend_returns_400_when_item_missing_required_fields(self):
        response = self.client.post(
            "/api/recommend-box/",
            {"items": [{"quantity": 1}]},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
