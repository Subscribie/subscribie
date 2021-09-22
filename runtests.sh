#! /bin/bash
. venv/bin/activate
python -m pytest
export PLAYWRIGHT_HEADLESS=false
export PLAYWRIGHT_HOST=http://127.0.0.1:5000/
cd tests/browser-automated-tests-playwright
npx playwright test
cd - # go back to previous current working directory
