from django.apps import AppConfig

from core.rights_declaration import RightsDeclaration

MODULE_NAME = "medical"


# Rights, by entity then by action. Two distinct entities - the medical item and the
# medical service - each in its own block of identifiers (1221xx and 1214xx).
#
# `diagnosis.query` stays without an identifier: there is no neighbouring read right to
# alias it onto (a diagnosis is neither an item nor a service), and the item and service
# reads are themselves open by design (OMT-281 exemption). Giving it an identifier of
# its own, or declaring it open reference data, is a product decision, not a rename.
DJANGO_PERMS = {
    "medicalItem": {
        "query": ("medical.view_item", 122101),
        "create": ("medical.add_item", 122102),
        "update": ("medical.change_item", 122103),
        "delete": ("medical.delete_item", 122104),
    },
    "medicalService": {
        "query": ("medical.view_service", 121401),
        "create": ("medical.add_service", 121402),
        "update": ("medical.change_service", 121403),
        "delete": ("medical.delete_service", 121404),
    },
}

_PERM_CFG = {
    "gql_query_medical_items_perms": ("medicalItem", "query"),
    "gql_mutation_medical_items_add_perms": ("medicalItem", "create"),
    "gql_mutation_medical_items_update_perms": ("medicalItem", "update"),
    "gql_mutation_medical_items_delete_perms": ("medicalItem", "delete"),
    "gql_query_medical_services_perms": ("medicalService", "query"),
    "gql_mutation_medical_services_add_perms": ("medicalService", "create"),
    "gql_mutation_medical_services_update_perms": ("medicalService", "update"),
    "gql_mutation_medical_services_delete_perms": ("medicalService", "delete"),
}

RIGHTS = RightsDeclaration(MODULE_NAME, DJANGO_PERMS, _PERM_CFG)

perms = RIGHTS.perms
django_perms = RIGHTS.django_perm_names
configured_perms = RIGHTS.configured
require = RIGHTS.require


DEFAULT_CFG = {
    # Still [] - deliberately left, not overlooked. There is no sibling read right to
    # alias onto: medical's two reads are medical_items (122101) and medical_services
    # (121401), and a Diagnosis is neither, so pointing this at either would gate the
    # ICD list on an unrelated entity. Meanwhile [] means `resolve_diagnoses_str` is
    # readable by any authenticated user.
    #
    # Note the module is inconsistent here: medical_items/medical_services are openly
    # readable *on purpose* (their has_perms is commented out, OMT-281), while this one
    # does check - it just checks nothing. Two ways to settle it, both a decision
    # rather than a rename: mint a dedicated id for diagnoses, or declare them the same
    # documented open reference data as items and services.
}


class MedicalConfig(AppConfig):
    name = MODULE_NAME

    # Rights: constants, no longer overridable. They go neither through DEFAULT_CFG
    # nor through ready(): `ModuleConfiguration.get_or_default` now ignores any
    # `_perms` key stored in the database.
    gql_query_diagnosis_perms = []
    gql_query_medical_items_perms = RIGHTS.perms("medicalItem", "query")
    gql_query_medical_services_perms = RIGHTS.perms("medicalService", "query")
    gql_mutation_medical_items_add_perms = RIGHTS.perms("medicalItem", "create")
    gql_mutation_medical_items_update_perms = RIGHTS.perms("medicalItem", "update")
    gql_mutation_medical_items_delete_perms = RIGHTS.perms("medicalItem", "delete")
    gql_mutation_medical_services_add_perms = RIGHTS.perms("medicalService", "create")
    gql_mutation_medical_services_update_perms = RIGHTS.perms("medicalService", "update")
    gql_mutation_medical_services_delete_perms = RIGHTS.perms("medicalService", "delete")

    def __load_config(self, cfg):
        for field in cfg:
            if hasattr(MedicalConfig, field):
                setattr(MedicalConfig, field, cfg[field])

    def ready(self):
        from core.models import ModuleConfiguration
        cfg = ModuleConfiguration.get_or_default(MODULE_NAME, DEFAULT_CFG)
        self.__load_config(cfg)
