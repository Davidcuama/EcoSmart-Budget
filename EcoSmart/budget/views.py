# budget/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Avg, Count
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
        total_gastos = Gasto.objects.filter(
            categoria=presupuesto.categoria,
            fecha__month=current_month,
            fecha__year=current_year
        ).aggregate(Sum('monto'))['monto__sum'] or 0
        
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
    import json
    
    if request.method == 'POST':
        descripcion  = request.POST.get('descripcion')
        monto        = request.POST.get('monto')
        categoria_id = request.POST.get('categoria')

        categoria = Categoria.objects.get(id=categoria_id) if categoria_id else None
        Ingreso.objects.create(descripcion=descripcion, monto=monto, categoria=categoria)

        return redirect('income_register')

    # Filtro por categoría (GET)
    filtro_categoria = request.GET.get('categoria', '').strip()

    ingresos = Ingreso.objects.all()
    if filtro_categoria:
        ingresos = ingresos.filter(categoria__id=filtro_categoria)

    categorias = Categoria.objects.all()
    
    # ========== NUEVO CÓDIGO PARA LA GRÁFICA ==========
    # Agrupar ingresos por categoría
    ingresos_query = Ingreso.objects.all()
    if filtro_categoria:
        ingresos_query = ingresos_query.filter(categoria__id=filtro_categoria)
    
    ingresos_por_categoria = ingresos_query.values('categoria__nombre').annotate(
        total=Sum('monto')
    ).order_by('-total')
    
    # Preparar listas para la gráfica
    categorias_list = []
    montos_list = []
    
    for ingreso in ingresos_por_categoria:
        nombre = ingreso['categoria__nombre'] or 'Sin categoría'
        monto = float(ingreso['total']) if ingreso['total'] else 0
        
        categorias_list.append(nombre)
        montos_list.append(monto)
    
    # Convertir a JSON para pasar al HTML
    categorias_json = json.dumps(categorias_list)
    montos_json = json.dumps(montos_list)
    # ========== FIN DEL CÓDIGO NUEVO ==========
    
    return render(request, 'budget/income_register.html', {
        'categorias':           categorias,
        'ingresos':             ingresos,
        'filtro_categoria':     filtro_categoria,
        'categorias_json':      categorias_json,      # NUEVO
        'montos_json':          montos_json,          # NUEVO
    })

def income_delete(request, id):
    ingreso = get_object_or_404(Ingreso, id=id)
    if request.method == 'POST':
        ingreso.delete()
        return redirect('income_register')
    return redirect('income_register')

# FR4: Registrar gasto
def expense_record(request):
    import json  # Agregar al inicio
    
    if request.method == 'POST':
        descripcion  = request.POST.get('descripcion')
        monto        = request.POST.get('monto')
        categoria_id = request.POST.get('categoria')

        categoria = Categoria.objects.get(id=categoria_id) if categoria_id else None
        Gasto.objects.create(descripcion=descripcion, monto=monto, categoria=categoria)

        return redirect('expense_record')

    # Filtro por categoría (GET)
    filtro_categoria = request.GET.get('categoria', '').strip()

    gastos = Gasto.objects.all()
    if filtro_categoria:
        gastos = gastos.filter(categoria__id=filtro_categoria)

    categorias = Categoria.objects.all()
    
    # Agrupar gastos por categoría
    gastos_query = Gasto.objects.all()
    if filtro_categoria:
        gastos_query = gastos_query.filter(categoria__id=filtro_categoria)
    
    gastos_por_categoria = gastos_query.values('categoria__nombre').annotate(
        total=Sum('monto')
    ).order_by('-total')
    
    # Preparar listas para la gráfica
    categorias_list = []
    montos_list = []
    
    for gasto in gastos_por_categoria:
        nombre = gasto['categoria__nombre'] or 'Sin categoría'
        monto = float(gasto['total']) if gasto['total'] else 0
        
        categorias_list.append(nombre)
        montos_list.append(monto)
    
    # Convertir a JSON para pasar al HTML
    categorias_json = json.dumps(categorias_list)
    montos_json = json.dumps(montos_list)
    # ========== FIN DEL CÓDIGO NUEVO ==========
    
    return render(request, 'budget/expense_record.html', {
        'categorias':           categorias,
        'gastos':               gastos,
        'filtro_categoria':     filtro_categoria,
        'categorias_json':      categorias_json,      
        'montos_json':          montos_json,          
    })

def expense_delete(request, id):
    gasto = get_object_or_404(Gasto, id=id)
    if request.method == 'POST':
        gasto.delete()
        return redirect('expense_record')
    return redirect('expense_record')


