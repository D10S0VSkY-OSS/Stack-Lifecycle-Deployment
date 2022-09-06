#!/bin/sh -e
set -x

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place ../sld-api-backend/api_v1 --exclude=__init__.py                                   
autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place ../sld-api-backend/config --exclude=__init__.py                                   
autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place ../sld-api-backend/db --exclude=__init__.py                                       
autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place ../sld-api-backend/crud --exclude=__init__.py
autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place ../sld-api-backend/core --exclude=__init__.py   
autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place ../sld-api-backend/helpers --exclude=__init__.py
autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place ../sld-api-backend/schemas --exclude=__init__.py
autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place ../sld-api-backend/security --exclude=__init__.py
autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place ../sld-api-backend/tasks --exclude=__init__.py

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place ../sld-dashboard/ --exclude=__init__.py
autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place ../sld-remote-state --exclude=__init__.py
autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place ../sld-schedule --exclude=__init__.py

black ../sld-api-backend/
black ../sld-dashboard/
black ../sld-remote-state
black ../sld-schedule

isort ../sld-api-backend/ --skip=../sld-api-backend/env/
isort ../sld-dashboard/ --skip=../sld-dashboard/env/
isort ../sld-remote-state --skip=../sld-remote-state/env/
isort ../sld-schedule --skip=../sld-schedule/env/
