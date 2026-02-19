# budget/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('ingreso/',     views.income_register, name='income_register'),  # FR3
    path('gasto/',       views.expense_record,  name='expense_record'),   # FR4
    path('presupuesto/', views.budget_create,   name='budget_create'),    # FR5
]
