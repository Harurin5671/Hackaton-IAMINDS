# Diccionario de Datos (Data Dictionary)

Este documento explica en detalle el significado de cada columna presente en los datasets del proyecto `GhostEnergy AI`.

---

## 1. Archivo: `sedes_uptc.csv` (Metadatos de Sedes)
Información estática sobre las características físicas y operativas de cada sede.

| Columna | Descripción |
|---------|-------------|
| **sede** | Nombre corto de la sede (ej: "Tunja"). Llave para unir con la tabla de consumos. |
| **sede_id** | Identificador único estándar (ej: "UPTC_TUN"). |
| **nombre_completo** | Nombre oficial de la sede. |
| **ciudad** | Ciudad donde se ubica la sede. |
| **area_m2** | Área total construida en metros cuadrados. Útil para normalizar consumos (kWh/m²). |
| **num_estudiantes** | Cantidad aproximada de estudiantes matriculados. Factor clave para la ocupación. |
| **num_empleados** | Cantidad de administrativos y docentes. |
| **num_edificios** | Número de bloques o edificios en la sede. |
| **tiene_residencias** | `True` si la sede cuenta con dormitorios (implica consumo nocturno/doméstico). |
| **tiene_laboratorios_pesados** | `True` si hay laboratorios de ingeniería/industrial (alto consumo de potencia). |
| **altitud_msnm** | Altitud sobre el nivel del mar. Afecta la eficiencia de equipos y temperatura. |
| **temp_promedio_c** | Temperatura ambiente promedio histórica de la ciudad. |
| **pct_comedores** | Porcentaje estimado del consumo total atribuible a comedores. |
| **pct_salones** | Porcentaje estimado del consumo total atribuible a salones. |
| **pct_laboratorios** | Porcentaje estimado del consumo total atribuible a laboratorios. |
| **pct_auditorios** | Porcentaje estimado del consumo total atribuible a auditorios. |
| **pct_oficinas** | Porcentaje estimado del consumo total atribuible a oficinas. |

---

## 2. Archivo: `consumos_uptc.csv` (y `_clean.csv`)
Registro histórico horario de consumo energético, agua y variables operativas.

### Identificación y Temporalidad Básica
| Columna | Descripción |
|---------|-------------|
| **reading_id** | Identificador único de cada fila (lectura horaria). |
| **timestamp** | Fecha y hora exacta del registro (AAAA-MM-DD HH:MM:SS). |
| **sede** | Nombre de la sede a la que pertenece el registro. |
| **sede_id** | ID de la sede. |

### Consumo Energético
| Columna | Descripción |
|---------|-------------|
| **energia_total_kwh** | Energía eléctrica total consumida en esa hora (Suma de todos los sectores). |
| **potencia_total_kw** | Demanda media de potencia en esa hora. (Relacionado con `energia_total_kwh` pero puede indicar picos). |
| **energia_comedor_kwh** | Consumo específico de cafeterías y comedores (Refrigeración, cocción eléctrica). |
| **energia_salones_kwh** | Consumo de aulas de clase (Iluminación, videoproyectores). |
| **energia_laboratorios_kwh** | Consumo de laboratorios (Equipos especializados, motores, hornos). |
| **energia_auditorios_kwh** | Consumo de auditorios (Sonido, iluminación escénica, aire acondicionado en eventos). |
| **energia_oficinas_kwh** | Consumo administrativo (Computadores, iluminación, servidores locales). |

### Variables Ambientales y Operativas
| Columna | Descripción |
|---------|-------------|
| **agua_litros** | Consumo de agua potable en litros para esa hora. |
| **temperatura_exterior_c** | Temperatura ambiente registrada en la sede (°C). |
| **ocupacion_pct** | Porcentaje estimado de ocupación humana en la sede (0-100%). |
| **co2_kg** | Emisiones de CO2 estimadas asociadas al consumo energético (Huella de carbono). |

### Variables Temporales (Calendario)
| Columna | Descripción |
|---------|-------------|
| **hora** | Hora del día (0-23). Importante para patrones diarios. |
| **dia_semana** | Día de la semana numérico (0=Lunes, 6=Domingo). |
| **dia_nombre** | Nombre del día (Lunes, Martes...). |
| **mes** | Mes del año (1-12). |
| **trimestre** | Trimestre del año (1-4). |
| **año** | Año del registro (2018-2025). |
| **periodo_academico** | Etapa del semestre: 'Semestre' (Clases normales), 'Vacaciones', 'Parciales', 'Finales'. |
| **es_fin_semana** | Booleano (`True`/`False`). Indica si es sábado o domingo. |
| **es_festivo** | Booleano. Indica si es un día feriado en Colombia. |
| **es_semana_parciales** | Booleano. Indica alta carga académica (posible mayor uso de bibliotecas/salas). |
| **es_semana_finales** | Booleano. Similar a parciales pero al final del semestre. |

### Variables Ingenieriles (Feature Engineering)
Estas columnas fueron generadas (`02_preprocessing.py`) para capturar la naturaleza cíclica del tiempo en los modelos de Inteligencia Artificial.

| Columna | Descripción |
|---------|-------------|
| **hour_sin / hour_cos** | Transformación seno/coseno de la hora. Permite al modelo entender que las 23:00 y las 00:00 están "cerca". |
| **day_sin / day_cos** | Transformación cíclica del día de la semana. |
| **month_sin / month_cos** | Transformación cíclica del mes (Enero está "cerca" de Diciembre). |
