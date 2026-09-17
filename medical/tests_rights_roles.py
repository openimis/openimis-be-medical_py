from core.rights_role_test_case import RightsRoleGraphQLTestCase
from core.test_helpers import (
    create_medical_advisor_role,
    create_raf_role,
    create_right_only_user,
    create_role_user,
)
from location.test_helpers import create_basic_test_locations
from medical.test_helpers import create_test_item, create_test_service


ITEMS_QUERY = """
query {
  medicalItems(first: 5) {
    edges { node { id code } }
  }
}
"""

SERVICES_QUERY = """
query {
  medicalServices(first: 5) {
    edges { node { id code } }
  }
}
"""

VALIDATE_ITEM = """
query {
  validateItemCode(itemCode: "NO-SUCH-ITEM")
}
"""

VALIDATE_SERVICE = """
query {
  validateServiceCode(serviceCode: "NO-SUCH-SVC")
}
"""


class MedicalRightsTests(RightsRoleGraphQLTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        create_basic_test_locations()
        create_test_item("A")
        create_test_service("A")

    def test_query_medical_items_right(self):
        allowed = create_right_only_user(
            "r_med_i", ["gql_query_medical_items_perms"], district_codes=self.DISTRICT_CODES
        )
        denied = create_right_only_user("r_med_i_no", [], district_codes=self.DISTRICT_CODES)
        self.assert_gql_ok(allowed, VALIDATE_ITEM)
        self.assert_gql_unauthorized(denied, VALIDATE_ITEM)
        self.assert_gql_ok(allowed, ITEMS_QUERY)

    def test_query_medical_services_right(self):
        allowed = create_right_only_user(
            "r_med_s",
            ["gql_query_medical_services_perms"],
            district_codes=self.DISTRICT_CODES,
        )
        denied = create_right_only_user("r_med_s_no", [], district_codes=self.DISTRICT_CODES)
        self.assert_gql_ok(allowed, VALIDATE_SERVICE)
        self.assert_gql_unauthorized(denied, VALIDATE_SERVICE)
        self.assert_gql_ok(allowed, SERVICES_QUERY)


class MedicalRoleTests(RightsRoleGraphQLTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        create_basic_test_locations()
        create_test_item("A")
        create_test_service("A")
        cls.users = {
            "medical_advisor": create_role_user(
                "med_ma", create_medical_advisor_role(), district_codes=cls.DISTRICT_CODES
            ),
            "raf": create_role_user(
                "med_raf", create_raf_role(), district_codes=cls.DISTRICT_CODES
            ),
        }

    def test_roles_can_query_medical_catalog(self):
        for name, user in self.users.items():
            with self.subTest(role=name):
                self.assert_user_has_named_perms(user, ["gql_query_medical_items_perms"])
                self.assert_user_has_named_perms(
                    user, ["gql_query_medical_services_perms"]
                )
                self.assert_gql_ok(user, VALIDATE_ITEM)
                self.assert_gql_ok(user, VALIDATE_SERVICE)
                self.assert_gql_ok(user, ITEMS_QUERY)
                self.assert_gql_ok(user, SERVICES_QUERY)
