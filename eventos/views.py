# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse,HttpResponseNotFound
from urllib2 import urlopen
from bs4 import BeautifulSoup
from models import Events
from models import upDate
from models import tabUserEvent
from models import miPagina
from django.contrib.auth import authenticate, login , logout
from django.contrib.auth.models import User
import time
from django.template.loader import get_template
from django.template import Context

# Create your views here.


@csrf_exempt
def showAllContent(request):
    verb = request.method
    recurso = request.path

    if (len(Events.objects.all())==0):
        parser()

    #Indicar plantilla
    plantilla = get_template('index.html')
    #Coger 10 actividades por fecha o todas segun sea :/ o :/todas
    listaActividades = contenido(recurso)
    #fecha actualizacion
    lastUpdate = "Ultima actualizacion : "+str(upDate.objects.all()[0].dateUpDate).split(':00+00:00')[0]

    #direcciones a ayuda y 10 paginas
    dirPrincipal = 'http://localhost:8000/'
    dirAyuda = 'http://localhost:8000/ayuda'
    dirTodas = 'http://localhost:8000/todas'

    #Si esta registrado
    if request.user.is_authenticated():

        dirLogOut = 'http://localhost:8000/cerrar_sesion'
        evento = 'http://localhost:8000/actividad/'
        dirInsertar = 'http://localhost:8000/insertar/actividad'
        pagUsu = 'http://localhost:8000/'+request.user.username
        actualizarPag = 'http://localhost:8000/actualizar'


        if verb == 'GET':
              
            c = Context({'logOut': dirLogOut,'contenido': listaActividades,'horaActualizacion':lastUpdate,'nEventos':numEventos(),'pagEvento':evento,'ayuda':dirAyuda,'inicio':dirPrincipal, 'insertar': dirInsertar, 'usuario':pagUsu,'filtro':dirTodas,'recargar':actualizarPag})
            #Renderizar
            renderizado = plantilla.render(c)

        elif verb == 'POST':
            #Lista actividades nueva
            if(request.body.split('=')[1] == 'megusta'):
                listaActividades = Events.objects.order_by("-likes")
                print("ordeno por me gusta")
            else:
                palabra = request.body.split('=')[1]          
                listaActividades = Events.objects.filter(titulo__icontains=palabra)
 
            c = Context({'logOut': dirLogOut,'contenido': listaActividades,'horaActualizacion':lastUpdate,'nEventos':numEventos(),'pagEvento':evento,'ayuda':dirAyuda,'inicio':dirPrincipal, 'insertar': dirInsertar, 'usuario':pagUsu,'filtro':dirTodas})
            #Renderizar
            renderizado = plantilla.render(c)

    #Si no esta registrado
    else:
        
        if request.method == 'POST':
            if(request.body.split('=')[1] == 'megusta'):
                listaActividades = Events.objects.order_by("-likes")
            else:
                palabra = request.body.split('=')[1]          
                listaActividades = Events.objects.filter(titulo__icontains=palabra)
        else:
            listaActividades = contenido(recurso)

        #creo etiquetas
        dirRegUsu = 'http://localhost:8000/nuevo_usuario'
        dirInicio = 'http://localhost:8000/iniciar_sesion'

        c = Context({'dirRegistro':                 dirRegUsu,'dirIniSesion':dirInicio,'contenido':listaActividades,'ayuda':dirAyuda,'inicio':dirPrincipal,'filtro':dirTodas})
        #Renderizar
        renderizado = plantilla.render(c)

    return HttpResponse(renderizado)

