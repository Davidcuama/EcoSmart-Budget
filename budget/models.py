# budget/models.py
from django.db import models


class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


# FR3
class Ingreso(models.Model):
    descripcion = models.CharField(max_length=200)
    monto       = models.DecimalField(max_digits=10, decimal_places=2)
    fecha       = models.DateField(auto_now_add=True)
    categoria   = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.descripcion


# FR4
class Gasto(models.Model):
    descripcion = models.CharField(max_length=200)
    monto       = models.DecimalField(max_digits=10, decimal_places=2)
    fecha       = models.DateField(auto_now_add=True)
    categoria   = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.descripcion


# FR5
class Presupuesto(models.Model):
    categoria    = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    monto_limite = models.DecimalField(max_digits=10, decimal_places=2)
    mes          = models.PositiveIntegerField()
    anio         = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.categoria} - {self.mes}/{self.anio}"
