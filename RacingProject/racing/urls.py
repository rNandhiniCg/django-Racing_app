from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import  *

urlpatterns = [
    path('home/',views.home,name='home'),

    path('team/', views.team_list, name='team_list'),
    path('team/create/', views.team_create, name='team_create'),
    path('team/<int:pk>/update/', views.team_edit, name='team_edit'),
    path('team/<int:pk>/delete/', TeamDeleteView.as_view(), name='team_delete'),

    path('driver/', views.driver_list, name='driver_list'),
    path('driver/create/', views.driver_create, name='driver_create'),
    path('driver/<int:pk>/update/', views.driver_edit, name='driver_edit'),
    path('driver/<int:pk>/delete/', DriverDeleteView.as_view(), name='driver_delete'),

    path('race/', views.race_list, name='race_list'),
    path('race/create/', views.race_create, name='race_create'),  
    path('race/<int:pk>/update/', views.race_edit, name='race_edit'),
    path('race/<int:pk>/delete/', RaceDeleteView.as_view(), name='race_delete'),

    path('driver/<int:driver_id>/race-register/', views.register_driver_to_race, name='register_driver_to_race'),
    path('race/<int:race_id>/edit-driver/', views.edit_race_drivers, name='edit_race_drivers'),

#API views urls
    path('teams/', TeamListView.as_view(), name='team-list'),
    path('teams/create/', TeamCreateView.as_view(), name='team-create'),
    path('teams/<int:pk>/', TeamRetrieveView.as_view(), name='team-detail'),
    path('teams/<int:pk>/update/', TeamUpdateView.as_view(), name='team-update'),
    path('teams/<int:pk>/delete/', TeamDeleteViewAPI.as_view(), name='team-delete'),

    path('drivers/', DriverListView.as_view(), name='driver-list'),
    path('drivers/create/', DriverCreateView.as_view(), name='driver-create'),
    path('drivers/<int:pk>/', DriverRetrieveView.as_view(), name='driver-detail'),
    path('drivers/<int:pk>/update/', DriverUpdateView.as_view(), name='driver-update'),
    path('drivers/<int:pk>/delete/', DriverDeleteViewAPI.as_view(), name='driver-delete'),

    path('races/', RaceListView.as_view(), name='race-list'),
    path('races/create/', RaceCreateView.as_view(), name='race-create'),
    path('races/<int:pk>/', RaceRetrieveView.as_view(), name='race-detail'),
    path('races/<int:pk>/update/', RaceUpdateView.as_view(), name='race-update'),
    path('races/<int:pk>/delete/', RaceDeleteViewAPI.as_view(), name='race-delete'),
   
    path('races/<int:race_id>/add-drivers/', AddDriversToRaceAPIView.as_view(), name='add-drivers-to-race'),
   
]