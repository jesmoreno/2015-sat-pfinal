from django.contrib.syndication.views import Feed
from eventos.models import Events
from eventos.models import tabUserEvent
from django.contrib.auth.models import User

class EventosFeed(Feed):
    # atributos basicos del feed
    title='Eventos elegidos'
    link='http://localhost:8000/'
    description='Eventos seleccionados por el usuario'


    def get_object(self, request, usu_name):
        idUsu = User.objects.get(username = usu_name).id
        return tabUserEvent.objects.filter(idUsuario=idUsu)


    def items(self, obj):
        salida = []
        for linea in obj:
            salida.append(Events.objects.get(id=linea.idEvento))
            
        return salida

    def item_title(self, item):
        return item.titulo
   
    def item_link(self,item):
             
        return "http://localhost:8000/actividad/"+str(item.id)

