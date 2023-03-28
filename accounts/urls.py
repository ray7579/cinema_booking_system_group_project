from django.urls import path
from .import views

urlpatterns=[
    #path('', views.home, name='home'),
    path('student_register/', views.student_register.as_view(), name='student_register'),
    path('clubrep_register/', views.clubrep_register.as_view(), name='clubrep_register'),
    path('cinemamanager_register/', views.cinemamanager_register.as_view(), name='cinemamanager_register'),
    path('accountmanager_register/', views.accountmanager_register.as_view(), name='accountmanager_register'),
    path('login/', views.login_request, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('404/', views.perm_denied, name = 'perm_blocked'),
    
    path('accountslist/', views.accountshome, name = "accountslist"),
    path('accountslist/updateuser/<user_id>', views.updateuser, name="updateuser"),
    path('accountslist/deleteuser/<user_id>', views.deleteuser, name="delete"),
 
]