@csrf_exempt
def actualizar(request):

    #Guardo hora actualizacion
    update = time.strftime("%Y-%m-%d %H:%M")
    oldDate = upDate.objects.all()[0]
    oldDate.dateUpDate = update
    oldDate.save()

    xmlPage = 'http://datos.madrid.es/portal/site/egob/menuitem.ac61933d6ee3c31cae77ae7784f1a5a0/?vgnextoid=00149033f2201410VgnVCM100000171f5a0aRCRD&format=xml&file=0&filename=206974-0-agenda-eventos-culturales-100&mgmtid=6c0b6d01df986410VgnVCM2000000c205a0aRCRD'

    soup = BeautifulSoup(urlopen(xmlPage),'xml')
    content = soup.findAll('contenido')
    #Saco mi base de datos de eventos para comparar con lo que ya tengo    
    db = Events.objects.all()

    existe = False

    for tag in content:
        #Titulos actividad
        title = tag.find(nombre = 'TITULO').string
        for evento in db:
            if(evento.titulo == title):
                existe = True

            if(not existe):
                #Tipo de evento, si no lo encuentra añado Sin titulo
                try:
                    typeEvent = tag.find(nombre = 'TIPO').string.split('actividades/')[1]       
                except:
                    typeEvent = "Sin tipo"
                #Busco los precios, si no tiene es gratuito
                try:
                    prize = tag.find(nombre = 'PRECIO').string        
                except:
                    prize = "Gratis"
                #Busco fecha de eventos
                date = tag.find(nombre = 'FECHA-EVENTO').string
                #Hora del evento
                hour = tag.find(nombre = 'HORA-EVENTO').string
                #Creo la fecha para el campo datefield
                date = date.replace('00:00:00.0',hour)
                #Si el valor devuelto es 1 sustituyo por larga duracion, si es 0 no
                try:
                    longDuration = tag.find(nombre = 'EVENTO-LARGA-DURACION').string
                except:
                    longDuration = 'Sin informacion de larga duracion'

                if longDuration == '0':
                    longDuration = longDuration.replace('0','Corta')

                elif longDuration == '1':
                    longDuration = longDuration.replace('1','Larga')
                #Busco urls con informacion adicional
                try:
                    Url = tag.find(nombre = 'CONTENT-URL-ACTIVIDAD').string       
                except:
                    Url = "Sin URL informacion"
                #Busco comentarios
                try:
                    coment = tag.find(nombre = 'DESCRIPCION').string       
                except:
                    coment = "Sin descripcion"
                #Busco fecha y hora finalizacion
                fechaFin = tag.find(nombre = 'FECHA-FIN-EVENTO').string
                #Guardo el que no existe
                Events( titulo =title, tipo = typeEvent , fecha = date , precio = prize , largaDuracion = longDuration , url = Url ,likes = 0,comentario = coment , fin = fechaFin).save() 

        
    
    return HttpResponse("<html>"
                        "<head>"
                        "<meta http-equiv= Refresh content= 0;url=http://localhost:8000/todas>"
                        "</head>"
                        "</html>")

def showContent(request):

    verb = request.method
    if (len(Events.objects.all())==0):
        parser()

    recurso = request.path

    #Indicar plantilla
    plantilla = get_template('index.html')
    #Coger 10 actividades por fecha o todas segun sea :/ o :/todas
    listaActividades = contenido(recurso)
    #direcciones a ayuda y todas las paginas
    dirTodas = 'http://localhost:8000/todas'
    dirAyuda = 'http://localhost:8000/ayuda'
    #lista de canales
    pagsPersonales = miPagina.objects.all()

    #Si esta registrado
    if request.user.is_authenticated():

        if verb == 'GET':
            
            #consigo mi nombre usuario una vez iniciada sesion
            nombreUsu = request.user.username

            dirLogOut = 'http://localhost:8000/cerrar_sesion'
            dirTodas = 'http://localhost:8000/todas'
            evento = 'http://127.0.0.1:8000/actividad/'
            dirInsertar = 'http://localhost:8000/insertar/actividad'
            pagUsu = 'http://localhost:8000/'+nombreUsu

            

            c = Context({'logOut': dirLogOut,'contenido': listaActividades,'pagEvento':evento,'todas':dirTodas,'ayuda':dirAyuda,'insertar': dirInsertar,'usuario' : pagUsu, 'canal': pagsPersonales})
            #Renderizar
            renderizado = plantilla.render(c)

    #Si no esta registrado
    else:
        
        #creo etiquetas
        dirRegUsu = 'http://localhost:8000/nuevo_usuario'
        dirInicio = 'http://localhost:8000/iniciar_sesion'
        listaActividades = contenido(recurso)
        c = Context({'dirRegistro':dirRegUsu,'dirIniSesion':dirInicio,'contenido':listaActividades,'todas':dirTodas,'ayuda':dirAyuda,'canal': pagsPersonales})
        #Renderizar
        renderizado = plantilla.render(c)

    return HttpResponse(renderizado)


