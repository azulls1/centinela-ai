# SKILL: Presentaciones PowerPoint (.pptx)

> **Version:** 3.8.0
> **Trigger:** Creacion de presentaciones profesionales
> **Agente:** nxt-docs
> **Track:** shared

## Proposito
Crear presentaciones profesionales para pitches, demos, reportes
y comunicacion con stakeholders.

## Cuando se Activa
- Crear pitch deck
- Presentar roadmap
- Demo de producto
- Reporte de progreso
- Presentacion a stakeholders

## Instrucciones

### 1. Formato Estandar NXT

#### Tamano de diapositiva
- Widescreen 16:9 (predeterminado)
- Alternativa: 4:3 para proyectores antiguos

#### Tipografia
- **Titulos**: Calibri Bold 44pt
- **Subtitulos**: Calibri Bold 32pt
- **Cuerpo**: Calibri 24pt
- **Notas**: Calibri 18pt

#### Colores
- **Fondo**: Blanco #FFFFFF o Azul oscuro #1E3A5F
- **Texto principal**: #1F2937 (oscuro) o #FFFFFF (claro)
- **Acento**: #3B82F6 (azul)
- **Secundario**: #F97316 (naranja)
- **Exito**: #10B981 (verde)

### 2. Estructura de Presentacion

#### Pitch Deck (10-15 slides)
1. Titulo + Tagline
2. Problema
3. Solucion
4. Demo/Producto
5. Mercado
6. Modelo de negocio
7. Traccion
8. Equipo
9. Financiamiento
10. Contacto

#### Reporte de Progreso
1. Titulo + Fecha
2. Resumen ejecutivo
3. Logros del periodo
4. Metricas clave
5. Proximos pasos
6. Riesgos/Bloqueadores
7. Q&A

#### Demo de Producto
1. Titulo
2. Contexto/Problema
3. Solucion (alto nivel)
4. Demo en vivo / Screenshots
5. Features clave
6. Roadmap
7. Q&A

### 3. Templates de Slides

#### Slide de Titulo
```
+--------------------------------------------------+
|                                                  |
|                                                  |
|                                                  |
|              TITULO PRINCIPAL                    |
|              ─────────────────                   |
|              Subtitulo o tagline                 |
|                                                  |
|              [Logo]                              |
|                                                  |
|              Fecha | Presentador                 |
|                                                  |
+--------------------------------------------------+
```

#### Slide de Contenido
```
+--------------------------------------------------+
|  TITULO DE SECCION                               |
|  ══════════════════════════════════════════════  |
|                                                  |
|  • Punto principal 1                             |
|    - Detalle                                     |
|                                                  |
|  • Punto principal 2                             |
|    - Detalle                                     |
|                                                  |
|  • Punto principal 3                             |
|    - Detalle                                     |
|                                                  |
+--------------------------------------------------+
```

#### Slide de Metricas
```
+--------------------------------------------------+
|  METRICAS CLAVE                                  |
|  ══════════════════════════════════════════════  |
|                                                  |
|   +--------+    +--------+    +--------+         |
|   |  150K  |    |  95%   |    |  4.8   |         |
|   | Users  |    | Uptime |    | Rating |         |
|   +--------+    +--------+    +--------+         |
|                                                  |
|   [Grafico de tendencia]                         |
|                                                  |
+--------------------------------------------------+
```

#### Slide de Timeline
```
+--------------------------------------------------+
|  ROADMAP 2025                                    |
|  ══════════════════════════════════════════════  |
|                                                  |
|  Q1        Q2        Q3        Q4                |
|  ─●────────●────────●────────●─                  |
|   │        │        │        │                   |
|   MVP      Beta     Launch   Scale               |
|                                                  |
+--------------------------------------------------+
```

### 4. Buenas Practicas

1. **Una idea por slide**
2. **Maximo 6 bullet points**
3. **Texto grande y legible**
4. **Imagenes de alta calidad**
5. **Consistencia en colores**
6. **Animaciones minimas**
7. **Notas del presentador**

### 5. Proceso de Generacion

1. Definir tipo de presentacion
2. Crear outline de contenido
3. Aplicar template correspondiente
4. Insertar contenido y graficos
5. Agregar notas del presentador
6. Exportar a .pptx
7. Guardar en `docs/presentations/`

## Comandos de Ejemplo

```
"Crea un pitch deck para el proyecto"
"Genera presentacion de roadmap"
"Crea slides para la demo del sprint"
"Genera reporte de progreso en PowerPoint"
"Convierte el PRD en presentacion ejecutiva"
```

## Integracion Python

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RgbColor

def crear_presentacion_nxt(titulo, slides_content, output_path):
    prs = Presentation()
    prs.slide_width = Inches(13.333)  # 16:9
    prs.slide_height = Inches(7.5)

    # Slide de titulo
    slide_layout = prs.slide_layouts[6]  # Blank
    slide = prs.slides.add_slide(slide_layout)

    # Agregar titulo
    title_box = slide.shapes.add_textbox(
        Inches(1), Inches(2.5), Inches(11.333), Inches(1.5)
    )
    title_frame = title_box.text_frame
    title_para = title_frame.paragraphs[0]
    title_para.text = titulo
    title_para.font.size = Pt(44)
    title_para.font.bold = True
    title_para.alignment = PP_ALIGN.CENTER

    # Slides de contenido
    for slide_data in slides_content:
        slide = prs.slides.add_slide(prs.slide_layouts[6])

        # Titulo del slide
        title = slide.shapes.add_textbox(
            Inches(0.5), Inches(0.5), Inches(12), Inches(1)
        )
        title.text_frame.paragraphs[0].text = slide_data['titulo']
        title.text_frame.paragraphs[0].font.size = Pt(32)
        title.text_frame.paragraphs[0].font.bold = True

        # Contenido
        content = slide.shapes.add_textbox(
            Inches(0.5), Inches(1.5), Inches(12), Inches(5)
        )
        tf = content.text_frame
        for punto in slide_data['puntos']:
            p = tf.add_paragraph()
            p.text = f"• {punto}"
            p.font.size = Pt(24)

    prs.save(output_path)
```

---

## Funcion Completa - Pitch Deck

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

def create_pitch_deck(title: str, slides_data: list, output: str = "pitch.pptx"):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Slide 1: Title
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank
    txBox = slide.shapes.add_textbox(Inches(1), Inches(2.5), Inches(11), Inches(2))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(44)
    p.font.bold = True
    p.font.color.rgb = RGBColor(0x3B, 0x82, 0xF6)
    p.alignment = PP_ALIGN.CENTER

    # Content slides
    for data in slides_data:
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        # Title
        txBox = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(12), Inches(1))
        p = txBox.text_frame.paragraphs[0]
        p.text = data["title"]
        p.font.size = Pt(32)
        p.font.bold = True
        # Body
        txBox = slide.shapes.add_textbox(Inches(0.5), Inches(1.5), Inches(12), Inches(5))
        tf = txBox.text_frame
        tf.word_wrap = True
        for bullet in data.get("bullets", []):
            p = tf.add_paragraph()
            p.text = f"• {bullet}"
            p.font.size = Pt(18)
            p.space_after = Pt(8)

    prs.save(output)
    return output
```

---

## Recursos Visuales

Para generar graficos y visualizaciones, usar:
- **nxt-media** para imagenes personalizadas
- **matplotlib** para graficos de datos
- **mermaid** para diagramas (exportar como imagen)
