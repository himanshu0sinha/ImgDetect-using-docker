pipeline {
    agent any

     parameters { string(name: 'YOLO5_IMAGE_URL', defaultValue: '', description: '') }

    stages {
        stage('Deploy') {
            steps {

                //authenticating eks cluster
                sh 'aws eks --region us-east-2 update-kubeconfig --name k8s-batch1'

                //going to k8s/yolo5.yaml,change image to $YOLO5_IMAGE_URL
                sh "sed -i 's|REPLACE_IMAGE_URL|${params.YOLO5_IMAGE_URL}|' k8s/yolo5.yaml"

               
                sh 'kubectl apply -f k8s/yolo5.yaml'

            }
        }
    }
}