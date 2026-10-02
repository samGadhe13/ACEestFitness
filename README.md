# ACEest Fitness & Gym - DevOps Assignment 1

## Project Overview

ACEest Fitness & Gym is a Flask-based fitness and gym management application developed as part of the DevOps Assignment 1.

The project demonstrates application development together with DevOps practices including:

* Git and GitHub version control
* Feature branch development and pull requests
* Automated testing with Pytest
* Docker containerization
* GitHub Actions CI
* Jenkins CI/CD pipeline and quality gate
* Multibranch Jenkins pipeline configuration

## Project Structure

```text
ACEestFitness/
├── app.py
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── Jenkinsfile
├── README.md
├── tests/
│   └── test_app.py
└── .github/
    └── workflows/
        └── main.yml
```

## Local Setup

Create and activate a Python virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the project dependencies:

```powershell
pip install -r requirements.txt
```

Start the Flask application:

```powershell
python app.py
```

The API starts on:

```text
http://localhost:5000
```

### Health Check

Open:

```text
http://localhost:5000/health
```

## Run Tests

Run the Pytest test suite with:

```powershell
python -m pytest -q
```

The test suite validates the main API functionality of the application.

## Build and Run Docker

Build the Docker image:

```powershell
docker build -t aceest-fitness .
```

Run the container:

```powershell
docker run --rm -p 5000:5000 aceest-fitness
```

Then open:

```text
http://localhost:5000/health
```

## Example API Requests

### Login

```powershell
curl -X POST http://localhost:5000/login `
  -H "Content-Type: application/json" `
  -d '{"username":"admin","password":"admin"}'
```

### Create Client

```powershell
curl -X POST http://localhost:5000/clients `
  -H "Content-Type: application/json" `
  -d '{"name":"John","age":30,"height":175,"weight":80}'
```

### Generate Program

```powershell
curl -X POST http://localhost:5000/clients/1/program `
  -H "Content-Type: application/json" `
  -d '{"program_type":"Muscle Gain"}'
```

## GitHub Actions CI

GitHub Actions is configured in:

```text
.github/workflows/main.yml
```

The workflow runs automatically for pushes and pull requests.

The CI pipeline performs the following steps:

1. Checks out the repository.
2. Sets up Python 3.12.
3. Installs the project dependencies.
4. Performs application compilation and Flake8 linting.
5. Runs the Pytest test suite.
6. Builds the Docker image.
7. Runs the Pytest suite inside the Docker container.

This provides automated validation of the application whenever changes are pushed to GitHub or submitted through a pull request.

## Jenkins CI/CD

Jenkins is configured using the `Jenkinsfile` located in the root of the repository.

The Jenkins pipeline is configured as a **Multibranch Pipeline**, allowing Jenkins to discover and build branches that contain the `Jenkinsfile`.

The Jenkins pipeline performs the following stages:

1. **Checkout** – Checks out the source code from the Git repository.
2. **Install Dependencies** – Installs the Python dependencies from `requirements.txt`.
3. **Build and Lint** – Compiles the Flask application and runs Flake8.
4. **Run Pytest** – Executes the automated test suite.
5. **Build Docker Image** – Builds the Docker image using the project `Dockerfile`.
6. **Docker Test** – Runs the Pytest suite inside the Docker container.

The Jenkins pipeline also includes a quality gate through its post-build status:

* A successful pipeline reports `BUILD & QUALITY GATE PASSED`.
* A failed pipeline reports `BUILD & QUALITY GATE FAILED`.

## Jenkins and GitHub Actions Integration

GitHub Actions and Jenkins provide two CI automation paths for the project.

### GitHub Actions

```text
Developer
   |
   | git push / Pull Request
   v
GitHub
   |
   v
GitHub Actions
   |
   +--> Install dependencies
   |
   +--> Build & Lint
   |
   +--> Pytest
   |
   +--> Docker Build
   |
   +--> Docker Test
```

GitHub Actions provides automated validation directly within the GitHub repository whenever code changes are pushed or submitted through a pull request.

### Jenkins

```text
Developer
   |
   | Push / Branch update
   v
GitHub Repository
   |
   v
Jenkins Multibranch Pipeline
   |
   +--> Checkout
   |
   +--> Install Dependencies
   |
   +--> Build & Lint
   |
   +--> Pytest
   |
   +--> Docker Build
   |
   +--> Docker Test
   |
   v
Quality Gate
```

Jenkins uses the `Jenkinsfile` stored in the repository to define the pipeline stages. The Multibranch Pipeline allows different Git branches to be discovered and built using the same pipeline definition.

For this assignment, Jenkins builds can also be started manually from Jenkins. A GitHub webhook is not required for the demonstrated Jenkins configuration.

## DevOps Workflow

The overall development workflow is:

```text
Feature Branch
      |
      v
Code Changes
      |
      v
Git Commit
      |
      v
GitHub
      |
      +----------------------+
      |                      |
      v                      v
GitHub Actions           Jenkins
      |                      |
      v                      v
Build & Test             Build & Quality Gate
      |                      |
      +----------+-----------+
                 |
                 v
          Pull Request
                 |
                 v
              main
```

This workflow demonstrates source control, automated testing, linting, Docker-based validation, and CI quality checks using both GitHub Actions and Jenkins.