@csrf_exempt
def insertar(request):

    #cojo el id del evento
    idEvent = request.body.split('=')[1]
    #consigo mi nombre usuario una vez iniciada sesion
    nombreUsu = request.user.username
    #saco su id
    usuario = User.objects.get(username = nombreUsu)
    idUser = usuario.id
    #cojo la fecha en la que selecciona el evento
    fechEvento = time.strftime("%Y-%m-%d %H:%M")
    
    if(len(tabUserEvent.objects.filter(idUsuario=idUser,idEvento = idEvent))==0): 
        tablaRelacion = tabUserEvent(idUsuario = idUser ,idEvento = idEvent ,fecha = fechEvento)
        tablaRelacion.save()

    return HttpResponse("<html>"
                        "<head>"
                        "<meta http-equiv= Refresh content= 0;url=http://localhost:8000/todas>"
                        "</head>"
                        "</html>")



def showEvent(request,event):

    plantilla = get_template('index.html')
    dirPrincipal = 'http://localhost:8000/'
    dirAyuda = 'http://localhost:8000/ayuda'

    try:
        contEvento = Events.objects.get(id = event)
    except:
        return HttpResponseNotFound("<html>"
                                    "<p>Error 404 Not found</p>"    
                                    "</html>")

    if request.user.is_authenticated():

        dirLogOut = 'http://localhost:8000/cerrar_sesion'
        dirInsertar = 'http://localhost:8000/insertar/actividad'
        pagUsu = 'http://localhost:8000/'+request.user.username
                
        
        try:
            idUsu = User.objects.get(username = request.user.username).id
            f = tabUserEvent.objects.get(idUsuario=idUsu,idEvento=event)
            fechaElegida = f.fecha
                                    
        except:
            
            fechaElegida = False                    

        c = Context({'logOut': dirLogOut,'evento':contEvento,'inicio':dirPrincipal,'insertar':dirInsertar,'ayuda':dirAyuda,'usuario':pagUsu,'fechaInsertado':fechaElegida})
        #Renderizar
        renderizado = plantilla.render(c)
    else:
        dirRegUsu = 'http://localhost:8000/nuevo_usuario'
        dirInicio = 'http://localhost:8000/iniciar_sesion'
        c = Context({'dirRegistro':dirRegUsu,'dirIniSesion':dirInicio,'evento':contEvento,'inicio':dirPrincipal,'ayuda':dirAyuda})
        #Renderizar
        renderizado = plantilla.render(c)

    return HttpResponse(renderizado)

@csrf_exempt
def cambiar(request,nameUser):

    tipo = request.path.split('/')[1]
    pag = miPagina.objects.get(nombre=nameUser)

    if tipo == 'comentario':
        
        pag.comentario = request.body.split('=')[1].replace('+',' ')
        pag.save()
    else:
        pag.titulo = request.body.split('=')[1].replace('+',' ')
        pag.save()
        
    return HttpResponse("<html>"
                        "<head>"
                        "<meta http-equiv= Refresh content= 0;url=http://localhost:8000/>"
                        "</head>"
                        "</html>") 


