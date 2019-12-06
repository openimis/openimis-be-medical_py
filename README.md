# openIMIS Backend Medical reference module
This repository holds the files of the openIMIS Backend Medical reference module.
It is dedicated to be deployed as a module of [openimis-be_py](https://github.com/openimis/openimis-be_py).

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

## Code climat (develop branch)

[![Maintainability](https://img.shields.io/codeclimate/maintainability/openimis/openimis-be-medical_py.svg)](https://codeclimate.com/github/openimis/openimis-be-medical_py/maintainability)
[![Test Coverage](https://img.shields.io/codeclimate/coverage/openimis/openimis-be-medical_py.svg)](https://codeclimate.com/github/openimis/openimis-be-medical_py)

## ORM mapping:
* tblICDCodes > Diagnosis
* tblItems > Item
* tblServices > Service

## Listened Django Signals
None

## Services
None

## Reports (template can be overloaded via report.ReportDefinition)
None

## GraphQL Queries
* diagnoses
* diagnoses_str: full text search on Diagnosis code + name
* medical_items
* medical_items_str: full text search on Diagnosis code + name
* medical_services
* medical_services_str: full text search on Diagnosis code + name

## GraphQL Mutations - each mutation emits default signals and return standard error lists (cfr. openimis-be-core_py)
None

## Configuration options (can be changed via core.ModuleConfiguration)

## openIMIS Modules Dependencies
* gql_query_diagnosis_perms: required rights to call diagnoses and diagnoses_str gql(default: [])
* gql_query_medical_items_perms: required rights to call medical_items and medical_items_str gql(default: [])
* gql_query_medical_services_perms: required rights to call medical_services and medical_services_str gql(default: [])