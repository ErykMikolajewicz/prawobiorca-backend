#!/bin/bash
granian --port 8000 --host 127.0.0.1 --interface asgi --ssl-certificate certificate.crt --ssl-keyfile private.key \
--reload app.main:app
