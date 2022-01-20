from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, include

from .views import *

urlpatterns = [
    # path('items/api/<characters:int>', ItemsView.as_view()),
    path('', index, name="index"),
    path('search/', search_result_ajax, name="search"),
    path('item_search/', ajax_items_live_search, name="item_search"),
    path('transfer/', transfer_to_ajax, name="transfer"),
    path('delete_item/', delete_item_ajax, name="delete_item"),
    path('login/', LoginView.as_view(template_name='login_index.html'), name="login"),
    path('logout/', LogoutView.as_view(template_name='logout.html'), name="logout"),
    path('register/', register, name="register"),
    path('upload/', upload, name="upload"),
    path('manage/', manage, name="manage"),
    path('create/', create_character, name="create_char"),

    path('', include('django.contrib.auth.urls')),

    # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)