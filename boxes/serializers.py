from decimal import Decimal

from rest_framework import serializers

from .models import Box, Order, OrderItem, Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "length_cm",
            "width_cm",
            "height_cm",
            "weight_kg",
        ]


class BoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Box
        fields = [
            "id",
            "name",
            "internal_length_cm",
            "internal_width_cm",
            "internal_height_cm",
            "max_weight_kg",
            "cost",
        ]


class OrderItemInputSerializer(serializers.Serializer):
    """Accepts either an existing product_id, or an inline product
    description (useful for quickly trying the recommendation endpoint
    without first creating Product rows).
    """

    product_id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False)
    length_cm = serializers.DecimalField(max_digits=8, decimal_places=2, required=False)
    width_cm = serializers.DecimalField(max_digits=8, decimal_places=2, required=False)
    height_cm = serializers.DecimalField(max_digits=8, decimal_places=2, required=False)
    weight_kg = serializers.DecimalField(max_digits=8, decimal_places=3, required=False)
    quantity = serializers.IntegerField(default=1, min_value=1)

    def validate(self, data):
        has_product_id = "product_id" in data
        has_inline_dims = all(
            key in data for key in ("length_cm", "width_cm", "height_cm", "weight_kg")
        )
        if not has_product_id and not has_inline_dims:
            raise serializers.ValidationError(
                "Provide either 'product_id' or all of "
                "'length_cm', 'width_cm', 'height_cm', 'weight_kg'."
            )
        return data


class RecommendBoxRequestSerializer(serializers.Serializer):
    items = OrderItemInputSerializer(many=True)

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("An order needs at least one item.")
        return value
