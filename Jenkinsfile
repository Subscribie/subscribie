pipeline {
  agent any
  stages {
    stage('ls dir') {
      parallel {
        stage('ls dir') {
          steps {
            sh 'ls -l'
          }
        }
        stage('Create & Activate Virtualenv') {
          steps {
            sh '''virtualenv -p python3 venv
. ./venv/bin/activate'''
          }
        }
      }
    }
    stage('Pip install requirements') {
      steps {
        sh 'pip install -r requirements.txt'
      }
    }
  }
}