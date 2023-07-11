pipeline {

    agent any
    stages {

        stage('Authentication and docker login') {

            steps {

                sh '''
                aws ecr get-login-password --region us-west-1 | docker login --username AWS --password-stdin 854171615125.dkr.ecr.us-west-1.amazonaws.com

                '''

            }

        }



        stage('Build') {

            steps {

                sh '''
                cd yolo5
                docker build -t himanshu .
                '''


            }

        }



        stage('Push to ECR') {

            steps {

                sh '''
                docker tag himanshu:latest 854171615125.dkr.ecr.us-west-1.amazonaws.com/himanshu:latest
                docker push 854171615125.dkr.ecr.us-west-1.amazonaws.com/himanshu:latest

                '''

            }

        }
        stage('Trigger Deploy') {
          steps {
              build job: 'Yolo5Deploy', wait: false, parameters: [
                 string(name: 'YOLO5_IMAGE_URL', value: "854171615125.dkr.ecr.us-west-1.amazonaws.com/gayatri-yolo5:${BUILD_NUMBER}")
                ]
              }
           }

    }

}
