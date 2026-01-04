#!/bin/bash
BOKEH_LOG_LEVEL=error bokeh serve --port=$PORT --allow-websocket-origin=* --address=0.0.0.0 --use-xheaders app.py
