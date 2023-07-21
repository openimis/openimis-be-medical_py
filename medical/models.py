import uuid

from core.models import VersionedModel, ObjectMutation
from django.db import models
from core import models as core_models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from graphql import ResolveInfo
from django.conf import settings
import core
from medical.apps import MedicalConfig
from medical.services import set_item_or_service_deleted


class Diagnosis(core_models.VersionedModel):
    id = models.AutoField(db_column='ICDID', primary_key=True)
    code = models.CharField(db_column='ICDCode', max_length=6)
    name = models.CharField(db_column='ICDName', max_length=255)

    audit_user_id = models.IntegerField(db_column='AuditUserID')
    # row_id = models.BinaryField(db_column='RowID', blank=True, null=True)

    def __str__(self):
        return self.code + " " + self.name

    @classmethod
    def filter_queryset(cls, queryset=None):
        if queryset is None:
            queryset = cls.objects.all()
        queryset = queryset.filter(*core.filter_validity())
        return queryset

    @classmethod
    def get_queryset(cls, queryset, user):
        queryset = Diagnosis.filter_queryset(queryset)
        # GraphQL calls with an info object while Rest calls with the user itself
        if isinstance(user, ResolveInfo):
            user = user.context.user
        if settings.ROW_SECURITY and user.is_anonymous:
            return queryset.filter(id=-1)

        return queryset

    class Meta:
        managed = True
        db_table = 'tblICDCodes'


class ItemOrService:
    CARE_TYPE_OUT_PATIENT = "O"
    CARE_TYPE_IN_PATIENT = "I"
    CARE_TYPE_BOTH = "B"

    CARE_TYPE_VALUES = [CARE_TYPE_BOTH, CARE_TYPE_IN_PATIENT, CARE_TYPE_OUT_PATIENT]


class Item(VersionedModel, ItemOrService):
    id = models.AutoField(db_column='ItemID', primary_key=True)
    uuid = models.CharField(db_column='ItemUUID', max_length=36, default=uuid.uuid4, unique=True)
    code = models.CharField(db_column='ItemCode', max_length=6)
    name = models.CharField(db_column='ItemName', max_length=100)
    type = models.CharField(db_column='ItemType', max_length=1)
    package = models.CharField(db_column='ItemPackage', max_length=255, blank=True, null=True)
    price = models.DecimalField(db_column='ItemPrice', max_digits=18, decimal_places=2)
    quantity = models.DecimalField(db_column='Quantity', max_digits=18, decimal_places=2, null=True)
    maximum_amount = models.DecimalField(db_column='MaximumAmount', max_digits=18, decimal_places=2, null=True)
    care_type = models.CharField(db_column='ItemCareType', max_length=1)
    frequency = models.SmallIntegerField(db_column='ItemFrequency', blank=True, null=True)
    patient_category = models.SmallIntegerField(db_column='ItemPatCat')
    audit_user_id = models.IntegerField(db_column='AuditUserID')
    # row_id = models.BinaryField(db_column='RowID', blank=True, null=True)

    def __bool__(self):
        return self.code is not None and len(self.code) >= 1

    def __eq__(self, other):
        equals = isinstance(other, Item) and \
                 self.code == other.code and \
                 self.name == other.name and \
                 self.type == other.type and \
                 self.price == other.price and \
                 self.care_type == other.care_type and \
                 self.patient_category == other.patient_category and \
                 self.quantity == other.quantity and \
                 self.frequency == other.frequency

        if equals:
            # optional string field -> making sure that None and empty string are treated as the same to avoid saving history
            if bool(self.package) == bool(other.package):
                if self.package:
                    return self.package == other.package
                else:
                    return True

        return False

    def __str__(self):
        return self.code + " " + self.name

    def __hash__(self):
        return hash((self.code, self.id, self.name, self.type, self.price, self.care_type, self.patient_category))

    @classmethod
    def filter_queryset(cls, queryset=None):
        if queryset is None:
            queryset = cls.objects.all()
        queryset = queryset.filter(*core.filter_validity())
        return queryset

    @classmethod
    def get_queryset(cls, queryset, user, show_history=False):
        # GraphQL calls with an info object while Rest calls with the user itself
        if isinstance(user, ResolveInfo):
            user = user.context.user
        # OMT-281 only allow history if the user has full permission
        if show_history and user.has_perms(MedicalConfig.gql_query_medical_items_perms):
            queryset = Item.objects.all()
        else:
            queryset = Item.filter_queryset(queryset)
        if settings.ROW_SECURITY and user.is_anonymous:
            return queryset.filter(id=-1)

        return queryset

    # This method might raise problems with bulk delete using query sets
    # https://docs.djangoproject.com/en/3.2/topics/db/models/#overriding-predefined-model-methods
    def delete(self, hard_delete=False, *args, **kwargs):
        if hard_delete:
            super(Item, self).delete(*args, **kwargs)
        else:
            set_item_or_service_deleted(self, "item")

    class Meta:
        managed = True
        db_table = 'tblItems'

    TYPE_DRUG = "D"
    TYPE_MEDICAL_CONSUMABLE = "M"
    TYPE_VALUES = [TYPE_DRUG, TYPE_MEDICAL_CONSUMABLE]


@receiver(pre_save, sender=Item)
def save_history_on_update(sender, instance, **kwargs):
    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        # The object is being created for the first time, so no history save is needed
        return
    # Compare the old and new instances to see if any fields have changed
    if instance != old_instance:
        # One or more fields have changed, so save history
        old_instance.save_history()
        from core import datetime
        now = datetime.datetime.now()
        instance.validity_from = now


