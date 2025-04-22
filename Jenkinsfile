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

        stage('Cleanup Old Container (Optional)') {
            steps {
                script {
                    sh "docker rm -f $CONTAINER_NAME || true"
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh 'docker version' // Verify Docker works
                    sh "docker build -t $FULL_IMAGE_NAME ."
                }
            }
        }

        stage('Run Docker Container') {
            steps {
                script {
                    sh 'docker run -d -p 5001:5000 --name bloodbank_container bloodbank_app:v1'

                }
            }
        }
    }
} 
