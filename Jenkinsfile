pipeline {
    agent any

    environment {
        IMAGE_NAME = 'blood-bank-app'
        CONTAINER_NAME = 'blood-bank-container'
        PORT = '5000'
    }

    stages {
        stage('Clone from GitHub') {
            steps {
                git branch: 'main', url: 'https://github.com/Raghuud/BloodBANK.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    echo "🛠️ Building Docker image: ${IMAGE_NAME}"
                    docker.build(IMAGE_NAME)
                }
            }
        }

        stage('Stop & Remove Old Container') {
            steps {
                script {
                    echo "🧹 Cleaning up any existing container: ${CONTAINER_NAME}"
                    sh "docker rm -f ${CONTAINER_NAME} || true"
                }
            }
        }

        stage('Run New Container') {
            steps {
                script {
                    echo "🚀 Running new container on port ${PORT}"
                    sh "docker run -d -p ${PORT}:${PORT} --name ${CONTAINER_NAME} ${IMAGE_NAME}"
                }
            }
        }
    }

    post {
        success {
            echo '✅ Build and deployment successful!'
        }
        failure {
            echo '❌ Build failed. Check logs.'
        }
    }
}
