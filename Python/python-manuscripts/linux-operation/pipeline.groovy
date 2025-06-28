pipeline {
    agent {
        kubernetes {
            cloud 'kubernetes'
        }
    }
    stages {
        stage('Hello') {
            agent {
                node {
                    label 'jenkins-jenkins-agent'
                }
            }
            steps {
                sh "cat /etc/docker/daemon.json"
            }
        }
    }
}