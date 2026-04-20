# SKILL: Hojas de Calculo Excel (.xlsx)

> **Version:** 3.8.0
> **Trigger:** Creacion de hojas de calculo profesionales
> **Agente:** nxt-docs
> **Track:** shared

## Proposito
Crear hojas de calculo profesionales para backlogs, tracking, reportes
de metricas y analisis de datos.

## Cuando se Activa
- Crear backlog de proyecto
- Tracking de sprints
- Reportes de metricas
- Analisis de datos
- Presupuestos y estimaciones
- Matrices de riesgo

## Instrucciones

### 1. Formato Estandar NXT

#### Tipografia
- **Headers**: Calibri Bold 12pt, fondo #3B82F6, texto blanco
- **Cuerpo**: Calibri 11pt
- **Totales**: Calibri Bold 11pt

#### Colores
- **Header**: #3B82F6 (azul) con texto blanco
- **Filas alternas**: #F3F4F6 (gris claro)
- **Bordes**: #E5E7EB
- **Totales**: #FEF3C7 (amarillo claro)
- **Exito**: #D1FAE5 (verde claro)
- **Error**: #FEE2E2 (rojo claro)
- **Advertencia**: #FEF3C7 (amarillo claro)

#### Formato de celdas
- Anchos de columna ajustados al contenido
- Altura de fila: 20px minimo
- Alineacion: Izquierda para texto, Derecha para numeros
- Formato de fecha: DD/MM/YYYY
- Formato numerico: #,##0.00

### 2. Templates de Excel

#### Backlog de Proyecto
```
+----+------------+------------------+----------+----------+--------+-------+
| ID | Tipo       | Titulo           | Prioridad| Estado   | Sprint | Story |
+----+------------+------------------+----------+----------+--------+-------+
| 1  | Epic       | Autenticacion    | Must     | In Prog  | -      | -     |
| 2  | Story      | Login con email  | Must     | Done     | 1      | 3     |
| 3  | Story      | Registro         | Must     | In Prog  | 1      | 5     |
| 4  | Story      | Reset password   | Should   | Backlog  | 2      | 3     |
+----+------------+------------------+----------+----------+--------+-------+
```

#### Sprint Tracking
```
+----+------------------+--------+----------+-----------+-------+-------+
| ID | Story            | Asign. | Estimado | Gastado   | Resta | Estado|
+----+------------------+--------+----------+-----------+-------+-------+
| 1  | Login form       | Dev    | 5h       | 4h        | 1h    | 80%   |
| 2  | API auth         | Dev    | 8h       | 10h       | 0h    | 100%  |
| 3  | Tests login      | QA     | 3h       | 2h        | 1h    | 67%   |
+----+------------------+--------+----------+-----------+-------+-------+
|    | TOTAL            |        | 16h      | 16h       | 2h    | 87%   |
+----+------------------+--------+----------+-----------+-------+-------+
```

#### Matriz de Riesgos
```
+------+------------------+-------------+---------+-------+------------------+
| ID   | Riesgo           | Probabilidad| Impacto | Score | Mitigacion       |
+------+------------------+-------------+---------+-------+------------------+
| R-01 | Retraso API ext  | Alta        | Alto    | 9     | Plan B interno   |
| R-02 | Rotacion equipo  | Media       | Medio   | 4     | Documentacion    |
| R-03 | Bug en produccion| Baja        | Alto    | 3     | Tests e2e        |
+------+------------------+-------------+---------+-------+------------------+
```

#### Reporte de Metricas
```
+-------------+--------+--------+--------+--------+---------+
| Metrica     | Sem 1  | Sem 2  | Sem 3  | Sem 4  | Total   |
+-------------+--------+--------+--------+--------+---------+
| Stories     | 5      | 7      | 6      | 8      | 26      |
| Bugs        | 2      | 1      | 3      | 1      | 7       |
| Velocidad   | 15     | 21     | 18     | 24     | 78      |
| Cobertura   | 75%    | 78%    | 80%    | 82%    | 82%     |
+-------------+--------+--------+--------+--------+---------+
```

### 3. Formulas Utiles

#### Velocidad del Sprint
```excel
=SUMIF(Estado, "Done", StoryPoints)
```

#### Burndown
```excel
=TotalPoints - SUMIF(Fecha, "<="&HOY(), Completado)
```

#### Score de Riesgo
```excel
=IF(Probabilidad="Alta",3,IF(Probabilidad="Media",2,1)) *
 IF(Impacto="Alto",3,IF(Impacto="Medio",2,1))
```

#### Progreso de Sprint
```excel
=COUNTIF(Estado, "Done") / COUNTA(Estado)
```

### 4. Validacion de Datos

#### Prioridad (MoSCoW)
```
Lista: Must, Should, Could, Won't
```

