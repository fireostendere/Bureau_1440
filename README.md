# Test Automation Framework

Playwright + Pytest UI automation framework for validating https://app.mera.fit.

## Features
- Page Object Model with shared `BasePage` helpers
- Strong fixture layer via `pytest_plugins` package
- Specialized helpers for network monitoring, UI validation, and navigation
- Faker-powered data factories for negative scenarios
- Visual regression helpers with baseline comparison
- Allure attachments for screenshots, HTML, videos, and traces
- Configurable browser headless/headed, video, and tracing options
- Automatic retry for flaky tests with external dependencies

## Quick Start
```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate
source venv/bin/activate          # Linux/macOS/WSL
.\venv\Scripts\Activate.ps1       # Windows PowerShell

# 3. Install dependencies
pip install -r requirements.txt
playwright install chromium
```

## Configuration
```bash
# Copy template and fill credentials
cp .env.example .env

# Required values inside .env
ADMIN_USERNAME=your_username
ADMIN_PASSWORD=your_password
```

All runtime configuration flows through `config.py` and `helpers.files.get_env`. Additional overrides can be provided with environment variables such as `APP_BASE_HOST`, `MARKETING_BASE_HOST`, `PLAYWRIGHT_VIDEO`, and `PLAYWRIGHT_TRACE`.

## Running Tests
```bash
# Basic run (headless)
pytest --alluredir=allure-results

# Headed browser
pytest --alluredir=allure-results --headed

# Record videos (failed tests by default)
pytest --alluredir=allure-results --video

# Keep videos for passing tests too
pytest --alluredir=allure-results --video --keep-video-on-pass

# Enable Playwright tracing (retain on failure)
pytest --alluredir=allure-results --pw-trace=retain-on-failure

# Single test example
pytest tests/login/test_authentication.py::test_login_with_valid_credentials_navigates_to_admin -v

# Run with automatic retry for flaky tests (recommended for CI)
pytest --reruns 2 --reruns-delay 2 --alluredir=allure-results
```

## Parallel Execution
The Playwright fixtures are process-safe, so you can fan out the suite with `pytest-xdist`:

```bash
# Auto-detect worker count
pytest -n auto --dist loadscope --alluredir=allure-results

# Explicit worker count (e.g., CI with 4 cores)
pytest -n 4 --dist loadscope --alluredir=allure-results
```

`--dist loadscope` keeps tests from the same module on one worker, allowing browser/session reuse while still running multiple workers in parallel. All artifacts, screenshots, traces, and Allure results remain isolated per test via their node IDs, so no extra configuration is required.

## Handling Flaky Tests

Tests that depend on external services (Calendly) are marked with `@pytest.mark.flaky(reruns=2, reruns_delay=2)` to automatically retry on failure. This reduces false negatives from network issues or service unavailability.

### Marked as Flaky
- All tests in `tests/book_demo/`

### Running Flaky Tests
```bash
# Run only flaky tests
pytest -m flaky

# Run excluding flaky tests
pytest -m "not flaky"

# Override reruns globally (useful in CI)
pytest --reruns 3 --reruns-delay 2
```

The framework uses `pytest-rerunfailures` to handle this automatically. Failed tests will be retried up to the specified number of times with a delay between attempts.

## Project Structure
```
config.py               # Application configuration
helpers/
  api.py                # API helpers
  data.py               # Test data generation
  files.py              # File and path utilities
  media.py              # Screenshot/video handling
  navigation.py         # HTTP redirect testing
  network_monitor.py    # Network request monitoring
  qa.py                 # QA utilities (centering, headers, etc.)
  ui_validator.py       # UI validation helpers
pages/
  base_page.py          # Abstract base with common methods
  login_page.py         # Login page object
  admin_page.py         # Admin dashboard page object
  book_demo_page.py     # Book-a-demo (Calendly) page object
pytest_plugins/
  __init__.py
  options.py            # CLI options
  configuration.py      # Config fixtures
  playwright.py         # Browser/page fixtures
  reporting.py          # Allure integration
tests/
  login/                # Login page test suite
    shared.py
    test_authentication.py
    test_navigation.py
    test_security.py
    test_stability.py
    test_ui.py
  book_demo/            # Book demo test suite
    shared.py
    test_navigation.py
    test_ui.py
  data_factory/
    credentials.py      # Credential generation
artifacts/              # Generated at runtime (videos/traces/screenshots)
pytest.ini              # Pytest configuration and custom markers
requirements.txt        # Python dependencies
```

## Test Coverage

### Login Suite
- Rendering and layout validation
- Successful authentication and session persistence
- Negative credential variants (invalid, empty, long, localized)
- Security defenses (SQL injection, XSS, cookie flags, headers)
- Navigation and UX flows (register link, back navigation)
- Stability checks for duplicate submissions and request tracking
- Visual regression comparisons against baseline screenshot

