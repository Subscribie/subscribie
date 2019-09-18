pipeline {
  agent any
  stages {
    stage('Create Virtualenv environment') {
      steps {
        sh 'virtualenv -p python3 venv'
      }
    }
    stage('Pip install module') {
      steps {
        sh '''. ./venv/bin/activate
pip install .'''
      }
    }
    stage('Test') {
      steps {
        sh '''. ./venv/bin/activate
pytest'''
      }
    }
  }
}