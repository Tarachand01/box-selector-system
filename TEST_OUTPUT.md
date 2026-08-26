# Test Run Output

Command:

```bash
python manage.py test boxes -v 2
```

Captured output:

```
Found 17 test(s).
Creating test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
Operations to perform:
  Synchronize unmigrated apps: messages, rest_framework, staticfiles
  Apply all migrations: admin, auth, boxes, contenttypes, sessions
Synchronizing apps without migrations:
  Creating tables...
    Running deferred SQL...
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying admin.0003_logentry_add_action_flag_choices... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying auth.0008_alter_user_username_max_length... OK
  Applying auth.0009_alter_user_last_name_max_length... OK
  Applying auth.0010_alter_group_name_max_length... OK
  Applying auth.0011_update_proxy_permissions... OK
  Applying auth.0012_alter_user_first_name_max_length... OK
  Applying boxes.0001_initial... OK
  Applying sessions.0001_initial... OK
System check identified no issues (0 silenced).
test_recommend_returns_400_for_empty_items (boxes.tests.RecommendBoxAPITests.test_recommend_returns_400_for_empty_items) ... ok
test_recommend_returns_400_when_item_missing_required_fields (boxes.tests.RecommendBoxAPITests.test_recommend_returns_400_when_item_missing_required_fields) ... ok
test_recommend_returns_422_when_nothing_fits (boxes.tests.RecommendBoxAPITests.test_recommend_returns_422_when_nothing_fits) ... ok
test_recommend_with_existing_product_id (boxes.tests.RecommendBoxAPITests.test_recommend_with_existing_product_id) ... ok
test_recommend_with_inline_item_dimensions (boxes.tests.RecommendBoxAPITests.test_recommend_with_inline_item_dimensions) ... ok
test_recommends_large_box_when_quantity_is_high (boxes.tests.RecommendBoxForOrderModelTests.test_recommends_large_box_when_quantity_is_high) ... ok
test_recommends_small_box_for_single_widget (boxes.tests.RecommendBoxForOrderModelTests.test_recommends_small_box_for_single_widget) ... ok
test_accounts_for_combined_volume_of_multiple_items (boxes.tests.SelectBoxUnitTests.test_accounts_for_combined_volume_of_multiple_items) ... ok
test_allows_rotation_to_fit_item (boxes.tests.SelectBoxUnitTests.test_allows_rotation_to_fit_item) ... ok
test_picks_cheapest_among_multiple_fitting_boxes (boxes.tests.SelectBoxUnitTests.test_picks_cheapest_among_multiple_fitting_boxes) ... ok
test_picks_the_only_box_that_fits (boxes.tests.SelectBoxUnitTests.test_picks_the_only_box_that_fits) ... ok
test_quantity_multiplies_weight_and_volume (boxes.tests.SelectBoxUnitTests.test_quantity_multiplies_weight_and_volume) ... ok
test_raises_on_empty_order (boxes.tests.SelectBoxUnitTests.test_raises_on_empty_order) ... ok
test_raises_when_item_too_heavy_for_every_box (boxes.tests.SelectBoxUnitTests.test_raises_when_item_too_heavy_for_every_box) ... ok
test_raises_when_item_too_large_for_every_box (boxes.tests.SelectBoxUnitTests.test_raises_when_item_too_large_for_every_box) ... ok
test_raises_when_no_boxes_available (boxes.tests.SelectBoxUnitTests.test_raises_when_no_boxes_available) ... ok
test_ties_on_cost_broken_by_smaller_volume (boxes.tests.SelectBoxUnitTests.test_ties_on_cost_broken_by_smaller_volume) ... ok

----------------------------------------------------------------------
Ran 17 tests in 0.024s

OK
Destroying test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
```

**Note:** this capture is from the development/verification run during
initial build. Per the assignment, re-run this yourself and either
replace this file with your own terminal output or link a GitHub
Actions run instead.
