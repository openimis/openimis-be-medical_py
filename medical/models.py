import uuid
from django.db import models
from core import fields


class Diagnosis(models.Model):
    id = models.AutoField(db_column='ICDID', primary_key=True)
    legacy_id = models.IntegerField(
        db_column='LegacyID', blank=True, null=True)
    code = models.CharField(db_column='ICDCode', max_length=6)
    name = models.CharField(db_column='ICDName', max_length=255)
    validity_from = fields.DateTimeField(db_column='ValidityFrom')
    validity_to = fields.DateTimeField(
        db_column='ValidityTo', blank=True, null=True)

    audit_user_id = models.IntegerField(db_column='AuditUserID')
    # row_id = models.BinaryField(db_column='RowID', blank=True, null=True)

    def __str__(self):
        return self.code + " " + self.name

    class Meta:
        managed = False
        db_table = 'tblICDCodes'


class Item(models.Model):
    id = models.AutoField(db_column='ItemID', primary_key=True)
    uuid = models.CharField(db_column='ItemUUID',
                            max_length=36, default=uuid.uuid4, unique=True)
    legacy_id = models.IntegerField(
        db_column='LegacyID', blank=True, null=True)
    code = models.CharField(db_column='ItemCode', max_length=6)
    name = models.CharField(db_column='ItemName', max_length=100)
    type = models.CharField(db_column='ItemType', max_length=1)
    package = models.CharField(
        db_column='ItemPackage', max_length=255, blank=True, null=True)
    price = models.DecimalField(
        db_column='ItemPrice', max_digits=18, decimal_places=2)
    care_type = models.CharField(db_column='ItemCareType', max_length=1)
    frequency = models.SmallIntegerField(
        db_column='ItemFrequency', blank=True, null=True)
    patient_category = models.SmallIntegerField(db_column='ItemPatCat')
    validity_from = fields.DateTimeField(db_column='ValidityFrom')
    validity_to = fields.DateTimeField(
        db_column='ValidityTo', blank=True, null=True)
    audit_user_id = models.IntegerField(db_column='AuditUserID')
    # row_id = models.BinaryField(db_column='RowID', blank=True, null=True)

    def __str__(self):
        return self.code + " " + self.name

    class Meta:
        managed = False
        db_table = 'tblItems'


class Service(models.Model):
    id = models.AutoField(db_column='ServiceID', primary_key=True)
    uuid = models.CharField(db_column='ServiceUUID',
                            max_length=36, default=uuid.uuid4, unique=True)
    legacy_id = models.IntegerField(
        db_column='LegacyID', blank=True, null=True)
    category = models.CharField(
        db_column='ServCategory', max_length=1, blank=True, null=True)
    code = models.CharField(db_column='ServCode', max_length=6)
    name = models.CharField(db_column='ServName', max_length=100)
    type = models.CharField(db_column='ServType', max_length=1)
    level = models.CharField(db_column='ServLevel', max_length=1)
    price = models.DecimalField(
        db_column='ServPrice', max_digits=18, decimal_places=2)
    care_type = models.CharField(db_column='ServCareType', max_length=1)
    frequency = models.SmallIntegerField(
        db_column='ServFrequency', blank=True, null=True)
    patient_category = models.SmallIntegerField(db_column='ServPatCat')

    validity_from = fields.DateTimeField(
        db_column='ValidityFrom', blank=True, null=True)
    validity_to = fields.DateTimeField(
        db_column='ValidityTo', blank=True, null=True)

    audit_user_id = models.IntegerField(
        db_column='AuditUserID', blank=True, null=True)
    # row_id = models.BinaryField(db_column='RowID', blank=True, null=True)

    def __str__(self):
        return self.code + " " + self.name

    class Meta:
        managed = False
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
