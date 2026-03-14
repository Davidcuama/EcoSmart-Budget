# budget/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('',                    views.home,               name='home'),                  # Home
    path('ingreso/',            views.income_register,    name='income_register'),       # FR3
    path('gasto/',              views.expense_record,     name='expense_record'),        # FR4
    path('presupuesto/',        views.budget_create,      name='budget_create'),         # FR5
    path('presupuesto/restante/', views.remaining_budget, name='remaining_budget'),     # FR6
    path('categorias/',         views.manage_categories,  name='manage_categories'),    # FR7
    path('categorias/crear/',   views.category_create,    name='category_create'),      # FR7
    path('categorias/<int:id>/editar/', views.category_edit, name='category_edit'),   # FR7
    path('categorias/<int:id>/eliminar/', views.category_delete, name='category_delete'), # FR7
]
