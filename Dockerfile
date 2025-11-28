FROM mcr.microsoft.com/devcontainers/python:3
COPY requirements.txt .
# Easier than virtualenv: https://pip.pypa.io/en/stable/cli/pip_install/#cmdoption-break-system-packages
ENV PIP_BREAK_SYSTEM_PACKAGES=1
RUN pip install -r requirements.txt \
    && playwright install --with-deps chromium
WORKDIR /workspaces/mera-tests
COPY . .