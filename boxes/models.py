from django.core.exceptions import ValidationError
from django.db import models


class Product(models.Model):
    """A sellable item with physical dimensions and weight.

    All dimensions are stored in centimetres and weight in kilograms so
    that every model in the app shares one consistent unit system.
    """

    name = models.CharField(max_length=255)
    length_cm = models.DecimalField(max_digits=8, decimal_places=2)
    width_cm = models.DecimalField(max_digits=8, decimal_places=2)
    height_cm = models.DecimalField(max_digits=8, decimal_places=2)
    weight_kg = models.DecimalField(max_digits=8, decimal_places=3)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def clean(self):
        for field_name in ("length_cm", "width_cm", "height_cm", "weight_kg"):
            value = getattr(self, field_name)
            if value is not None and value <= 0:
                raise ValidationError({field_name: "Must be a positive number."})

    @property
    def volume_cm3(self):
        return self.length_cm * self.width_cm * self.height_cm

    @property
    def sorted_dimensions(self):
        """Dimensions sorted ascending, so rotation of the item is allowed
        when checking whether it fits inside a box."""
        return sorted([self.length_cm, self.width_cm, self.height_cm])


class Box(models.Model):
    """A shipping box the warehouse can pack an order into."""

    name = models.CharField(max_length=255)
    internal_length_cm = models.DecimalField(max_digits=8, decimal_places=2)
    internal_width_cm = models.DecimalField(max_digits=8, decimal_places=2)
    internal_height_cm = models.DecimalField(max_digits=8, decimal_places=2)
    max_weight_kg = models.DecimalField(max_digits=8, decimal_places=3)
    cost = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["cost"]

    def __str__(self):
        return self.name

    def clean(self):
        for field_name in (
            "internal_length_cm",
            "internal_width_cm",
            "internal_height_cm",
            "max_weight_kg",
            "cost",
        ):
            value = getattr(self, field_name)
            if value is not None and value <= 0:
                raise ValidationError({field_name: "Must be a positive number."})

    @property
    def volume_cm3(self):
        return self.internal_length_cm * self.internal_width_cm * self.internal_height_cm

    @property
    def sorted_dimensions(self):
        return sorted(
            [self.internal_length_cm, self.internal_width_cm, self.internal_height_cm]
        )


class Order(models.Model):
    """A customer order awaiting a box recommendation."""

    created_at = models.DateTimeField(auto_now_add=True)
    recommended_box = models.ForeignKey(
        Box, null=True, blank=True, on_delete=models.SET_NULL, related_name="orders"
    )

    def __str__(self):
        return f"Order #{self.pk}"

    @property
    def total_weight_kg(self):
        return sum(item.quantity * item.product.weight_kg for item in self.items.all())

    @property
    def total_volume_cm3(self):
        return sum(item.quantity * item.product.volume_cm3 for item in self.items.all())


class OrderItem(models.Model):
    """A line item: a product and how many units of it were ordered."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)

    def clean(self):
        if self.quantity is not None and self.quantity <= 0:
            raise ValidationError({"quantity": "Must be at least 1."})

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
