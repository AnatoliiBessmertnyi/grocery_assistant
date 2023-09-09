# from django.contrib import admin
# from django.urls import include, path
# from django.views.generic import TemplateView

# urlpatterns = [
#     path("admin/", admin.site.urls),
#     path("api/", include("api.urls")),
#     path(
#         "redoc/",
#         TemplateView.as_view(template_name="redoc.html"),
#         name="redoc",
#     ),
# ]

from django.urls import path

from recipes.views import api_recipes, api_recipes_detail

urlpatterns = [
    path('api/recipes/', api_recipes, name='api_recipes'),
    path('api/recipes/<int:pk>/', api_recipes_detail, name='api_recipes_pk'),
]