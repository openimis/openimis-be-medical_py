from medical.models import Service, Item, Diagnosis
import random


def create_test_diagnosis(custom_props=None):
    if custom_props is None:
        custom_props = {}        
    diag = None
    if 'code' in custom_props:
        diag_id = custom_props.get('id')     
        diag = Diagnosis.objects.filter(id=diag_id).first()
    if not diag and 'code' in custom_props:
        code = custom_props.get('code')     
        diag = Diagnosis.objects.filter(code=code).first()
    if 'audit_user_id' not in custom_props:
        custom_props['audit_user_id'] = 1
    ref = str(random.randint(1, 999))
    custom_props['code'] = custom_props.pop('code', ('D-' + ref))
    custom_props['name'] = custom_props.pop('name', ('Diagnostic' + ref))
    if not diag:
        diag = Diagnosis.objects.create(**custom_props)
    return diag


def get_service_of_category(category, valid=True):
    return Service.objects.filter(category=category).filter(validity_to__isnull=valid).first()


def get_item_of_type(item_type, valid=True):
    return Item.objects.filter(type=item_type).filter(validity_to__isnull=valid).first()


def create_test_service(category, valid=True, custom_props=None):
    if custom_props is None:
        custom_props = {}
    else:
        custom_props = {k: v for k, v in custom_props.items() if hasattr(Service, k)}
    ref = str(random.randint(1, 999))
    code = custom_props.pop('code', ('TS-' + ref))
    name = custom_props.pop('name', ('test S service ' + ref))
    obj = Service.objects.filter(code=code, validity_to__isnull=valid).first()
    if obj is not None:
        if custom_props:
            Service.objects.filter(id=obj.id).update(**custom_props)
            obj.refresh_from_db()
    else:
        obj = Service.objects.create(
            **{
                "maximum_amount": 5000,
                "code": code,
                "category": category,
                "name": name,
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
    # reseting custom props to avoid having it in next calls
    return obj


def create_test_item(item_type, valid=True, custom_props=None):
    if custom_props is None:
        custom_props = {}
    else:
        custom_props = {k: v for k, v in custom_props.items() if hasattr(Item, k)} 
    code = custom_props.pop('code', ('TI-' + str(random.randint(1, 999))))  
        
    obj = Item.objects.filter(code=code, validity_to__isnull=valid).first()
    if obj is not None:
        if custom_props:
            Item.objects.filter(id=obj.id).update(**custom_props)
            obj.refresh_from_db()
    else:
        obj = Item.objects.create(
            **{
                "quantity":1,
                "maximum_amount":225000,
                "code": code,
                "type": item_type,
                "name": "Test item",
                "price": 100,
                "patient_category": 15,
                "care_type": 1,
                "validity_from": "2019-06-01",
                "validity_to": None if valid else "2019-06-01",
                "audit_user_id": -1,
                **custom_props
            }
        )

    return obj
