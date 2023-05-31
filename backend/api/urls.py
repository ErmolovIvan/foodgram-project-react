from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'tags', views.TagViewSet, basename='tags')
router.register(
    r'ingredients', views.IngredientViewSet,
    basename='ingredients'
)
router.register(r'recipes', views.RecipeViewSet, basename='recipes')


urlpatterns = [
    path(
        'users/subscriptions/',
        views.SubscriptionsView.as_view({'get': 'list'})
    ),
    path('users/<int:user_id>/subscribe/', views.SubscribeView.as_view()),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
