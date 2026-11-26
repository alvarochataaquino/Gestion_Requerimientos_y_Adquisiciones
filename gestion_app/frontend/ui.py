# ============================================================================
# MÓDULO: CAPA DE PRESENTACIÓN (Tkinter)
#   Responsable de eventos, formularios, tablas, mensajes, navegación y exportación.
#   Flujo: usuario -> callback Tkinter -> Service -> Database -> PostgreSQL.
#   Las filas de pantalla no se escriben por sí solas; el usuario debe confirmar Guardar.
# ============================================================================

"""Vista Tkinter: 10 módulos, formularios, tablas, advertencias y exportación CSV.
La aplicación no inventa un login que no está previsto en el modelo físico.
"""
import csv
from datetime import date
from decimal import Decimal
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from ..config.settings import load_config, save_config
from ..backend.database import Database
from ..backend.service import Service, CATALOGS, CRITERIA
from ..backend.reports import REPORTS

# Modulos disponibles en el menu lateral.
NAV = ['Inicio','Áreas','Empleados','Productos y servicios','Proveedores',
       'Requerimientos','Evaluaciones','Órdenes de compra','Órdenes de servicio','Reportes']
NAV_ICONS = ['◫','▦','♙','▤','▣','≡','☑','▧','▨','▥']
# Paleta de colores centralizada para mantener consistencia visual.
COLORS = {'navy':'#10243D','navy2':'#18334F','blue':'#176BA0','teal':'#0F877C',
          'cream':'#F4F7FB','text':'#243449','muted':'#64748B','stroke':'#D9E2EC'}


# -----------------------------------------------------------------
# FUNCIÓN: display
# Objetivo: Transforma None en texto vacío para evitar mostrar "None" en tablas.
# Entradas: value: resultado recuperado de una consulta.
# Salida/reglas: Retorna una cadena apta para una celda de Treeview.
# -----------------------------------------------------------------
def display(value):
    """Da formato legible a los valores de celdas en las tablas."""
    return '' if value is None else str(value)


# -----------------------------------------------------------------
# FUNCIÓN: combo_id
# Objetivo: Separa el identificador antes del separador visual « · » del Combobox.
# Entradas: value: opción como «001 · Logística».
# Salida/reglas: Devuelve «001», sin espacios laterales.
# -----------------------------------------------------------------
def combo_id(value):
    """Extrae el codigo seleccionado en una lista de opciones."""
    return str(value).split(' · ',1)[0].strip()

