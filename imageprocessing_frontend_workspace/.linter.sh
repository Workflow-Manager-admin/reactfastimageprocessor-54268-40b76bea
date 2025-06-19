#!/bin/bash
cd /home/kavia/workspace/code-generation/reactfastimageprocessor-54268-40b76bea/imageprocessing_frontend_workspace/imageprocessing_frontend
npm run build
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
   exit 1
fi

