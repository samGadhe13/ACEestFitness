pipeline {
agent any

```
stages {

    stage('Checkout') {
        steps {
            checkout scm
        }
    }

    stage('Install Dependencies') {
        steps {
            bat '''
                python -m pip install --upgrade pip
                pip install -r requirements.txt
            '''
        }
    }

    stage('Build and Lint') {
        steps {
            bat '''
                python -m py_compile app.py
                flake8 app.py tests
            '''
        }
    }

    stage('Run Pytest') {
        steps {
            bat '''
                set PYTHONPATH=.
                pytest -q
            '''
        }
    }

    stage('Build Docker Image') {
        steps {
            bat 'docker build -t aceest-fitness:jenkins .'
        }
    }

    stage('Docker Test') {
        steps {
            bat 'docker run --rm aceest-fitness:jenkins sh -c "PYTHONPATH=/app pytest -q"'
        }
    }
}

post {
    success {
        echo 'BUILD & QUALITY GATE PASSED'
    }

    failure {
        echo 'BUILD & QUALITY GATE FAILED'
    }

    always {
        echo 'Jenkins pipeline execution completed.'
    }
}
```

}
