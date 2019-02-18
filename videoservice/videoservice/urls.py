from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from .views import home, contact_view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('memberships/', include('memberships.urls', namespace='memberships')),
    path('courses/', include('courses.urls', namespace='courses')),
    path('blog/', include('blog.urls', namespace='blog')),
    path('comments/', include('comments.urls', namespace='comments')),
    path('', home, name='home'),
    path('contact/', contact_view),
]

# if settings.DEBUG:
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
