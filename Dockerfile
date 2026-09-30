FROM python:3.11-slim

WORKDIR /app

#Colocamos unas variables de entorno y las activamos para que a la hora de ejecutarse el código
#Si buscamos eficiencia como son el parámetro DONTWRITEBYTECODE y NONBUFFERED. Lo ponemos en 1 que es True en booleano.
#Que una es para no crear carpetas __pycache__ y la otra para activar el modo "sin búfer".
#Es para el correcto funcionamiento en modo contenedor ya que es una imagen estática. 
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 5000

#Define el  comando que se ejecutará dentro del contenedor cuando este se ponga en marcha.
#Es una especie de instrucción de arranque.
CMD ["flask", "--app", "app.main:app", "run", "--host=0.0.0.0", "--port=5000"]
