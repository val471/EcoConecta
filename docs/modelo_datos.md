# Modelo de datos · EcoConecta Villas de San Pablo

Base de datos: **PostgreSQL**, acceso con SQLAlchemy y Psycopg.

## Diagrama de relaciones

```mermaid
erDiagram
    USUARIOS ||--o{ SOLICITUDES : "crea"
    SOLICITUDES ||--o{ HISTORIAL_ESTADO : "registra cambios"
    SOLICITUDES ||--o| ASIGNACIONES : "se asigna"
    USUARIOS ||--o{ ASIGNACIONES : "coordinador / recolector"
    SOLICITUDES ||--o| PROGRAMACIONES : "se programa"
    SOLICITUDES ||--o| RECOLECCIONES : "se cierra"
    RECOLECCIONES ||--o| PUNTOS : "genera"
    USUARIOS ||--o{ PUNTOS : "recibe"
    REGLAS_PUNTOS ||--o{ PUNTOS : "se aplica"
    SOLICITUDES ||--o{ NOTIFICACIONES : "genera"
    USUARIOS {
        int id PK
        string nombre
        string email
        string password_hash
        string rol
        string flujo
        string tipo
        string telefono
        bool es_piloto
    }
    SOLICITUDES {
        int id PK
        string codigo
        int usuario_id FK
        string flujo
        string tipo_generador
        string direccion
        string contacto
        string observaciones
        string preferencia_horaria
        string estado
        datetime creada
    }
    HISTORIAL_ESTADO {
        int id PK
        int solicitud_id FK
        string estado
        string por
        string nota
        datetime fecha
    }
    ASIGNACIONES {
        int id PK
        int solicitud_id FK
        int coordinador_id FK
        int recolector_id FK
        datetime fecha
    }
    PROGRAMACIONES {
        int id PK
        int solicitud_id FK
        date fecha
        string hora
        string persona
    }
    RECOLECCIONES {
        int id PK
        int solicitud_id FK
        string tipo_residuo
        numeric cantidad
        string unidad
        datetime fecha
    }
    REGLAS_PUNTOS {
        int id PK
        string tipo_residuo
        string unidad
        numeric puntos_por_unidad
    }
    PUNTOS {
        int id PK
        int usuario_id FK
        int solicitud_id FK
        int puntos
        string explicacion
        datetime fecha
    }
    NOTIFICACIONES {
        int id PK
        int solicitud_id FK
        string canal
        string mensaje
        string estado
        datetime fecha
    }
```

## Tablas principales

| Tabla | Para qué sirve |
|---|---|
| `usuarios` | Todas las personas, con su rol: solicitante, coordinador de huerteros, coordinador de recicladores, recolector o administrador. `es_piloto` habilita a quien puede solicitar (RN-08). |
| `solicitudes` | Cada solicitud con su código, flujo (orgánico o reciclable) y estado actual. |
| `historial_estado` | Una fila por cada cambio de estado, para la trazabilidad (RN-04). |
| `asignaciones` | Asocia la solicitud con su coordinador y su recolector (RN-03). |
| `programaciones` | Día, hora y persona encargada (RN-02). |
| `recolecciones` | Cierre de la solicitud con el tipo y la cantidad entregada. |
| `reglas_puntos` | Puntos por unidad según el material; la edita el administrador (RN-06). |
| `puntos` | Movimientos de puntos del usuario, con la explicación del cálculo. |
| `notificaciones` | Mensajes enviados o simulados por WhatsApp. |

## Valores permitidos

- **Roles:** `solicitante`, `coord_huerteros`, `coord_recicladores`, `recolector`, `admin`
- **Flujos:** `organico`, `reciclable`
- **Estados:** `recibida`, `en_revision`, `asignada`, `programada`, `recolectada`, `cancelada`
- **Tipos de residuo:** `organico`, `plastico`, `carton_papel`, `vidrio`, `metal`

## Privacidad (RN-07)

El contacto y la dirección solo se entregan por la API a quien necesita atender la solicitud (coordinador del flujo y recolector asignado). Al modelo de IA no se envían datos personales.