class Service(VersionedModel, ItemOrService):
    id = models.AutoField(db_column='ServiceID', primary_key=True)
    uuid = models.CharField(db_column='ServiceUUID',
                            max_length=36, default=uuid.uuid4, unique=True)
    # legacy_id = models.IntegerField(db_column='LegacyID', blank=True, null=True)
    category = models.CharField(db_column='ServCategory', max_length=1, blank=True, null=True)
    code = models.CharField(db_column='ServCode', max_length=6)
    name = models.CharField(db_column='ServName', max_length=100)
    type = models.CharField(db_column='ServType', max_length=1)
    level = models.CharField(db_column='ServLevel', max_length=1)
    price = models.DecimalField(db_column='ServPrice', max_digits=18, decimal_places=2)
    maximum_amount = models.DecimalField(db_column='MaximumAmount', max_digits=18, decimal_places=2, null=True)
    care_type = models.CharField(db_column='ServCareType', max_length=1)
    frequency = models.SmallIntegerField(db_column='ServFrequency', blank=True, null=True)
    patient_category = models.SmallIntegerField(db_column='ServPatCat')

    # validity_from = fields.DateTimeField(db_column='ValidityFrom', blank=True, null=True)
    # validity_to = fields.DateTimeField(db_column='ValidityTo', blank=True, null=True)
    audit_user_id = models.IntegerField(db_column='AuditUserID', blank=True, null=True)
    # row_id = models.BinaryField(db_column='RowID', blank=True, null=True)

    def __bool__(self):
        return self.code is not None and len(self.code) >= 1

    def __str__(self):
        return self.code + " " + self.name

    def __eq__(self, other):
        equals = isinstance(other, Service) and \
                 self.code == other.code and \
                 self.name == other.name and \
                 self.type == other.type and \
                 self.level == other.level and \
                 self.price == other.price and \
                 self.care_type == other.care_type and \
                 self.patient_category == other.patient_category and \
                 self.frequency == other.frequency

        if equals:
            # optional string field -> making sure that None and empty string are treated as the same to avoid saving history
            if bool(self.category) == bool(other.category):
                if self.category:
                    return self.category == other.category
                else:
                    return True

        return False

    def __hash__(self):
        return hash((self.code, self.id, self.name, self.type, self.price, self.care_type, self.patient_category))

    # This method might raise problems with bulk delete using query sets
    # https://docs.djangoproject.com/en/3.2/topics/db/models/#overriding-predefined-model-methods
    def delete(self, hard_delete=False, *args, **kwargs):
        if hard_delete:
            super(Service, self).delete(*args, **kwargs)
        else:
            set_item_or_service_deleted(self, "service")

    @classmethod
    def filter_queryset(cls, queryset=None):
        if queryset is None:
            queryset = cls.objects.all()
        queryset = queryset.filter(*core.filter_validity())
        return queryset

    @classmethod
    def get_queryset(cls, queryset, user, show_history=False):
        # GraphQL calls with an info object while Rest calls with the user itself
        if isinstance(user, ResolveInfo):
            user = user.context.user

        # OMT-281 only allow history if the user has full permission
        if show_history and user.has_perms(MedicalConfig.gql_query_medical_services_perms):
            queryset = Service.objects.all()
        else:
            queryset = Service.filter_queryset(queryset)
        if settings.ROW_SECURITY and user.is_anonymous:
            return queryset.filter(id=-1)

        return queryset

    class Meta:
        managed = True
        db_table = 'tblServices'

    TYPE_PREVENTATIVE = "P"
    TYPE_CURATIVE = "C"
    TYPE_VALUES = [TYPE_PREVENTATIVE, TYPE_CURATIVE]

    CATEGORY_SURGERY = "S"
    CATEGORY_DELIVERY = "D"
    CATEGORY_ANTENATAL = "A"
    CATEGORY_HOSPITALIZATION = "H"
    CATEGORY_CONSULTATION = "C"
    CATEGORY_OTHER = "O"
    CATEGORY_VISIT = "V"
    CATEGORY_VALUES = [CATEGORY_SURGERY, CATEGORY_DELIVERY, CATEGORY_ANTENATAL,
                       CATEGORY_HOSPITALIZATION, CATEGORY_CONSULTATION, CATEGORY_OTHER, CATEGORY_VISIT]

    LEVEL_SIMPLE_SERVICE = "S"
    LEVEL_VISIT = "V"
    LEVEL_DAY_HOSPITAL = "D"
    LEVEL_HOSPITAL_CARE = "H"
    LEVEL_VALUES = [LEVEL_SIMPLE_SERVICE, LEVEL_VISIT, LEVEL_DAY_HOSPITAL, LEVEL_HOSPITAL_CARE]


@receiver(pre_save, sender=Service)
def save_history_on_update(sender, instance, **kwargs):
    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        # The object is being created for the first time, so no history save is needed
        return
    # Compare the old and new instances to see if any fields have changed
    if instance != old_instance:
        # One or more fields have changed, so save history
        old_instance.save_history()
        from core import datetime
        now = datetime.datetime.now()
        instance.validity_from = now


class ItemMutation(core_models.UUIDModel, ObjectMutation):
    item = models.ForeignKey(Item, models.DO_NOTHING, related_name='mutations')
    mutation = models.ForeignKey(core_models.MutationLog, models.DO_NOTHING, related_name='items')

    class Meta:
        managed = True
        db_table = "medical_ItemMutation"


class ServiceMutation(core_models.UUIDModel, ObjectMutation):
    service = models.ForeignKey(Service, models.DO_NOTHING, related_name='mutations')
    mutation = models.ForeignKey(core_models.MutationLog, models.DO_NOTHING, related_name='services')

    class Meta:
        managed = True
        db_table = "medical_ServiceMutation"