#### Estado
```
Lista: Backlog, Ready, In Progress, In Review, Done, Blocked
```

#### Tipo
```
Lista: Epic, Story, Task, Bug, Tech Debt
```

### 5. Graficos Recomendados

| Tipo de Grafico | Uso |
|-----------------|-----|
| Burndown | Progreso del sprint |
| Velocity | Velocidad historica |
| Pie | Distribucion de estados |
| Bar | Comparacion entre sprints |
| Line | Tendencias de metricas |

### 6. Proceso de Generacion

1. Definir tipo de hoja de calculo
2. Crear estructura de columnas
3. Aplicar formato NXT
4. Agregar validaciones de datos
5. Insertar formulas
6. Crear graficos si aplica
7. Proteger celdas con formulas
8. Guardar en `docs/tracking/`

## Comandos de Ejemplo

```
"Crea el backlog en Excel"
"Genera hoja de tracking del sprint 1"
"Crea matriz de riesgos en xlsx"
"Genera reporte de metricas semanal"
"Exporta las stories a Excel"
```

## Integracion Python

```python
import openpyxl
from openpyxl.styles import Font, Fill, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.chart import BarChart, Reference

def crear_backlog_nxt(stories, output_path):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Backlog"

    # Estilos
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = Fill(start_color="3B82F6", fill_type="solid")

    # Headers
    headers = ["ID", "Tipo", "Titulo", "Prioridad", "Estado", "Sprint", "Points"]
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill

    # Datos
    for row, story in enumerate(stories, 2):
        ws.cell(row=row, column=1, value=story['id'])
        ws.cell(row=row, column=2, value=story['tipo'])
        ws.cell(row=row, column=3, value=story['titulo'])
        ws.cell(row=row, column=4, value=story['prioridad'])
        ws.cell(row=row, column=5, value=story['estado'])
        ws.cell(row=row, column=6, value=story.get('sprint', ''))
        ws.cell(row=row, column=7, value=story.get('points', 0))

    # Ajustar anchos
    for column in ws.columns:
        max_length = max(len(str(cell.value or '')) for cell in column)
        ws.column_dimensions[column[0].column_letter].width = max_length + 2

    # Validacion de datos
    from openpyxl.worksheet.datavalidation import DataValidation

    prioridad_dv = DataValidation(
        type="list",
        formula1='"Must,Should,Could,Won\'t"'
    )
    ws.add_data_validation(prioridad_dv)
    prioridad_dv.add(f'D2:D{len(stories)+1}')

    wb.save(output_path)

def crear_burndown_chart(ws, data_range, title="Burndown Chart"):
    chart = BarChart()
    chart.type = "col"
    chart.title = title

    data = Reference(ws, min_col=2, min_row=1, max_col=2, max_row=10)
    cats = Reference(ws, min_col=1, min_row=2, max_row=10)

    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)

    ws.add_chart(chart, "E2")
```

---

## Funcion Completa con Formulas

```python
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def create_backlog_sheet(tasks: list, output: str = "backlog.xlsx"):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Sprint Backlog"

    # Headers
    headers = ["ID", "Story", "Prioridad", "Estimacion", "Estado", "Asignado"]
    header_fill = PatternFill(start_color="3B82F6", fill_color="3B82F6", patternType="solid")
    header_font = Font(color="FFFFFF", bold=True, size=11)

    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")

    # Data
    for row_idx, task in enumerate(tasks, 2):
        for col_idx, val in enumerate(task.values(), 1):
            ws.cell(row=row_idx, column=col_idx, value=val)

    # Formulas de resumen
    last_row = len(tasks) + 1
    ws.cell(row=last_row + 2, column=1, value="RESUMEN").font = Font(bold=True)
    ws.cell(row=last_row + 3, column=1, value="Total stories")
    ws.cell(row=last_row + 3, column=2, value=f"=COUNTA(B2:B{last_row})")
    ws.cell(row=last_row + 4, column=1, value="Total puntos")
    ws.cell(row=last_row + 4, column=2, value=f"=SUM(D2:D{last_row})")
    ws.cell(row=last_row + 5, column=1, value="Completadas")
    ws.cell(row=last_row + 5, column=2, value=f'=COUNTIF(E2:E{last_row},"Done")')

    # Auto-width
    for col in range(1, len(headers) + 1):
        ws.column_dimensions[get_column_letter(col)].width = 18

    wb.save(output)
    return output
```

---

## Hojas Multiples

Para proyectos complejos, usar multiples hojas:

1. **Resumen** - Dashboard con metricas clave
2. **Backlog** - Lista completa de items
3. **Sprint Actual** - Tracking del sprint en curso
4. **Historico** - Sprints anteriores
5. **Riesgos** - Matriz de riesgos
6. **Configuracion** - Listas para validaciones
