# ML Model Card

> **Fase:** Construir / Verificar
> **Agente:** nxt-aiml
> **Version:** 3.8.0
> **Estado:** [Draft | Review | Approved]

---

## Informacion del Modelo

| Campo | Valor |
|-------|-------|
| Nombre | [nombre del modelo] |
| Version | [v1.0.0] |
| Tipo | [clasificacion/regresion/NLP/vision/generativo] |
| Framework | [PyTorch/TensorFlow/scikit-learn/HuggingFace] |
| Fecha de Entrenamiento | YYYY-MM-DD |
| Autor | [nombre/equipo] |
| Licencia | [MIT/Apache 2.0/propietaria] |

## Uso Previsto

- **Caso de uso primario:** [descripcion]
- **Usuarios objetivo:** [quienes usaran el modelo]
- **Fuera de scope:** [usos NO soportados]

## Datos de Entrenamiento

| Aspecto | Detalle |
|---------|---------|
| Dataset | [nombre/fuente] |
| Tamano | [N registros / N GB] |
| Split train/val/test | [70/15/15 %] |
| Preprocesamiento | [normalizacion, tokenizacion, etc.] |

## Metricas de Performance

| Metrica | Train | Validation | Test | Objetivo |
|---------|-------|------------|------|----------|
| Accuracy | [%] | [%] | [%] | >= [%] |
| Precision | [%] | [%] | [%] | >= [%] |
| Recall | [%] | [%] | [%] | >= [%] |
| F1-Score | [%] | [%] | [%] | >= [%] |
| AUC-ROC | [N] | [N] | [N] | >= [N] |
| Latencia (p95) | - | - | [N]ms | < [N]ms |

## Limitaciones Conocidas

- **Sesgo de datos:** [ej. subrepresentacion de grupo X]
- **Dominio limitado:** [ej. solo funciona con texto en espanol]
- **Drift:** [ej. performance degrada si datos cambian de distribucion]

## Consideraciones Eticas

| Aspecto | Evaluacion | Mitigacion |
|---------|-----------|------------|
| Fairness entre grupos | [evaluado/no evaluado] | [accion tomada] |
| Privacidad de datos | [PII removida/anonimizada] | [tecnica usada] |
| Transparencia | [explicable/caja negra] | [SHAP/LIME si aplica] |
| Impacto de errores | [bajo/medio/alto] | [fallback/human-in-loop] |

## Infraestructura

| Componente | Detalle |
|------------|---------|
| Entrenamiento | [GPU tipo, horas, costo] |
| Serving | [API/batch, instancia, latencia] |
| Almacenamiento | [S3/GCS, tamano del modelo] |
| Monitoreo | [metricas monitoreadas, alertas] |

## Proximos Pasos

- [ ] Monitorear drift en produccion
- [ ] Reentrenar con datos actualizados
- [ ] Evaluar fairness en subgrupos adicionales

---

*Generado con NXT AI Development v3.8.0*
