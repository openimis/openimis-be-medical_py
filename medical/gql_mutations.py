import functools
from gettext import gettext as _
from operator import or_

import django.db.models.base
import graphene
from core import assert_string_length, PATIENT_CATEGORY_MASK_ADULT, PATIENT_CATEGORY_MASK_MALE, \
    PATIENT_CATEGORY_MASK_MINOR, PATIENT_CATEGORY_MASK_FEMALE
from core.schema import OpenIMISMutation
from medical.exceptions import CodeAlreadyExistsError
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError, PermissionDenied
from medical.apps import MedicalConfig
from medical.models import Service, ServiceMutation, Item, ItemMutation
from medical.services import set_item_or_service_deleted


class ServiceCodeInputType(graphene.String):
    @staticmethod
    def coerce_string(value):
        assert_string_length(value, 6)
        return value

    serialize = coerce_string
    parse_value = coerce_string

    @staticmethod
    def parse_literal(ast):
        result = graphene.String.parse_literal(ast)
        assert_string_length(result, 6)
        return result

# The following Enums would be more GraphQL friendly than the current String types but they are less configurable
# and actually make the frontend work harder, so leaving them here for illustration purpose, feel free to remove.
#
# SVC_TYPE_PREVENTATIVE = "PREVENTATIVE"
# SVC_TYPE_CURATIVE = "CURATIVE"
# ServiceTypeEnum = graphene.Enum("ServiceTypes", [
#     (SVC_TYPE_PREVENTATIVE, Service.TYPE_PREVENTATIVE),
#     (SVC_TYPE_CURATIVE, Service.TYPE_CURATIVE),
# ])
#
#
# CARE_TYPE_IN_PATIENT = "IN"
# CARE_TYPE_OUT_PATIENT = "OUT"
# CARE_TYPE_BOTH = "BOTH"
# CareTypeEnum = graphene.Enum("CareTypes", [
#     (CARE_TYPE_IN_PATIENT, Service.CARE_TYPE_IN_PATIENT),
#     (CARE_TYPE_OUT_PATIENT, Service.CARE_TYPE_OUT_PATIENT),
#     (CARE_TYPE_BOTH, Service.CARE_TYPE_BOTH),
# ])


# SERVICE_LEVEL_DAY_HOSPITAL = "DAY_HOSPITAL"
# SERVICE_LEVEL_VISIT = "VISIT"
# SERVICE_LEVEL_SIMPLE_SERVICE = "SIMPLE_SERVICE"
# SERVICE_LEVEL_HOSPITAL_CARE = "HOSPITAL_CARE"
# ServiceLevelEnum = graphene.Enum("ServiceLevels", [
#     (SERVICE_LEVEL_DAY_HOSPITAL, Service.LEVEL_DAY_HOSPITAL),
#     (SERVICE_LEVEL_VISIT, Service.LEVEL_VISIT),
#     (SERVICE_LEVEL_SIMPLE_SERVICE, Service.LEVEL_SIMPLE_SERVICE),
#     (SERVICE_LEVEL_HOSPITAL_CARE, Service.LEVEL_HOSPITAL_CARE),
# ])
#

PATIENT_CATEGORY_ADULT = "ADULT"
PATIENT_CATEGORY_MINOR = "MINOR"
PATIENT_CATEGORY_MALE = "MALE"
PATIENT_CATEGORY_FEMALE = "FEMALE"
PatientCategoriesEnum = graphene.Enum("PatientCategories", [
    (PATIENT_CATEGORY_ADULT, PATIENT_CATEGORY_MASK_ADULT),
    (PATIENT_CATEGORY_MINOR, PATIENT_CATEGORY_MASK_MINOR),
    (PATIENT_CATEGORY_MALE, PATIENT_CATEGORY_MASK_MALE),
    (PATIENT_CATEGORY_FEMALE, PATIENT_CATEGORY_MASK_FEMALE),
])


class ItemOrServiceInputType(OpenIMISMutation.Input):
    id = graphene.Int(required=False, read_only=True)
    uuid = graphene.String(required=False)
    code = ServiceCodeInputType(required=True)
    name = graphene.String(required=True)
    type = graphene.String(required=True)
    care_type = graphene.String(required=True)
    patient_category = graphene.Int(required=False)
    patient_categories = graphene.List(of_type=PatientCategoriesEnum, required=False)
    frequency = graphene.Decimal(required=False)
    price = graphene.Decimal(required=True)
    maximum_amount = graphene.Decimal(required=False)


class ServiceInputType(ItemOrServiceInputType):
    level = graphene.String(required=True)
    category = graphene.String(required=False)


def reset_item_or_service_before_update(item_service):
    fields = [
        "code",
        "name",
        "code",
        "name",
        "type",
        "price",
        "frequency",
        "care_type",
        "patient_category",
        "category",
        "level",    # service only
        "category", # service only
        "package",  # item only
        "quantity", # item only
    ]
    for field in fields:
        if hasattr(item_service, field):
            setattr(item_service, field, None)


def update_or_create_item_or_service(data, user, item_service_model):
    client_mutation_id = data.pop('client_mutation_id', None)
    data.pop('client_mutation_label', None)
    item_service_uuid = data.pop('uuid') if 'uuid' in data else None
    # update_or_create(uuid=service_uuid, ...)
    # doesn't work because of explicit attempt to set null to uuid!
    data["audit_user_id"] = user.id_for_audit

    incoming_code = data.get('code')
    item_service = item_service_model.objects.filter(uuid=item_service_uuid).first()
    current_code = item_service.code if item_service else None
    if current_code != incoming_code:
        check_if_code_already_exists(data, item_service_model)

    if item_service_uuid:
        reset_item_or_service_before_update(item_service)
        [setattr(item_service, key, data[key]) for key in data]
    else:
        item_service = item_service_model.objects.create(**data)

    item_service.save()
    if client_mutation_id:
        if isinstance(item_service, Service):
            ServiceMutation.object_mutated(user, client_mutation_id=client_mutation_id, service=item_service)
        elif isinstance(item_service, Item):
            ItemMutation.object_mutated(user, client_mutation_id=client_mutation_id, item=item_service)


