# budget/views.py
from django.shortcuts import render, redirect
from .models import Ingreso, Gasto, Presupuesto, Categoria


# FR3: Registrar ingreso
def income_register(request):
    if request.method == 'POST':
        descripcion  = request.POST.get('descripcion')
        monto        = request.POST.get('monto')
        categoria_id = request.POST.get('categoria')

        categoria = Categoria.objects.get(id=categoria_id) if categoria_id else None
        Ingreso.objects.create(descripcion=descripcion, monto=monto, categoria=categoria)

        return redirect('income_register')

    categorias = Categoria.objects.all()
    ingresos   = Ingreso.objects.all()
    return render(request, 'budget/income_register.html', {
        'categorias': categorias,
        'ingresos':   ingresos,
    })


# FR4: Registrar gasto
def expense_record(request):
    if request.method == 'POST':
        descripcion  = request.POST.get('descripcion')
        monto        = request.POST.get('monto')
        categoria_id = request.POST.get('categoria')

        categoria = Categoria.objects.get(id=categoria_id) if categoria_id else None
        Gasto.objects.create(descripcion=descripcion, monto=monto, categoria=categoria)

        return redirect('expense_record')

    categorias = Categoria.objects.all()
    gastos     = Gasto.objects.all()
    return render(request, 'budget/expense_record.html', {
        'categorias': categorias,
        'gastos':     gastos,
    })


# FR5: Crear presupuesto
def budget_create(request):
    if request.method == 'POST':
        categoria_id = request.POST.get('categoria')
        monto_limite = request.POST.get('monto_limite')
        mes          = request.POST.get('mes')
        anio         = request.POST.get('anio')

        categoria = Categoria.objects.get(id=categoria_id)
        Presupuesto.objects.create(
            categoria=categoria,
            monto_limite=monto_limite,
            mes=mes,
            anio=anio,
        )
        return redirect('budget_create')

    categorias   = Categoria.objects.all()
    presupuestos = Presupuesto.objects.all()
    return render(request, 'budget/budget_create.html', {
        'categorias':   categorias,
        'presupuestos': presupuestos,
    })
