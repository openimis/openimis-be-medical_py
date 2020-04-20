from medical.models import Service, Item


def get_service_of_category(category, valid=True):
    return Service.objects.filter(category=category).filter(validity_to__isnull=valid).first()


def get_item_of_type(item_type, valid=True):
    return Item.objects.filter(type=item_type).filter(validity_to__isnull=valid).first()


def create_test_service(category, valid=True, custom_props={}):
    return Service.objects.create(
        **{
            "code": "TST-" + category,
            "category": category,
            "name": "Test service " + category,
            "type": Service.TYPE_CURATIVE,
            "level": 1,
            "price": 100,
            "patient_category": 15,
            "care_type": Service.CARE_TYPE_OUT_PATIENT,
            "validity_from": "2019-06-01",
            "validity_to": None if valid else "2019-06-01",
            "audit_user_id": -1,
            **custom_props
        }
    )


def create_test_item(item_type, valid=True, custom_props=None):
    return Item.objects.create(
        **{
            "code": "XXX",
            "type": item_type,
            "name": "Test item",
            "price": 100,
            "patient_category": 15,
            "care_type": 1,
            "validity_from": "2019-06-01",
            "validity_to": None if valid else "2019-06-01",
            "audit_user_id": -1,
            **(custom_props if custom_props else {})
        }
    )
