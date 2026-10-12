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

- [Parte 1: Contenedorización de nuestro gestor de S3](#parte-1-contenedorizacion-de-nuestro-gestor-s3)
- [Parte 2: Paso del gestor de S3 a IaC con Terraform](#parte-2-paso-del-gestor-de-s3-a-iac-con-terraform)
- [Parte 3: Publicación y alojamiento de la imagen de Docker en Amazon ECR](#parte-3-publicacion-y-alojamiento-de-la-imagen-de-docker-en-amazon-ecr)
- [Parte 4: Configuración de IAM y definición de las tareas en ECS](#parte-4-configuracion-de-iam-y-definicion-de-las-tareas-en-ecs)
- [Parte 5: Despliegue del servicio en Fargate, redes y resolución de problemas](#parte-5-despliegue-del-servicio-en-fargate-redes-y-resolucion-de-problemas)

## Limpieza del entorno
```bash
terraform destroy
```
---

## Parte 1: Contenedorización de nuestro gestor de S3
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
Parte 2:

En esta segunda parte de la serie nos acercaremos al objetivo, que es **automatizar el despliegue con IaC** (Infraestructura como Código).

![Imagen08](images/08.png)

Para empezar, instalamos Terraform desde sus [repositorios oficiales](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli
).
Para estructurar correctamente el código de _manera limpia_, dividimos la configuración en tres archivos principales dentro de una misma carpeta: 'providers.tf', 'main.tf' y 'variables.tf'.

* **'providers.tf'**, para la conexión. Definiendo con quién habla Terraform (en este caso, AWS) y qué versión del plugin tiene que descargar.
* **'variables.tf'**, para las entradas. Definiendo parámetros que pueden cambiar como son la región, los nombres, las dimensiones de la máquina. Valores que harían difícil el despliegue si se quedaran fijos (hardcoded).
* **'main.tf'**, los recursos: Donde se encuentra la infraestructura real a crear: servidores, buckets, redes, BDs.

Separarlo de esta forma nos da la posibilidad de reutilizar la misma infraestructura en otros entornos o con diferentes nombres de bucket. Es más fácil de mantener, de la misma manera que cuando dividimos el código del gestor de S3. Aunque sea posible tenerlo todo en el mismo archivo, no es nada recomendable de cara al futuro. En proyectos más grandes, todavía se podría separar aún más.

Ubicados en la raíz del proyecto, generamos la carpeta 'terraform' y entramos en ella y le añadimos los archivos necesarios, que la estructura quedará así:

![Imagen09](images/09.png)
![Imagen10](images/10.png)
![Imagen11](images/11.png)

Después de definir los tres archivos, la estructura queda así:
![Imagen12](images/12.png)
![Imagen13](images/13.png)
![Imagen14](images/14.png)
![Imagen15](images/15.png)

He tenido que modificar el código del gestor de S3 para **orientarlo a un usuario final** y no tanto a un administrador root que lo gestiona todo. Así que le he dejado funciones de subir, borrar, listar y actualizar archivos nada más.
He adaptado la aplicación al nuevo bucket que hemos creado expresamente con Terraform para este proyecto, llamado 'terraform-file-manager-default-s3bucket-daniel-2026'. He limpiado también la parte de Flask eliminando las rutas de crear y listar buckets que teníamos en la versión anterior.

**Un consejo**: Tenemos que tener cuidado a la hora de cambiar todas las partes. Si se queda alguna línea antigua, seguirá conectándose al bucket antiguo. Un comando que me fue de utilidad para encontrar referencias fue: 'grep -rn' 'app.config' o buscar términos como 'test-s3' o 'file-manager' en la raíz del gestor.

Uno de los puntos fuertes del proyecto del Gestor es que al tenerlo todo bien separado (de manera modular) no me costó identificar qué tenía que cambiar. Os dejaré el resultado de [esta versión](https://github.com/ortizens9/flask_s3_file_manager/tree/feature/terraform-aws-migration) en una rama del repositorio de mi GitHub por si os es de utilidad.

Con el gestor actualizado, volvemos a crear la imagen de Docker como hicimos en la **Parte 1**.

![Imagen17](images/16.png)

Para probar la imagen (y como tengo el [AWS CLI](https://aws.amazon.com/es/cli/) instalado y configurado), le podemos compartir los permisos que tiene nuestro sistema local para que pueda realizar las operaciones en S3 (subir, listar, borrar...):
```bash
docker run --rm --env-file .env   -v ~/.aws:/root/.aws:ro   -p 5000:5000   flask-s3-app:latest
```
En esa orden:
* **'--rm'**: Indica que se borre el contenedor una vez parado de manera automática.
* **'--env-file .env'**: Especificamos donde se encuentra el archivo .env, donde se encuentran las variables de entorno.
* **'-v ~/.aws:/root/.aws:ro'**: Montamos la carpeta local de las credenciales de AWS en el contenedor en modo lectura (para pruebas locales).
* **'-p 5000:5000'**: Vinculamos el puerto 5000 del sistema con el contenedor.
* **'flask-s3-app:latest'**: Definimos la imagen de Docker que utilizamos.
![Imagen18](images/17.png)
Haré una serie de acciones con el bucket para asegurarme de que todo está en correcto funcionamiento.
![Imagen19](images/18.png)
![Imagen20](images/19.png)
![Imagen21](images/20.png)
![Imagen22](images/21.png)
![Imagen23](images/22.png)
![Imagen24](images/23.png)
![Imagen25](images/24.png)
![Imagen26](images/25.png)
![Imagen27](images/26.png)

Como podemos ver en las capturas, ya tenemos el Gestor adaptado para IaC y funcionando correctamente.
El siguiente paso será alojar esta imagen de Docker en [Amazon ECR](https://aws.amazon.com/es/ecr/) (Elastic Container Registry) para poder desplegarla en una estrategia 100% automatizada en la nube de AWS.

## Parte 3: Publicación y alojamiento de la imagen de Docker en Amazon ECR
## Parte 4: Configuración de IAM y definición de las tareas en ECS
## Parte 5: Despliegue del servicio en Fargate, redes y resolución de problemas