# FR6: Historial de transacciones
def transaction_history(request):
    filtro_tipo      = request.GET.get('tipo', '')
    filtro_categoria = request.GET.get('categoria', '').strip()
    filtro_desde     = request.GET.get('desde', '')
    filtro_hasta     = request.GET.get('hasta', '')

    ingresos = Ingreso.objects.all()
    gastos   = Gasto.objects.all()

    if filtro_categoria:
        ingresos = ingresos.filter(categoria__id=filtro_categoria)
        gastos   = gastos.filter(categoria__id=filtro_categoria)

    if filtro_desde:
        ingresos = ingresos.filter(fecha__gte=filtro_desde)
        gastos   = gastos.filter(fecha__gte=filtro_desde)

    if filtro_hasta:
        ingresos = ingresos.filter(fecha__lte=filtro_hasta)
        gastos   = gastos.filter(fecha__lte=filtro_hasta)

    transacciones = []

    if filtro_tipo != 'gasto':
        for i in ingresos:
            transacciones.append({
                'tipo':       'ingreso',
                'descripcion': i.descripcion,
                'monto':       i.monto,
                'fecha':       i.fecha,
                'categoria':   i.categoria,
                'id':          i.id,
            })

    if filtro_tipo != 'ingreso':
        for g in gastos:
            transacciones.append({
                'tipo':       'gasto',
                'descripcion': g.descripcion,
                'monto':       g.monto,
                'fecha':       g.fecha,
                'categoria':   g.categoria,
                'id':          g.id,
            })

    transacciones.sort(key=lambda t: t['fecha'], reverse=True)

    categorias = Categoria.objects.all()

    return render(request, 'budget/transaction_history.html', {
        'transacciones':   transacciones,
        'categorias':      categorias,
        'filtro_tipo':     filtro_tipo,
        'filtro_categoria': int(filtro_categoria) if filtro_categoria else '',
        'filtro_desde':    filtro_desde,
        'filtro_hasta':    filtro_hasta,
    })


# FR20: Estadísticas financieras
def financial_statistics(request):
    from django.db.models.functions import TruncMonth
    from collections import defaultdict

    total_ingresos = Ingreso.objects.aggregate(total=Sum('monto'))['total'] or 0
    total_gastos   = Gasto.objects.aggregate(total=Sum('monto'))['total'] or 0
    balance        = float(total_ingresos) - float(total_gastos)
    tasa_ahorro    = round((balance / float(total_ingresos) * 100), 2) if total_ingresos > 0 else 0

    num_ingresos = Ingreso.objects.count()
    num_gastos   = Gasto.objects.count()

    promedio_ingreso = round(float(total_ingresos) / num_ingresos, 2) if num_ingresos > 0 else 0
    promedio_gasto   = round(float(total_gastos) / num_gastos, 2)     if num_gastos   > 0 else 0

    # Categoría con más gasto
    cat_gastos = (
        Gasto.objects
        .values('categoria__nombre')
        .annotate(total=Sum('monto'))
        .order_by('-total')
    )
    top_categoria = cat_gastos.first() if cat_gastos.exists() else None

    # Ingresos y gastos agrupados por mes
    ingresos_por_mes = (
        Ingreso.objects
        .annotate(mes=TruncMonth('fecha'))
        .values('mes')
        .annotate(total=Sum('monto'))
        .order_by('mes')
    )

    gastos_por_mes = (
        Gasto.objects
        .annotate(mes=TruncMonth('fecha'))
        .values('mes')
        .annotate(total=Sum('monto'))
        .order_by('mes')
    )

    meses = sorted(set(
        [r['mes'] for r in ingresos_por_mes] +
        [r['mes'] for r in gastos_por_mes]
    ))

    ing_dict   = {r['mes']: float(r['total']) for r in ingresos_por_mes}
    gasto_dict = {r['mes']: float(r['total']) for r in gastos_por_mes}

    evolucion = []
    for mes in meses:
        ing = ing_dict.get(mes, 0)
        gas = gasto_dict.get(mes, 0)
        evolucion.append({
            'mes':     mes.strftime('%b %Y'),
            'ingreso': ing,
            'gasto':   gas,
            'balance': round(ing - gas, 2),
        })

    # Mes con mayor gasto
    mes_mayor_gasto = max(evolucion, key=lambda x: x['gasto']) if evolucion else None

    return render(request, 'budget/financial_statistics.html', {
        'total_ingresos':  total_ingresos,
        'total_gastos':    total_gastos,
        'balance':         balance,
        'tasa_ahorro':     tasa_ahorro,
        'num_ingresos':    num_ingresos,
        'num_gastos':      num_gastos,
        'promedio_ingreso': promedio_ingreso,
        'promedio_gasto':  promedio_gasto,
        'top_categoria':   top_categoria,
        'evolucion':       evolucion,
        'mes_mayor_gasto': mes_mayor_gasto,
        'cat_gastos':      cat_gastos,
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