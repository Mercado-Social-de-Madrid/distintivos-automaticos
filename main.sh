#!/usr/bin/env bash

python autodistintivos.py \
  --template "plantillas/SelloDIGITAL_PLANTILLA.pdf" \
  --template-logo-xy 240 480 \
  --template-logo-wh 120 120 \
  --logos-dir nuevos_logos \
  --destination-dir distintivos/digital_ok

python autodistintivos.py \
  --template "plantillas/SelloIMPRESO_PLANTILLA-1-2.pdf" \
  --template-logo-xy 255 365 \
  --template-logo-wh 120 120 \
  --template-qr-xy 170 265 \
  --template-qr-wh 120 120 \
  --logos-dir nuevos_logos \
  --qrs-dir qrs \
  --destination-dir distintivos/impreso_ok