### Book Demo Suite
- Calendly embed rendering and interaction
- Day and time slot selection
- Timezone control visibility
- Form navigation and validation
- Security checks (HTTPS, iframe src)

## Pytest CLI Options
| Option | Description |
| ------ | ----------- |
| `--headed` | Launch browser with UI instead of headless mode |
| `--base-url URL` | Override default host |
| `--video` | Enable Playwright video recording |
| `--keep-video-on-pass` | Preserve videos even when tests pass |
| `--pw-trace {off,on,retain-on-failure}` | Control Playwright tracing behavior |
| `--reruns N` | Retry failed tests N times (for flaky tests) |
| `--reruns-delay SEC` | Wait SEC seconds between reruns |

Environment variables `PLAYWRIGHT_VIDEO`, `PLAYWRIGHT_KEEP_VIDEO_ON_PASS`, and `PLAYWRIGHT_TRACE` provide the same controls when running in CI.

## Debugging Failures
On test failure the framework captures:
1. Full-page screenshot (`artifacts/screenshots`)
2. Current DOM HTML (`artifacts/screenshots`)
3. Optional video (`artifacts/videos`) when enabled
4. Playwright trace zip (`artifacts/traces`) when tracing is enabled

Open traces with:
```bash
playwright show-trace artifacts/traces/<trace-file>.zip
```

## Environment Variables
| Variable | Required | Default | Purpose |
| -------- | -------- | ------- | ------- |
| `ADMIN_USERNAME` | Yes | - | Valid admin account username |
| `ADMIN_PASSWORD` | Yes | - | Valid admin account password |
| `APP_BASE_HOST` | No | app.mera.fit | Admin portal host |
| `MARKETING_BASE_HOST` | No | Derived from admin host | Marketing portal host (`book-demo`) |
| `ARTIFACTS_ROOT` | No | artifacts | Root folder for generated outputs |

`.env` values are loaded with `dotenv.load_dotenv(override=False)` so CI secrets take precedence.

## Architecture Highlights

### SOLID Principles (10/10)
The codebase follows SOLID principles rigorously:
- **Single Responsibility**: Each Page Object handles only form interaction; specialized helpers for monitoring, UI validation, and navigation
- **Open/Closed**: Extensible through BasePage inheritance and helper composition
- **Liskov Substitution**: All Page Objects properly extend BasePage
- **Interface Segregation**: Tests depend only on needed interfaces (no bloated Page Objects)
- **Dependency Inversion**: Depends on abstractions (AppConfig) rather than concrete implementations

### Specialized Helpers
- **LoginRequestMonitor** (`helpers/network_monitor.py`) - Network request tracking
- **LoginPageUIValidator** (`helpers/ui_validator.py`) - UI visual validation
- **HTTPRedirectTester** (`helpers/navigation.py`) - HTTP→HTTPS redirect testing

### Page Object Model
- All page interactions encapsulated in Page Object classes
- Tests written at high level using declarative methods
- Selectors and DOM access abstracted away from tests
- Consistent interface through BasePage

## Implementation Notes
- Session-scoped Playwright browser with function-scoped contexts/pages
- Configurable media preferences through `ArtifactPreferences` dataclass
- Automatic Allure attachments for diagnostics
- Faker locale `ru_RU` for localized credential scenarios
- Helpers split into focused modules (`files`, `media`, `qa`, `data`, `api`, `network_monitor`, `ui_validator`, `navigation`)
- Abstract base page with property `url` enforced via ABC

## Troubleshooting
- Run `playwright install chromium` if browsers are missing
- For Linux/WSL dependencies use `playwright install-deps`
- Ensure virtual environment is activated before invoking pytest
- Use `pytest -vv --maxfail=1` for verbose output during debugging
- Check `artifacts/` directory for screenshots and traces after failures
- Flaky test failures in CI? Increase `--reruns` count

## Quick Reference
```bash
# Setup (once)
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# Run locally
pytest --alluredir=allure-results

# Run with retries (recommended)
pytest --reruns 2 --reruns-delay 2 --alluredir=allure-results

# Parallel execution
pytest -n auto --dist loadscope --alluredir=allure-results

# View Allure report
allure serve allure-results

# Run specific marker
pytest -m auth  # Only authentication tests
pytest -m flaky # Only flaky tests
```

## Visual Baselines
Baseline screenshots live in `src/login-page.png`. To refresh:
1. Run `pytest tests/login/test_ui.py::test_ui_login_page_visual_baseline`
2. Copy the generated `artifacts/screenshots/login-page.png` over the baseline
3. Commit the updated baseline image

## CI/CD Integration
```yaml
# Example GitHub Actions workflow
- name: Run tests with reruns
  run: |
    pytest -n auto \
      --dist loadscope \
      --reruns 3 \
      --reruns-delay 2 \
      --alluredir=allure-results \
      --video \
      --pw-trace=retain-on-failure
```
