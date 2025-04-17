import base64
import json
from dataclasses import dataclass

from core.models import User
from core.test_helpers import create_test_interactive_user
from django.conf import settings
from graphene_django.utils.testing import GraphQLTestCase
from graphql_jwt.shortcuts import get_token
from medical.models import Item, ServiceItem, ServiceService
from medical.test_helpers import create_test_item, create_test_service
from medical.utils import item_create_hook, service_create_hook
from rest_framework import status

# from openIMIS import schema

from core.models.openimis_graphql_test_case import openIMISGraphQLTestCase, BaseTestContext


class MedicalGQLTestCase(openIMISGraphQLTestCase):
    GRAPHQL_URL = f'/{settings.SITE_ROOT()}graphql'
    # This is required by some version of graphene but is never used. It should be set to the schema but the import
    # is shown as an error in the IDE, so leaving it as True.
    GRAPHQL_SCHEMA = True
    admin_user = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.AUTH_HEADER = settings.GRAPHQL_JWT.get('JWT_AUTH_HEADER_PREFIX', 'Bearer')
        cls.admin_user = create_test_interactive_user(username="testMedicalAdmin")
        cls.admin_context = BaseTestContext(user=cls.admin_user)
        cls.admin_token = cls.admin_context.get_jwt()
        cls.noright_user = create_test_interactive_user(username="testMedicalNoRight", roles=[1])
        cls.noright_context = BaseTestContext(user=cls.noright_user)
        cls.noright_token = cls.noright_context.get_jwt()
        cls.test_item_hist = create_test_item(item_type="M", custom_props={
            "name": "Test history API", "code": "TSTAP9"})
        cls.test_item_hist.save_history()
        cls.test_item = create_test_item(item_type="M", custom_props={
            "name": "Test name API", "code": "TSTAP0", "package": "box of 12"})
        cls.test_service = create_test_service(category="A", custom_props={
            "name": "Test svc API", "code": "SVCAP0", "level": "C"})
        cls.test_item_update = create_test_item(item_type="M", custom_props={
            "name": "Test update API", "code": "TSTAP4", "package": "box of 1"})
        cls.test_service_update = create_test_service(category="A", custom_props={
            "name": "Test update API", "code": "SVCAP4", "level": "C"})
        cls.test_item_delete = create_test_item(item_type="M", custom_props={
            "name": "Test update API", "code": "TSTAP5", "package": "box of 1"})
        cls.test_service_delete = create_test_service(category="A", custom_props={
            "name": "Test update API", "code": "SVCAP5", "level": "C"})

    def _getItemFromAPI(self, code):
        response = self.query(
            '''
            query {
                medicalItems(code:"%s") {
                    edges {
                        node {
                            id name validityFrom validityTo legacyId uuid code type package price careType frequency
                                  patientCategory auditUserId
                        }
                    }
                }
            }
            ''' % (code,),
            headers={"HTTP_AUTHORIZATION": f"{self.AUTH_HEADER} {self.admin_token}"},
        )

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)

        self.assertResponseNoErrors(response)
        return content["data"]["medicalItems"]["edges"][0]["node"]

    def test_basic_services_query(self):
        response = self.query(
            '''
            query {
                medicalServices {
                    edges {
                        node {
                            id
                            name
                        }
                    }
                }
            }
            ''',
            headers={"HTTP_AUTHORIZATION": f"{self.AUTH_HEADER} {self.admin_token}"},
        )

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)

        # This validates the status code and if you get errors
        self.assertResponseNoErrors(response)

        # Add some more asserts if you like
        self.assertGreater(len(content["data"]["medicalServices"]["edges"]), 0)
        self.assertIsNotNone(content["data"]["medicalServices"]["edges"][0]["node"]["id"])
        self.assertIsNotNone(content["data"]["medicalServices"]["edges"][0]["node"]["name"])

    def _test_arg_services_query(self, arg):
        response = self.query(
            '''
            query {
                medicalServices(%s) {
                    edges {
                        node {
                            id
                            name
                            code
                        }
                    }
                }
            }
            ''' % (arg,),
            headers={"HTTP_AUTHORIZATION": f"{self.AUTH_HEADER} {self.admin_token}"},
        )

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)

        self.assertResponseNoErrors(response)

        self.assertEqual(len(content["data"]["medicalServices"]["edges"]), 1)
        self.assertEqual(content["data"]["medicalServices"]["edges"][0]["node"]["name"], self.test_service.name)
        self.assertEqual(content["data"]["medicalServices"]["edges"][0]["node"]["id"],
                         base64.b64encode(f"ServiceGQLType:{self.test_service.id}".encode("utf8")).decode("ascii"))

    def test_code_services_query(self):
        self._test_arg_services_query('code:"%s"' % self.test_service.code)
        self._test_arg_services_query('uuid:"%s"' % self.test_service.uuid)
        self._test_arg_services_query('careType:"%s", name_Icontains: "est svc AP"' % self.test_service.care_type)
        self._test_arg_services_query('category:"%s", name_Istartswith: "Test svc AP"' % self.test_service.category)

    def _test_arg_items_query(self, arg):
        response = self.query(
            '''
            query {
                medicalItems(%s) {
                    edges {
                        node {
                            id
                            name
                            code
                        }
                    }
                }
            }
            ''' % (arg,),
            headers={"HTTP_AUTHORIZATION": f"{self.AUTH_HEADER} {self.admin_token}"},
        )

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)

        # This validates the status code and if you get errors
        self.assertResponseNoErrors(response)

        # Add some more asserts if you like
        self.assertEqual(len(content["data"]["medicalItems"]["edges"]), 1)
        self.assertEqual(content["data"]["medicalItems"]["edges"][0]["node"]["name"], self.test_item.name)
        self.assertEqual(content["data"]["medicalItems"]["edges"][0]["node"]["id"],
                         base64.b64encode(f"ItemGQLType:{self.test_item.id}".encode("utf8")).decode("ascii"))

    def test_code_items_query(self):
        self._test_arg_items_query('code:"%s"' % self.test_item.code)
        self._test_arg_items_query('uuid:"%s"' % self.test_item.uuid)
        self._test_arg_items_query('package_Icontains:"%s", name_Icontains: "est name A"' % self.test_item.package)

    def test_no_auth_services_query(self):
        """ Query without any auth token """
        response = self.query(' query { medicalServices { edges { node { id name } } } } ')

        self.assertResponseHasErrors(response)

    def test_no_auth_items_query(self):
        """ Query without any auth token """
        response = self.query(' query { medicalItems { edges { node { id name } } } } ')

        self.assertResponseHasErrors(response)

    def test_no_right_services_query(self):
        """
        Query with a valid token but not the right to perform this full operation.
        Unlike some other modules, medical services and items are available to everyone but limited,
        i.e. no showHistory so we're accessing a modified service and make sure that history is not available.
        """
        query = 'query { medicalServices(showHistory: true, code:"M1") { edges { node { id name } } } }'
        response = self.query(query, headers={"HTTP_AUTHORIZATION": f"{self.AUTH_HEADER} {self.noright_token}"})
        response_admin = self.query(query, headers={"HTTP_AUTHORIZATION": f"{self.AUTH_HEADER} {self.admin_token}"})

        content = json.loads(response.content)
        content_admin = json.loads(response_admin.content)
        self.assertEqual(len(content["data"]["medicalServices"]["edges"]), 1)
        self.assertEqual(len(content_admin["data"]["medicalServices"]["edges"]), 2)

    def test_no_right_items_query(self):
        """
        Query with a valid token but not the right to perform this full operation.
        Unlike some other modules, medical services and items are available to everyone but limited,
        i.e. no showHistory so we're accessing a modified service and make sure that history is not available.
        """
        query = 'query { medicalItems(showHistory: true, code:"TSTAP9") { edges { node { id name } } } }'
        response = self.query(query, headers={"HTTP_AUTHORIZATION": f"{self.AUTH_HEADER} {self.noright_token}"})
        response_admin = self.query(query, headers={"HTTP_AUTHORIZATION": f"{self.AUTH_HEADER} {self.admin_token}"})

        content = json.loads(response.content)
        content_admin = json.loads(response_admin.content)
        self.assertEqual(len(content["data"]["medicalItems"]["edges"]), 1)
        self.assertEqual(len(content_admin["data"]["medicalItems"]["edges"]), 2)

    def test_basic_items_query(self):
        response = self.query(
            '''
            query {
                medicalItems {
                    edges {
                        node {
                            id
                            name
                        }
                    }
                }
            }
            ''',
            headers={"HTTP_AUTHORIZATION": f"{self.AUTH_HEADER} {self.admin_token}"},
        )

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)

        self.assertResponseNoErrors(response)

        self.assertGreater(len(content["data"]["medicalItems"]["edges"]), 0)
        self.assertIsNotNone(content["data"]["medicalItems"]["edges"][0]["node"]["id"])
        self.assertIsNotNone(content["data"]["medicalItems"]["edges"][0]["node"]["name"])

    def test_full_items_query(self):
        response = self.query(
            '''
            query {
                medicalItems {
                    edges {
                        node {
                                  id
                                  name
                                  validityFrom
                                  validityTo
                                  legacyId
                                  uuid
                                  code
                                  type
                                  package
                                  price
                                  careType
                                  frequency
                                  patientCategory
                                  auditUserId
                        }
                    }
                }
            }
            ''',
            headers={"HTTP_AUTHORIZATION": f"{self.AUTH_HEADER} {self.admin_token}"},
        )

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)

        self.assertResponseNoErrors(response)

        self.assertGreater(len(content["data"]["medicalItems"]["edges"]), 0)
        self.assertIsNotNone(content["data"]["medicalItems"]["edges"][0]["node"]["id"])
        self.assertIsNotNone(content["data"]["medicalItems"]["edges"][0]["node"]["name"])

    def test_mutation_create_item(self):
        response = self.query(
            '''
            mutation {
              createItem(input: {
                clientMutationId: "testapi2"
                code: "TSTAPI"
                name: "Auto test of create API"
                type: "D",
                maximumAmount: "225000.0",
                quantity: "2.0"
                careType: "B"
                patientCategory: 11
                price: "321"
                package: "box of 1"
              }) {
                internalId
                clientMutationId
              }
            }
            ''',
            headers={"HTTP_AUTHORIZATION": f"{self.AUTH_HEADER} {self.admin_token}"},
        )

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)

        self.assertResponseNoErrors(response)

        self.assertEqual(content["data"]["createItem"]["clientMutationId"], "testapi2")

        db_item = Item.objects.get(code="TSTAPI")
        self.assertIsNotNone(db_item)
        self.assertEqual(db_item.name, "Auto test of create API")
        self.assertEqual(db_item.type, Item.TYPE_DRUG)
        self.assertEqual(db_item.care_type, "B")
        self.assertEqual(db_item.patient_category, 11)
        self.assertEqual(db_item.price, 321)
        self.assertEqual(db_item.package, "box of 1")

        retrieved_item = self._getItemFromAPI(code="TSTAPI")
        self.assertIsNotNone(retrieved_item)
        self.assertEqual(retrieved_item["name"], db_item.name)

    def test_mutation_update_item(self):
        response = self.query(
            '''
            mutation {
              updateItem(input: {
                clientMutationId: "testapi4"
                uuid: "%s"
                code: "SVCAX4"
                name: "New name"
                type: "D"
                careType: "O"
                patientCategory: 5,
                quantity: "1.0"
                price: "555"
                package: "box of 12"
              }) {
                internalId
                clientMutationId
              }
            }
            ''' % self.test_item_update.uuid,
            headers={"HTTP_AUTHORIZATION": f"{self.AUTH_HEADER} {self.admin_token}"},
        )

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)

        self.assertResponseNoErrors(response)
        self.assertEqual(content["data"]["updateItem"]["clientMutationId"], "testapi4")

        self.test_item_update.refresh_from_db()

        self.assertEqual(self.test_item_update.name, "New name")
        self.assertEqual(self.test_item_update.type, Item.TYPE_DRUG)
        self.assertEqual(self.test_item_update.care_type, "O")
        self.assertEqual(self.test_item_update.patient_category, 5)
        self.assertEqual(self.test_item_update.price, 555)
        self.assertEqual(self.test_item_update.package, "box of 12")

    def test_mutation_update_service(self):
        response = self.query(
            '''
            mutation {
              updateService(input: {
                clientMutationId: "testapi4"
                uuid: "%s"
                code: "SVCAX4"
                name: "New name"
                type: "A"
                level: "H"
                careType: "O"
                patientCategory: 5
                price: "555"
                manualPrice: "0"
                packagetype: "S"
              }) {
                internalId
                clientMutationId
              }
            }
            ''' % self.test_service_update.uuid,
            headers={"HTTP_AUTHORIZATION": f"{self.AUTH_HEADER} {self.admin_token}"},
        )

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)

        self.assertResponseNoErrors(response)
        self.assertEqual(content["data"]["updateService"]["clientMutationId"], "testapi4")

        self.test_service_update.refresh_from_db()

        self.assertEqual(self.test_service_update.name, "New name")
        self.assertEqual(self.test_service_update.type, "A")
        self.assertEqual(self.test_service_update.care_type, "O")
        self.assertEqual(self.test_service_update.patient_category, 5)
        self.assertEqual(self.test_service_update.price, 555)
        self.assertEqual(self.test_service_update.level, "H")

    def test_mutation_delete_service(self):
        response = self.query(
            '''
            mutation {
              deleteService(input: {
                uuids: ["%s"]
                clientMutationId: "testapi5"
              }) {
                internalId
                clientMutationId
              }
            }
            ''' % self.test_service_delete.uuid,
            headers={"HTTP_AUTHORIZATION": f"{self.AUTH_HEADER} {self.admin_token}"},
        )

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)

        self.assertResponseNoErrors(response)
        self.assertEqual(content["data"]["deleteService"]["clientMutationId"], "testapi5")

        self.test_service_delete.refresh_from_db()

        self.assertIsNotNone(self.test_service_delete.validity_to)

    def test_mutation_delete_item(self):
        response = self.query(
            '''
            mutation {
              deleteItem(input: {
                uuids: ["%s"]
                clientMutationId: "testapi5"
              }) {
                internalId
                clientMutationId
              }
            }
            ''' % self.test_item_delete.uuid,
            headers={"HTTP_AUTHORIZATION": f"{self.AUTH_HEADER} {self.admin_token}"},
        )

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        content = json.loads(response.content)

        self.assertResponseNoErrors(response)
        self.assertEqual(content["data"]["deleteItem"]["clientMutationId"], "testapi5")

        self.test_item_delete.refresh_from_db()

        self.assertIsNotNone(self.test_item_delete.validity_to)

    def test_process_child_relation(self):
        self.query(
            '''
            mutation {
              updateService(input: {
                clientMutationId: "testapi4"
                uuid: "%s"
                code: "SVCAX4"
                name: "New name"
                type: "A"
                level: "H"
                careType: "O"
                patientCategory: 5
                price: "555"
                manualPrice: "0"
                packagetype: "S"
                services:  [
                    {
                        serviceId: %s,
                        priceAsked: "600.00",
                        qtyProvided: "1.00",
                        status: 1
                    }
                ]
                items:  [
                    {
                        itemId: %s,
                        priceAsked: "1200.00",
                        qtyProvided: "800.00",
                        status: 1
                    }
                ]
              }) {
                internalId
                clientMutationId
              }
            }
            ''' % (self.test_service_update.uuid, self.test_service.id, self.test_item.id),
            headers={"HTTP_AUTHORIZATION": f"{self.AUTH_HEADER} {self.admin_token}"},
        )
        self.get_mutation_result('testapi4', self.admin_token)
        self.test_service_update.refresh_from_db()
        serv_item = ServiceItem.objects.filter(parent=self.test_service_update.id).first()
        self.assertEquals(serv_item.price_asked, 1200)
        self.assertEquals(serv_item.qty_provided, 800)
        self.assertEquals(serv_item.item.id, self.test_item.id)

        service_serv = ServiceService.objects.filter(parent=self.test_service_update.id).first()
        self.assertEquals(service_serv.price_asked, 600)
        self.assertEquals(service_serv.qty_provided, 1)
        self.assertEquals(service_serv.service.id, self.test_service.id)