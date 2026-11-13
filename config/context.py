from django.urls import reverse

MENUS = {
    'paciente': [('Mis citas', 'citas:mis_citas', 'bi-calendar-check'), ('Solicitar cita', 'citas:agendar', 'bi-plus-circle'),
                 ('Mi historial', 'historial:mio', 'bi-journal-medical'), ('Médicos', 'medicos:lista', 'bi-person-badge'),
                 ('Mis datos', 'pacientes:perfil', 'bi-person')],
    'medico': [('Resumen', 'reportes:dashboard', 'bi-grid'), ('Mi agenda', 'citas:agenda', 'bi-calendar3'),
               ('Pacientes', 'pacientes:lista', 'bi-people'), ('Médicos', 'medicos:lista', 'bi-person-badge')],
    'recepcionista': [('Resumen', 'reportes:dashboard', 'bi-grid'), ('Citas', 'citas:lista', 'bi-calendar3'),
                      ('Agendar cita', 'citas:agendar', 'bi-plus-circle'), ('Pacientes', 'pacientes:lista', 'bi-people'),
                      ('Médicos', 'medicos:lista', 'bi-person-badge'), ('Reporte de citas', 'reportes:citas', 'bi-bar-chart')],
}
MENUS['admin'] = MENUS['recepcionista'] + [('Ingresos', 'reportes:ingresos', 'bi-cash-coin'), ('Usuarios', 'usuarios:lista', 'bi-shield-lock'),
                                           ('Configuración', '/admin/', 'bi-gear')]


def menu(request):
    if not request.user.is_authenticated:
        return {}
    items = [{'etq': e, 'icono': i, 'url': n if n.startswith('/') else reverse(n)} for e, n, i in MENUS.get(request.user.rol, MENUS['recepcionista'])]
    candidatos = [i for i in items if request.path.startswith(i['url'])]
    activo = max(candidatos, key=lambda i: len(i['url']), default=None)
    for i in items:
        i['activo'] = i is activo
    u = request.user
    return {'menu': items, 'iniciales': ((u.first_name[:1] + u.last_name[:1]) or u.username[:2]).upper()}
