import random

from medical.models import Service, Item, Diagnosis
from medical.test_factories import DiagnosisFactory, ServiceFactory, ItemFactory


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
        diag = DiagnosisFactory(**custom_props)
    return diag


def get_service_of_category(category, valid=True):
    return Service.objects.filter(category=category).filter(validity_to__isnull=valid).first()


def get_item_of_type(item_type, valid=True):
    return Item.objects.filter(type=item_type).filter(validity_to__isnull=valid).first()


def create_test_service(category, valid=True, custom_props=None, create_history=False):
    custom_props = {k: v for k, v in (custom_props or {}).items() if hasattr(Service, k)}
    ref = str(random.randint(1, 999))
    code = custom_props.pop('code', ('TS-' + ref))
    name = custom_props.pop('name', ('test S service ' + ref))
    obj = Service.objects.filter(code=code, validity_to__isnull=valid).first()
    if obj is not None:
        if custom_props:
            Service.objects.filter(id=obj.id).update(**custom_props)
            obj.refresh_from_db()
    else:
        obj = ServiceFactory(
            **{
                "code": code,
                "category": category,
                "name": name,
                "validity_to": None if valid else "2019-06-01",
                **custom_props
            }
        )
    if create_history:
        obj.save_history()
    return obj


def create_test_item(item_type, valid=True, custom_props=None):
    custom_props = {k: v for k, v in (custom_props or {}).items() if hasattr(Item, k)}
    code = custom_props.pop('code', ('TI-' + str(random.randint(1, 999))))
    obj = Item.objects.filter(code=code, validity_to__isnull=valid).first()
    if obj is not None:
        if custom_props:
            Item.objects.filter(id=obj.id).update(**custom_props)
            obj.refresh_from_db()
    else:
        obj = ItemFactory(
            **{
                "code": code,
                "type": item_type,
                "validity_to": None if valid else "2019-06-01",
                **custom_props
            }
        )
    return obj
