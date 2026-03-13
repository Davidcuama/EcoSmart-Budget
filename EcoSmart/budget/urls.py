# budget/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('',                    views.home,               name='home'),                  # Home
    path('ingreso/',            views.income_register,    name='income_register'),       # FR3
    path('ingreso/<int:id>/eliminar/', views.income_delete, name='income_delete'),     # FR3
    path('gasto/',              views.expense_record,     name='expense_record'),        # FR4
    path('gasto/<int:id>/eliminar/', views.expense_delete, name='expense_delete'),     # FR4
    path('presupuesto/',        views.budget_create,      name='budget_create'),         # FR5
    path('presupuesto/<int:id>/eliminar/', views.budget_delete, name='budget_delete'), # FR5
    path('presupuesto/restante/', views.remaining_budget, name='remaining_budget'),     # FR6
    path('categorias/',         views.manage_categories,  name='manage_categories'),    # FR7
    path('categorias/crear/',   views.category_create,    name='category_create'),      # FR7
    path('categorias/<int:id>/editar/', views.category_edit, name='category_edit'),   # FR7
    path('categorias/<int:id>/eliminar/', views.category_delete, name='category_delete'), # FR7
    path('transacciones/',      views.transaction_history, name='transaction_history'), # FR6
    path('estadisticas/',       views.financial_statistics, name='financial_statistics'), # FR20
]
