pipeline {
    agent any

    environment {
        IMAGE_NAME = "bloodbank_app"
        IMAGE_TAG = "v1"
        FULL_IMAGE_NAME = "${IMAGE_NAME}:${IMAGE_TAG}"
        CONTAINER_NAME = "bloodbank_container"
    }

    stages {
        stage('Clone Repository') {
            steps {
                git branch: 'main', url: 'https://github.com/Raghuud/BloodBANK.git'
            }
        }

        stage('Check Docker Access') {
            steps {
                script {
                    echo "Checking Docker access..."
                    sh 'whoami'
                    sh 'groups'
                    sh 'docker version || echo "Docker not accessible"'
                }
            }
        }

        stage('Cleanup Old Container (Optional)') {
            steps {
                script {
                    echo "Trying to remove old container..."
                    sh "docker rm -f $CONTAINER_NAME || true"
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    echo "Building Docker image: $FULL_IMAGE_NAME"
                    sh "docker build -t $FULL_IMAGE_NAME ."
                }
            }
        }

        stage('Run Docker Container') {
            steps {
                script {
                    echo "Running Docker container: $CONTAINER_NAME"
                    sh "docker run -d -p 5001:5000 --name $CONTAINER_NAME $FULL_IMAGE_NAME"
                }
            }
        }
    }
}
