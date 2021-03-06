from django.conf.urls import patterns, include, url
from django.contrib import admin
from eventos.feeds import EventosFeed

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'myproject.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^todas$', 'eventos.views.showAllContent'),
    url(r'^iniciar_sesion$', 'eventos.views.signIn'),
    url(r'^nuevo_usuario$', 'eventos.views.signUp'),
    url(r'^cerrar_sesion$', 'eventos.views.logOut'),
    url(r'^actividad/(.*)', 'eventos.views.showEvent'),
    url(r'^megusta', 'eventos.views.plusLike'),
    url(r'^$', 'eventos.views.showContent'),
    url(r'^ayuda$', 'eventos.views.ayuda'),
    url(r'^insertar/actividad$', 'eventos.views.insertar'),
    url(r'^titulo/(.*)', 'eventos.views.cambiar'),
    url(r'^comentario/(.*)', 'eventos.views.cambiar'), 
    url(r'^actualizar$', 'eventos.views.actualizar'),
    url(r'^cambiar/css/(.*)', 'eventos.views.cambiarCss'), 
    url(r'^(?P<usu_name>.*)/rss$', EventosFeed()),     
    url(r'^(.*)', 'eventos.views.usuario'),
)
