# budget/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db.models import Sum, Avg, Count
from datetime import datetime
from decimal import Decimal, InvalidOperation
from .models import Ingreso, Gasto, Presupuesto, Categoria, ObjetivoAhorro


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


def savings_goal(request):
    error = None

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_progress':
            objetivo_id = request.POST.get('objetivo_id')
            abono_raw = request.POST.get('abono', '').strip()

            if not objetivo_id or not abono_raw:
                error = 'Debes indicar un objetivo y un monto para registrar avance.'
            else:
                try:
                    abono = Decimal(abono_raw)
                    if abono <= 0:
                        error = 'El abono debe ser mayor que 0.'
                    else:
                        objetivo = get_object_or_404(ObjetivoAhorro, id=objetivo_id)
                        objetivo.monto_ahorrado = objetivo.monto_ahorrado + abono
                        objetivo.save(update_fields=['monto_ahorrado'])
                        return redirect('savings_goal')
                except InvalidOperation:
                    error = 'El monto del abono no es válido.'
        else:
            nombre = request.POST.get('nombre', '').strip()
            monto_objetivo_raw = request.POST.get('monto_objetivo', '').strip()
            fecha_objetivo = request.POST.get('fecha_objetivo') or None

            if not nombre or not monto_objetivo_raw:
                error = 'Debes completar nombre y monto objetivo.'
            else:
                try:
                    monto_objetivo = Decimal(monto_objetivo_raw)
                    if monto_objetivo <= 0:
                        error = 'El monto objetivo debe ser mayor que 0.'
                    else:
                        ObjetivoAhorro.objects.create(
                            nombre=nombre,
                            monto_objetivo=monto_objetivo,
                            fecha_objetivo=fecha_objetivo,
                        )
                        return redirect('savings_goal')
                except InvalidOperation:
                    error = 'El monto objetivo no es válido.'

    objetivos_db = ObjetivoAhorro.objects.all().order_by('-fecha_creacion', '-id')
    objetivos = []
    for objetivo in objetivos_db:
        monto_objetivo = float(objetivo.monto_objetivo)
        monto_ahorrado = float(objetivo.monto_ahorrado)
        progreso = 0
        if monto_objetivo > 0:
            progreso = round((monto_ahorrado / monto_objetivo) * 100, 2)
        progreso_visual = min(progreso, 100)
        restante = round(monto_objetivo - monto_ahorrado, 2)
        objetivos.append({
            'obj': objetivo,
            'progreso': progreso,
            'progreso_visual': progreso_visual,
            'restante': restante,
            'completado': monto_ahorrado >= monto_objetivo,
        })

    return render(request, 'budget/savings_goal.html', {
        'objetivos': objetivos,
        'error': error,
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


# Export mensual a PDF
def export_pdfpage(request):
    """Mostrar página de descarga de reportes (PDF y Excel)"""
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # Generar lista de años (últimos 5 años y próximos 2)
    years = list(range(current_year - 5, current_year + 3))
    
    return render(request, 'budget/export_pdf.html', {
        'current_month': current_month,
        'current_year': current_year,
        'years': years,
    })


def export_monthly_pdf(request):
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib.units import inch
    
    # Obtener mes y año del request
    mes = request.GET.get('mes', datetime.now().month)
    anio = request.GET.get('anio', datetime.now().year)
    
    try:
        mes = int(mes)
        anio = int(anio)
    except (ValueError, TypeError):
        mes = datetime.now().month
        anio = datetime.now().year
    
    # Crear respuesta PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_{mes:02d}_{anio}.pdf"'
    
    # Crear documento PDF
    doc = SimpleDocTemplate(response, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a472a'),
        spaceAfter=30,
        alignment=1  # centrado
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2d7a4a'),
        spaceAfter=12,
        spaceBefore=12,
    )
    
    # Título
    mes_nombre = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'][mes-1]
    title = Paragraph(f'Reporte Financiero - {mes_nombre} {anio}', title_style)
    story.append(title)
    story.append(Spacer(1, 0.3*inch))
    
    # ==================== PRESUPUESTOS Y GASTOS ====================
    story.append(Paragraph('Presupuestos vs Gastos', heading_style))
    
    presupuestos = Presupuesto.objects.filter(mes=mes, anio=anio)
    
    if presupuestos.exists():
        datos_presupuesto = [['Categoría', 'Límite', 'Gasto', 'Disponible', 'Estado']]
        
        for presupuesto in presupuestos:
            gasto_total = Gasto.objects.filter(
                categoria=presupuesto.categoria,
                fecha__month=mes,
                fecha__year=anio
            ).aggregate(Sum('monto'))['monto__sum'] or 0
            
            disponible = float(presupuesto.monto_limite) - float(gasto_total)
            estado = 'EXCEDIDO' if disponible < 0 else 'OK'
            
            datos_presupuesto.append([
                str(presupuesto.categoria),
                f"${presupuesto.monto_limite:,.2f}",
                f"${gasto_total:,.2f}",
                f"${disponible:,.2f}",
                estado
            ])
        
        tabla_presupuesto = Table(datos_presupuesto, colWidths=[1.8*inch, 1.1*inch, 1.1*inch, 1.1*inch, 0.9*inch])
        tabla_presupuesto.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d7a4a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
        ]))
        
        story.append(tabla_presupuesto)
    else:
        story.append(Paragraph('No hay presupuestos registrados para este mes.', styles['Normal']))
    
    story.append(Spacer(1, 0.2*inch))
    
    # ==================== INGRESOS ====================
    story.append(Paragraph('Ingresos del Mes', heading_style))
    
    ingresos = Ingreso.objects.filter(fecha__month=mes, fecha__year=anio)
    total_ingresos = ingresos.aggregate(Sum('monto'))['monto__sum'] or 0
    
    if ingresos.exists():
        datos_ingresos = [['Descripción', 'Categoría', 'Monto', 'Fecha']]
        
        for ingreso in ingresos:
            datos_ingresos.append([
                ingreso.descripcion,
                str(ingreso.categoria) if ingreso.categoria else 'Sin categoría',
                f"${ingreso.monto:,.2f}",
                ingreso.fecha.strftime('%d/%m/%Y')
            ])
        
        datos_ingresos.append(['TOTAL', '', f"${total_ingresos:,.2f}", ''])
        
        tabla_ingresos = Table(datos_ingresos, colWidths=[2.2*inch, 1.5*inch, 1.3*inch, 1.2*inch])
        tabla_ingresos.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d7a4a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor('#e8f5e9')),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#c8e6c9')),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f0f8f0')]),
        ]))
        
        story.append(tabla_ingresos)
    else:
        story.append(Paragraph('No hay ingresos registrados para este mes.', styles['Normal']))
    
    story.append(Spacer(1, 0.2*inch))
    
    # ==================== GASTOS ====================
    story.append(Paragraph('Gastos del Mes', heading_style))
    
    gastos = Gasto.objects.filter(fecha__month=mes, fecha__year=anio)
    total_gastos = gastos.aggregate(Sum('monto'))['monto__sum'] or 0
    
    if gastos.exists():
        datos_gastos = [['Descripción', 'Categoría', 'Monto', 'Fecha']]
        
        for gasto in gastos:
            datos_gastos.append([
                gasto.descripcion,
                str(gasto.categoria) if gasto.categoria else 'Sin categoría',
                f"${gasto.monto:,.2f}",
                gasto.fecha.strftime('%d/%m/%Y')
            ])
        
        datos_gastos.append(['TOTAL', '', f"${total_gastos:,.2f}", ''])
        
        tabla_gastos = Table(datos_gastos, colWidths=[2.2*inch, 1.5*inch, 1.3*inch, 1.2*inch])
        tabla_gastos.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#c62828')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor('#ffebee')),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#ef9a9a')),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#fff0f0')]),
        ]))
        
        story.append(tabla_gastos)
    else:
        story.append(Paragraph('No hay gastos registrados para este mes.', styles['Normal']))
    
    story.append(Spacer(1, 0.2*inch))
    
    # ==================== RESUMEN ====================
    story.append(Paragraph('Resumen Mensual', heading_style))
    
    balance = float(total_ingresos) - float(total_gastos)
    
    datos_resumen = [
        ['Total Ingresos', f"${total_ingresos:,.2f}"],
        ['Total Gastos', f"${total_gastos:,.2f}"],
        ['Balance', f"${balance:,.2f}"],
    ]
    
    tabla_resumen = Table(datos_resumen, colWidths=[3*inch, 2*inch])
    tabla_resumen.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f5f5f5')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
    ]))
    
    story.append(tabla_resumen)
    
    story.append(PageBreak())
    
    # ==================== OBJETIVOS DE AHORRO ====================
    story.append(Paragraph('Objetivos de Ahorro y Progreso', heading_style))
    
    objetivos = ObjetivoAhorro.objects.all()
    
    if objetivos.exists():
        datos_objetivos = [['Objetivo', 'Meta', 'Ahorrado', 'Progreso', 'Restante']]
        
        for objetivo in objetivos:
            monto_objetivo = float(objetivo.monto_objetivo)
            monto_ahorrado = float(objetivo.monto_ahorrado)
            progreso = round((monto_ahorrado / monto_objetivo * 100), 2) if monto_objetivo > 0 else 0
            restante = round(monto_objetivo - monto_ahorrado, 2)
            
            # Crear barra de progreso con caracteres
            barra_length = 20
            filled = int(barra_length * progreso / 100)
            barra = '█' * filled + '░' * (barra_length - filled)
            
            datos_objetivos.append([
                objetivo.nombre,
                f"${monto_objetivo:,.2f}",
                f"${monto_ahorrado:,.2f}",
                f"{progreso}%",
                f"${restante:,.2f}"
            ])
        
        tabla_objetivos = Table(datos_objetivos, colWidths=[1.8*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1.2*inch])
        tabla_objetivos.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d7a4a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0fdf0')),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        ]))
        
        story.append(tabla_objetivos)
    else:
        story.append(Paragraph('No hay objetivos de ahorro registrados.', styles['Normal']))
    
    # Construir el PDF
    doc.build(story)
    
    return response


