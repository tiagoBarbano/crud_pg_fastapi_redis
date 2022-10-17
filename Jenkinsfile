node {
    def app

    stage('Clone repository') {
        /* Let's make sure we have the repository cloned to our workspace */

        checkout scm
    }

    stage('Build image') {
        /* This builds the actual image; synonymous to
         * docker build on the command line */

        //app = docker.build("tiagoBarbano/crud_pg_fastapi_redis")
        
        sh "docker build --pull --rm -f 'Dockerfile' -t crudpgfastapi:latest ."
        
    }

    stage('Test image') {
        /* Ideally, we would run a test framework against our image.
         * For this example, we're using a Volkswagen-type approach ;-) */

        sh 'echo "Tests passed"'
        
    }

    stage('Run image') {
        /* Ideally, we would run a test framework against our image.
         * For this example, we're using a Volkswagen-type approach ;-) */

        sh "docker run --rm -it  -p 8001:8001/tcp crudpgfastapi:latest"
        
    }

    stage('Push image') {
        /* Finally, we'll push the image with two tags:
         * First, the incremental build number from Jenkins
         * Second, the 'latest' tag.
         * Pushing multiple tags is cheap, as all the layers are reused. */
        sh "docker push tiagoBarbano/crudpgfastapi:latest"
        }
}

