#!/bin/bash

ARGS=""

ARGS="$ARGS --log-to-terminal"
ARGS="$ARGS --port 8080"

exec mod_wsgi-express start-server $ARGS wsgi/application