# -----------------------------------------------------------------
# CLASE: GestionApp
# Objetivo: Controlador de la interfaz de escritorio en Tkinter: compone las vistas y eventos.
# Entradas: root: instancia principal de tk.Tk.
# Salida/reglas: Deriva toda la persistencia a Service y Database; no contiene SQL propio de
#   escritura.
# -----------------------------------------------------------------
class GestionApp:
    """Controla las pantallas Tkinter y delega los datos al servicio de negocio."""
    # -----------------------------------------------------------------
    # FUNCIÓN: GestionApp.__init__
    # Objetivo: Inicializa la ventana y conecta las capas gráfica, de negocio y de datos.
    # Entradas: root: ventana Tk principal creada en main.py.
    # Salida/reglas: Prepara el menú; la base se verifica solamente al usar «Comprobar conexión».
    # -----------------------------------------------------------------
    def __init__(self, root):
        """Configura ventana, acceso a datos, paneles y evento de cierre."""
        self.root=root
        root.title('Aplicativo para Gestión de Requerimientos y Adquisiciones')
        root.geometry('1350x790')
        root.configure(bg=COLORS['cream'])
        # La capa visual no abre conexión hasta que el usuario comprueba parámetros.
        self.db=Database()
        self.service=Service(self.db)
        self.connected=False
        self.current='Inicio'
        # Estados de UI: selección temporal y última consulta; no son datos persistentes.
        self.row_data={}
        self.last_report=[]
        # Primero se crean estilos y contenedores; después se pinta el módulo inicial.
        self._styles()
        self._shell()
        self.navigate('Inicio')
        self.root.protocol('WM_DELETE_WINDOW',self.close)

    # -----------------------------------------------------------------
    # FUNCIÓN: GestionApp._styles
    # Objetivo: Configura estilos ttk globales para tablas, encabezados, listas y cuadros.
    # Entradas: self: estado de la aplicación.
    # Salida/reglas: No accede a datos; únicamente modifica la apariencia de los widgets.
    # -----------------------------------------------------------------
    def _styles(self):
        """Define tema visual y estilos de controles ttk."""
        style=ttk.Style(self.root)
        if 'clam' in style.theme_names(): style.theme_use('clam')
        style.configure('Treeview',background='#FFFFFF',fieldbackground='#FFFFFF',foreground=COLORS['text'],
                        rowheight=30,borderwidth=0,font=('Segoe UI',10))
        style.configure('Treeview.Heading',background='#E7EDF6',foreground=COLORS['navy'],
                        relief='flat',font=('Segoe UI',10,'bold'),padding=(8,10))
        style.map('Treeview',background=[('selected','#CCE7F5')],foreground=[('selected','#0B304C')])
        style.configure('TCombobox',padding=5,font=('Segoe UI',10))
        style.configure('TEntry',padding=5,font=('Segoe UI',10))

    # -----------------------------------------------------------------
    # FUNCIÓN: GestionApp._shell
    # Objetivo: Construye el armazón fijo: barra lateral, título, contenido y estado.
    # Entradas: self: raíz y paleta de colores previamente inicializadas.
    # Salida/reglas: Los botones de navegación invocan navigate y los de conexión usan sus diálogos.
    # -----------------------------------------------------------------
    def _shell(self):
        """Construye menu lateral, cabecera y espacio central de trabajo."""
        outer=tk.Frame(self.root,bg=COLORS['cream']);outer.pack(fill='both',expand=True)
        self.sidebar=tk.Frame(outer,bg=COLORS['navy'],width=238)
        self.sidebar.pack(side='left',fill='y');self.sidebar.pack_propagate(False)
        tk.Label(self.sidebar,text='GESTIÓN',bg=COLORS['navy'],fg='white',font=('Segoe UI',23,'bold')).pack(anchor='w',padx=23,pady=(27,0))
        tk.Label(self.sidebar,text='REQUERIMIENTOS Y\nADQUISICIONES',justify='left',bg=COLORS['navy'],fg='#90B7CE',font=('Segoe UI',9,'bold')).pack(anchor='w',padx=24,pady=(0,25))
        self.nav_buttons={}
        # Se captura n=name en lambda para evitar que todos los botones abran el último módulo.
        for icon,name in zip(NAV_ICONS,NAV):
            b=tk.Button(self.sidebar,text=f'  {icon}   {name}',bg=COLORS['navy'],fg='#D8E7F1',
                font=('Segoe UI',10),bd=0,anchor='w',pady=11,activebackground=COLORS['navy2'],
                activeforeground='white',command=lambda n=name:self.navigate(n))
            b.pack(fill='x',padx=12,pady=1);self.nav_buttons[name]=b
        tk.Label(self.sidebar,text='Aplicativo académico · v1.0',bg=COLORS['navy'],fg='#9FB7C7',
                 font=('Segoe UI',9)).pack(side='bottom',pady=20)
        right=tk.Frame(outer,bg=COLORS['cream']);right.pack(side='left',fill='both',expand=True)
        header=tk.Frame(right,bg='#FFFFFF',height=95);header.pack(fill='x');header.pack_propagate(False)
        titles=tk.Frame(header,bg='#FFFFFF');titles.pack(side='left',padx=28,pady=17)
        self.title=tk.Label(titles,text='Panel de inicio',bg='#FFFFFF',fg=COLORS['navy'],font=('Segoe UI',20,'bold'))
        self.title.pack(anchor='w')
        self.subtitle=tk.Label(titles,text='Sistema de gestión de requerimientos y adquisiciones',
                               bg='#FFFFFF',fg=COLORS['muted'],font=('Segoe UI',10));self.subtitle.pack(anchor='w')
        tk.Button(header,text='Configurar PostgreSQL',command=self.config_dialog,bg='#E9F1F7',fg=COLORS['navy'],
                  font=('Segoe UI',10,'bold'),bd=0,padx=15,pady=10).pack(side='right',padx=12)
        tk.Button(header,text='Comprobar conexión',command=self.check_connection,bg=COLORS['blue'],fg='white',
                  font=('Segoe UI',10,'bold'),bd=0,padx=15,pady=10).pack(side='right')
        self.content=tk.Frame(right,bg=COLORS['cream']);self.content.pack(fill='both',expand=True,padx=25,pady=23)
        footer=tk.Frame(right,bg='#FFFFFF',height=38);footer.pack(side='bottom',fill='x');footer.pack_propagate(False)
        self.status=tk.Label(footer,text='●  Sin conexión comprobada',bg='#FFFFFF',fg='#AD5C28',font=('Segoe UI',9))
        self.status.pack(side='left',padx=25,pady=8)
        tk.Label(footer,text='Python · PostgreSQL · MVC',bg='#FFFFFF',fg=COLORS['muted'],
                 font=('Segoe UI',9)).pack(side='right',padx=25)

    # -----------------------------------------------------------------
    # FUNCIÓN: GestionApp._clear
    # Objetivo: Retira los widgets de una vista anterior antes de mostrar otra.
    # Entradas: self.content: contenedor central.
    # Salida/reglas: Evita duplicación de formularios y libera los widgets antiguos.
    # -----------------------------------------------------------------
    def _clear(self):
        """Limpia el contenido antes de dibujar una nueva pantalla."""
        for child in self.content.winfo_children(): child.destroy()

    # -----------------------------------------------------------------
    # FUNCIÓN: GestionApp._panel
    # Objetivo: Crea un panel blanco reutilizable con borde discreto.
    # Entradas: master: contenedor alternativo opcional.
    # Salida/reglas: Retorna un Frame ya empaquetado para mostrar datos.
    # -----------------------------------------------------------------
    def _panel(self,master=None):
        """Crea un contenedor de contenido con el estilo de la aplicacion."""
        frame=tk.Frame(master or self.content,bg='#FFFFFF',highlightbackground=COLORS['stroke'],
                       highlightthickness=1)
        frame.pack(fill='both',expand=True,pady=(0,12))
        return frame

    # -----------------------------------------------------------------
    # FUNCIÓN: GestionApp._action
    # Objetivo: Construye un botón estándar con estilo principal o secundario.
    # Entradas: parent, title, callback y primary: lugar, texto, acción y tema.
    # Salida/reglas: Devuelve el botón sin insertarlo; el llamador decide su disposición.
    # -----------------------------------------------------------------
    def _action(self,parent,title,callback,primary=True):
        """Crea un boton de accion con estilos principal o secundario."""
        return tk.Button(parent,text=title,command=callback,bg=COLORS['blue'] if primary else '#E8EFF5',
               fg='white' if primary else COLORS['navy'],font=('Segoe UI',10,'bold'),bd=0,padx=16,pady=10)

    # -----------------------------------------------------------------
    # FUNCIÓN: GestionApp._bar
    # Objetivo: Dibuja la franja de acciones situada encima de los listados.
    # Entradas: label: resumen; buttons: ternas (texto, callback, principal).
    # Salida/reglas: Coloca acciones a la derecha respetando su orden visible.
    # -----------------------------------------------------------------
    def _bar(self,label,buttons=()):
        """Presenta el titulo de seccion y sus acciones contextuales."""
        bar=tk.Frame(self.content,bg=COLORS['cream']);bar.pack(fill='x',pady=(0,14))
        tk.Label(bar,text=label,bg=COLORS['cream'],fg=COLORS['muted'],font=('Segoe UI',10)).pack(side='left')
        for caption,callback,primary in reversed(buttons):
            self._action(bar,caption,callback,primary).pack(side='right',padx=(9,0))
        return bar

    # -----------------------------------------------------------------
    # FUNCIÓN: GestionApp._table
    # Objetivo: Genera una tabla con encabezados, scroll horizontal y vertical.
    # Entradas: parent, rows, empty_cols, height: contenedor y filas/dimensiones.
    # Salida/reglas: Retorna (Treeview, mapa por identificador); conserva los registros originales.
    # -----------------------------------------------------------------
    def _table(self,parent,rows,empty_cols=('Código','Descripción'),height=12):
        """Construye una tabla Treeview para registros o resultados SQL."""
        # Las columnas se derivan del resultado SQL cuando hay filas; si no, usan esquema vacío.
        cols=list(rows[0].keys()) if rows else list(empty_cols)
        wrap=tk.Frame(parent,bg='#FFFFFF');wrap.pack(fill='both',expand=True,padx=16,pady=12)
        tree=ttk.Treeview(wrap,columns=cols,show='headings',height=height,selectmode='browse')
        for col in cols:
            tree.heading(col,text=col.replace('_',' ').capitalize())
            w=min(230,max(112,len(col)*10+32))
            tree.column(col,width=w,anchor='w',stretch=True)
        vs=ttk.Scrollbar(wrap,orient='vertical',command=tree.yview)
        hs=ttk.Scrollbar(wrap,orient='horizontal',command=tree.xview)
        tree.configure(yscrollcommand=vs.set,xscrollcommand=hs.set)
        tree.grid(row=0,column=0,sticky='nsew');vs.grid(row=0,column=1,sticky='ns');hs.grid(row=1,column=0,sticky='ew')
        wrap.rowconfigure(0,weight=1);wrap.columnconfigure(0,weight=1)
        # Mapa IID -> fila original: la selección conserva tipos y valores de consulta.
        data={}
        for i,row in enumerate(rows):
            iid=str(i)
            tree.insert('', 'end',iid=iid,values=[display(row.get(c)) for c in cols])
            data[iid]=row
        return tree,data

    # -----------------------------------------------------------------
    # FUNCIÓN: GestionApp._selected
    # Objetivo: Valida que el usuario seleccione una fila antes de ejecutar una acción.
    # Entradas: tree y mapping: widget y diccionario de filas.
    # Salida/reglas: Retorna registro seleccionado o None y muestra un aviso cuando falta selección.
    # -----------------------------------------------------------------
    def _selected(self,tree,mapping):
        """Obtiene la fila seleccionada en la tabla y el registro asociado."""
        selection=tree.selection()
        if not selection:
            messagebox.showinfo('Seleccionar registro','Selecciona primero un registro en la tabla.',parent=self.root)
            return None
        return mapping[selection[0]]

    # -----------------------------------------------------------------
    # FUNCIÓN: GestionApp._safe
    # Objetivo: Protege callbacks de la interfaz contra excepciones no controladas.
    # Entradas: callback: acción de UI o servicio.
    # Salida/reglas: Muestra el error al usuario y evita que se cierre inesperadamente la ventana.
    # -----------------------------------------------------------------
    def _safe(self,callback):
        """Ejecuta una accion mostrando mensajes de error en lugar de cerrar la interfaz."""
        try: return callback()
        except Exception as error:
            messagebox.showerror('Operación no completada',str(error),parent=self.root)
            return None

    # -----------------------------------------------------------------
    # FUNCIÓN: GestionApp.navigate
    # Objetivo: Cambia de módulo y mantiene resaltado el elemento activo del menú.
    # Entradas: name: rótulo de NAV.
    # Salida/reglas: Sin una BD verificada, muestra una pantalla de requisitos en vez del módulo.
    # -----------------------------------------------------------------
    def navigate(self,name):
        """Actualiza la navegacion y muestra pantalla o aviso de conexion pendiente."""
        self.current=name
        self._clear()
        for label,b in self.nav_buttons.items():
            b.configure(bg=COLORS['navy2'] if label==name else COLORS['navy'],
                        fg='#FFFFFF' if label==name else '#D8E7F1')
        self.title.config(text=name if name!='Inicio' else 'Panel de inicio')
        if name=='Inicio': self.dashboard();return
        # Bloquea los módulos operativos hasta haber validado el esquema PostgreSQL.
        if not self.connected:
            self._needs_connection();return
        self._safe(lambda: self._route(name))

    # -----------------------------------------------------------------
    # FUNCIÓN: GestionApp._route
    # Objetivo: Enruta cada opción del menú al renderizador del módulo correspondiente.
    # Entradas: name: opción validada de la barra de navegación.
    # Salida/reglas: Los catálogos comparten una vista; solicitudes, evaluaciones y reportes son
    #   específicos.
    # -----------------------------------------------------------------
    def _route(self,name):
        """Dirige el menu seleccionado a su modulo de catalogo, compras o informes."""
        if name in CATALOGS:self.catalog_view(name)
        elif name=='Requerimientos':self.requirement_view()
        elif name=='Evaluaciones':self.evaluation_view()
        elif name=='Órdenes de compra':self.order_view('Compra')
        elif name=='Órdenes de servicio':self.order_view('Servicio')
        elif name=='Reportes':self.report_view()

    # -----------------------------------------------------------------
    # FUNCIÓN: GestionApp._needs_connection
    # Objetivo: Explica cómo configurar la base antes de usar el programa.
    # Entradas: Estado de conexión todavía no validado.
    # Salida/reglas: Muestra instrucciones y acceso al diálogo de configuración.
    # -----------------------------------------------------------------
    def _needs_connection(self):
        """Muestra instrucciones si todavia no se valido la conexion."""
        panel=self._panel();tk.Label(panel,text='Primero conecta tu base de datos PostgreSQL',
                bg='#FFFFFF',fg=COLORS['navy'],font=('Segoe UI',18,'bold')).pack(pady=(60,12))
        tk.Label(panel,text='Utiliza «Configurar PostgreSQL» y después «Comprobar conexión».\n'
                 'La BD debe contener las 12 tablas y los procedimientos almacenados del proyecto.',
                 bg='#FFFFFF',fg=COLORS['muted'],font=('Segoe UI',11),justify='center').pack(pady=12)
        self._action(panel,'Configurar conexión',self.config_dialog).pack(pady=15)

    # -----------------------------------------------------------------
    # FUNCIÓN: GestionApp.dashboard
    # Objetivo: Renderiza los indicadores y accesos rápidos del panel inicial.
    # Entradas: self.connected: indica si la comprobación del esquema fue satisfactoria.
    # Salida/reglas: Con conexión válida consulta cinco conteos; ante fallo lo refleja sin cerrar la
    #   app.
    # -----------------------------------------------------------------
    def dashboard(self):
        """Presenta el panel inicial y los indicadores de actividad."""
        self._bar('Visión general de la funcionalidad de logística')
        panel=self._panel()
        tk.Label(panel,text='Gestión de Requerimientos y Adquisiciones',font=('Segoe UI',20,'bold'),
                 bg='#FFFFFF',fg=COLORS['navy']).pack(anchor='w',padx=26,pady=(26,8))
        tk.Label(panel,text='Registro de solicitudes · Evaluación de proveedores · Órdenes de compra y servicio',
                 font=('Segoe UI',11),bg='#FFFFFF',fg=COLORS['muted']).pack(anchor='w',padx=27,pady=(0,20))
        if not self.connected:
            tk.Label(panel,text='Estado actual: pendiente de conexión PostgreSQL',bg='#FFF5E9',fg='#96530F',
                     font=('Segoe UI',12,'bold'),padx=20,pady=13).pack(anchor='w',padx=26,pady=12)
            tk.Label(panel,text='1. Crea la base gestion_adquisiciones en pgAdmin 4.\n'
                    '2. Ejecuta 01_creacion_base_datos.sql y 03_procedimientos_funciones_triggers.sql.\n'
                    '3. Configura host, puerto, usuario y contraseña.\n'
                    '4. Presiona Comprobar conexión y accede a los módulos.',
                     font=('Segoe UI',11),justify='left',bg='#FFFFFF',fg=COLORS['text']).pack(anchor='w',padx=30,pady=18)
            return
        try: data=self.service.summary()
        except Exception as exc:
            self.connected=False;self.status.config(text='●  Conexión interrumpida',fg='#A84444')
            tk.Label(panel,text=str(exc),bg='#FFFFFF',fg='#A84444',wraplength=720).pack(padx=25,pady=25)
            return
        stats=tk.Frame(panel,bg='#FFFFFF');stats.pack(fill='x',padx=18,pady=24)
        for title,key in [('Requerimientos','requerimientos'),('Proveedores','proveedores'),
                           ('Evaluaciones','evaluaciones'),('Compras','compras'),('Servicios','servicios')]:
            card=tk.Frame(stats,bg='#EDF4FA',highlightbackground='#D8E6F2',highlightthickness=1)
            card.pack(side='left',expand=True,fill='x',padx=5)
            tk.Label(card,text=str(data[key]),bg='#EDF4FA',fg=COLORS['blue'],
                     font=('Segoe UI',25,'bold')).pack(pady=(15,2))
            tk.Label(card,text=title,bg='#EDF4FA',fg=COLORS['navy'],font=('Segoe UI',10)).pack(pady=(0,15))
        actions=tk.Frame(panel,bg='#FFFFFF');actions.pack(anchor='w',padx=26,pady=18)
        for caption,nav in [('Registrar requerimiento','Requerimientos'),
                            ('Evaluar proveedor','Evaluaciones'),('Consultar reportes','Reportes')]:
            self._action(actions,caption,lambda n=nav:self.navigate(n)).pack(side='left',padx=(0,12))

    # -----------------------------------------------------------------
    # FUNCIÓN: GestionApp.check_connection
    # Objetivo: Lee la configuración, abre PostgreSQL y comprueba los objetos obligatorios.
    # Entradas: Archivo JSON del perfil y servicio PostgreSQL externo.
    # Salida/reglas: Actualiza el estado, notifica éxito/fallo y recrea el servicio de negocio.
    # -----------------------------------------------------------------
    def check_connection(self):
        """Comprueba la conexion y la existencia del esquema obligatorio."""
        try:
            self.db=Database(load_config())
            # No solo prueba contraseña: confirma tablas, procedimientos y triggers.
            self.db.verify()
            self.service=Service(self.db)
            self.connected=True
            self.status.configure(text=f"●  Conectado a {self.db.config['dbname']} · {self.db.config['host']}",fg='#158064')
            self.navigate(self.current)
            messagebox.showinfo('Conexión correcta','Conexión validada: 12 tablas y procedimientos disponibles.',parent=self.root)
        except Exception as exc:
            self.connected=False
            self.status.configure(text='●  No conectado',fg='#A84444')
            self.navigate('Inicio')
            messagebox.showerror('No fue posible conectar',str(exc),parent=self.root)

    # -----------------------------------------------------------------
    # FUNCIÓN: GestionApp.config_dialog
    # Objetivo: Solicita host, puerto, base, usuario y contraseña de PostgreSQL.
    # Entradas: Valores de load_config(); password se presenta oculto.
    # Salida/reglas: Entrega la configuración a save_config y obliga a volver a validar la conexión.
    # -----------------------------------------------------------------
    def config_dialog(self):
        """Muestra el dialogo de configuracion del servidor PostgreSQL."""
        cfg=load_config()
        fields=[(k,{'host':'Servidor / host','port':'Puerto','dbname':'Base de datos',
                    'user':'Usuario','password':'Contraseña PostgreSQL'}[k],'secret' if k=='password' else 'text',cfg[k])
                for k in cfg]
        self.form_dialog('Configuración de PostgreSQL',fields,
            lambda d:(save_config(d),self._set_unchecked(),messagebox.showinfo('Configuración guardada',
                'Ahora presiona «Comprobar conexión».',parent=self.root)),width=550)

    # -----------------------------------------------------------------
    # FUNCIÓN: GestionApp._set_unchecked
    # Objetivo: Invalida una conexión anterior al cambiar la configuración local.
    # Entradas: self.connected y la etiqueta del estado.
    # Salida/reglas: Vuelve al inicio para impedir usar datos con una conexión no comprobada.
    # -----------------------------------------------------------------
    def _set_unchecked(self):
        """Invalida el estado de conexion al cambiar los parametros."""
        self.connected=False
        self.status.config(text='●  Configuración guardada, falta comprobar conexión',fg='#AD5C28')
        self.navigate('Inicio')

    # -----------------------------------------------------------------
    # FUNCIÓN: GestionApp.form_dialog
    # Objetivo: Crea formularios de alta, edición y configuración con metadatos comunes.
    # Entradas: fields: lista de (clave, etiqueta, tipo, inicial); on_save: callback.
    # Salida/reglas: Recoge valores, convierte IDs visuales y captura errores de validación.
    # -----------------------------------------------------------------
    def form_dialog(self,title,fields,on_save,width=570):
        """Formulario reutilizable. fields = (clave, etiqueta, tipo, valor)."""
        # Toplevel es un diálogo hijo; grab_set impide ediciones concurrentes de otra ventana.
        window=tk.Toplevel(self.root);window.title(title);window.configure(bg='#FFFFFF')
        window.geometry(f'{width}x{min(740,170+53*len(fields))}')
        window.transient(self.root);window.grab_set()
        tk.Label(window,text=title,bg='#FFFFFF',fg=COLORS['navy'],
                 font=('Segoe UI',17,'bold')).pack(anchor='w',padx=22,pady=(18,15))
        wrapper=tk.Frame(window,bg='#FFFFFF');wrapper.pack(fill='both',expand=True,padx=24)
        variables={}
        for key,label,kind,initial in fields:
            row=tk.Frame(wrapper,bg='#FFFFFF');row.pack(fill='x',pady=5)
            tk.Label(row,text=label,bg='#FFFFFF',fg=COLORS['text'],font=('Segoe UI',10),
                     width=25,anchor='w').pack(side='left')
            var=tk.StringVar(value=display(initial))
            variables[key]=var
            # Los campos vinculados usan listas readonly basadas en claves foráneas existentes.
            if kind in ('area','empleado','requerimiento','proveedor','producto'):
                choices=[f"{r['code']} · {r['label']}" for r in self.service.lookup(kind)]
                widget=ttk.Combobox(row,textvariable=var,values=choices,state='readonly')
                for choice in choices:
                    if combo_id(choice)==str(initial):var.set(choice);break
            # Las opciones restringidas impiden introducir valores que no pertenecen al dominio.
            elif kind in ('tipo','moneda','score'):
                choices={'tipo':['Producto','Servicio'],'moneda':['Soles','Dolares'],
                         'score':['0','1','2']}[kind]
                widget=ttk.Combobox(row,textvariable=var,values=choices,state='readonly')
            else:
                # Los campos secretos usan máscara visual, sin cifrar el valor en disco.
                widget=ttk.Entry(row,textvariable=var,show='•' if kind=='secret' else '')
            widget.pack(side='left',fill='x',expand=True,padx=(8,0))
        bar=tk.Frame(window,bg='#FFFFFF');bar.pack(fill='x',padx=24,pady=20)
        self._action(bar,'Cancelar',window.destroy,False).pack(side='right')
        # -----------------------------------------------------------------
        # FUNCIÓN: GestionApp.form_dialog.save
        # Objetivo: Callback interno del botón Guardar del formulario genérico.
        # Entradas: variables: StringVar de los campos visibles.
        # Salida/reglas: Llama on_save con diccionario limpio; conserva la ventana si hay error.
        # -----------------------------------------------------------------
        def save():
            """Recoge las entradas y solicita al modulo correspondiente que las guarde."""
            data={k:(combo_id(v.get()) if next(x[2] for x in fields if x[0]==k) in
                              ('area','empleado','requerimiento','proveedor','producto') else v.get())
                  for k,v in variables.items()}
            try:
                on_save(data)
            except Exception as exc:
                messagebox.showerror('No se guardó',str(exc),parent=window);return
            window.destroy()
        self._action(bar,'Guardar',save).pack(side='right',padx=12)
        return window

    # -----------------------------------------------------------------
    # FUNCIÓN: GestionApp.catalog_view
    # Objetivo: Lista registros de área, empleados, productos o proveedores.
    # Entradas: name: clave de CATALOGS.
    # Salida/reglas: Conecta botones y doble clic con altas, cambios y eliminaciones.
    # -----------------------------------------------------------------
    def catalog_view(self,name):
        """Muestra el listado y las acciones del catalogo elegido."""
        rows=self.service.catalog(name)
        self._bar(f'{len(rows)} registros · Doble clic para modificar',[
            ('Nuevo registro',lambda:self.catalog_form(name),True),
            ('Modificar',lambda:self._selected_action(tree,data,lambda row:self.catalog_form(name,row)),False),
            ('Eliminar',lambda:self._selected_action(tree,data,lambda row:self.remove_catalog(name,row)),False)])
        panel=self._panel();tree,data=self._table(panel,rows,[x[0] for x in CATALOGS[name][2]])
        tree.bind('<Double-1>',lambda e:self._selected_action(tree,data,lambda row:self.catalog_form(name,row)))

    # -----------------------------------------------------------------
    # FUNCIÓN: GestionApp._selected_action
    # Objetivo: Ejecuta una acción solamente sobre una fila de tabla ya escogida.
    # Entradas: tree, data, action: tabla, mapa de filas y callback.
    # Salida/reglas: No actúa si no hay selección; evita índices inválidos.
    # -----------------------------------------------------------------
    def _selected_action(self,tree,data,action):
        """Aplica una accion al registro seleccionado en la tabla."""
        record=self._selected(tree,data)
        if record is not None: action(record)

    # -----------------------------------------------------------------
    # FUNCIÓN: GestionApp.catalog_form
    # Objetivo: Compone el formulario de un catálogo según sus campos definidos.
    # Entradas: name: catálogo; record: registro actual o None para nuevo.
    # Salida/reglas: Entrega el guardado a Service.save_catalog y actualiza el listado.
    # -----------------------------------------------------------------
    def catalog_form(self,name,record=None):
        """Abre el formulario de alta o edicion de un elemento de catalogo."""
        _,pk,metadata=CATALOGS[name]
        fields=[(key,label,kind,display(record.get(key)) if record else ('Producto' if kind=='tipo' else ''))
                for key,label,kind in metadata]
        # -----------------------------------------------------------------
        # FUNCIÓN: GestionApp.catalog_form.save
        # Objetivo: Callback de persistencia del formulario de catálogo.
        # Entradas: data: valores ingresados; record indica edición frente a alta.
        # Salida/reglas: Reutiliza la validación de Service y vuelve a mostrar la tabla.
        # -----------------------------------------------------------------
        def save(data):
            """Guarda el catalogo y actualiza el listado cuando la operacion termina."""
            self.service.save_catalog(name,data,record[pk] if record else None)
            self.navigate(name)
        self.form_dialog(('Modificar ' if record else 'Registrar ')+name.lower(),fields,save)

    # -----------------------------------------------------------------
    # FUNCIÓN: GestionApp.remove_catalog
    # Objetivo: Pide confirmación explícita antes de borrar un registro.
    # Entradas: name y row: catálogo y registro seleccionado.
    # Salida/reglas: Si las claves foráneas lo impiden, _safe muestra la razón del fallo.
    # -----------------------------------------------------------------
    def remove_catalog(self,name,row):
        """Solicita confirmacion y elimina el registro seleccionado."""
        _,pk,_=CATALOGS[name]
        if messagebox.askyesno('Confirmar eliminación',
            f"¿Eliminar el registro {row[pk]}?\nSi está relacionado con otros datos, PostgreSQL impedirá borrarlo.",parent=self.root):
            self._safe(lambda:(self.service.delete_catalog(name,row[pk]),self.navigate(name)))

    # -----------------------------------------------------------------
    # FUNCIÓN: GestionApp.requirement_view
    # Objetivo: Muestra requerimientos y, abajo, sus líneas asociadas.
    # Entradas: Filas retornadas por Service.requirements.
    # Salida/reglas: Seleccionar una solicitud refresca detalles sin crear otra pantalla.
    # -----------------------------------------------------------------
    def requirement_view(self):
        """Presenta requerimientos y las lineas del requerimiento seleccionado."""
        # La tabla superior es el maestro; la inferior muestra el detalle de la fila elegida.
        rows=self.service.requirements()
        self._bar(f'{len(rows)} solicitudes registradas',[
            ('Nuevo requerimiento',self.new_requirement,True),
            ('Añadir detalle',lambda:self._selected_action(tree,data,lambda x:self.requirement_line_form(x['numero'])),False),
            ('Editar detalle',lambda:self._line_action(tree,data,detail,detail_map,True),False),
            ('Quitar detalle',lambda:self._line_action(tree,data,detail,detail_map,False),False)])
        top=self._panel();tree,data=self._table(top,rows,('numero','fecha','area','solicitante'),8)
        lower=self._panel()
        tk.Label(lower,text='Detalle de productos y servicios del requerimiento seleccionado',
                 bg='#FFFFFF',fg=COLORS['navy'],font=('Segoe UI',12,'bold')).pack(anchor='w',padx=17,pady=(13,0))
        detail,detail_map=self._table(lower,[],('codigo','nombre','tipo','cantidad','unidad','especificaciones'),7)
        # -----------------------------------------------------------------
        # FUNCIÓN: GestionApp.requirement_view.refresh_detail
        # Objetivo: Callback disparado al seleccionar otro requerimiento en la tabla.
        # Entradas: Selección actual en Treeview.
        # Salida/reglas: Reconstruye solo la tabla de detalles; no modifica la base de datos.
        # -----------------------------------------------------------------
        def refresh_detail(_=None):
            """Actualiza los detalles cuando cambia el requerimiento seleccionado."""
            nonlocal detail,detail_map
            req=self._selected_no_prompt(tree,data)
            if req is None: return
            for w in lower.winfo_children()[1:]:w.destroy()
            detail,detail_map=self._table(lower,self.service.requirement_lines(req['numero']),
                ('codigo','nombre','tipo','cantidad','unidad','especificaciones'),7)
        tree.bind('<<TreeviewSelect>>',lambda _:self._safe(refresh_detail))
        if rows:tree.selection_set('0');refresh_detail()

    # -----------------------------------------------------------------
    # FUNCIÓN: GestionApp._selected_no_prompt
    # Objetivo: Obtiene una fila opcional sin mostrar un cuadro de diálogo.
    # Entradas: tree y data: selección y diccionario de registros.
    # Salida/reglas: Se utiliza en actualizaciones automáticas provocadas por eventos.
    # -----------------------------------------------------------------
    def _selected_no_prompt(self,tree,data):
        """Recupera el registro seleccionado sin mostrar un mensaje de aviso."""
        selection=tree.selection()
        return data[selection[0]] if selection else None

    # -----------------------------------------------------------------
    # FUNCIÓN: GestionApp._line_action
    # Objetivo: Coordina edición o supresión de la línea de un requerimiento.
    # Entradas: edit: True modifica; False solicita confirmar eliminación.
    # Salida/reglas: Primero comprueba selección de requerimiento y de detalle.
    # -----------------------------------------------------------------
    def _line_action(self,tree,data,detail,detail_map,edit):
        """Ejecuta una accion de detalle teniendo en cuenta la seleccion actual."""
        req=self._selected(tree,data)
        if req is None:return
        line=self._selected(detail,detail_map)
        if line is None:return
        if edit:self.requirement_line_form(req['numero'],line)
        elif messagebox.askyesno('Confirmar','¿Quitar el detalle seleccionado?',parent=self.root):
            self._safe(lambda:(self.service.delete_requirement_line(req['numero'],line['codigo']),
                               self.navigate('Requerimientos')))

    # -----------------------------------------------------------------
    # FUNCIÓN: GestionApp.new_requirement
    # Objetivo: Presenta campos de cabecera para crear una solicitud de adquisición.
    # Entradas: Número, fecha ISO, área, empleado y observaciones.
    # Salida/reglas: Guarda mediante el servicio y orienta a añadir los detalles posteriormente.
    # -----------------------------------------------------------------
    def new_requirement(self):
        """Abre el formulario para crear un requerimiento."""
        fields=[('numero','Número de requerimiento (1-8 dígitos)','text',''),
                ('fecha','Fecha (AAAA-MM-DD)','text',date.today().isoformat()),
                ('area','Área solicitante','area',''),('empleado','Empleado solicitante','empleado',''),
                ('observaciones','Observaciones','text','')]
        # -----------------------------------------------------------------
        # FUNCIÓN: GestionApp.new_requirement.save
        # Objetivo: Callback interno que confirma el alta de requerimiento.
        # Entradas: d: diccionario del formulario genérico.
        # Salida/reglas: Registra la cabecera y muestra aviso para completar los detalles.
        # -----------------------------------------------------------------
        def save(d):
            """Valida las entradas a traves del servicio y refresca la pantalla."""
            self.service.new_requirement(d['numero'],d['fecha'],d['area'],d['empleado'],d['observaciones'])
            self.navigate('Requerimientos')
            messagebox.showinfo('Requerimiento registrado',
                'Ahora selecciona el requerimiento y usa «Añadir detalle» para registrar sus productos o servicios.',parent=self.root)
        self.form_dialog('Nuevo requerimiento de compra',fields,save)

    # -----------------------------------------------------------------
    # FUNCIÓN: GestionApp.requirement_line_form
    # Objetivo: Permite añadir o modificar cantidad y especificaciones de un detalle.
    # Entradas: req: número de solicitud; line: detalle existente opcional.
    # Salida/reglas: Impide cambiar la clave del producto durante la edición del mismo detalle.
    # -----------------------------------------------------------------
    def requirement_line_form(self,req,line=None):
        """Abre el formulario para agregar o modificar el detalle solicitado."""
        fields=[('producto','Producto o servicio','producto',line['codigo'] if line else ''),
                ('cantidad','Cantidad solicitada','text',line['cantidad'] if line else '1'),
                ('especificaciones','Especificaciones técnicas','text',line['especificaciones'] if line else '')]
        # -----------------------------------------------------------------
        # FUNCIÓN: GestionApp.requirement_line_form.save
        # Objetivo: Callback para guardar la línea solicitada.
        # Entradas: d: producto, cantidad y especificaciones.
        # Salida/reglas: Usa el procedimiento adecuado (insertar/actualizar) y refresca la vista.
        # -----------------------------------------------------------------
        def save(d):
            """Guarda una linea de requerimiento y actualiza el modulo."""
            if line and d['producto']!=line['codigo']:
                raise ValueError('No puedes cambiar el producto al editar. Quita y vuelve a agregar el detalle.')
            self.service.add_requirement_line(req,d['producto'],d['cantidad'],d['especificaciones'],bool(line))
            self.navigate('Requerimientos')
        self.form_dialog(('Editar' if line else 'Añadir')+f' detalle · Req. {req}',fields,save)

    # -----------------------------------------------------------------
    # FUNCIÓN: GestionApp.evaluation_view
    # Objetivo: Presenta la lista de evaluaciones y su calificación calculada.
    # Entradas: Consulta Service.evaluations con criterios y puntos.
    # Salida/reglas: Ofrece crear nueva evaluación o editar calificaciones.
    # -----------------------------------------------------------------
    def evaluation_view(self):
        """Presenta las evaluaciones de proveedores y sus puntajes."""
        rows=self.service.evaluations()
        self._bar('Seis criterios con puntuación 0–2; aceptado desde 7 puntos',[
            ('Nueva evaluación',lambda:self.evaluation_form(),True),
            ('Editar calificaciones',lambda:self._selected_action(tree,data,self.evaluation_form),False)])
        panel=self._panel();tree,data=self._table(panel,rows,('numero','fecha','requerimiento','proveedor','puntos','resultado'),13)
        tree.bind('<Double-1>',lambda e:self._selected_action(tree,data,self.evaluation_form))

    # -----------------------------------------------------------------
    # FUNCIÓN: GestionApp.evaluation_form
    # Objetivo: Presenta los seis criterios de evaluación para alta o actualización.
    # Entradas: record: evaluación a editar; None si se crea desde cero.
    # Salida/reglas: Muestra opciones de nota 0, 1 y 2; el servicio valida coherencia y transacción.
    # -----------------------------------------------------------------
    def evaluation_form(self,record=None):
        """Abre un formulario de evaluacion nueva o existente."""
        if record:
            # En edición se recuperan notas; en alta se solicitan también cabecera y proveedor.
            scores={r['criterio']:r['calificacion'] for r in self.service.evaluation_lines(record['numero'])}
            fields=[('numero','N.º evaluación','text',record['numero'])]
        else:
            scores={}
            fields=[('numero','Número de evaluación (1-6 dígitos)','text',''),
                    ('fecha','Fecha (AAAA-MM-DD)','text',date.today().isoformat()),
                    ('requerimiento','Requerimiento','requerimiento',''),
                    ('proveedor','Proveedor','proveedor','')]
        for i,crit in enumerate(CRITERIA): fields.append((f'criterio_{i}',crit,'score',scores.get(crit,'2')))
        # -----------------------------------------------------------------
        # FUNCIÓN: GestionApp.evaluation_form.save
        # Objetivo: Callback que envía seis puntuaciones a la lógica de negocio.
        # Entradas: d: valores de criterios, código y datos de la evaluación.
        # Salida/reglas: Refresca la vista y comunica el puntaje obtenido.
        # -----------------------------------------------------------------
        def save(d):
            """Registra los seis criterios de evaluacion y refresca el modulo."""
            totals=self.service.save_evaluation(
                d['numero'],d.get('fecha',''),d.get('requerimiento',''),d.get('proveedor',''),
                [d[f'criterio_{i}'] for i in range(6)],bool(record))
            self.navigate('Evaluaciones')
            messagebox.showinfo('Evaluación guardada',
                f"Puntuación: {totals}/12. Resultado: {'ACEPTADO' if totals>=7 else 'RECHAZADO'}.",parent=self.root)
        self.form_dialog('Evaluación de proveedor',fields,save,width=640)

    # -----------------------------------------------------------------
    # FUNCIÓN: GestionApp.order_view
    # Objetivo: Lista órdenes de compra/servicio y sus líneas relacionadas.
    # Entradas: kind: «Compra» o «Servicio».
    # Salida/reglas: Al cambiar de fila obtiene los detalles desde el servicio.
    # -----------------------------------------------------------------
    def order_view(self,kind):
        """Muestra las ordenes de compra o servicio y sus detalles."""
        rows=self.service.orders(kind)
        name='Órdenes de compra' if kind=='Compra' else 'Órdenes de servicio'
        self._bar(f'{len(rows)} órdenes · Los precios ingresados incluyen IGV (18 %)',[
            (f'Nueva orden de {kind.lower()}',lambda:self.new_order_dialog(kind),True)])
        top=self._panel();tree,data=self._table(top,rows,('numero','fecha','requerimiento','proveedor','total_con_igv'),8)
        lower=self._panel()
        tk.Label(lower,text='Detalles de la orden seleccionada',bg='white',fg=COLORS['navy'],
                 font=('Segoe UI',12,'bold')).pack(anchor='w',padx=16,pady=(12,0))
        # -----------------------------------------------------------------
        # FUNCIÓN: GestionApp.order_view.update_details
        # Objetivo: Callback del selector de una orden en Treeview.
        # Entradas: Fila de orden actualmente seleccionada.
        # Salida/reglas: Reemplaza solo la tabla inferior con los detalles de la orden.
        # -----------------------------------------------------------------
        def update_details(_=None):
            """Refresca las lineas de la orden elegida."""
            row=self._selected_no_prompt(tree,data)
            if row is None:return
            for w in lower.winfo_children()[1:]:w.destroy()
            self._table(lower,self.service.order_lines(kind,row['numero']),
                ('codigo','nombre','cantidad','unidad','precio_unitario','importe'),7)
        tree.bind('<<TreeviewSelect>>',lambda _:self._safe(update_details))
        if rows:tree.selection_set('0');update_details()

    # -----------------------------------------------------------------
    # FUNCIÓN: GestionApp.new_order_dialog
    # Objetivo: Construye la ventana para registrar una orden y un borrador de sus líneas.
    # Entradas: kind: controla los campos adicionales de Compra o Servicio.
    # Salida/reglas: El borrador no se confirma en PostgreSQL hasta pulsar «Registrar orden».
    # -----------------------------------------------------------------
    def new_order_dialog(self,kind):
        """Crea un formulario de orden con un conjunto temporal de lineas."""
        window=tk.Toplevel(self.root);window.title(f'Nueva orden de {kind.lower()}')
        window.geometry('900x700');window.configure(bg='white');window.transient(self.root);window.grab_set()
        tk.Label(window,text=f'Nueva orden de {kind.lower()}',bg='white',fg=COLORS['navy'],
                 font=('Segoe UI',18,'bold')).pack(anchor='w',padx=23,pady=(18,6))
        tk.Label(window,text='Los detalles se registran junto con la orden en una sola transacción.',
                 bg='white',fg=COLORS['muted']).pack(anchor='w',padx=24,pady=(0,8))
        main=tk.Frame(window,bg='white');main.pack(fill='x',padx=24)
        names=[('numero','Número de orden'),('fecha','Fecha AAAA-MM-DD'),
               ('requerimiento','Requerimiento'),('proveedor','Proveedor evaluado'),
               ('genera','Empleado que genera'),('aprueba','Empleado que aprueba')]
        if kind=='Compra':names.extend([('moneda','Moneda'),('pago','Condición de pago'),
                        ('descuento','Descuento total'),('lugar','Punto de entrega'),
                        ('justificacion','Justificación')])
        else:names.extend([('lugar','Lugar del servicio'),('pago','Condición de pago')])
        vars={};inputs={}
        for idx,(key,label) in enumerate(names):
            r=idx//2;c=idx%2
            cell=tk.Frame(main,bg='white');cell.grid(row=r,column=c,sticky='ew',padx=9,pady=6)
            main.columnconfigure(c,weight=1)
            tk.Label(cell,text=label,bg='white',fg=COLORS['text'],font=('Segoe UI',9,'bold')).pack(anchor='w')
            default={'fecha':date.today().isoformat(),'descuento':'0','moneda':'Soles'}.get(key,'')
            var=tk.StringVar(value=default);vars[key]=var
            lookup={'requerimiento':'requerimiento','proveedor':'proveedor',
                    'genera':'empleado','aprueba':'empleado'}
            if key in lookup:
                opts=[f"{r['code']} · {r['label']}" for r in self.service.lookup(lookup[key])]
                widget=ttk.Combobox(cell,textvariable=var,values=opts,state='readonly')
            elif key=='moneda':widget=ttk.Combobox(cell,textvariable=var,values=['Soles','Dolares'],state='readonly')
            else:widget=ttk.Entry(cell,textvariable=var)
            widget.pack(fill='x',pady=(4,0));inputs[key]=widget
        # No se hace un CALL por elemento mientras se edita el borrador de orden.
        # Las lineas permanecen en memoria hasta confirmar la orden completa.
        lines=[]
        detail_head=tk.Frame(window,bg='white');detail_head.pack(fill='x',padx=26,pady=(18,2))
        tk.Label(detail_head,text='Elementos de la orden',bg='white',fg=COLORS['navy'],
                 font=('Segoe UI',12,'bold')).pack(side='left')
        chosen_req=lambda: combo_id(vars['requerimiento'].get())
        # -----------------------------------------------------------------
        # FUNCIÓN: GestionApp.new_order_dialog.add
        # Objetivo: Abre una subventana para elegir un elemento del requerimiento.
        # Entradas: Requerimiento seleccionado y tipo de orden.
        # Salida/reglas: Filtra los productos/servicios disponibles, evitando agregar elementos
        #   ajenos.
        # -----------------------------------------------------------------
        def add():
            """Selecciona un elemento que pertenece al requerimiento de la orden."""
            req=chosen_req()
            if not req:
                messagebox.showwarning('Falta requerimiento','Selecciona primero el requerimiento.',parent=window);return
            try: candidates=self.service.requirement_lines(req,kind if kind=='Servicio' else 'Producto')
            except Exception as exc:messagebox.showerror('Error',str(exc),parent=window);return
            if not candidates:
                messagebox.showwarning('Sin elementos','El requerimiento no contiene elementos de ese tipo.',parent=window);return
            opts={f"{x['codigo']} · {x['nombre']} (máx. {x['cantidad']})":x for x in candidates}
            sub=tk.Toplevel(window);sub.title('Añadir elemento');sub.configure(bg='white')
            sub.geometry('510x295');sub.transient(window);sub.grab_set()
            tk.Label(sub,text='Producto o servicio solicitado',bg='white',fg=COLORS['navy'],
                     font=('Segoe UI',12,'bold')).pack(anchor='w',padx=20,pady=(18,7))
            prod_var=tk.StringVar();cb=ttk.Combobox(sub,values=list(opts),textvariable=prod_var,state='readonly')
            cb.pack(fill='x',padx=20)
            tk.Label(sub,text='Cantidad',bg='white').pack(anchor='w',padx=20,pady=(12,2))
            qty=tk.StringVar(value='1');ttk.Entry(sub,textvariable=qty).pack(fill='x',padx=20)
            tk.Label(sub,text='Precio unitario con IGV (18 %)',bg='white').pack(anchor='w',padx=20,pady=(12,2))
            price=tk.StringVar();ttk.Entry(sub,textvariable=price).pack(fill='x',padx=20)
            # -----------------------------------------------------------------
            # FUNCIÓN: GestionApp.new_order_dialog.add.accept
            # Objetivo: Valida y agrega al borrador una línea con cantidad y precio.
            # Entradas: Opción de producto, cantidad y precio ingresados.
            # Salida/reglas: Impide duplicados y cantidades superiores a las solicitadas; no hace
            #   INSERT aún.
            # -----------------------------------------------------------------
            def accept():
                """Comprueba cantidad y precio y agrega una linea al borrador."""
                try:
                    from .service import positive_integer,money
                    item=opts[prod_var.get()]
                    q=positive_integer(qty.get())
                    if q>int(item['cantidad']):raise ValueError('La cantidad supera la solicitada en este requerimiento')
                    if item['codigo'] in {x['codigo'] for x in lines}:
                        raise ValueError('Ese elemento ya está agregado')
                    p=money(price.get())
                    lines.append({'codigo':item['codigo'],'nombre':item['nombre'],'cantidad':q,'precio':p})
                    redraw();sub.destroy()
                except Exception as exc:messagebox.showerror('Detalle inválido',str(exc),parent=sub)
            self._action(sub,'Añadir',accept).pack(pady=12)
        self._action(detail_head,'Agregar producto / servicio',add).pack(side='right')
        box=tk.Frame(window,bg='white');box.pack(fill='both',expand=True,padx=25,pady=(5,0))
        columns=['Código','Elemento','Cantidad','Precio unitario','Importe con IGV']
        table=ttk.Treeview(box,columns=columns,show='headings',height=5)
        for i,col in enumerate(columns):
            table.heading(col,text=col);table.column(col,width=[75,280,100,155,150][i],anchor='w')
        table.pack(fill='both',expand=True)
        total_label=tk.Label(window,text='Total bruto con IGV: 0.00',bg='white',fg=COLORS['navy'],
                 font=('Segoe UI',12,'bold'));total_label.pack(anchor='e',padx=28,pady=(10,4))
        # -----------------------------------------------------------------
        # FUNCIÓN: GestionApp.new_order_dialog.redraw
        # Objetivo: Vuelve a pintar el borrador y recalcula el importe bruto.
        # Entradas: lines: lista de elementos agregados a la orden.
        # Salida/reglas: Total = suma de cantidad por precio unitario, antes del descuento de compra.
        # -----------------------------------------------------------------
        def redraw():
            """Redibuja las lineas y recalcula el total bruto con IGV."""
            for iid in table.get_children():table.delete(iid)
            for i,x in enumerate(lines):
                table.insert('', 'end', iid=str(i),values=(x['codigo'],x['nombre'],x['cantidad'],
                                         f"{x['precio']:.2f}",f"{x['precio']*x['cantidad']:.2f}"))
            total=sum((x['precio']*x['cantidad'] for x in lines),Decimal('0'))
            total_label.config(text=f'Total bruto con IGV: {total:.2f} (antes de descuento, si aplica)')
        # -----------------------------------------------------------------
        # FUNCIÓN: GestionApp.new_order_dialog.remove
        # Objetivo: Retira una línea del borrador pendiente de confirmar.
        # Entradas: Fila seleccionada de la tabla temporal.
        # Salida/reglas: No elimina registros de PostgreSQL porque todavía no existe la orden.
        # -----------------------------------------------------------------
        def remove():
            """Quita del borrador la linea seleccionada."""
            selection=table.selection()
            if selection:lines.pop(int(selection[0]));redraw()
        # -----------------------------------------------------------------
        # FUNCIÓN: GestionApp.new_order_dialog.req_changed
        # Objetivo: Vacía el borrador al escoger otro requerimiento.
        # Entradas: Evento de cambio de StringVar de requerimiento.
        # Salida/reglas: Evita mezclar líneas pertenecientes a solicitudes distintas.
        # -----------------------------------------------------------------
        def req_changed(*_):
            """Vacía el borrador cuando se cambia de requerimiento."""
            if lines:
                lines.clear();redraw()
        # Al cambiar la cabecera del borrador, las líneas anteriores dejan de ser válidas.
        vars['requerimiento'].trace_add('write',req_changed)
        buttons=tk.Frame(window,bg='white');buttons.pack(fill='x',padx=24,pady=16)
        self._action(buttons,'Quitar línea seleccionada',remove,False).pack(side='left')
        self._action(buttons,'Cancelar',window.destroy,False).pack(side='right')
        # -----------------------------------------------------------------
        # FUNCIÓN: GestionApp.new_order_dialog.save
        # Objetivo: Confirma la orden completa mediante un único llamado al servicio.
        # Entradas: Datos de cabecera y lista temporal de líneas.
        # Salida/reglas: Tras un commit válido cierra el formulario; si falla conserva los datos.
        # -----------------------------------------------------------------
        def save():
            """Registra la orden y sus lineas mediante el servicio de negocio."""
            form={k:(combo_id(v.get()) if k in ('requerimiento','proveedor','genera','aprueba') else v.get())
                  for k,v in vars.items()}
            try:
                self.service.new_order(kind,form,lines)
            except Exception as exc:
                messagebox.showerror('Orden no registrada',str(exc),parent=window);return
            window.destroy()
            self.navigate('Órdenes de compra' if kind=='Compra' else 'Órdenes de servicio')
            messagebox.showinfo('Operación exitosa','Orden registrada con todos sus detalles.',parent=self.root)
        self._action(buttons,'Registrar orden',save).pack(side='right',padx=12)

    # -----------------------------------------------------------------
    # FUNCIÓN: GestionApp.report_view
    # Objetivo: Crea la pantalla para elegir entre diez consultas de informes.
    # Entradas: REPORTS: catálogo seguro de SQL predefinido.
    # Salida/reglas: Habilita botones Consultar y Exportar CSV y ejecuta el primero por defecto.
    # -----------------------------------------------------------------
    def report_view(self):
        """Muestra el selector de los diez reportes y el boton para exportar CSV."""
        top=tk.Frame(self.content,bg=COLORS['cream']);top.pack(fill='x',pady=(0,12))
        tk.Label(top,text='Selecciona una de las diez consultas del proyecto:',bg=COLORS['cream'],
                 fg=COLORS['text'],font=('Segoe UI',10)).pack(side='left')
        selection=tk.StringVar(value=next(iter(REPORTS)))
        choices=ttk.Combobox(top,textvariable=selection,values=list(REPORTS),width=43,state='readonly')
        choices.pack(side='left',padx=12)
        self._action(top,'Exportar CSV',lambda:self.export_csv(),False).pack(side='right')
        self._action(top,'Consultar',lambda:self.run_report(selection.get()),True).pack(side='right',padx=12)
        self.report_panel=self._panel()
        self.run_report(selection.get())

    # -----------------------------------------------------------------
    # FUNCIÓN: GestionApp.run_report
    # Objetivo: Ejecuta un SELECT predefinido y presenta el conjunto de resultados.
    # Entradas: name: etiqueta de reporte existente en REPORTS.
    # Salida/reglas: Actualiza last_report para habilitar su exportación.
    # -----------------------------------------------------------------
    def run_report(self,name):
        """Ejecuta la consulta elegida y presenta sus resultados."""
        try:
            # REPORTS actúa como lista blanca: el usuario escoge un SELECT ya construido.
            self.last_report=self.db.query(REPORTS[name]);self.last_report_name=name
        except Exception as exc:
            messagebox.showerror('No se pudo generar el reporte',str(exc),parent=self.root);return
        for child in self.report_panel.winfo_children():child.destroy()
        tk.Label(self.report_panel,text=f'{name}  ·  {len(self.last_report)} filas',bg='white',fg=COLORS['navy'],
                 font=('Segoe UI',12,'bold')).pack(anchor='w',padx=16,pady=(16,0))
        self._table(self.report_panel,self.last_report,('Sin resultados para esta consulta',),16)

    # -----------------------------------------------------------------
    # FUNCIÓN: GestionApp.export_csv
    # Objetivo: Escribe el reporte actual en un archivo CSV elegido por el usuario.
    # Entradas: last_report: lista de filas con cabeceras.
    # Salida/reglas: Utiliza UTF-8 con BOM para facilitar lectura en Excel; informa errores de E/S.
    # -----------------------------------------------------------------
    def export_csv(self):
        """Exporta el reporte a CSV compatible con Excel (UTF-8 con BOM)."""
        if not self.last_report:
            messagebox.showinfo('Sin datos','El informe no contiene filas para exportar.',parent=self.root);return
        path=filedialog.asksaveasfilename(parent=self.root,defaultextension='.csv',
                 filetypes=[('CSV','*.csv')],initialfile='reporte_adquisiciones.csv')
        if not path:return
        try:
            # El BOM UTF-8 facilita que Excel detecte caracteres con tildes.
            with open(path,'w',encoding='utf-8-sig',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=list(self.last_report[0]))
                writer.writeheader();writer.writerows(self.last_report)
            messagebox.showinfo('Exportación correcta',f'Archivo guardado: {path}',parent=self.root)
        except OSError as exc:messagebox.showerror('Error al exportar',str(exc),parent=self.root)

    # -----------------------------------------------------------------
    # FUNCIÓN: GestionApp.close
    # Objetivo: Solicita confirmación de salida y cierra la ventana Tk.
    # Entradas: Evento WM_DELETE_WINDOW de Windows.
    # Salida/reglas: Destruye la raíz únicamente cuando el usuario acepta.
    # -----------------------------------------------------------------
    def close(self):
        """Pide confirmacion antes de finalizar la aplicacion."""
        if messagebox.askokcancel('Salir del sistema','¿Deseas cerrar el aplicativo de Gestión de Requerimientos y Adquisiciones?',parent=self.root):
            self.root.destroy()
