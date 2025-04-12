pipeline {
    agent any

    environment {
        IMAGE_NAME = 'blood-bank-system'
        CONTAINER_NAME = 'blood-bank-container'
        HOST_PORT = '5018'
        CONTAINER_PORT = '5000'
    }

    stages {
        stage('Clone Repo') {
            steps {
                echo 'Cloning repository...'
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

        stage('Run Docker Container') {
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
