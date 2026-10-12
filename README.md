# Despliegue automatizado de aplicación Flask en ECS Fargate con Terraform

![AWS](https://img.shields.io/badge/AWS-ECS%20Fargate%20%7C%20ECR%20%7C%20S3-orange)
![Terraform](https://img.shields.io/badge/IaC-Terraform-purple)
![Docker](https://img.shields.io/badge/Containers-Docker-blue)
![Python](https://img.shields.io/badge/Backend-Flask%20%2B%20Gunicorn-green)

Esta es la documentación técnica completa del ciclo de vida de migración y automatización de una aplicación web **Flask** con integración a **AWS S3**, desde el entorno local hasta un entorno serverless en la nube utilizando **Terraform**, **Docker**, **AWS ECR** y **AWS ECS Fargate**.

## Arquitectura y tecnologías


<img src="images/esquema_proyecto.png" width="700px" alt="estructura">

* **Backend:** Python, Flask, Gunicorn, 'boto3'.
* **Contenedores:** Docker, AWS ECR.
* **Infraestructura como Código (IaC):** Terraform
* **Orquestación y Red** AWS ECS Fargate, VPC, subredes, grupos de seguridad, S3, IAM.

## Comandos rápidos de despliegue

```bash
# 1. Autenticación y push a ECR
aws ecr get-login-password --region <REGION> | docker login --username AWS --password-stdin <AWS_ACCOUNT_ID>.dkr.ecr.<REGION>.amazon.com
docker build -t flask-app .
docker tag flask-app:latest <URL_ECR>:latest
docker push <URL_ECR>:latest

# 2. Desplegar infraestructura
cd terraform/
terraform init
terraform apply

# 3. Obtener IP pública del contenedor
aws ecs list-tasks --cluster flask-app-cluster --query "taskArns[0]" --output text
aws ecs describe-tasks --cluster flask-app-cluster --tasks <TASK_ARN> --query "tasks[0].attachments[0].details[?name=='networkInterfaceId'].value" --output text
aws ec2 describe-network-interfaces --network-interface-ids <ENI_ID> --query "NetworkInterfaces[0].Association.PublicIp" --output text
```

## Bitácora de despliegue paso a paso (Índice)

<div id="parte-1"></div>
##Parte 1: Contenedorización de nuestro gestor de S3
- [Parte 2: Paso del gestor de S3 a IaC con Terraform](#parte-2-paso-del-gestor-de-s3-a-iac-con-terraform)
- [Parte 3: Publicación y alojamiento de la imagen de Docker en Amazon ECR](#parte-3-publicacion-y-alojamiento-de-la-imagen-de-docker-en-amazon-ecr)
- [Parte 4: Configuración de IAM y definición de las tareas en ECS](#parte-4-configuracion-de-iam-y-definicion-de-las-tareas-en-ecs)
- [Parte 5: Despliegue del servicio en Fargate, redes y resolución de problemas](#parte-5-despliegue-del-servicio-en-fargate-redes-y-resolucion-de-problemas)

## Limpieza del entorno
```bash
terraform destroy
```

## Parte 1: Contenedorización de nuestro gestor de S3(#parte-1)
Buenas tardes a todos. Después de un tiempo liado con temas de AWS, retomo el blog para rescatar el gestor de S3 con boto3 que creé y que esta vez lo contenedorizaremos (lo convertiremos en un contenedor de Docker).

![Imagen01](images/01.png)

Como hemos cambiado varias veces de SO me aseguro de que el gestor continua funcionando correctamente. En mi carpeta de Proyectos he clonado desde mi cuenta de Github el [código](https://github.com/ortizens9/flask_s3_file_manager) que escribí.

![Imagen02](images/02.png)

Activamos el entorno, actualizamos las dependencias con el archivo requirements.txt y la ponemos en marcha con:
```bash
flask run --host=0.0.0.0 --port=5000
```
Nos muestra dos IP, depende desde donde la estemos ejecutando usamos una u otra. En el caso de estar probándola en la misma máquina, usaremos la que dice _127.0.0.1:5000_ (localhost) y si la ejecutamos en un servidor remoto (accediendo vía SSH), accedemos desde el navegador con la IP de la máquina (ej. _192.168.X.X:5000_).

![Imagen03](images/03.png)

En la imagen muestro la disposición de la estructura interna de la app con su árbol de directorios.

![Imagen04](images/04.png)

Pasamos a crear el Dockerfile, que es un documento de texto que se utiliza para hacer una imagen de contenedor; hacemos un _nano Dockerfile_. Y el contenido quedaría de la siguiente manera (he dejado comentarios explicando el funcionamiento interno).

![Imagen05](images/05.png)

Construimos la imagen del contenedor:

![Imagen06](images/06.png)

Para verificar si se ha creado con éxito escribimos _docker images_. Ahí deberíamos ver la imagen con el nombre _flask-s3-app_. Para poner a prueba el contenedor, arrancamos uno de prueba:

![Imagen07](images/07.png)

Esta solicitud en el navegador web se puede hacer tanto con _127.0.0.1_ como por _localhost_. Una vez verificado, lo paramos y eliminamos con:
```bash
docker stop prueba_flask && docker rm prueba_flask
```

Siguiente paso:
Ya tenemos empaquetada la app en un contenedor funcional. En la siguiente parte tengo pensado crear la infraestructura AWS utilizando **Terraform**.
Un detalle importante: En este contenedor todavía nos quedarían gestionar las credenciales para poder subir los archivos a los buckets de S3 (el "envoltorio" funciona pero nos queda la conexión con AWS y no podemos subir nada).
Aunque haya maneras de editar el archivo _.gitignore_ para no subir estas credenciales, no lo considero una buena práctica y preferiría usar roles IAM, evitando exponerlas.

Dejo un [enlace](https://docs.docker.com/get-started/docker-concepts/building-images/writing-a-dockerfile/) que me ha servido para crear el Dockerfile.

## Parte 2: Paso del gestor de S3 a IaC con Terraform
## Parte 3: Publicación y alojamiento de la imagen de Docker en Amazon ECR
## Parte 4: Configuración de IAM y definición de las tareas en ECS
## Parte 5: Despliegue del servicio en Fargate, redes y resolución de problemas
