pipeline {
    agent any

    environment {
        IMAGE_NAME = 'blood-bank-management'
        CONTAINER_NAME = 'blood-bank-prod-5019'
        HOST_PORT = '5019'
        CONTAINER_PORT = '5000'
        GIT_REPO = 'https://github.com/Raghuud/BloodBANK.git'
        GIT_BRANCH = 'main'
    }

    stages {
        stage('Clone Repo') {
            steps {
                echo 'Cloning repository...'
                git branch: "${GIT_BRANCH}", url: "${GIT_REPO}"
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh "docker build -t $IMAGE_NAME ."
                }
            }
        }

        stage('Stop & Remove Old Container') {
            steps {
                script {
                    sh "docker stop $CONTAINER_NAME || true"
                    sh "docker rm $CONTAINER_NAME || true"
                }
            }
        }

        stage('Run Container on Port 5019') {
            steps {
                script {
                    sh """
                        docker run -d \
                        --name $CONTAINER_NAME \
                        -p $HOST_PORT:$CONTAINER_PORT \
                        $IMAGE_NAME
                    """
                }
            }
        }
    }

    post {
        always {
            echo 'Pipeline completed.'
        }
    }
}
