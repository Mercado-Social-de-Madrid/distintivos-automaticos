#!/usr/bin/env bash

python autodistintivos.py \
  --data-file "datos/Distintivo 20_Plantillas_info.csv" \
  --template "plantillas/SelloDIGITAL_PLANTILLA.pdf" \
  --template-xy 250 490 \
  --template-wh 100 100 \
  --destination-dir distintivos/digital

python autodistintivos.py \
  --data-file "datos/Distintivo 20_Plantillas_info.csv" \
  --template "plantillas/SelloIMPRESO_PLANTILLA-1-2.pdf" \
  --template-xy 265 375 \
  --template-wh 100 100 \
  --destination-dir distintivos/impreso
