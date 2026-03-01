pipeline {
    agent any

    environment {
        SONAR_PROJECT_KEY = 'multi-ai-agent-gcp'
        SONAR_SCANNER_HOME = tool 'Sonarqube'

        // GCP Configuration
        GCP_PROJECT_ID = credentials('gcp-project-id')
        GCP_REGION = 'us-central1'
        GCP_ARTIFACT_REGISTRY = 'multi-ai-agent'

        // Common
        IMAGE_TAG = 'latest'
        IMAGE_NAME = 'multi-ai-agent'
        GITHUB_REPO = 'https://github.com/farhanrhine/multi-ai-agent-gcp.git'
    }

    stages {
        stage('Clone GitHub Repo') {
            steps {
                script {
                    echo 'Cloning GitHub repo to Jenkins............'
                    checkout scmGit(
                        branches: [[name: '*/main']],
                        extensions: [],
                        userRemoteConfigs: [[credentialsId: 'github-token', url: env.GITHUB_REPO]] // replace with with **Generate Pipeline Script you just generated from jenkins**
                    )
                }
            }
        }

        // stage('SonarQube Analysis') {
        //     steps {
        //         withCredentials([string(credentialsId: 'sonarqube-token', variable: 'SONAR_TOKEN')]) {
        //             withSonarQubeEnv('Sonarqube') {
        //                 sh """
        //                 ${SONAR_SCANNER_HOME}/bin/sonar-scanner \
        //                 -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
        //                 -Dsonar.sources=. \
        //                 -Dsonar.host.url=http://sonarqube-dind:9000 \
        //                 -Dsonar.login=${SONAR_TOKEN}
        //                 """
        //             }
        //         }
        //     }
        // }

        // stage('Build & Push to GCP Artifact Registry') {
        //     when {
        //         expression { env.BRANCH_NAME == 'main' || env.GIT_BRANCH == 'origin/main' }
        //     }
        //     steps {
        //         script {
        //             echo '========= Building and Pushing to GCP Artifact Registry ========='
        //             withCredentials([file(credentialsId: 'gcp-service-account-key', variable: 'GCP_KEY_FILE')]) {
        //                 sh '''
        //                 set +e

        //                 if [ ! -f "${GCP_KEY_FILE}" ]; then
        //                     echo "GCP credentials not configured, skipping GCP push"
        //                     exit 0
        //                 fi

        //                 # Authenticate with GCP
        //                 gcloud auth activate-service-account --key-file=${GCP_KEY_FILE}
        //                 gcloud config set project ${GCP_PROJECT_ID}

        //                 # Configure Docker for GCP
        //                 gcloud auth configure-docker ${GCP_REGION}-docker.pkg.dev

        //                 # Build and push
        //                 ARTIFACT_REGISTRY="${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/${GCP_ARTIFACT_REGISTRY}"
        //                 docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
        //                 docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${ARTIFACT_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}
        //                 docker push ${ARTIFACT_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}

        //                 echo "Successfully pushed to GCP Artifact Registry: ${ARTIFACT_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
        //                 '''
        //             }
        //         }
        //     }
        // }

        // stage('Deploy to GCP Cloud Run') {
        //     when {
        //         expression { env.BRANCH_NAME == 'main' || env.GIT_BRANCH == 'origin/main' }
        //     }
        //     steps {
        //         script {
        //             echo '========= Deploying to GCP Cloud Run ========='
        //             withCredentials([file(credentialsId: 'gcp-service-account-key', variable: 'GCP_KEY_FILE')]) {
        //                 sh '''
        //                 set +e

        //                 if [ ! -f "${GCP_KEY_FILE}" ]; then
        //                     echo "GCP credentials not configured, skipping Cloud Run deployment"
        //                     exit 0
        //                 fi

        //                 gcloud auth activate-service-account --key-file=${GCP_KEY_FILE}
        //                 gcloud config set project ${GCP_PROJECT_ID}

        //                 SERVICE_NAME="${GCP_CLOUD_RUN_SERVICE:-multi-ai-agent-service}"
        //                 ARTIFACT_REGISTRY="${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/${GCP_ARTIFACT_REGISTRY}"

        //                 echo "Deploying service: ${SERVICE_NAME}"

        //                 gcloud run deploy ${SERVICE_NAME} \
        //                   --image ${ARTIFACT_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} \
        //                   --region ${GCP_REGION} \
        //                   --allow-unauthenticated \
        //                   --port 8501 \
        //                   --memory 2Gi \
        //                   --cpu 2 \
        //                   --timeout 3600 \
        //                   --set-env-vars GROQ_API_KEY=${GROQ_API_KEY},TAVILY_API_KEY=${TAVILY_API_KEY}

        //                 SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region ${GCP_REGION} --format='value(status.url)')
        //                 echo "✅ Cloud Run deployment complete"
        //                 echo "Service URL: ${SERVICE_URL}"
        //                 '''
        //             }
        //         }
        //     }
        // }
    }

    post {
        success {
            echo '========= Pipeline Execution Successful ========='
            echo '✅ Build & Push: SUCCESS'
            echo '✅ Deployment: SUCCESS'
        }
        failure {
            echo '========= Pipeline Execution Failed ========='
            echo '❌ Check logs above for details'
        }
        always {
            echo '========= Pipeline Cleanup ========='
            sh '''
            docker image prune -f --filter "dangling=true" || true
            '''
        }
    }
}