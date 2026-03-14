from django.contrib import admin
from django.urls import path
from budget import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('historial/', views.transaction_history, name='transaction_history'),
    path('estadisticas/', views.financial_statistics, name='financial_statistics'),
    path('ahorro/objetivo/', views.savings_goal, name='savings_goal'),
    path('ingreso/', views.income_register, name='income_register'),
    path('ingreso/eliminar/<int:id>/', views.income_delete, name='income_delete'),
    path('gasto/', views.expense_record, name='expense_record'),
    path('presupuesto/', views.budget_create, name='budget_create'),
    path('presupuesto/restante/', views.remaining_budget, name='remaining_budget'),
    path('categorias/', views.manage_categories, name='manage_categories'),
    path('categorias/crear/', views.category_create, name='category_create'),
    path('categorias/editar/<int:id>/', views.category_edit, name='category_edit'),
    path('categorias/eliminar/<int:id>/', views.category_delete, name='category_delete'),
    path('gasto/eliminar/<int:id>/', views.expense_delete, name='expense_delete'),
]