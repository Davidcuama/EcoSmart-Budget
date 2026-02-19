# budget/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from datetime import datetime
from .models import Ingreso, Gasto, Presupuesto, Categoria


# Home
def home(request):
    total_ingresos = Ingreso.objects.aggregate(Sum('monto'))['monto__sum'] or 0
    total_gastos = Gasto.objects.aggregate(Sum('monto'))['monto__sum'] or 0
    balance = float(total_ingresos) - float(total_gastos)
    
    return render(request, 'budget/home.html', {
        'total_ingresos': total_ingresos,
        'total_gastos': total_gastos,
        'balance': balance,
    })


# FR6: Calcular presupuesto restante
def remaining_budget(request):
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    presupuestos = Presupuesto.objects.filter(mes=current_month, anio=current_year)
    
    presupuestos_con_restante = []
    for presupuesto in presupuestos:
        # Calcular total de gastos por categoría en el mes/año actual
        total_gastos = Gasto.objects.filter(
            categoria=presupuesto.categoria,
            fecha__month=current_month,
            fecha__year=current_year
        ).aggregate(Sum('monto'))['monto__sum'] or 0
        
        # Calcular restante
        restante = float(presupuesto.monto_limite) - float(total_gastos)
        porcentaje = (float(total_gastos) / float(presupuesto.monto_limite) * 100) if presupuesto.monto_limite > 0 else 0
        
        presupuestos_con_restante.append({
            'presupuesto': presupuesto,
            'total_gastos': total_gastos,
            'restante': restante,
            'porcentaje': round(porcentaje, 2),
            'estado': 'Excedido' if restante < 0 else 'OK'
        })
    
    return render(request, 'budget/remaining_budget.html', {
        'presupuestos': presupuestos_con_restante,
        'mes': current_month,
        'anio': current_year,
    })


# FR8: Gestionar categorías - Listar
def manage_categories(request):
    categorias = Categoria.objects.all()
    return render(request, 'budget/manage_categories.html', {
        'categorias': categorias,
    })


# FR8: Gestionar categorías - Crear
def category_create(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        if nombre:
            Categoria.objects.create(nombre=nombre)
            return redirect('manage_categories')
    
    return render(request, 'budget/category_form.html', {
        'titulo': 'Crear Categoría',
        'action': 'crear',
    })


# FR8: Gestionar categorías - Editar
def category_edit(request, id):
    categoria = get_object_or_404(Categoria, id=id)
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        if nombre:
            categoria.nombre = nombre
            categoria.save()
            return redirect('manage_categories')
    
    return render(request, 'budget/category_form.html', {
        'titulo': 'Editar Categoría',
        'action': 'editar',
        'categoria': categoria,
    })


# FR8: Gestionar categorías - Eliminar
def category_delete(request, id):
    categoria = get_object_or_404(Categoria, id=id)
    
    if request.method == 'POST':
        categoria.delete()
        return redirect('manage_categories')
    
    return render(request, 'budget/category_confirm_delete.html', {
        'categoria': categoria,
    })


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

