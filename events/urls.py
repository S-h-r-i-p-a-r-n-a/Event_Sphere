from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
from .views import register_event
urlpatterns = [
    path("register/", views.register_user, name="register"),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
    path("create-event/", views.create_event, name="create_event"),
    path("events/", views.event_list, name="home"),
    path("profile/", views.my_account, name="my_account"),
    path("edit-profile/", views.edit_profile, name="edit_profile"),
    path("delete-profile/", views.delete_profile, name="delete_profile"),
    path('register/<int:event_id>/', register_event, name='register_event'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
