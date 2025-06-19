#!/bin/bash
cd /home/kavia/workspace/code-generation/reactfastimageprocessor-54268-40b76bea/imageprocessing_backend_workspace/imageprocessing_backend
source venv/bin/activate
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