def usuario(request,nameUser):


    plantilla = get_template('index.html')

        
    dirAyuda = 'http://localhost:8000/ayuda' 
    dirPrincipal = 'http://localhost:8000/'
    dirRegUsu = 'http://localhost:8000/nuevo_usuario'
    dirInicio = 'http://localhost:8000/iniciar_sesion'   
    misEventos = []          

    idUsu = User.objects.get(username = nameUser).id
    misPags = tabUserEvent.objects.filter(idUsuario = idUsu)
    nombrePag = miPagina.objects.get(nombre=nameUser).titulo

    #Si el usuario que accede es el dueño de la pagina y esta registrado
    if(request.user.is_authenticated() and nameUser==request.user.username):    
        colorPag = miPagina.objects.get(nombre=nameUser).color
        letraPag = miPagina.objects.get(nombre=nameUser).letra
        dirCambio = 'http://localhost:8000/cambiar/css/'+nameUser
        tituloPag = 'http://localhost:8000/titulo/'+nameUser
        comentPag = 'http://localhost:8000/comentario/'+nameUser
        dirLogOut = 'http://localhost:8000/cerrar_sesion'
        pagUsu = 'http://localhost:8000/'+request.user.username
        dirInicio = False 
    elif(request.user.is_authenticated()):
        colorPag = False
        letraPag = False
        dirCambio = False
        tituloPag = False
        comentPag = False
        dirLogOut = 'http://localhost:8000/cerrar_sesion'
        pagUsu = 'http://localhost:8000/'+request.user.username
        dirRegUsu = False
        dirInicio = False
    else:  
        colorPag = False
        letraPag = False
        dirCambio = False
        tituloPag = False
        comentPag = False
        dirLogOut = False
        pagUsu = False
                      

    #Eventos seleccionados
    for line in misPags:
        misEventos.append(Events.objects.get(id = line.idEvento))    

    c = Context({'ayuda':dirAyuda,'logOut': dirLogOut,'inicio':dirPrincipal,'usuario':pagUsu,'seleccionados':misEventos,'titPage':tituloPag,
'comPage':comentPag,'namePag':nombrePag,'color':colorPag,'letra':letraPag,'css':dirCambio,'dirIniSesion':dirInicio,'dirRegistro':dirRegUsu})
    #Renderizar
    renderizado = plantilla.render(c)
    
    return HttpResponse(renderizado)


@csrf_exempt
def cambiarCss(request,nameUser):

    if(request.user.is_authenticated() and nameUser==request.user.username):
        cambio = request.body.split('=')[0]
        if(cambio=='size'):
            page = miPagina.objects.get(nombre=nameUser)
            page.letra = request.body.split('=')[1]
            page.save()
        elif(cambio=='color'):
            page = miPagina.objects.get(nombre=nameUser)
            page.color = request.body.split('=')[1]
            page.save()

    return HttpResponse("<html>"
                        "<head>"
                        "<meta http-equiv= Refresh content= 0;url=http://localhost:8000/"+nameUser+">"
                        "</head>"
                        "</html>")



def ayuda(request):

    dirInicio = 'http://localhost:8000'
    plantilla = get_template('ayuda.html')

    c = Context({'inicio':dirInicio})
    #Renderizar
    renderizado = plantilla.render(c)


    return HttpResponse(renderizado)

    return HttpResponse(renderizado)

@csrf_exempt
def plusLike(request):
    print request.body
    identificador = request.body.split('=')[1]
    evento = Events.objects.get(id=identificador)
    evento.likes = evento.likes+1
    evento.save()
    return HttpResponse("<html>"
                        "<head>"
                        "<meta http-equiv= Refresh content= 0;url=http://localhost:8000/todas>"
                        "</head>"
                        "</html>")


@csrf_exempt
def signUp(request):

    plantilla = get_template('sesion.html')

    verb = request.method
    dirAyuda = 'http://localhost:8000/ayuda'
    dirInicio = 'http://localhost:8000/todas'
    form = "REGISTRO" 
    dirRegistro = 'http://localhost:8000/nuevo_usuario' 

    if verb == 'GET':

        mensaje = False

    elif verb == 'POST':

        usuario = request.body.split('&')[0].split('=')[1]
        passw = request.body.split('&')[1].split('=')[1]
        usersList = User.objects.all()

        existe = False
        for name in usersList:
            
            if str(name) == str(usuario):
                existe = True
     
        if not existe:
            
            user = User.objects.create_user(usuario, '/', passw)
            return HttpResponse("<html>"
                    "<head>"
                    "<meta http-equiv= Refresh content= 0;url=http://localhost:8000/todas>"
                    "</head>"
                    "</html>")
        else:
            mensaje = "Usuario ya existente: "+usuario
        

    c = Context({'formUsu':dirRegistro,'fallo':mensaje,'inicio':dirInicio,'ayuda':dirAyuda,'titulo':form})
    #Renderizar
    renderizado = plantilla.render(c)
    return HttpResponse(renderizado)


