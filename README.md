# AI-Assisted Box Selection System

A small Django + Django REST Framework service that recommends the
cheapest shipping box able to hold a given order, based on each
product's dimensions/weight and each box's internal dimensions,
maximum weight capacity, and cost.

## Problem

An ecommerce warehouse needs to know, for every order, which box to
pack it into. Each **product** has length, width, height, and weight.
Each **box** has internal length, width, height, a maximum weight
capacity, and a cost. Given an order (one or more products, each with
a quantity), the system should recommend a box that:

1. Is strong enough to hold the total weight of the order.
2. Is large enough to hold the total volume of the order.
3. Can physically fit every individual item (checked with rotation
   allowed — an item can be laid on any side).
4. Among all boxes satisfying 1–3, is the **cheapest**. Ties are
   broken by picking the smaller box, then alphabetically by name, so
   the result is always deterministic.

## Project layout

```
box_selector_project/
├── manage.py
├── requirements.txt
├── box_selector_project/      # Django project settings/urls
└── boxes/                     # The app containing all the logic
    ├── models.py               # Product, Box, Order, OrderItem
    ├── services.py             # select_box() — the core algorithm
    ├── serializers.py          # DRF request/response shapes
    ├── views.py                # /api/recommend-box/ and CRUD viewsets
    ├── urls.py
    ├── admin.py
    └── tests.py                # 17 unit + integration tests
```

## The algorithm (`boxes/services.py`)

The selection logic is deliberately kept as a **pure, framework-free
function**, `select_box(items, available_boxes)`, so it can be tested
without touching the database and reused anywhere (API, admin,
management command, etc.). Django model instances are converted to
plain `PackItem`/`PackBox` dataclasses at the boundary
(`recommend_box_for_order()`).

- **Fit check (with rotation):** an item fits a box if, after sorting
  both the item's and the box's three dimensions ascending, every
  item dimension is ≤ the corresponding box dimension. Sorting first
  is what allows "rotating" the item to whichever orientation lets it
  fit, without enumerating all 6 rotations explicitly.
- **Weight check:** total order weight (`Σ quantity × item weight`)
  must not exceed the box's `max_weight_kg`.
- **Volume check:** total order volume (`Σ quantity × item volume`)
  must not exceed the box's internal volume. This is a simplifying
  approximation — true 3D bin-packing (fitting arbitrary combinations
  of boxes without gaps) is a much harder problem, and volume-sum is
  a standard, practical heuristic for this kind of assignment.
- **Selection:** among all boxes that pass every check, pick the one
  with the lowest `cost`.

This is a heuristic, not an exact 3D packer. It is documented as a
known limitation in `AI_USAGE.md`.

## Setup

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser   # optional, for /admin/
python manage.py runserver
```

## API

### `POST /api/recommend-box/`

Accepts a list of order items. Each item is either an existing
product (`product_id`) or an inline, one-off item description.

```bash
curl -X POST http://localhost:8000/api/recommend-box/ \
  -H "Content-Type: application/json" \
  -d '{
        "items": [
          {"product_id": 1, "quantity": 2},
          {"name": "Extra gadget", "length_cm": 10, "width_cm": 8,
           "height_cm": 4, "weight_kg": 0.6, "quantity": 1}
        ]
      }'
```

Successful response (`200`):

```json
{
  "recommended_box": {
    "id": 2,
    "name": "Medium",
    "internal_length_cm": "30.00",
    "internal_width_cm": "30.00",
    "internal_height_cm": "30.00",
    "max_weight_kg": "10.000",
    "cost": "3.50"
  },
  "order_total_weight_kg": "2.6",
  "order_total_volume_cm3": "1200.0"
}
```

If no box can hold the order, the endpoint returns `422` with a
`detail` message. If the request body is malformed (e.g. no items, or
an item missing required fields), it returns `400`.

### `GET/POST /api/products/`, `GET/POST /api/boxes/`

Standard CRUD viewsets for managing the `Product` and `Box` catalogs,
so you can create test data via the API instead of only the admin.

## Running the tests

```bash
python manage.py test boxes -v 2
```

17 tests cover: the core algorithm in isolation (fit checks, rotation,
weight limits, volume accumulation across quantities, tie-breaking,
error cases), the Django-model-backed convenience wrapper, and the
`/api/recommend-box/` HTTP endpoint end to end. See `TEST_OUTPUT.md`
for a captured run.

## Known limitations

- Volume-sum is used instead of true 3D bin packing, so in rare edge
  cases (e.g. many oddly-shaped items that don't tessellate) the
  recommended box could theoretically be tighter than reality allows.
- The system assumes a single box per order; it doesn't currently
  support splitting one order across multiple boxes.
- No authentication is configured on the API — this was left at
  Django defaults since the assignment scope is the recommendation
  logic itself, not production hardening.
