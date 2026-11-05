"""The fixture helpers must hand back what was asked for (OP-3198).

`create_test_service` and `create_test_item` build a code from
`random.randint(1, 999)` and reuse any row that already carries it. They used
to return that row untouched, so a caller asking for a service of category
"S" could be given a seeded one of category "A" - silently, and only when the
random number happened to collide. `get_claim_category` reads that field, so
the claim-category tests failed about one run in ten with no way to reproduce
it.
"""

from django.test import TestCase
from medical.models import Item, Service
from medical.test_helpers import create_test_item, create_test_service


class HelperHonoursTheRequestedKindTest(TestCase):
    def test_service_category_is_the_one_asked_for(self):
        existing = create_test_service("A", custom_props={"code": "TSCOLL"})
        self.assertEqual(existing.category, "A")

        # Service.code is varchar(6), hence the cramped names.
        # The collision the random code makes by accident, made on purpose:
        same_code = create_test_service("S", custom_props={"code": "TSCOLL"})

        self.assertEqual(same_code.id, existing.id, "expected the same row")
        self.assertEqual(same_code.category, "S")
        self.assertEqual(
            Service.objects.get(id=existing.id).category,
            "S",
            "the category was not persisted",
        )

    def test_item_type_is_the_one_asked_for(self):
        existing = create_test_item("D", custom_props={"code": "TICOLL"})
        self.assertEqual(existing.type, "D")

        same_code = create_test_item("M", custom_props={"code": "TICOLL"})

        self.assertEqual(same_code.id, existing.id, "expected the same row")
        self.assertEqual(same_code.type, "M")

    def test_a_fresh_code_still_creates_what_was_asked_for(self):
        created = create_test_service("H", custom_props={"code": "TSFRSH"})

        self.assertEqual(created.category, "H")
        self.assertEqual(Service.objects.get(code="TSFRSH").category, "H")
