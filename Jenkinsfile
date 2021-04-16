pipeline {
  agent any

  environment {
    WORKSPACE_DIR = """${sh(
            returnStdout: true,
            script: 'echo -n "${WORKSPACE##*/}"'
        )}"""
    DOCKER_VERSION = """${sh(
        script: 'echo -n "$(date +%Y.%m.%d)-\$(git rev-parse --short HEAD)"',
        returnStdout: true
    )}"""
    HOST_SRC_PATH = """${sh(
            returnStdout: true,
            script: 'echo -n "$HOST_WORKSPACE_PATH${WORKSPACE##*/}/"'
        )}"""
  }

  stages {
    stage('Check Jenkins/Docker') {
      steps {
        sh 'docker version'
        sh 'chmod +x run.sh'
      }
    }

    stage('Docker Build') {
      steps {
        sh '''docker build \
        --target production \
        --build-arg DOCKER_TAG=$DOCKER_VERSION \
        --build-arg BUILD_DATE="$BUILD_DATE" \
        --build-arg GIT_COMMIT=$GIT_COMMIT \
        --build-arg BRANCH=$BRANCH_NAME \
        -t image-swarm:$BRANCH_NAME .'''
        sh './run.sh build-dev'
      }
    }

    stage('Test') {
      steps {
        sh 'run.sh test'
      }
      post {
        always {
          junit "test-results.xml"
        }
      }
    }
    stage('Deployment') {
      when {
        anyOf {
          branch 'master'
          branch 'stage'
        }
      }

      steps {
        script {
          if (env.BRANCH_NAME == 'master') {
            env.DOCKER_TAG = 'stable'
          } else {
            env.DOCKER_TAG = 'latest'
          }

          sh('\$(aws ecr get-login --region eu-west-2 --no-include-email)')
          sh('docker tag "image-swarm:$BRANCH_NAME" "598950368936.dkr.ecr.eu-west-2.amazonaws.com/image-swarm:$DOCKER_TAG"')
          sh('docker tag "image-swarm:$BRANCH_NAME" "598950368936.dkr.ecr.eu-west-2.amazonaws.com/image-swarm:$DOCKER_VERSION"')
          docker.withRegistry("https://598950368936.dkr.ecr.eu-west-2.amazonaws.com"){docker.image("598950368936.dkr.ecr.eu-west-2.amazonaws.com/image-swarm:$DOCKER_TAG").push("$DOCKER_TAG")}
          docker.withRegistry("https://598950368936.dkr.ecr.eu-west-2.amazonaws.com"){docker.image("598950368936.dkr.ecr.eu-west-2.amazonaws.com/image-swarm:$DOCKER_TAG").push("$DOCKER_VERSION")}
        }
      }
    }
  }

  post {
    always {
      cleanWs()
    }
  }

}
