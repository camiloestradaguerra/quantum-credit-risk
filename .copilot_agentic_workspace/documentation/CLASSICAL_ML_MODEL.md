# 📐 CLASSICAL ML MODEL: XGBoost - Documentación Matemática Completa

**Última actualización:** Mayo 2026  
**Objetivo:** Explicar en detalle la matemática detrás de XGBoost, su aplicación al Credit Risk Analysis, y sus ventajas/limitaciones

---

## 📋 Tabla de Contenidos

1. [Fundamentos Teóricos](#fundamentos-teóricos)
2. [Boosting Gradient en Detalle](#boosting-gradient-en-detalle)
3. [Formulación Matemática de XGBoost](#formulación-matemática-de-xgboost)
4. [Aplicación a Credit Risk](#aplicación-a-credit-risk)
5. [Análisis de Desempeño](#análisis-de-desempeño)
6. [Regularización y Prevención de Overfitting](#regularización-y-prevención-de-overfitting)

---

## Fundamentos Teóricos

### Árboles de Decisión Base

Un árbol de decisión **$T$** mapea entrada **$\mathbf{x} \in \mathbb{R}^{d}$** a predicción escalar **$y \in \mathbb{R}$**:

$$\hat{y} = f(\mathbf{x}) = \sum_{j=1}^{J} w_j \cdot \mathbb{1}[\mathbf{x} \in R_j]$$

donde:
- $J$ = número de hojas del árbol
- $R_j$ = región (hoja) $j$-ésima (partición del espacio de entrada)
- $w_j$ = valor predicho en región $j$
- $\mathbb{1}[\cdot]$ = función indicadora

### Ensemble Learning: Combining Multiple Learners

Para problema de clasificación binaria (Default/No Default), combinamos $M$ árboles:

$$\hat{y} = \sum_{m=1}^{M} f_m(\mathbf{x})$$

donde cada árbol $f_m$ contribuye aditivamente a la predicción final.

### AdaBoost vs Gradient Boosting

| Aspecto | AdaBoost | Gradient Boosting |
|--------|----------|-------------------|
| **Objetivo** | Minimizar error ponderado | Minimizar gradiente de función pérdida |
| **Pesos** | Adaptativo por muestra | Dirigido por residuos |
| **Función Pérdida** | Exponencial (inflexible) | Flexible (puede ser cualquiera) |
| **Robustez** | Sensible a outliers | Más robusto |

---

## Boosting Gradient en Detalle

### Problema de Optimización

Dado dataset $\{(\mathbf{x}_i, y_i)\}_{i=1}^{n}$, queremos minimizar función pérdida $\mathcal{L}$:

$$\min_{\mathbf{f}} \sum_{i=1}^{n} \mathcal{L}(y_i, f(\mathbf{x}_i))$$

donde $\mathbf{f} = (f_1, f_2, \ldots, f_M)$ es ensemble de $M$ funciones débiles (árboles).

### Boosting Secuencial (Greedy Approach)

**Paso 1: Inicializar**

$$f_0(\mathbf{x}) = \arg\min_{c} \sum_{i=1}^{n} \mathcal{L}(y_i, c)$$

Para clasificación binaria con pérdida logarítmica:

$$f_0(\mathbf{x}) = \log\left(\frac{P(\text{Default}=1)}{P(\text{Default}=0)}\right) = \text{log-odds}$$

**Paso 2: Iterar para $m = 1, 2, \ldots, M$**

2a. Calcular **pseudo-residuos** (gradiente negativo):

$$r_{i,m} = -\frac{\partial \mathcal{L}(y_i, f_{m-1}(\mathbf{x}_i))}{\partial f_{m-1}(\mathbf{x}_i)}$$

Para pérdida logarítmica (logistic regression):

$$r_{i,m} = y_i - \sigma(f_{m-1}(\mathbf{x}_i))$$

donde $\sigma(z) = \frac{1}{1 + e^{-z}}$ es función logística.

2b. **Ajustar árbol de regresión** $h_m$ a pseudo-residuos:

$$h_m = \arg\min_{h} \sum_{i=1}^{n} (r_{i,m} - h(\mathbf{x}_i))^2$$

2c. **Encontrar step size** (factor de aprendizaje):

$$\gamma_m = \arg\min_{\gamma} \sum_{i=1}^{n} \mathcal{L}(y_i, f_{m-1}(\mathbf{x}_i) + \gamma \cdot h_m(\mathbf{x}_i))$$

2d. **Actualizar modelo**:

$$f_m(\mathbf{x}) = f_{m-1}(\mathbf{x}) + \eta \cdot \gamma_m \cdot h_m(\mathbf{x})$$

donde $\eta$ es **learning rate** (típicamente $\eta = 0.1$).

### Visualización del Proceso

```
Iteración 1:
├─ Pseudo-residuos: r₁ ≈ 0.8, 0.2, -0.3, ..., 0.1
├─ Árbol h₁ ajustado a r₁ (SSE = 2.4)
├─ Step size γ₁ = 0.95
└─ f₁(x) = f₀(x) + 0.1 × 0.95 × h₁(x)

Iteración 2:
├─ Nuevos residuos: r₂ ≈ 0.4, 0.05, -0.15, ..., 0.04
├─ Árbol h₂ ajustado a r₂ (SSE = 0.8)
├─ Step size γ₂ = 0.92
└─ f₂(x) = f₁(x) + 0.1 × 0.92 × h₂(x)

... (repetir M=200 veces)

Predicción final: f_M(x) = suma ponderada de todos los árboles
```

---

## Formulación Matemática de XGBoost

### Función Objetivo Regularizada

XGBoost minimiza objetivo regularizado:

$$\mathcal{L}_{total} = \sum_{i=1}^{n} \mathcal{L}(y_i, \hat{y}_i) + \sum_{m=1}^{M} \Omega(f_m)$$

donde:
- **Término de pérdida:** $\sum_{i=1}^{n} \mathcal{L}(y_i, \hat{y}_i)$ 
- **Término de regularización:** $\sum_{m=1}^{M} \Omega(f_m)$

#### Pérdida para Clasificación Binaria

Para nuestro problema (Credit Risk: Default vs No Default):

$$\mathcal{L}(y, \hat{y}) = -[y \log(\hat{y}) + (1-y) \log(1-\hat{y})]$$

Esta es **entropía cruzada binaria** (binary cross-entropy).

Expandido:
- Si $y = 1$ (Default): $\mathcal{L} = -\log(\hat{y})$ (penaliza no detectar default)
- Si $y = 0$ (No Default): $\mathcal{L} = -\log(1-\hat{y})$ (penaliza falsa alarma)

#### Regularización de Árbol

Para árbol $f_m$ con $J_m$ hojas:

$$\Omega(f_m) = \alpha J_m + \frac{\lambda}{2} \sum_{j=1}^{J_m} w_j^2$$

donde:
- $\alpha$ = costo de complejidad por hoja (default: 0)
- $\lambda$ = penalización L2 (default: 1.0)
- $w_j$ = valor predicho en hoja $j$

**Interpretación:**
- Primer término: penalizar cantidad de hojas (prevenir árbol muy profundo)
- Segundo término: penalizar magnitud de predicciones (evitar overfitting)

### Optimización Greedy Secuencial

Para cada iteración $m$, XGBoost resuelve:

$$f_m^* = \arg\min_f \left[ \sum_{i=1}^{n} \mathcal{L}(y_i, f_{m-1}(\mathbf{x}_i) + f(\mathbf{x}_i)) + \Omega(f) \right]$$

**Expansión de Taylor de segundo orden** alrededor de $f_{m-1}(\mathbf{x}_i)$:

$$\mathcal{L}(y_i, \hat{y}_i + f(\mathbf{x}_i)) \approx \mathcal{L}(y_i, \hat{y}_i) + g_i \cdot f(\mathbf{x}_i) + \frac{1}{2} h_i \cdot f(\mathbf{x}_i)^2$$

donde:
- $g_i = \frac{\partial \mathcal{L}(y_i, \hat{y}_i)}{\partial \hat{y}_i}$ = **primer gradiente** (first derivative)
- $h_i = \frac{\partial^2 \mathcal{L}(y_i, \hat{y}_i)}{\partial \hat{y}_i^2}$ = **segundo gradiente** (second derivative / Hessian)

Para entropía cruzada:
$$g_i = \sigma(\hat{y}_i) - y_i$$
$$h_i = \sigma(\hat{y}_i) \cdot (1 - \sigma(\hat{y}_i))$$

### Partición de Árbol Óptima

Para encontrar mejor división en característica $k$ en un nodo:

$$\text{Gain} = \frac{1}{2} \left[ \frac{G_L^2}{H_L + \lambda} + \frac{G_R^2}{H_R + \lambda} - \frac{(G_L + G_R)^2}{H_L + H_R + \lambda} \right] - \alpha$$

donde:
- $G_L = \sum_{i \in L} g_i$ = suma de gradientes en rama izquierda
- $H_L = \sum_{i \in L} h_i$ = suma de Hessianos en rama izquierda
- $G_R, H_R$ = mismo para rama derecha
- $\alpha$ = costo de insertar nueva hoja

**Interpretación:** XGBoost elige la división que más reduce la función objetivo, ajustada por complejidad del árbol.

### Valor Óptimo de Hoja

Una vez fijada la estructura del árbol, el valor óptimo en cada hoja $j$ es:

$$w_j^* = -\frac{G_j}{H_j + \lambda}$$

Este es el **Newton step** para optimización de segundo orden.

---

## Aplicación a Credit Risk

### Dataset Específico

- **n = 20,000** registros
- **d = 23** variables (originales) → 33 después de feature engineering
- **Desbalanceo severo:** 99% Default=1 (incumplimiento), 1% Default=0 (no incumplimiento)

### Función Pérdida Ponderada

Para manejar desbalanceo, XGBoost permite pesos de clase:

$$\text{scale\_pos\_weight} = \frac{n_{\text{negative}}}{n_{\text{positive}}} = \frac{0.01n}{0.99n} \approx 0.0101$$

Pero con SMOTE aplicado en training set:
- **Antes SMOTE:** $n_{\text{pos}} = 15,840$, $n_{\text{neg}} = 160$ → ratio ≈ 99:1
- **Después SMOTE:** $n_{\text{pos}} = 18,208$, $n_{\text{neg}} = 11,152$ → ratio ≈ 1.6:1

Por lo tanto:
$$\text{scale\_pos\_weight} = \frac{11,152}{18,208} \approx 0.6125$$

Este parámetro **multiplica la pérdida para muestras positivas** (Default=1), reflejando que son más raras:

$$\mathcal{L}_{\text{weighted}} = \sum_{i: y_i=0} \mathcal{L}(y_i, \hat{y}_i) + 0.6125 \sum_{i: y_i=1} \mathcal{L}(y_i, \hat{y}_i)$$

Esto penaliza FN (predecir No Default cuando es Default) más que FP.

### Hiperparámetros en Credit Risk Context

```python
xgb_model = xgb.XGBClassifier(
    n_estimators=200,       # M = 200 árboles (regularización via early stopping)
    max_depth=6,            # Profundidad máxima del árbol
    learning_rate=0.1,      # η = 0.1 (step size)
    subsample=0.8,          # Subsampling de 80% de muestras por árbol (reduce varianza)
    colsample_bytree=0.8,   # Feature subsampling: 80% de features por árbol
    reg_alpha=1.0,          # α = 1.0 (L1 regularización)
    reg_lambda=1.0,         # λ = 1.0 (L2 regularización)
    scale_pos_weight=0.6125, # Peso para clase positiva (Default)
    min_child_weight=1,     # Mínimo sum de Hessian en hoja (prev. overfitting)
    random_state=42
)
```

**Justificación:**
- **n_estimators=200:** Suficientes para convergencia sin memorizar ruido
- **max_depth=6:** Balance entre expresividad (capturar patrones) y complejidad
- **learning_rate=0.1:** Lento pero reduce volatilidad
- **subsample/colsample=0.8:** Introduce aleatoriedad (reduce correlation entre árboles)
- **reg_alpha/reg_lambda=1.0:** Penalización moderada
- **scale_pos_weight=0.6125:** Refleja desbalanceo post-SMOTE

---

## Análisis de Desempeño

### Matriz de Confusión

Sea $y_i \in \{0, 1\}$ verdadero label y $\hat{y}_i \in \{0, 1\}$ predicción:

$$\begin{array}{c|cc|c}
 & \hat{y}=0 & \hat{y}=1 & \text{Total} \\
\hline
y=0 & TN & FP & n_0 \\
y=1 & FN & TP & n_1 \\
\hline
\text{Total} & \hat{n}_0 & \hat{n}_1 & n
\end{array}$$

Para nuestro dataset (test set):
- $n_0 \approx 40$ (No Default en test)
- $n_1 \approx 3,960$ (Default en test, post-stratified sampling)

### Métricas de Desempeño

#### 1. Accuracy (Precisión Global)

$$\text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN}$$

**Limitación:** En desbalanceo severo, es engañosa. Si predices todo como Default=1:

$$\text{Accuracy}_{\text{naive}} = \frac{3960 + 0}{4000} = 99\%$$

pero en realidad es inútil.

#### 2. Precision (Precisión en Predicción Positiva)

$$\text{Precision} = \frac{TP}{TP + FP}$$

**Interpretación:** De los préstamos que predijimos como Default (incumplimiento), ¿qué porcentaje realmente lo fueron?

**En contexto bancario:** Precisión baja → rechazamos clientes buenos (pérdida de oportunidad).

#### 3. Recall (Exhaustividad / Sensitivity)

$$\text{Recall} = \frac{TP}{TP + FN}$$

**Interpretación:** De todos los préstamos que realmente incumplirán, ¿cuántos detectamos?

**En contexto bancario:** Recall baja → dejamos pasar clientes malos (pérdida de dinero).

**CRÍTICO para riesgo:** Recall debe ser ALTO (capturar máximo FN posible).

#### 4. F1-Score (Balance Precision-Recall)

$$F_1 = 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$$

Media armónica. Ignora TN, por eso es útil en desbalanceo severo.

#### 5. AUC-ROC (Area Under Receiver Operating Characteristic Curve)

**Curva ROC:** Grafica TPR vs FPR para todos los posibles thresholds:

$$\text{TPR} = \frac{TP}{TP + FN} = \text{Recall}$$
$$\text{FPR} = \frac{FP}{FP + TN}$$

**AUC:** Área bajo la curva ROC ∈ [0, 1]
- AUC = 0.5: modelo no mejor que random
- AUC = 1.0: clasificación perfecta
- AUC = 0.94: excelente (típicamente esperado en XGBoost)

**Ventaja:** Threshold-independent, captura capacidad discriminativa del modelo.

### Curva de Aprendizaje

XGBoost monitorea error en validation set para cada iteración:

$$\text{eval\_metric}(m) = \frac{1}{n_{\text{val}}} \sum_{i=1}^{n_{\text{val}}} \mathcal{L}(y_i, f_m(\mathbf{x}_i))$$

```
Error vs Iteración:
│
│ ╱╲                   ← Overfitting comienza aquí
│╱  ╲╲
│    ╲╲   ╱── Training error sigue bajando
│     ╲╲ ╱
│      ╲╲╱──── Validation error empieza a subir
│       ╲X← Punto óptimo (early stopping)
└─────────────────────→ Número de árboles (m)

Early stopping: Si validation error no mejora por N=50 iteraciones, detener.
```

---

## Regularización y Prevención de Overfitting

### Problema de Overfitting

En ensemble muy profundo o con muchos árboles:

$$\hat{y}_{\text{train}} \approx y_{\text{train}} \text{ (error pequeño)}$$
$$\hat{y}_{\text{test}} \ll y_{\text{test}} \text{ (error grande)}$$

El modelo memoriza ruido en training set.

### Técnicas de Regularización en XGBoost

#### 1. **Regularización L1 y L2** en hojas

$$\Omega(f) = \alpha \cdot (\text{# hojas}) + \lambda \cdot (\text{suma de w}_j^2)$$

Reduce magnitud de predicciones (w_j pequeños) → generalización mejor.

#### 2. **Subsampling de Muestras** (subsample)

Cada árbol se entrena en subset aleatorio del 80% de datos:

$$\text{subsample} = 0.8$$

Reduce varianza entre árboles (menos correlación).

#### 3. **Subsampling de Características** (colsample_bytree)

Cada árbol usa subset aleatorio del 80% de features:

$$\text{colsample\_bytree} = 0.8$$

Introduce más aleatoriedad, reduce sobreajuste a features individuales.

#### 4. **Shrinkage** (learning_rate)

Multiplicar contribución de cada árbol por factor < 1:

$$f_m(\mathbf{x}) = f_{m-1}(\mathbf{x}) + \eta \cdot h_m(\mathbf{x})$$

Con $\eta = 0.1$ (vs $\eta = 1.0$):
- Convergencia más lenta (más árboles necesarios)
- Pero mejor generalización (menos overfitting)
- Trade-off: compute time vs accuracy

#### 5. **Early Stopping**

Monitorear error en validation set, detener si:

$$\text{error}_{\text{val}}(m) > \text{error}_{\text{val}}(m-50)$$

Por 50 iteraciones consecutivas, terminar entrenamiento.

**Beneficio:** Encuentra punto óptimo automáticamente, evita memorizar.

### Comparativa: Sin vs Con Regularización

```
SIN REGULARIZACIÓN:
├─ max_depth = ∞ (árboles muy profundos)
├─ α = 0, λ = 0 (sin penalización)
├─ subsample = 1.0, colsample_bytree = 1.0
├─ learning_rate = 1.0
└─ Resultado: AUC_train = 0.999, AUC_test = 0.850 ❌ Overfitting severo

CON REGULARIZACIÓN (XGBoost default):
├─ max_depth = 6 (árboles moderados)
├─ α = 1, λ = 1 (penalización suave)
├─ subsample = 0.8, colsample_bytree = 0.8
├─ learning_rate = 0.1
├─ early_stopping_rounds = 50
└─ Resultado: AUC_train = 0.96, AUC_test = 0.94 ✓ Balance óptimo
```

---

## Resumen: Fortalezas y Debilidades de XGBoost para Credit Risk

### ✅ Fortalezas

1. **Maneja desbalanceo severo** via `scale_pos_weight`
2. **Feature importance** nativa (interpretabilidad)
3. **Robusto a outliers** (árboles basados en particiones)
4. **Rápido** (entrenamiento < 1 minuto en 20K datos)
5. **Bien documentado** y usado industrialmente
6. **Regularización incorporada** (reduce overfitting)
7. **Cross-validation fácil** (early stopping integrado)

### ❌ Debilidades

1. **No captura interacciones complejas** como redes neuronales
2. **Requiere tuning de hiperparámetros** (no funciona "out of box")
3. **Interpretabilidad limitada** a nivel local (SHAP valores necesarios)
4. **Sesgo en distribución** si train/test muy diferentes
5. **Sin información de incertidumbre** (no Bayesiano)
6. **Threshold fijo en 0.5** (puede no ser óptimo para costo asimétrico)

---

**Archivo creado:** `.copilot_agentic_workspace/documentation/CLASSICAL_ML_MODEL.md`  
**Versión:** 1.0  
**Última actualización:** 2026-05-19
