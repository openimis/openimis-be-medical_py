import string
import uuid

from core.models import VersionedModel, ObjectMutation
from django.db import models
from django.utils import timezone as django_tz 
from core import models as core_models
from graphql import ResolveInfo
from django.conf import settings
import core
from medical.apps import MedicalConfig
from medical import models as medical_models

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
        managed = False
        db_table = 'tblICDCodes'


class Item(VersionedModel):
    id = models.AutoField(db_column='ItemID', primary_key=True)
    uuid = models.CharField(db_column='ItemUUID', max_length=36, default=uuid.uuid4, unique=True)
    code = models.CharField(db_column='ItemCode', max_length=6)
    name = models.CharField(db_column='ItemName', max_length=100)
    type = models.CharField(db_column='ItemType', max_length=1)
    package = models.CharField(db_column='ItemPackage', max_length=255, blank=True, null=True)
    price = models.DecimalField(db_column='ItemPrice', max_digits=18, decimal_places=2)
    quantity = models.DecimalField(db_column='Quantity', max_digits=18, decimal_places=2, null=True)
    care_type = models.CharField(db_column='ItemCareType', max_length=1)
    frequency = models.SmallIntegerField(db_column='ItemFrequency', blank=True, null=True)
    patient_category = models.SmallIntegerField(db_column='ItemPatCat')
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

    class Meta:
        managed = False
        db_table = 'tblItems'

    TYPE_DRUG = "D"
    TYPE_MEDICAL_CONSUMABLE = "M"


class Service(VersionedModel):
    id = models.AutoField(db_column='ServiceID', primary_key=True)
    uuid = models.CharField(db_column='ServiceUUID',
                            max_length=36, default=uuid.uuid4, unique=True)
    # legacy_id = models.IntegerField(db_column='LegacyID', blank=True, null=True)
    category = models.CharField(db_column='ServCategory', max_length=1, blank=True, null=True)
    code = models.CharField(db_column='ServCode', max_length=6)
    name = models.CharField(db_column='ServName', max_length=100)
    type = models.CharField(db_column='ServType', max_length=1)
    packagetype = models.CharField(db_column='ServPackageType', max_length=1, default="S")
    manualPrice = models.BooleanField(default=False)
    level = models.CharField(db_column='ServLevel', max_length=1)
    price = models.DecimalField(db_column='ServPrice', max_digits=18, decimal_places=2)
    care_type = models.CharField(db_column='ServCareType', max_length=1)
    frequency = models.SmallIntegerField(db_column='ServFrequency', blank=True, null=True)
    patient_category = models.SmallIntegerField(db_column='ServPatCat', default="15")

    # validity_from = fields.DateTimeField(db_column='ValidityFrom', blank=True, null=True)
    # validity_to = fields.DateTimeField(db_column='ValidityTo', blank=True, null=True)
    #
    audit_user_id = models.IntegerField(db_column='AuditUserID', blank=True, null=True)
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

    CARE_TYPE_OUT_PATIENT = "O"
    CARE_TYPE_IN_PATIENT = "I"
    CARE_TYPE_BOTH = "B"

    CATEGORY_SURGERY = "S"
    CATEGORY_DELIVERY = "D"
    CATEGORY_ANTENATAL = "A"
    CATEGORY_HOSPITALIZATION = "H"
    CATEGORY_CONSULTATION = "C"
    CATEGORY_OTHER = "O"
    CATEGORY_VISIT = "V"

    LEVEL_SIMPLE_SERVICE = "S"
    LEVEL_VISIT = "V"
    LEVEL_DAY_HOSPITAL = "D"
    LEVEL_HOSPITAL_CARE = "H"


class ServiceService(models.Model):
    """class representing relation between package and services """
    id = models.AutoField(primary_key=True, db_column='idSCP')
    service = models.ForeignKey(Service, models.DO_NOTHING,
                              db_column='ServiceId', related_name='servicesServices')
    servicelinkedService = models.ForeignKey( Service,
                                          models.DO_NOTHING, db_column="ServiceLinked")
    qty_provided = models.IntegerField(db_column="qty",
                                      blank=True, null=True)
    scpDate = models.DateTimeField(db_column="created_date", default=django_tz.now,
                                   blank=True, null=True)
    price_asked = models.DecimalField(db_column="price",
                                   max_digits=18, decimal_places=2, blank=True, null=True)
    status = models.BooleanField(default=True)

    class Meta:
        managed = True
        db_table = 'tblServiceContainedPackage'


class ServiceItem(models.Model):
    """class representing relation between package and product """
    id = models.AutoField(primary_key=True, db_column='idPCP')
    item = models.ForeignKey(Item, models.DO_NOTHING, db_column='ItemID', related_name="itemsServices")                           
    servicelinkedItem = models.ForeignKey( Service,
                                          models.DO_NOTHING, db_column="ServiceID",related_name='servicesLinked')
    qty_provided = models.IntegerField(db_column="qty",
                                      blank=True, null=True)
    pcpDate = models.DateTimeField(db_column="created_date", default=django_tz.now,
                                   blank=True, null=True)
    price_asked = models.DecimalField(db_column="price",
                                   max_digits=18, decimal_places=2, blank=True, null=True)
    status = models.BooleanField(default=True)
    
    class Meta:
        managed = True
        db_table = 'tblProductContainedPackage'



class ItemMutation(core_models.UUIDModel, core_models.ObjectMutation):
    item = models.ForeignKey(Item, models.DO_NOTHING, related_name='mutations')
    mutation = models.ForeignKey(core_models.MutationLog, models.DO_NOTHING, related_name='items')

    class Meta:
        managed = True
        db_table = "medical_ItemMutation"


class ServiceMutation(core_models.UUIDModel, core_models.ObjectMutation):
    service = models.ForeignKey(Service, models.DO_NOTHING, related_name='mutations')
    mutation = models.ForeignKey(core_models.MutationLog, models.DO_NOTHING, related_name='services')

    class Meta:
        managed = True
        db_table = "medical_ServiceMutation"
