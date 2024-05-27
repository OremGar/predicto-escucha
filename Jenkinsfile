pipeline {
  agent any
    parameters {
        string(name: 'nombre_contenedor', defaultValue: 'predicto_escucha_container', description: 'nombre del contenedor')
        string(name: 'nombre_imagen', defaultValue: 'predicto_escucha', description: 'nombre de la imagen')
        string(name: 'tag_imagen', defaultValue: 'latest', description: 'etiqueta de la imagen')
    }
    environment {
        nombre_final = "${nombre_contenedor}"        
    }
    stages {
          stage('stop/rm') {
            when {
                expression { 
                    DOCKER_EXIST = sh(returnStdout: true, script: 'echo "$(docker ps -a -q --filter name=${nombre_final})"').trim()
                    return  DOCKER_EXIST != '' 
                }
            }
            steps {
                script{
                    sh """
                        docker stop ${nombre_final}
                        docker rm -vf ${nombre_final}
                    """
                    }
                }                                   
            }
        stage('build') {
            steps {
                script{
                    sh """
                    docker build . -t ${nombre_imagen}:${tag_imagen}
                    """
                    }
                }                                       
            }
            stage('run') {
            steps {
                script{
                    sh """ 
                        docker run -d --name ${nombre_final} ${nombre_imagen}:${tag_imagen}
                    """
                    }
                }                                  
            }
        }
    }