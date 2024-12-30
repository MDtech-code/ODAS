
from django.conf import settings
from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.core.urls')),
    path('account/', include('app.account.urls')),
    path('appointment/', include('app.appointments.urls')),
    path('blog/', include('app.blog.urls')),
    path('chat/', include('app.chat.urls')),
    path('notifications/',include('app.notification.urls')),
]

if settings.DEBUG: 
    import debug_toolbar
    urlpatterns = [ path('__debug__/', include(debug_toolbar.urls)) ] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)