#!/usr/bin/env bash

python autodistintivos.py \
  --template "plantillas/SelloDIGITAL_PLANTILLA.pdf" \
  --template-xy 240 480 \
  --template-wh 120 120 \
  --logos-dir nuevos_logos \
  --destination-dir distintivos/digital_ok

python autodistintivos.py \
  --template "plantillas/SelloIMPRESO_PLANTILLA-1-2.pdf" \
  --template-xy 255 365 \
  --template-wh 120 120 \
  --logos-dir nuevos_logos \
  --destination-dir distintivos/impreso_ok
