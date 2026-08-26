"""Core box-selection logic, kept independent of the request/response cycle
so it can be unit tested directly and reused from the API view, the admin,
or a management command.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable, List, Optional, Sequence


@dataclass
class PackItem:
    """A lightweight, framework-agnostic stand-in for an OrderItem."""

    name: str
    length_cm: Decimal
    width_cm: Decimal
    height_cm: Decimal
    weight_kg: Decimal
    quantity: int = 1

    @property
    def volume_cm3(self) -> Decimal:
        return self.length_cm * self.width_cm * self.height_cm

    @property
    def sorted_dimensions(self) -> List[Decimal]:
        return sorted([self.length_cm, self.width_cm, self.height_cm])


@dataclass
class PackBox:
    """A lightweight, framework-agnostic stand-in for a Box."""

    name: str
    internal_length_cm: Decimal
    internal_width_cm: Decimal
    internal_height_cm: Decimal
    max_weight_kg: Decimal
    cost: Decimal

    @property
    def volume_cm3(self) -> Decimal:
        return self.internal_length_cm * self.internal_width_cm * self.internal_height_cm

    @property
    def sorted_dimensions(self) -> List[Decimal]:
        return sorted(
            [self.internal_length_cm, self.internal_width_cm, self.internal_height_cm]
        )


class NoSuitableBoxError(Exception):
    """Raised when no available box can hold the order."""


def _item_fits_in_box(item: PackItem, box: PackBox) -> bool:
    """An item fits if, after freely rotating it, each of its dimensions
    is no larger than the box's corresponding dimension.

    Comparing the dimensions sorted ascending is what allows rotation:
    it checks the item's smallest side against the box's smallest side,
    and so on, rather than assuming a fixed orientation.
    """
    return all(
        item_dim <= box_dim
        for item_dim, box_dim in zip(item.sorted_dimensions, box.sorted_dimensions)
    )


def _box_can_hold_order(items: Sequence[PackItem], box: PackBox) -> bool:
    total_weight = sum(item.quantity * item.weight_kg for item in items)
    if total_weight > box.max_weight_kg:
        return False

    total_volume = sum(item.quantity * item.volume_cm3 for item in items)
    if total_volume > box.volume_cm3:
        return False

    # Every individual item must physically fit inside the box; volume
    # alone doesn't rule out a single oversized item in an otherwise
    # roomy-enough box.
    return all(_item_fits_in_box(item, box) for item in items)


def select_box(
    items: Iterable[PackItem], available_boxes: Iterable[PackBox]
) -> PackBox:
    """Return the cheapest box able to hold all given items.

    Ties on cost are broken by choosing the smaller box (less wasted
    space / dead air in shipping), then alphabetically by name for a
    fully deterministic result.

    Raises NoSuitableBoxError if no box in `available_boxes` can hold
    the order, or if `items` is empty.
    """
    items = list(items)
    if not items:
        raise NoSuitableBoxError("Cannot recommend a box for an empty order.")

    candidates = [box for box in available_boxes if _box_can_hold_order(items, box)]
    if not candidates:
        raise NoSuitableBoxError(
            "No available box is large or strong enough for this order."
        )

    return min(candidates, key=lambda box: (box.cost, box.volume_cm3, box.name))


def recommend_box_for_order(order, boxes: Optional[Iterable] = None):
    """Convenience wrapper for Django Order/Box model instances.

    Converts them to the framework-agnostic PackItem/PackBox dataclasses
    and delegates to select_box().
    """
    from .models import Box  # local import to avoid a hard Django dependency above

    if boxes is None:
        boxes = Box.objects.all()

    pack_items = [
        PackItem(
            name=oi.product.name,
            length_cm=oi.product.length_cm,
            width_cm=oi.product.width_cm,
            height_cm=oi.product.height_cm,
            weight_kg=oi.product.weight_kg,
            quantity=oi.quantity,
        )
        for oi in order.items.select_related("product").all()
    ]
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

    chosen = select_box(pack_items, pack_boxes)

    # Map the chosen PackBox back to its Django Box instance by name.
    return next(b for b in boxes if b.name == chosen.name)
