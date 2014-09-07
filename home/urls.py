from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', views.home, name='home'),
     
    
)