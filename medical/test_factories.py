import factory

from medical.models import Service, Item, Diagnosis


class DiagnosisFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Diagnosis

    code = factory.Sequence(lambda n: f"D-{n}")
    name = factory.LazyAttribute(lambda o: "Diagnostic " + o.code)
    audit_user_id = 1


class ServiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Service

    code = factory.Sequence(lambda n: f"TS-{n}")
    name = factory.LazyAttribute(lambda o: "test S service " + o.code)
    maximum_amount = 5000
    type = Service.TYPE_CURATIVE
    level = 1
    price = 100
    patient_category = 15
    care_type = Service.CARE_TYPE_BOTH
    validity_from = "2019-06-01"
    audit_user_id = -1


class ItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Item

    code = factory.Sequence(lambda n: f"TI-{n}")
    name = "Test item"
    quantity = 1
    maximum_amount = 225000
    price = 100
    patient_category = 15
    care_type = Item.CARE_TYPE_BOTH
    validity_from = "2019-06-01"
    audit_user_id = -1
