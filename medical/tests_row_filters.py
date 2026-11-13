"""get_queryset honours the OP-2029 validity contract (epic OP-3317, phase 1).

Explicit validity values return the expected rows; a caller asking for
nothing gets what it got before the contract existed.
"""

from django.test import TestCase

from core.test_helpers import assert_row_filters, create_test_interactive_user, mark_deleted
from medical.models import Diagnosis, Item, Service
from medical.test_helpers import create_test_diagnosis, create_test_item, create_test_service


class MedicalRowFiltersTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = create_test_interactive_user(username="medicalrowfilters")

    def test_diagnosis(self):
        live = create_test_diagnosis(custom_props={"code": "RWF1"})
        deleted = mark_deleted(create_test_diagnosis(custom_props={"code": "RWF2"}))
        assert_row_filters(
            self, Diagnosis, Diagnosis.objects.filter(id__in=[live.id, deleted.id]), self.user,
            live.id, deleted.id, default_hides_deleted=True,
        )

    def test_item(self):
        live = create_test_item("D", custom_props={"code": "RWF1"})
        deleted = mark_deleted(create_test_item("D", custom_props={"code": "RWF2"}))
        assert_row_filters(
            self, Item, Item.objects.filter(id__in=[live.id, deleted.id]), self.user,
            live.id, deleted.id, default_hides_deleted=True,
        )

    def test_service(self):
        live = create_test_service("A", custom_props={"code": "RWF1"})
        deleted = mark_deleted(create_test_service("A", custom_props={"code": "RWF2"}))
        assert_row_filters(
            self, Service, Service.objects.filter(id__in=[live.id, deleted.id]), self.user,
            live.id, deleted.id, default_hides_deleted=True,
        )

    def test_the_item_audit_trail_needs_the_items_right(self):
        from core.models.row_filters import Audits
        from core.test_helpers import create_test_role

        item = create_test_item("D", custom_props={"code": "RWF3"})
        copy_id = item.save_history()
        rows = Item.objects.filter(code="RWF3")
        self.assertIn(copy_id, Item.get_queryset(rows, self.user, audits=Audits.ALL).values_list("id", flat=True))
        no_right = create_test_interactive_user(
            username="medicalrowfiltersnoright", roles=[create_test_role(name="rowfilters-no-right").id]
        )
        self.assertNotIn(copy_id, Item.get_queryset(rows, no_right, audits=Audits.ALL).values_list("id", flat=True))
