from django.urls import path
from users.views.user_views import UserListCreateView, UserDetailView

urlpatterns = [
    path('', UserListCreateView.as_view(), name='user-list-create'),
    path('<int:id>', UserDetailView.as_view(), name='user-detail'),
]
