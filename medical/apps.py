from django.apps import AppConfig

MODULE_NAME = "medical"

DEFAULT_CFG = {
    "gql_query_diagnosis_perms": [],
    "gql_query_medical_items_perms": ['122101'],
    "gql_query_medical_services_perms": ['121401'],
    "gql_mutation_medical_items_add_perms": ['122102'],
    "gql_mutation_medical_items_update_perms": ['122103'],
    "gql_mutation_medical_items_delete_perms": ['122104'],
    "gql_mutation_medical_services_add_perms": ['121402'],
    "gql_mutation_medical_services_update_perms": ['121403'],
    "gql_mutation_medical_services_delete_perms": ['121404'],
}


class MedicalConfig(AppConfig):
    name = MODULE_NAME

    gql_query_diagnosis_perms = []
    gql_query_medical_items_perms = []
    gql_query_medical_services_perms = []
    gql_mutation_medical_items_add_perms = []
    gql_mutation_medical_items_update_perms = []
    gql_mutation_medical_items_delete_perms = []
    gql_mutation_medical_services_add_perms = []
    gql_mutation_medical_services_update_perms = []
    gql_mutation_medical_services_delete_perms = []

    def _configure_permissions(self, cfg):
        MedicalConfig.gql_query_diagnosis_perms = cfg["gql_query_diagnosis_perms"]
        MedicalConfig.gql_query_medical_items_perms = cfg["gql_query_medical_items_perms"]
        MedicalConfig.gql_query_medical_services_perms = cfg["gql_query_medical_services_perms"]
        MedicalConfig.gql_mutation_medical_items_add_perms = cfg["gql_mutation_medical_items_add_perms"]
        MedicalConfig.gql_mutation_medical_items_update_perms = cfg["gql_mutation_medical_items_update_perms"]
        MedicalConfig.gql_mutation_medical_items_delete_perms = cfg["gql_mutation_medical_items_delete_perms"]
        MedicalConfig.gql_mutation_medical_services_add_perms = cfg["gql_mutation_medical_services_add_perms"]
        MedicalConfig.gql_mutation_medical_services_update_perms = cfg["gql_mutation_medical_services_update_perms"]
        MedicalConfig.gql_mutation_medical_services_delete_perms = cfg["gql_mutation_medical_services_delete_perms"]

    def ready(self):
        from core.models import ModuleConfiguration
        cfg = ModuleConfiguration.get_or_default(MODULE_NAME, DEFAULT_CFG)
        self._configure_permissions(cfg)
