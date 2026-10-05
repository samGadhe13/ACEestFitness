pipeline {
agent any

stages {

    stage('Checkout') {
        steps {
            checkout scm
        }
    }

    stage('Install Dependencies') {
        steps {
            sh '''
                python3 -m venv .venv
                .venv/bin/pip install --upgrade pip
                .venv/bin/pip install -r requirements.txt
            '''
        }
    }

    stage('Build and Lint') {
        steps {
            sh '''
                .venv/bin/python -m py_compile app.py
                .venv/bin/flake8 app.py tests
            '''
        }
    }

    stage('Run Pytest') {
        steps {
            sh '''
                export PYTHONPATH=.
                .venv/bin/pytest -q
            '''
        }
    }

    stage('Build Docker Image') {
        steps {
            sh 'docker build -t aceest-fitness:jenkins .'
        }
    }

    stage('Docker Test') {
        steps {
            sh 'docker run --rm aceest-fitness:jenkins sh -c "PYTHONPATH=/app pytest -q"'
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
}
