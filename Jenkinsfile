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
        sh '''. ./venv/bin/activate
subscribie init
subscribie migrate
'''
      }
    }
    stage('Test') {
      steps {
        sh '''. ./venv/bin/activate
pytest'''
      }
    }
    stage('Deploy') {
      steps {
        input 'Proceed'
      }
    }
  }
}