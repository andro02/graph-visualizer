"""
URL configuration for graph_explorer project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', views.IndexView.as_view(), name='index'),
    path('api/graphs/', views.api_graphs, name='api_graphs'),
    path('api/visualize/<path:graph_id>/', views.api_visualize, name='api_visualize'),
    path('api/graph_data/<path:graph_id>/', views.api_graph_json, name='api_graph_data'),
    path("api/graph/search", views.api_search, name='api_search'),
    path("api/graph/filter", views.api_filter, name='api_filter'),
    path("api/graph/reset", views.api_reset, name='api_reset'),
]
