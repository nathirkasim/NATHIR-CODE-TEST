# UI Data Consistency Testing

A browser-only Python framework for finding inconsistent values across pages, filters, charts, tables, pagination, and captured API responses. It does not import or inspect application source code.

## Setup

From this directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env
```

Set `BASE_URL` to the running application. Set `USERNAME` and `PASSWORD` only when the configured login page requires them. Credentials are read from `.env`; they are never written to test code.

## Configuration

Edit `config/pages.yaml`:

- `login.path` and `login.selectors` describe the login form. Remove the login block if the application is already public.
- Each `pages` entry has a URL and named metrics.
- A metric can use CSS (default), `text`, or `xpath` selectors. Prefer stable `data-testid` selectors when available.
- `value_pattern` can extract a value from a label, and `context` records repository, branch, organization, severity, status, or date range.
- Add comparison pairs to the YAML as the application becomes known. The example tests demonstrate dashboard/detail, filter/result, summary/chart, UI/API, and repository/detail checks.

The first successful run writes `reports/storage_state.json`; later runs reuse it. Delete that file to force a fresh login. Set `HEADLESS=false` to observe the browser.

## Reports and behavior

XHR/fetch JSON responses are written to `reports/api/`. Mismatches are normalized before comparison, then screenshots are saved under `screenshots/`. AI analysis is optional: set `OPENAI_API_KEY` and optionally `OPENAI_MODEL`; without a key, the report records that AI analysis was disabled. Only the mismatch data and context are sent to the model.

Generated files include:

- `reports/consistency_report.json`
- `reports/consistency_report.html`
- `reports/mismatches.json`
- `reports/bug_reports/*.json`

The HTML report includes expected/actual values, differences, context, API value, AI decision/confidence, and screenshot links.

## Run

```bash
pytest
pytest -v
pytest --html=reports/test-report.html --self-contained-html
```

Without `BASE_URL`, browser tests are skipped but deterministic normalization/comparison tests still run. With an application configured, use the selectors and URLs for that application, then run from the VS Code terminal in `ui-data-consistency/`.
