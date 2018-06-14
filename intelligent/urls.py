from django.conf.urls import url, include
from django.conf.urls import static  
from django.conf import settings  
from django.views.static import serve 
from  .dm import entry
 

'''
    flm : classify machine
    jlm : cluster machine
    asm : associate machine

'''


urlpatterns = [
    url(r'^tumnus/dm/flm$', entry.guide),
    url(r'^tumnus/dm/jlm$', entry.guide),
    url(r'^static/(?P<path>.*)$', serve,{'document_root':settings.STATIC_ROOT}),
    url(r'^static/<?P<path>.*>$', serve,{'document_root':settings.MEDIA_ROOT})
]

