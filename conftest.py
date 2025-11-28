"""Root pytest configuration that wires plugin modules."""

pytest_plugins = [
    "pytest_plugins.options",
    "pytest_plugins.configuration",
    "pytest_plugins.playwright",
    "pytest_plugins.reporting",
]