# Export mensual a Excel
def export_monthly_excel(request):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    
    # Obtener mes y año del request
    mes = request.GET.get('mes', datetime.now().month)
    anio = request.GET.get('anio', datetime.now().year)
    
    try:
        mes = int(mes)
        anio = int(anio)
    except (ValueError, TypeError):
        mes = datetime.now().month
        anio = datetime.now().year
    
    # Crear workbook
    wb = Workbook()
    ws = wb.active
    ws.title = 'Reporte'
    
    # Estilos
    titulo_font = Font(name='Calibri', size=16, bold=True, color='FFFFFF')
    titulo_fill = PatternFill(start_color='1a472a', end_color='1a472a', fill_type='solid')
    
    header_font = Font(name='Calibri', size=11, bold=True, color='FFFFFF')
    header_fill = PatternFill(start_color='2d7a4a', end_color='2d7a4a', fill_type='solid')
    
    total_font = Font(name='Calibri', size=11, bold=True)
    total_fill = PatternFill(start_color='E8F5E9', end_color='E8F5E9', fill_type='solid')
    
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # Título
    mes_nombre = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'][mes-1]
    
    ws.merge_cells('A1:E1')
    titulo = ws['A1']
    titulo.value = f'Reporte Financiero - {mes_nombre} {anio}'
    titulo.font = titulo_font
    titulo.fill = titulo_fill
    titulo.alignment = Alignment(horizontal='center', vertical='center')
    ws.row_dimensions[1].height = 25
    
    row = 3
    
    # ==================== PRESUPUESTOS ====================
    ws.merge_cells(f'A{row}:E{row}')
    header = ws[f'A{row}']
    header.value = 'Presupuestos vs Gastos'
    header.font = header_font
    header.fill = header_fill
    header.alignment = Alignment(horizontal='left', vertical='center')
    row += 1
    
    presupuestos = Presupuesto.objects.filter(mes=mes, anio=anio)
    
    if presupuestos.exists():
        # Headers
        headers = ['Categoría', 'Límite', 'Gasto', 'Disponible', 'Estado']
        for col, header_val in enumerate(headers, 1):
            cell = ws.cell(row=row, column=col)
            cell.value = header_val
            cell.font = header_font
            cell.fill = header_fill
            cell.border = border
            cell.alignment = Alignment(horizontal='center')
        
        row += 1
        
        for presupuesto in presupuestos:
            gasto_total = Gasto.objects.filter(
                categoria=presupuesto.categoria,
                fecha__month=mes,
                fecha__year=anio
            ).aggregate(Sum('monto'))['monto__sum'] or 0
            
            disponible = float(presupuesto.monto_limite) - float(gasto_total)
            estado = 'EXCEDIDO' if disponible < 0 else 'OK'
            
            ws.cell(row=row, column=1).value = str(presupuesto.categoria)
            ws.cell(row=row, column=2).value = float(presupuesto.monto_limite)
            ws.cell(row=row, column=3).value = float(gasto_total)
            ws.cell(row=row, column=4).value = disponible
            ws.cell(row=row, column=5).value = estado
            
            for col in range(1, 6):
                ws.cell(row=row, column=col).border = border
                ws.cell(row=row, column=col).alignment = Alignment(horizontal='center')
                if col > 1:
                    ws.cell(row=row, column=col).number_format = '$#,##0.00'
            
            row += 1
    else:
        ws.merge_cells(f'A{row}:E{row}')
        ws.cell(row=row, column=1).value = 'No hay presupuestos registrados para este mes.'
        row += 1
    
    row += 1
    
    # ==================== INGRESOS ====================
    ws.merge_cells(f'A{row}:E{row}')
    header = ws[f'A{row}']
    header.value = 'Ingresos del Mes'
    header.font = header_font
    header.fill = header_fill
    header.alignment = Alignment(horizontal='left', vertical='center')
    row += 1
    
    ingresos = Ingreso.objects.filter(fecha__month=mes, fecha__year=anio)
    total_ingresos = ingresos.aggregate(Sum('monto'))['monto__sum'] or 0
    
    if ingresos.exists():
        # Headers
        headers = ['Descripción', 'Categoría', 'Monto', 'Fecha']
        for col, header_val in enumerate(headers, 1):
            cell = ws.cell(row=row, column=col)
            cell.value = header_val
            cell.font = header_font
            cell.fill = PatternFill(start_color='E8F5E9', end_color='E8F5E9', fill_type='solid')
            cell.border = border
        
        row += 1
        
        for ingreso in ingresos:
            ws.cell(row=row, column=1).value = ingreso.descripcion
            ws.cell(row=row, column=2).value = str(ingreso.categoria) if ingreso.categoria else 'Sin categoría'
            ws.cell(row=row, column=3).value = float(ingreso.monto)
            ws.cell(row=row, column=4).value = ingreso.fecha
            
            for col in range(1, 5):
                ws.cell(row=row, column=col).border = border
            ws.cell(row=row, column=3).number_format = '$#,##0.00'
            ws.cell(row=row, column=4).number_format = 'dd/mm/yyyy'
            
            row += 1
        
        # Total
        ws.cell(row=row, column=1).value = 'TOTAL'
        ws.cell(row=row, column=3).value = float(total_ingresos)
        for col in range(1, 5):
            ws.cell(row=row, column=col).font = total_font
            ws.cell(row=row, column=col).fill = total_fill
            ws.cell(row=row, column=col).border = border
        ws.cell(row=row, column=3).number_format = '$#,##0.00'
        
        row += 1
    else:
        ws.merge_cells(f'A{row}:E{row}')
        ws.cell(row=row, column=1).value = 'No hay ingresos registrados para este mes.'
        row += 1
    
    row += 1
    
    # ==================== GASTOS ====================
    ws.merge_cells(f'A{row}:E{row}')
    header = ws[f'A{row}']
    header.value = 'Gastos del Mes'
    header.font = header_font
    header.fill = PatternFill(start_color='C62828', end_color='C62828', fill_type='solid')
    header.alignment = Alignment(horizontal='left', vertical='center')
    row += 1
    
    gastos = Gasto.objects.filter(fecha__month=mes, fecha__year=anio)
    total_gastos = gastos.aggregate(Sum('monto'))['monto__sum'] or 0
    
    if gastos.exists():
        # Headers
        headers = ['Descripción', 'Categoría', 'Monto', 'Fecha']
        for col, header_val in enumerate(headers, 1):
            cell = ws.cell(row=row, column=col)
            cell.value = header_val
            cell.font = header_font
            cell.fill = PatternFill(start_color='FFEBEE', end_color='FFEBEE', fill_type='solid')
            cell.border = border
        
        row += 1
        
        for gasto in gastos:
            ws.cell(row=row, column=1).value = gasto.descripcion
            ws.cell(row=row, column=2).value = str(gasto.categoria) if gasto.categoria else 'Sin categoría'
            ws.cell(row=row, column=3).value = float(gasto.monto)
            ws.cell(row=row, column=4).value = gasto.fecha
            
            for col in range(1, 5):
                ws.cell(row=row, column=col).border = border
            ws.cell(row=row, column=3).number_format = '$#,##0.00'
            ws.cell(row=row, column=4).number_format = 'dd/mm/yyyy'
            
            row += 1
        
        # Total
        ws.cell(row=row, column=1).value = 'TOTAL'
        ws.cell(row=row, column=3).value = float(total_gastos)
        for col in range(1, 5):
            ws.cell(row=row, column=col).font = total_font
            ws.cell(row=row, column=col).fill = PatternFill(start_color='EF9A9A', end_color='EF9A9A', fill_type='solid')
            ws.cell(row=row, column=col).border = border
        ws.cell(row=row, column=3).number_format = '$#,##0.00'
        
        row += 1
    else:
        ws.merge_cells(f'A{row}:E{row}')
        ws.cell(row=row, column=1).value = 'No hay gastos registrados para este mes.'
        row += 1
    
    row += 1
    
    # ==================== RESUMEN ====================
    ws.merge_cells(f'A{row}:E{row}')
    header = ws[f'A{row}']
    header.value = 'Resumen Mensual'
    header.font = header_font
    header.fill = header_fill
    header.alignment = Alignment(horizontal='left', vertical='center')
    row += 1
    
    balance = float(total_ingresos) - float(total_gastos)
    
    resumen_data = [
        ['Total Ingresos', float(total_ingresos)],
        ['Total Gastos', float(total_gastos)],
        ['Balance', balance],
    ]
    
    for desc, valor in resumen_data:
        ws.cell(row=row, column=1).value = desc
        ws.cell(row=row, column=2).value = valor
        ws.cell(row=row, column=1).font = total_font
        ws.cell(row=row, column=2).font = total_font
        ws.cell(row=row, column=1).fill = total_fill
        ws.cell(row=row, column=2).fill = total_fill
        ws.cell(row=row, column=1).border = border
        ws.cell(row=row, column=2).border = border
        ws.cell(row=row, column=2).number_format = '$#,##0.00'
        row += 1
    
    row += 2
    
    # ==================== OBJETIVOS DE AHORRO ====================
    ws.merge_cells(f'A{row}:E{row}')
    header = ws[f'A{row}']
    header.value = 'Objetivos de Ahorro y Progreso'
    header.font = header_font
    header.fill = header_fill
    header.alignment = Alignment(horizontal='left', vertical='center')
    row += 1
    
    objetivos = ObjetivoAhorro.objects.all()
    
    if objetivos.exists():
        # Headers
        headers = ['Objetivo', 'Meta', 'Ahorrado', 'Progreso %', 'Restante']
        for col, header_val in enumerate(headers, 1):
            cell = ws.cell(row=row, column=col)
            cell.value = header_val
            cell.font = header_font
            cell.fill = PatternFill(start_color='F0FDF0', end_color='F0FDF0', fill_type='solid')
            cell.border = border
        
        row += 1
        
        for objetivo in objetivos:
            monto_objetivo = float(objetivo.monto_objetivo)
            monto_ahorrado = float(objetivo.monto_ahorrado)
            progreso = round((monto_ahorrado / monto_objetivo * 100), 2) if monto_objetivo > 0 else 0
            restante = round(monto_objetivo - monto_ahorrado, 2)
            
            ws.cell(row=row, column=1).value = objetivo.nombre
            ws.cell(row=row, column=2).value = monto_objetivo
            ws.cell(row=row, column=3).value = monto_ahorrado
            ws.cell(row=row, column=4).value = progreso
            ws.cell(row=row, column=5).value = restante
            
            for col in range(1, 6):
                ws.cell(row=row, column=col).border = border
                if col > 1:
                    ws.cell(row=row, column=col).number_format = '$#,##0.00' if col != 4 else '0.00'
            
            row += 1
    else:
        ws.merge_cells(f'A{row}:E{row}')
        ws.cell(row=row, column=1).value = 'No hay objetivos de ahorro registrados.'
        row += 1
    
    # Ajustar ancho de columnas
    ws.column_dimensions['A'].width = 25
    ws.column_dimensions['B'].width = 15
    ws.column_dimensions['C'].width = 15
    ws.column_dimensions['D'].width = 15
    ws.column_dimensions['E'].width = 15
    
    # Crear respuesta
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="reporte_{mes:02d}_{anio}.xlsx"'
    
    wb.save(response)
    return response