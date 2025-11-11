# LaniakeA Protocol User Guide

This guide provides instructions for setting up, deploying, and using the LaniakeA Protocol, an 8-Dimensional Blockchain with AI Intelligence.

## 1. Prerequisites

You will need the following software installed on your system:

*   **Git:** For cloning the repository.
*   **Docker** and **Docker Compose:** For running the application and its dependencies (PostgreSQL, Redis, Prometheus, Grafana).

## 2. Installation and Setup

### 2.1. Clone the Repository

Open your terminal and clone the project:

```bash
git clone https://github.com/QalamHipHop/laniakea-protocol.git
cd laniakea-protocol
```

### 2.2. Configure Environment Variables

The project uses a `.env` file for configuration. A template has been provided.

1.  **Copy the template:**
    ```bash
    cp .env.example .env
    ```
2.  **Edit the `.env` file** to set your desired values. **Crucially, update the security keys:**
    ```ini
    # Database Configuration
    POSTGRES_USER=laniakea_user
    POSTGRES_PASSWORD=laniakea_password
    POSTGRES_DB=laniakea_db
    DATABASE_URL=postgresql+psycopg2://laniakea_user:laniakea_password@db:5432/laniakea_db

    # Security Configuration
    SECRET_KEY="YOUR_NEW_SECRET_KEY_HERE"
    ALGORITHM="HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES=30

    # Monitoring Configuration
    GRAFANA_USER=admin
    GRAFANA_PASSWORD=admin
    ```

## 3. Running the Application with Docker Compose

The easiest way to run the entire stack (FastAPI app, PostgreSQL, Redis, Prometheus, Grafana) is with Docker Compose.

1.  **Build the images:**
    ```bash
    docker-compose build
    ```
2.  **Start the services:**
    ```bash
    docker-compose up -d
    ```

| Service | Port | Description |
| :--- | :--- | :--- |
| **FastAPI App** | `8000` | The main API and P2P network interface. |
| **PostgreSQL** | `5432` | Persistent storage for blockchain and SCDA state. |
| **Prometheus** | `9090` | Metrics collection endpoint. |
| **Grafana** | `3000` | Visualization dashboard for metrics. |

## 4. Using the Dashboard (`dashboard.html`)

The main user interface is the `dashboard.html` file, which connects to the FastAPI backend.

1.  **Access the Dashboard:** Open your web browser and navigate to:
    ```
    http://localhost:8000/web/dashboard.html
    ```
    *(Note: The `Dockerfile` serves the `/web` directory as static content.)*

2.  **Authentication:**
    Before interacting with protected API endpoints (most of them), you must authenticate.
    *   **Endpoint:** `POST /token`
    *   **Method:** Use `x-www-form-urlencoded` with `username` and `password`.
    *   **Mock Credentials:** `username: testuser`, `password: testpass`
    *   **Usage:** The dashboard's underlying JavaScript should handle this, but for manual testing (e.g., with Postman or `curl`), you will receive a JWT access token. This token must be included in the `Authorization` header of all subsequent requests as `Bearer <token>`.

3.  **Key Interactions:**
    *   **Check Status:** `GET /api/v1/status`
    *   **Create Transaction:** `POST /api/v1/transaction`
    *   **Mine Block:** `POST /api/v1/mine`
    *   **SCDA Management:** `GET /api/v1/scda/{scda_id}`

## 5. Monitoring with Grafana

Grafana is pre-configured to connect to Prometheus.

1.  **Access Grafana:** Open your web browser and navigate to:
    ```
    http://localhost:3000
    ```
2.  **Login:** Use the credentials from your `.env` file (default: `admin`/`admin`).
3.  **Explore Dashboards:** You can now create dashboards to visualize metrics like:
    *   `laniakea_api_requests_total`
    *   `laniakea_api_request_latency_seconds`
    *   `laniakea_p2p_network_size`
    *   `laniakea_energy_consumption_joules`

## 6. Deployment (CI/CD)

The project includes a GitHub Actions workflow (`.github/workflows/ci-cd.yml`) for automated testing and deployment.

*   **Triggers:** Pushes and Pull Requests to `main` and `develop` branches.
*   **Steps:**
    1.  Code Quality Checks (Linting, Type Checking, Security Scan).
    2.  Unit and Integration Tests (`pytest`).
    3.  Docker Image Build.
    4.  **Deployment:** The workflow is set up to build and push the Docker image to a container registry (e.g., GitHub Container Registry or Docker Hub). You must configure the deployment step in the YAML file to target your specific cloud provider (Heroku, AWS ECS, Vercel for static assets, etc.) and provide the necessary secrets.
