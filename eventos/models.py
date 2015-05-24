from django.db import models

# Create your models here.

class Events (models.Model):
    titulo = models.CharField(max_length=50)
    tipo = models.CharField(max_length=50)
    fecha = models.DateTimeField()
    precio = models.CharField(max_length=50)
    largaDuracion = models.CharField(max_length=33)
    url = models.URLField()
    likes = models.IntegerField()
    comentario = models.TextField()
    fin = models.DateTimeField()


class tabUserEvent (models.Model):
    idUsuario = models.IntegerField()
    idEvento = models.IntegerField()
    fecha = models.DateTimeField()

class upDate(models.Model):
    dateUpDate = models.DateTimeField()

class miPagina(models.Model):
    nombre = models.CharField(max_length=20)
    titulo = models.CharField(max_length=30)
    comentario = models.TextField()
    color = models.CharField(max_length=10)
    letra = models.IntegerField()
    
