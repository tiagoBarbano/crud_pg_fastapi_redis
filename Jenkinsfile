node {
    def app

    stage('Clone repository') {
        checkout scm
    }

    stage('Build image') {
        app = docker.build("tiagobarbano/crudpgfastapi:latest")      
    }

    stage('Test image') {
        sh "echo TESTE"
        //app.inside {
        //    sh 'make test'
        //}
    }
        
    //stage('Run image') {
        /* Ideally, we would run a test framework against our image.
         * For this example, we're using a Volkswagen-type approach ;-) */

      //  sh "docker run --rm -p 8001:8001/tcp --env-file .env  crudpgfastapi:latest"
        
    //}
    stage('Push image') {
        docker.withRegistry('https://registry-1.docker.io/v2/', 'GitHub') {
            app.push()
        }


    }
}

