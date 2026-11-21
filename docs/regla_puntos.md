# Regla de puntos · EcoConecta

> **Importante:** los valores de esta tabla son **ejemplos configurables definidos por el equipo**. Los documentos de la Fundación Santo Domingo no establecen equivalencias ni valores de puntos, por lo que **no son reglas oficiales** y están sujetos a validación de FSD (RN-06).

## Cómo se calculan

Los puntos se calculan **solo después de que el recolector registra la recolección** (RN-05), con esta fórmula:

```
puntos = cantidad entregada × puntos por unidad del material
```

El resultado se redondea al entero más cercano. Si el material no tiene regla configurada, no se asignan puntos y el sistema lo explica en pantalla.

## Valores de ejemplo

| Material | Unidad | Puntos por unidad |
|---|---|---|
| Orgánico | kg | 5 |
| Plástico | kg | 8 |
| Cartón y papel | kg | 4 |
| Vidrio | kg | 3 |
| Metal | kg | 10 |

**Ejemplo:** 2,5 kg de plástico × 8 = 20 puntos. Cada movimiento guarda esa explicación y el usuario la ve en "Mis solicitudes".

## Quién los cambia y cómo

El **administrador** modifica los puntos por unidad desde la pantalla *Administrar → Puntos por material*. El cambio se aplica a las recolecciones registradas **a partir de ese momento**; los puntos ya otorgados no se recalculan.

## Garantías

- Los puntos no se asignan antes de la recolección (RN-05).
- Cada asignación guarda el cálculo, por lo que es explicable y auditable.
- La regla es parametrizable sin modificar el código (RN-06).
- La interfaz muestra siempre un aviso de que los valores no son oficiales de FSD.