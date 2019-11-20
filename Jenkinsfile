pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        echo 'Hello world!'
        sh label: 'Make', script: 'make'
      }
    }
  }
}
