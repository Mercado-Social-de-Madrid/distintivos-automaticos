#!/usr/bin/env bash

python autodistintivos.py \
  --data-file datos/distintivos_plantillas_info_consolidado.csv \
  --template "plantillas/SelloDIGITAL_PLANTILLA.pdf" \
  --template-logo-xy 240 480 \
  --template-logo-wh 120 120 \
  --logos-dir logos \
  --destination-dir distintivos/digital

python autodistintivos.py \
  --data-file datos/distintivos_plantillas_info_consolidado.csv \
  --template "plantillas/SelloIMPRESO_PLANTILLA-1-2.pdf" \
  --template-logo-xy 255 365 \
  --template-logo-wh 120 120 \
  --template-qr-xy 170 265 \
  --template-qr-wh 120 120 \
  --logos-dir logos \
  --qrs-dir qrs \
  --destination-dir distintivos/impreso
