# K Power Tariffs - Developer Guide

This repository is a Kotlin Spring Boot application managed with Gradle (via the Gradle Wrapper).

## Prerequisites

- JDK 17 or later installed (match your team's standard JDK if specified)
- Git
- No need for a global Gradle install; we use the Gradle Wrapper (./gradlew)

## Running the app locally

```bash
make start-deps
make run
make stop-deps
```

By default, Spring Boot runs on http://localhost:8080

Application configuration lives in src/main/resources/application*.yaml

- application.yaml (defaults)
- application-dev.yaml (dev profile)
  You can set the active profile with: SPRING_PROFILES_ACTIVE=dev make run

### Running checks

- To run the full verification lifecycle (compilation, tests, static checks):
  ./gradlew check
  or using Makefile:
  make check

### Git pre-commit hook (Gradle check)

We use a pre-commit hook that runs Gradle check to prevent commits if checks fail.

### Install the hook:

```bash
make hooks-install
```

This sets git config core.hooksPath to .githooks and ensures the scripts are executable.

### Uninstall the hook (optional):

- Revert to the default .git/hooks path:
  make hooks-uninstall
