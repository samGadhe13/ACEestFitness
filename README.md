# ACEest Fitness & Gym - DevOps Assignment 1



## Project structure



```text

ACEestFitness/

├── app.py

├── requirements.txt

├── Dockerfile

├── .dockerignore

├── README.md

├── tests/

│   └── test_app.py

└── .github/

    └── workflows/

        └── main.yml

```



## Local setup



```powershell

python -m venv .venv

.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt

python app.py

```



The API starts on:



```text

http://localhost:5000

```



Health check:



```text

http://localhost:5000/health

```



## Run tests



```powershell

python -m pytest -q

```



## Build and run Docker



```powershell

docker build -t aceest-fitness .

docker run --rm -p 5000:5000 aceest-fitness

```



Then open:



```text

http://localhost:5000/health

```



## Example API requests



Login:



```powershell

curl -X POST http://localhost:5000/login `

  -H "Content-Type: application/json" `

  -d '{"username":"admin","password":"admin"}'

```



Create client:



```powershell

curl -X POST http://localhost:5000/clients `

  -H "Content-Type: application/json" `

  -d '{"name":"John","age":30,"height":175,"weight":80}'

```



Generate program:



```powershell

curl -X POST http://localhost:5000/clients/1/program `

  -H "Content-Type: application/json" `

  -d '{"program_type":"Muscle Gain"}'

```



## CI/CD



GitHub Actions is configured in `.github/workflows/main.yml`.



For every push or pull request to `main`/`master`, it:

1. Checks out the repository.

2. Installs Python dependencies.

3. Compiles and lints the Flask application.

4. Runs the Pytest suite.

5. Builds the Docker image.

6. Runs the Pytest suite inside the Docker image.

