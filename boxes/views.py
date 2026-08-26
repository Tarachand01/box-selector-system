from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Box, Product
from .serializers import (
    BoxSerializer,
    ProductSerializer,
    RecommendBoxRequestSerializer,
)
from .services import NoSuitableBoxError, PackBox, PackItem, select_box


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class BoxViewSet(viewsets.ModelViewSet):
    queryset = Box.objects.all()
    serializer_class = BoxSerializer


class RecommendBoxView(APIView):
    """POST /api/recommend-box/

    Body:
        {
          "items": [
            {"product_id": 1, "quantity": 2},
            {"name": "Mystery item", "length_cm": 10, "width_cm": 5,
             "height_cm": 5, "weight_kg": 0.5, "quantity": 1}
          ]
        }

    Returns the cheapest available box that fits every item and the
    order's total weight, or a 404-style error payload if none fit.
    """

    def post(self, request):
        serializer = RecommendBoxRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        pack_items = []
        for raw_item in serializer.validated_data["items"]:
            quantity = raw_item["quantity"]
            if "product_id" in raw_item:
                product = get_object_or_404(Product, pk=raw_item["product_id"])
                pack_items.append(
                    PackItem(
                        name=product.name,
                        length_cm=product.length_cm,
                        width_cm=product.width_cm,
                        height_cm=product.height_cm,
                        weight_kg=product.weight_kg,
                        quantity=quantity,
                    )
                )
            else:
                pack_items.append(
                    PackItem(
                        name=raw_item.get("name", "Unnamed item"),
                        length_cm=raw_item["length_cm"],
                        width_cm=raw_item["width_cm"],
                        height_cm=raw_item["height_cm"],
                        weight_kg=raw_item["weight_kg"],
                        quantity=quantity,
                    )
                )

        boxes = Box.objects.all()
        pack_boxes = [
            PackBox(
                name=b.name,
                internal_length_cm=b.internal_length_cm,
                internal_width_cm=b.internal_width_cm,
                internal_height_cm=b.internal_height_cm,
                max_weight_kg=b.max_weight_kg,
                cost=b.cost,
            )
            for b in boxes
        ]

        try:
            chosen = select_box(pack_items, pack_boxes)
        except NoSuitableBoxError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        chosen_box = boxes.get(name=chosen.name)
        total_weight = sum(item.quantity * item.weight_kg for item in pack_items)
        total_volume = sum(item.quantity * item.volume_cm3 for item in pack_items)

        return Response(
            {
                "recommended_box": BoxSerializer(chosen_box).data,
                "order_total_weight_kg": total_weight,
                "order_total_volume_cm3": total_volume,
            },
            status=status.HTTP_200_OK,
        )