def check_if_code_already_exists(
        data: dict,
        item_service_model: django.db.models.base.ModelBase
):
    if item_service_model.objects.all().filter(code=data['code'], validity_to__isnull=True).exists():
        raise CodeAlreadyExistsError(_("Code already exists."))


class CreateOrUpdateItemOrServiceMutation(OpenIMISMutation):
    @classmethod
    def do_mutate(cls, perms, user, **data):
        if type(user) is AnonymousUser or not user.id:
            raise ValidationError(
                _("mutation.authentication_required"))
        if not user.has_perms(perms):
            raise PermissionDenied(_("unauthorized"))

        # Patient categories a bit-wise masks,
        # one can specify the result in patient_category or a list in patient_categories
        patient_categories = data.pop("patient_categories", None)
        if patient_categories:
            data["patient_category"] = functools.reduce(or_, patient_categories)
        elif "patient_category" not in data:
            raise ValidationError(_("medical.mutation.patient_category_missing"))

        data['audit_user_id'] = user.id_for_audit
        from core.utils import TimeUtils
        data['validity_from'] = TimeUtils.now()
        update_or_create_item_or_service(data, user, cls.item_service_model)
        return None


class CreateServiceMutation(CreateOrUpdateItemOrServiceMutation):
    _mutation_module = "medical"
    _mutation_class = "CreateServiceMutation"
    item_service_model = Service

    class Input(ServiceInputType):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            return cls.do_mutate(MedicalConfig.gql_mutation_medical_services_add_perms, user, **data)
        except Exception as exc:
            return [{
                'message': _("service.mutation.failed_to_create_service") % {'code': data['code']},
                'detail': str(exc)}]


class UpdateServiceMutation(CreateOrUpdateItemOrServiceMutation):
    _mutation_module = "medical"
    _mutation_class = "UpdateServiceMutation"
    item_service_model = Service

    class Input(ServiceInputType):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            return cls.do_mutate(MedicalConfig.gql_mutation_medical_services_update_perms, user, **data)
        except Exception as exc:
            return [{
                'message': _("service.mutation.failed_to_update_service") % {'code': data['code']},
                'detail': str(exc)}]


class DeleteServiceMutation(OpenIMISMutation):
    _mutation_module = "medical"
    _mutation_class = "DeleteServiceMutation"

    class Input(OpenIMISMutation.Input):
        uuids = graphene.List(graphene.String)

    @classmethod
    def async_mutate(cls, user, **data):
        if not user.has_perms(MedicalConfig.gql_mutation_medical_services_delete_perms):
            raise PermissionDenied(_("unauthorized"))
        errors = []
        for service_uuid in data["uuids"]:
            service = Service.objects \
                .filter(uuid=service_uuid) \
                .first()
            if service is None:
                errors.append({
                    'title': service_uuid,
                    'list': [{'message': _(
                        "service.validation.id_does_not_exist") % {'id': service_uuid}}]
                })
                continue
            errors += set_item_or_service_deleted(service, "service")
        if len(errors) == 1:
            errors = errors[0]['list']
        return errors


class ItemInputType(ItemOrServiceInputType):
    package = graphene.String()
    quantity = graphene.Decimal()


class CreateItemMutation(CreateOrUpdateItemOrServiceMutation):
    _mutation_module = "medical"
    _mutation_class = "CreateItemMutation"
    item_service_model = Item

    class Input(ItemInputType):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            return cls.do_mutate(MedicalConfig.gql_mutation_medical_items_add_perms, user, **data)
        except Exception as exc:
            return [{
                'message': _("item.mutation.failed_to_create_item") % {'code': data['code']},
                'detail': str(exc)}]


class UpdateItemMutation(CreateOrUpdateItemOrServiceMutation):
    _mutation_module = "medical"
    _mutation_class = "UpdateItemMutation"
    item_service_model = Item

    class Input(ItemInputType):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            return cls.do_mutate(MedicalConfig.gql_mutation_medical_items_update_perms, user, **data)
        except Exception as exc:
            return [{
                'message': _("item.mutation.failed_to_update_item") % {'code': data['code']},
                'detail': str(exc)}]


class DeleteItemMutation(OpenIMISMutation):
    _mutation_module = "medical"
    _mutation_class = "DeleteItemMutation"

    class Input(OpenIMISMutation.Input):
        uuids = graphene.List(graphene.String)

    @classmethod
    def async_mutate(cls, user, **data):
        if not user.has_perms(MedicalConfig.gql_mutation_medical_items_delete_perms):
            raise PermissionDenied(_("unauthorized"))
        errors = []
        for item_uuid in data["uuids"]:
            item = Item.objects \
                .filter(uuid=item_uuid) \
                .first()
            if item is None:
                errors.append({
                    'title': item_uuid,
                    'list': [{'message': _(
                        "item.validation.id_does_not_exist") % {'id': item_uuid}}]
                })
                continue
            errors += set_item_or_service_deleted(item, "item")
        if len(errors) == 1:
            errors = errors[0]['list']
        return errors
