# budget/admin.py
from django.contrib import admin
from .models import Categoria, Ingreso, Gasto, Presupuesto

admin.site.register(Categoria)
admin.site.register(Ingreso)
admin.site.register(Gasto)
admin.site.register(Presupuesto)
