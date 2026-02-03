# Sistema de Gestión de Recursos Humanos

Sistema web para gestión de búsquedas laborales, postulantes y evaluación automática de CVs.

## Funcionalidades

- **Gestión de Puestos**: Crear vacantes con requisitos específicos (experiencia, tecnologías, inglés, título)
- **Gestión de Postulantes**: Cargar candidatos con sus CVs (PDF/DOCX)
- **Parser de CVs**: Extracción automática de experiencia, tecnologías, nivel de inglés y título universitario
- **Evaluación Automática**: Matching candidato-puesto con puntaje y cumplimiento de requisitos
- **Workflow de Estados**: Pendiente → En Revisión → Entrevista → Aprobado/Rechazado

## Instalación

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python run.py
```

Abrir http://localhost:5000 en el navegador.

## Estructura del Proyecto

```
├── app/
│   ├── models/          # Modelos de datos (Puesto, Postulante, Postulación)
│   ├── services/        # Lógica de negocio (CVParser, PostulacionService)
│   ├── routes/          # Rutas Flask (endpoints)
│   └── templates/       # Templates HTML (Jinja2)
├── uploads/             # CVs subidos
├── config.py            # Configuración
├── run.py               # Punto de entrada
└── requirements.txt     # Dependencias
```

## Tecnologías

- **Backend**: Python 3, Flask, SQLAlchemy
- **Frontend**: Bootstrap 5, Bootstrap Icons
- **Base de datos**: SQLite
- **Parsing CVs**: pdfplumber, python-docx
Sistema de gestion y procesamiento para cvs en una empresa de RRHH
