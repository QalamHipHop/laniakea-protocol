# Contributing to LaniakeA Protocol

We welcome contributions from the community to help advance the LaniakeA Protocol, an 8-Dimensional Blockchain with AI Intelligence. Your efforts in development, documentation, testing, and research are highly valued.

## Code of Conduct

Please note that this project is governed by a Code of Conduct. By participating, you are expected to uphold this code.

## How to Contribute

### 1. Reporting Bugs

If you find a bug, please report it by opening a new issue on the GitHub repository.

*   **Provide a clear and descriptive title.**
*   **Describe the exact steps to reproduce the bug.**
*   **Include the expected behavior and the actual behavior.**
*   **Specify your environment** (OS, Python version, dependencies, etc.).

### 2. Suggesting Enhancements

We are always looking for ways to improve the protocol. Suggestions for new features, optimizations, or architectural changes are welcome.

*   **Open a new issue** with a clear title.
*   **Describe the enhancement** in detail, explaining why it would be beneficial.
*   **Provide a use case** to illustrate how the feature would be used.

### 3. Making Code Contributions

The preferred workflow for code contributions is as follows:

1.  **Fork** the repository on GitHub.
2.  **Clone** your forked repository locally.
3.  **Create a new branch** for your feature or fix: `git checkout -b feature/my-new-feature` or `git checkout -b bugfix/fix-issue-123`.
4.  **Install dependencies** and set up your environment (see the User Guide).
5.  **Make your changes.** Ensure your code adheres to the project's coding standards (e.g., use `black` for formatting).
6.  **Write tests** for your changes. All new features and bug fixes must be covered by tests.
7.  **Run the test suite** to ensure all tests pass: `pytest tests/`.
8.  **Commit your changes** with a clear, descriptive commit message.
9.  **Push your branch** to your fork: `git push origin feature/my-new-feature`.
10. **Open a Pull Request (PR)** against the `develop` branch of the main repository.

### 4. Documentation Contributions

High-quality documentation is crucial. Contributions to the `README.md`, `User Guide`, and internal code comments are highly appreciated.

## Development Environment Setup

The project uses Docker and Docker Compose for a consistent development environment.

1.  **Install Docker and Docker Compose.**
2.  **Build the services:** `docker-compose build`
3.  **Start the services:** `docker-compose up -d`
4.  The FastAPI application will be available at `http://localhost:8000`.

## Coding Standards

*   **Style:** We use `black` for code formatting. Please run `black .` before committing.
*   **Type Hinting:** All new code should use Python type hints.
*   **Linting:** We use `flake8` and `mypy` for linting and type checking.

Thank you for your interest in contributing to the LaniakeA Protocol!