@csrf_exempt
def signIn(request):

    plantilla = get_template('sesion.html')
    verb = request.method



    dirAyuda = 'http://localhost:8000/ayuda'
    dirInicio = 'http://localhost:8000/todas'
    dirInicioSesion = 'http://localhost:8000/iniciar_sesion' 
    mensaje = False
    form = "INICIO SESION"
    
 
    if verb == 'POST':
        print request.body
        usuario = request.body.split('&')[0].split('=')[1]
        passw = request.body.split('&')[1].split('=')[1]
        user = authenticate(username= usuario, password= passw)

        if user is not None:
            if user.is_active:
                login(request, user)
                #Creo la tabla correspondiente al canal del usuario
                try:
                    pag = miPagina.objects.get(nombre=usuario)

                except:
                    print("creo pagina usuario")            
                    miPagina(nombre=usuario,titulo="Pagina de "+usuario,comentario = "Sin comentario",color='black',letra=16).save()
                
                print("User is valid, active and authenticated")
                html = ("<html>"
                        "<head>"
                        "<meta http-equiv= Refresh content= 0;url=http://localhost:8000/todas>"
                        "</head>"
                        "</html>")
                return HttpResponse(html)

        else:
            print("The username and password were incorrect.")
            mensaje = 'Contraseña o usuario incorrectos'
            
    c = Context({'formUsu':dirInicioSesion,'fallo':mensaje,'inicio':dirInicio,'ayuda':dirAyuda,'titulo':form})
    #Renderizar
    renderizado = plantilla.render(c)
    return HttpResponse(renderizado)


def logOut(request):

    logout(request)

    return HttpResponse("<html>"
                        "<head>"
                        "<meta http-equiv= Refresh content= 0;url=http://localhost:8000/todas>"
                        "</head>"
                        "</html>")


def numEventos():
    return (str(len(Events.objects.all())))

def contenido(path):
    eventos = Events.objects.order_by('fecha')
    if path == '/':
        eventos = eventos[:10]           
    else:
        eventos
    return eventos

def parser():

    xmlPage = 'http://datos.madrid.es/portal/site/egob/menuitem.ac61933d6ee3c31cae77ae7784f1a5a0/?vgnextoid=00149033f2201410VgnVCM100000171f5a0aRCRD&format=xml&file=0&filename=206974-0-agenda-eventos-culturales-100&mgmtid=6c0b6d01df986410VgnVCM2000000c205a0aRCRD'

    soup = BeautifulSoup(urlopen(xmlPage),'xml')
    content = soup.findAll('contenido')

    update = time.strftime("%Y-%m-%d %H:%M")
    fh = upDate(dateUpDate = update)
    fh.save()
    for tag in content:
        #Titulos actividad
        title = tag.find(nombre = 'TITULO').string
        #Tipo de evento, si no lo encuentra añado Sin titulo
        try:
            typeEvent = tag.find(nombre = 'TIPO').string.split('actividades/')[1]       
        except:
            typeEvent = "Sin tipo"
        #Busco los precios, si no tiene es gratuito
        try:
            prize = tag.find(nombre = 'PRECIO').string        
        except:
            prize = "Gratis"
        #Busco fecha de eventos
        date = tag.find(nombre = 'FECHA-EVENTO').string
        #Hora del evento
        hour = tag.find(nombre = 'HORA-EVENTO').string
        #Creo la fecha para el campo datefield
        date = date.replace('00:00:00.0',hour)
        #Si el valor devuelto es 1 sustituyo por larga duracion, si es 0 no
        try:
            longDuration = tag.find(nombre = 'EVENTO-LARGA-DURACION').string
        except:
            longDuration = 'Sin informacion de larga duracion'

        if longDuration == '0':
            longDuration = longDuration.replace('0','Corta')

        elif longDuration == '1':
            longDuration = longDuration.replace('1','Larga')
        #Busco urls con informacion adicional
        try:
            Url = tag.find(nombre = 'CONTENT-URL-ACTIVIDAD').string       
        except:
            Url = "Sin URL informacion"
        #Busco comentarios
        try:
            coment = tag.find(nombre = 'DESCRIPCION').string       
        except:
            coment = "Sin descripcion"
        #Busco fecha y hora finalizacion
        fechaFin = tag.find(nombre = 'FECHA-FIN-EVENTO').string       
                
                        
        tableEvents = Events( titulo =title, tipo = typeEvent , fecha = date , precio = prize , largaDuracion = longDuration , url = Url ,likes = 0,comentario = coment , fin = fechaFin)    
        tableEvents.save()

    return None
    
