import csv

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.db.models.functions import TruncDay, TruncMonth, TruncYear
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.dateparse import parse_date

from citas.models import Cita
from config.utils import rol_required
from medicos.models import Medico


@login_required
def dashboard(request):
    u = request.user
    if u.rol == 'paciente':
        return redirect('citas:mis_citas')
    hoy = timezone.localdate()
    qs = Cita.objects.all()
    if u.rol == 'medico':
        qs = qs.filter(medico__user=u)
    mes = qs.filter(fecha__year=hoy.year, fecha__month=hoy.month)
    conteo = dict(mes.values_list('estado').annotate(n=Count('id')))
    por_estado = [(etq, conteo.get(k, 0), k) for k, etq in Cita.ESTADOS]
    hora = timezone.localtime().hour
    ctx = {
        'hoy': hoy,
        'saludo': 'Buenos días' if hora < 12 else 'Buenas tardes' if hora < 19 else 'Buenas noches',
        'citas_hoy': qs.filter(fecha=hoy).select_related('paciente', 'medico__user').order_by('hora'),
        'total_mes': mes.count(),
        'atendidas_mes': conteo.get('atendida', 0),
        'pacientes_atendidos': mes.filter(estado='atendida').values('paciente').distinct().count(),
        'por_estado': por_estado,
    }
    if u.rol == 'admin':
        ctx['ingresos_mes'] = mes.filter(pagado=True).aggregate(t=Sum('valor'))['t'] or 0
        ctx['carga'] = [(m.nombre, m.citas.filter(fecha__year=hoy.year, fecha__month=hoy.month).exclude(estado='cancelada').count())
                        for m in Medico.objects.filter(activo=True).select_related('user')]
        ctx['carga_max'] = max([n for _, n in ctx['carga']] + [1])
    return render(request, 'reportes/dashboard.html', ctx)


def _filtrar(g):
    qs = Cita.objects.select_related('paciente', 'medico__user', 'medico__especialidad')
    desde, hasta = parse_date(g.get('desde', '') or ''), parse_date(g.get('hasta', '') or '')
    if desde:
        qs = qs.filter(fecha__gte=desde)
    if hasta:
        qs = qs.filter(fecha__lte=hasta)
    if g.get('medico', '').isdigit():
        qs = qs.filter(medico_id=g['medico'])
    if g.get('estado'):
        qs = qs.filter(estado=g['estado'])
    return qs.order_by('fecha', 'hora')


def _csv(nombre, cabecera, filas):
    r = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    r['Content-Disposition'] = f'attachment; filename="{nombre}.csv"'
    w = csv.writer(r)
    w.writerow(cabecera)
    w.writerows(filas)
    return r


@rol_required('recepcionista', 'admin')
def citas(request):
    qs = _filtrar(request.GET)
    if request.GET.get('export') == 'csv':
        return _csv('reporte_citas', ['Fecha', 'Hora', 'Paciente', 'Documento', 'Médico', 'Especialidad', 'Estado', 'Valor', 'Pagado'],
                    [(c.fecha, c.hora.strftime('%H:%M'), c.paciente.nombre_completo, c.paciente.documento, c.medico.nombre,
                      c.medico.especialidad, c.get_estado_display(), c.valor, 'Sí' if c.pagado else 'No') for c in qs])
    resumen = [(dict(Cita.ESTADOS)[e['estado']], e['n']) for e in qs.values('estado').annotate(n=Count('id'))]
    return render(request, 'reportes/citas.html', {
        'citas': qs, 'resumen': resumen, 'g': request.GET, 'estados': Cita.ESTADOS,
        'medicos': Medico.objects.select_related('user'), 'query': request.GET.urlencode()})


@rol_required('admin')
def ingresos(request):
    g = request.GET
    periodo = g.get('periodo', 'dia')
    trunc = {'dia': TruncDay, 'mes': TruncMonth, 'anio': TruncYear}.get(periodo, TruncDay)
    fmt = {'dia': '%d/%m/%Y', 'mes': '%m/%Y', 'anio': '%Y'}.get(periodo, '%d/%m/%Y')
    qs = _filtrar(g).filter(pagado=True)
    filas = [(r['p'].strftime(fmt), r['n'], r['total']) for r in
             qs.annotate(p=trunc('fecha')).values('p').annotate(n=Count('id'), total=Sum('valor')).order_by('p')]
    if g.get('export') == 'csv':
        return _csv('reporte_ingresos', ['Periodo', 'Citas pagadas', 'Ingresos'], filas)
    return render(request, 'reportes/ingresos.html', {
        'filas': filas, 'total': sum(f[2] or 0 for f in filas), 'periodo': periodo, 'g': g,
        'medicos': Medico.objects.select_related('user'), 'query': g.urlencode()})
