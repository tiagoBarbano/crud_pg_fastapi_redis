node {
    def app

    stage('Clone repository') {
        checkout scm
    }

    stage('Build image') {
        app = docker.build("crudpgfastapi:latest")      
    }

    stage('Test image') {
        app.inside {
            sh 'make test'
        }
    }
        
    //stage('Run image') {
        /* Ideally, we would run a test framework against our image.
         * For this example, we're using a Volkswagen-type approach ;-) */

      //  sh "docker run --rm -p 8001:8001/tcp --env-file .env  crudpgfastapi:latest"
        
    //}
    stage('Push image') {
        app.push()
        app.push('latest')
    }
}

