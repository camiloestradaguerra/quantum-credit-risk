# ⚛️ QUANTUM ML MODEL: QSVM con ZZFeatureMap - Documentación Física-Matemática

**Última actualización:** Mayo 2026  
**Objetivo:** Explicar en detalle la mecánica cuántica, circuitos cuánticos, feature maps, y Support Vector Machines en dominio cuántico

---

## 📋 Tabla de Contenidos

1. [Fundamentos de Mecánica Cuántica](#fundamentos-de-mecánica-cuántica)
2. [Computación Cuántica Basics](#computación-cuántica-basics)
3. [Circuitos Cuánticos y Puertas](#circuitos-cuánticos-y-puertas)
4. [ZZFeatureMap Detallado](#zzfeaturemap-detallado)
5. [QuantumKernel y QSVM](#quantumkernel-y-qsvm)
6. [Aplicación a Credit Risk](#aplicación-a-credit-risk-quantum)
7. [Ventaja Cuántica y Limitaciones](#ventaja-cuántica-y-limitaciones)

---

## Fundamentos de Mecánica Cuántica

### Qubit (Quantum Bit)

Un **qubit** es la unidad fundamental de información cuántica. A diferencia de un bit clásico (0 o 1), un qubit puede existir en **superposición**:

$$|\psi\rangle = \alpha |0\rangle + \beta |1\rangle$$

donde:
- $|0\rangle, |1\rangle$ = estados base (eigenstates)
- $\alpha, \beta \in \mathbb{C}$ = amplitudes complejas
- **Normalización:** $|\alpha|^2 + |\beta|^2 = 1$

**Interpretación física:**
- $|\alpha|^2$ = probabilidad de medir 0
- $|\beta|^2$ = probabilidad de medir 1
- La superposición permite procesamiento paralelo

### Ejemplo: Un Qubit

$$|\psi\rangle = \frac{1}{\sqrt{2}} |0\rangle + \frac{1}{\sqrt{2}} |1\rangle$$

Este es el estado **|+⟩ (plus state)**: superposi ción igual de ambos estados.

Probabilidades: $P(0) = 1/2$, $P(1) = 1/2$.

### Sistema de n Qubits

Para $n$ qubits, el espacio Hilbert tiene dimensión $2^n$:

$$|\Psi\rangle = \sum_{i=0}^{2^n-1} c_i |i\rangle$$

donde $|i\rangle$ son los $2^n$ estados base computacionales, y $\sum_i |c_i|^2 = 1$.

**Para 8 qubits:** $2^8 = 256$ amplitudes, pero el estado es descrito por solo 256 números complejos en computadora clásica simulándolo.

**Entrelazamiento:** Si no todos los $c_i$ factorizan en productos de qubits individuales, el sistema está **entrelazado** (correlacionado cuánticamente).

---

## Computación Cuántica Basics

### Puertas Cuánticas como Matrices Unitarias

Una puerta cuántica es transformación unitaria $U: \mathbb{C}^{2^n} \to \mathbb{C}^{2^n}$:

$$U^\dagger U = I \quad \text{(propiedad unitaria)}$$

#### Puertas de 1-Qubit (Pauli Matrices)

**Pauli-X (NOT gate):**

$$X = \begin{pmatrix} 0 & 1 \\ 1 & 0 \end{pmatrix}, \quad X|0\rangle = |1\rangle, \quad X|1\rangle = |0\rangle$$

**Pauli-Y:**

$$Y = \begin{pmatrix} 0 & -i \\ i & 0 \end{pmatrix}$$

**Pauli-Z:**

$$Z = \begin{pmatrix} 1 & 0 \\ 0 & -1 \end{pmatrix}, \quad Z|0\rangle = |0\rangle, \quad Z|1\rangle = -|1\rangle$$

**Hadamard (superposición):**

$$H = \frac{1}{\sqrt{2}} \begin{pmatrix} 1 & 1 \\ 1 & -1 \end{pmatrix}, \quad H|0\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$$

#### Rotaciones Paramétricas

$$R_x(\theta) = \begin{pmatrix} \cos(\theta/2) & -i\sin(\theta/2) \\ -i\sin(\theta/2) & \cos(\theta/2) \end{pmatrix}$$

$$R_y(\theta) = \begin{pmatrix} \cos(\theta/2) & -\sin(\theta/2) \\ \sin(\theta/2) & \cos(\theta/2) \end{pmatrix}$$

$$R_z(\theta) = \begin{pmatrix} e^{-i\theta/2} & 0 \\ 0 & e^{i\theta/2} \end{pmatrix}$$

Estas rotaciones son fundamentales para **feature encoding** (mapeo de datos clásicos a espacio cuántico).

#### Puertas de 2-Qubits (Entrelazamiento)

**CNOT (Controlled-X):**

$$\text{CNOT} = \begin{pmatrix} 1 & 0 & 0 & 0 \\ 0 & 1 & 0 & 0 \\ 0 & 0 & 0 & 1 \\ 0 & 0 & 1 & 0 \end{pmatrix}$$

Aplicado a sistema 2-qubit: Si qubit control es |1⟩, aplica X al qubit target.

**CZ (Controlled-Z):**

$$\text{CZ} = \begin{pmatrix} 1 & 0 & 0 & 0 \\ 0 & 1 & 0 & 0 \\ 0 & 0 & 1 & 0 \\ 0 & 0 & 0 & -1 \end{pmatrix}$$

Aplica fase -1 si ambos qubits son |1⟩.

---

## Circuitos Cuánticos y Puertas

### Representación de Circuitos

Un circuito cuántico es secuencia ordenada de puertas:

```
q[0] ────────●────────────
             │
q[1] ────────X────────────

Notación Qiskit:
qc = QuantumCircuit(2)
qc.cx(0, 1)  # CNOT: control=qubit 0, target=qubit 1
```

### Feature Encoding: Mapeando Datos Clásicos a Espacio Cuántico

El **feature map** $\Phi$ mapea punto de dato clásico $\mathbf{x} \in \mathbb{R}^d$ a estado cuántico $|\Phi(\mathbf{x})\rangle \in \mathbb{C}^{2^n}$:

$$\Phi: \mathbb{R}^d \to \mathbb{C}^{2^n}, \quad \mathbf{x} \mapsto |\Phi(\mathbf{x})\rangle = U_\Phi(\mathbf{x}) |0^n\rangle$$

donde:
- $U_\Phi(\mathbf{x})$ es circuito unitario parametrizado por $\mathbf{x}$
- $|0^n\rangle = |0\rangle^{\otimes n}$ es estado base inicial (todos los qubits en |0⟩)

---

## ZZFeatureMap Detallado

### Definición del ZZFeatureMap

El **ZZFeatureMap** en Qiskit es feature map entrelazado específicamente diseñado para datos clásicos:

$$U_{\text{ZZ}}(\mathbf{x}) = \prod_{\text{rep}=1}^{r} \left[ \prod_{i=0}^{n-1} R_z(2x_i) \cdot \prod_{i=0}^{n-2} \text{CZ}(i, i+1) \cdot R_z(2x_i x_{i+1}) \right]$$

donde:
- $r$ = número de repeticiones (reps=2 en nuestro caso)
- $n$ = número de dimensiones de entrada = número de qubits
- $x_i$ = valor de la $i$-ésima característica (normalizado a $[0, 1]$)
- $R_z(\theta)$ = rotación Z parametrizada por ángulo $\theta$
- $\text{CZ}(i, i+1)$ = puerta CZ entre qubits adyacentes

### Circuito Explícito para n=2, reps=1

```
Entrada: x = [x₀, x₁]

q[0]: ─Rz(2x₀)──●──Rz(2x₀x₁)──
               │
q[1]: ─Rz(2x₁)─Z──────────────

Paso a paso:
1. Aplicar Rz(2x₀) al qubit 0 (rotar en eje Z por 2x₀ radianes)
2. Aplicar Rz(2x₁) al qubit 1
3. Aplicar CZ entre qubit 0 y 1 (puerta entrelazante)
4. Aplicar Rz(2x₀x₁) al qubit 0 (interacción entre características)

Resultado: |ψ(x)⟩ = U_ZZ(x)|0⟩²

Con reps=2, repetir el patrón 2 veces → más expresividad.
```

### Interpretación Matemática

El ZZFeatureMap codifica:

1. **Información individual:** $R_z(2x_i)$ codifica cada característica $x_i$
2. **Interacciones lineales:** CZ entre qubits adyacentes (entrelazamiento)
3. **Interacciones cuadráticas:** $R_z(2x_i x_{i+1})$ interacción entre características adyacentes

**Por qué ZZ?** El nombre viene de que CZ y las rotaciones Z interactúan via "ZZ-coupling" (término de Hamiltonian de sistemas spin).

### Dimensionalidad del Espacio de Características

Con $n$ qubits:
- Espacio clásico: $\mathbb{R}^n$ (lineal en $n$)
- Espacio de estado cuántico: $\mathbb{C}^{2^n}$ (exponencial en $n$)

**Ventaja cuántica potencial:** Mapear $d=8$ características clásicas a espacio $\mathbb{C}^{256}$ (exponencial).

Pero **desventaja práctica:** Simulación también exponencial O(2^n) en tiempo.

---

## QuantumKernel y QSVM

### Kernel Methods: Representación Dual

En lugar de trabajar directamente con features, kernel methods trabajan con **inner products**:

$$K(\mathbf{x}_i, \mathbf{x}_j) = \langle \mathbf{x}_i | \mathbf{x}_j \rangle$$

Ventaja: No necesitamos datos explícitamente, solo kernel matrix.

### Quantum Kernel

El **quantum kernel** es inner product en espacio de estado cuántico:

$$K_Q(\mathbf{x}_i, \mathbf{x}_j) = \langle \Phi(\mathbf{x}_i) | \Phi(\mathbf{x}_j) \rangle$$

donde $|\Phi(\mathbf{x})\rangle = U_\Phi(\mathbf{x}) |0^n\rangle$.

Expandido:
$$K_Q(\mathbf{x}_i, \mathbf{x}_j) = \langle 0^n | U_\Phi^\dagger(\mathbf{x}_i) \cdot U_\Phi(\mathbf{x}_j) | 0^n \rangle$$

### Cálculo Práctico de Quantum Kernel

En computadora clásica simulando quantum:

1. **Preparar estado inicial:** $|0^n\rangle$
2. **Aplicar circuito:** $U_\Phi(\mathbf{x}_i)$ 
3. **Aplicar inverse:** $U_\Phi^\dagger(\mathbf{x}_j)$
4. **Medir probabilidad de retornar a |0^n⟩:**

$$K_Q(\mathbf{x}_i, \mathbf{x}_j) = P(\text{medición result} = 0^n) = |\langle 0^n | U_\Phi^\dagger(\mathbf{x}_i) U_\Phi(\mathbf{x}_j) | 0^n \rangle|^2$$

### Kernel Matrix

Para dataset $\{\mathbf{x}_1, \ldots, \mathbf{x}_N\}$ con $N$ muestras:

$$K = \begin{pmatrix}
K(\mathbf{x}_1, \mathbf{x}_1) & K(\mathbf{x}_1, \mathbf{x}_2) & \cdots & K(\mathbf{x}_1, \mathbf{x}_N) \\
K(\mathbf{x}_2, \mathbf{x}_1) & K(\mathbf{x}_2, \mathbf{x}_2) & \cdots & K(\mathbf{x}_2, \mathbf{x}_N) \\
\vdots & \vdots & \ddots & \vdots \\
K(\mathbf{x}_N, \mathbf{x}_1) & K(\mathbf{x}_N, \mathbf{x}_2) & \cdots & K(\mathbf{x}_N, \mathbf{x}_N)
\end{pmatrix} \in \mathbb{R}^{N \times N}$$

**Propiedades:**
- **Simétrica:** $K_{ij} = K_{ji}$
- **Semidefinida positiva:** $\mathbf{v}^T K \mathbf{v} \geq 0$ para todo $\mathbf{v}$
- **Diagonal ≤ 1:** $K_{ii} = \langle \Phi(\mathbf{x}_i) | \Phi(\mathbf{x}_i) \rangle = 1$ (si feature map es normalizado)

**Para N=5000 muestras:** Matriz 5000×5000 ≈ 100 MB (float64) o 50 MB (float32).

### Support Vector Machine (SVM) Clásico

SVM resuelve problema de optimización **cuadrático:**

$$\min_{\mathbf{w}, b, \boldsymbol{\xi}} \frac{1}{2} \mathbf{w}^T \mathbf{w} + C \sum_{i=1}^{N} \xi_i$$

sujeto a:

$$y_i (\mathbf{w}^T \phi(\mathbf{x}_i) + b) \geq 1 - \xi_i, \quad \xi_i \geq 0$$

donde:
- $\mathbf{w}$ = vector de pesos (normal al hiperplano)
- $b$ = bias
- $\xi_i$ = variables de holgura (slack variables)
- $C$ = parámetro de regularización
- $\phi(\mathbf{x}_i)$ = feature mapping

**Formulación dual (kernel trick):**

$$\min_{\boldsymbol{\alpha}} \frac{1}{2} \sum_{i,j} \alpha_i \alpha_j y_i y_j K(\mathbf{x}_i, \mathbf{x}_j) - \sum_{i} \alpha_i$$

sujeto a:

$$0 \leq \alpha_i \leq C, \quad \sum_{i} \alpha_i y_i = 0$$

donde $\boldsymbol{\alpha}$ son **coeficientes duales** (Lagrange multipliers).

### QSVM (Quantum SVM)

**Quantum SVM** usa quantum kernel en lugar de kernel clásico:

$$\min_{\boldsymbol{\alpha}} \frac{1}{2} \sum_{i,j} \alpha_i \alpha_j y_i y_j K_Q(\mathbf{x}_i, \mathbf{x}_j) - \sum_{i} \alpha_i$$

**Ventaja potencial:** Quantum kernel puede explorar espacios de feature mucho más altos (exponenciales) que kernel clásico.

**Predicción:**

$$\hat{y}(\mathbf{x}_{\text{new}}) = \text{sign}\left( \sum_{i \in SV} \alpha_i y_i K_Q(\mathbf{x}_i, \mathbf{x}_{\text{new}}) + b \right)$$

donde $SV$ son **support vectors** (muestras con $\alpha_i > 0$).

---

## Aplicación a Credit Risk (Quantum)

### Dataset en Espacio Cuántico

- **d = 8** características clásicas reducidas (via PCA desde 10 features top)
- **n = 8** qubits (mapeo 1-a-1)
- **N = 4,000 a 20,000** muestras (dependiendo de budget computacional)

### Codificación de Features en [0, 1]

Como features deben estar en $[0, 1]$ para ser ángulos en rotaciones $R_z(2x_i)$:

$$x_i' = \frac{x_i - \min(x_i)}{\max(x_i) - \min(x_i)}$$

**Ejemplo:** Si Credit_Score_normalized ∈ [0.351, 0.850], mapear a [0, 1]:

$$x_i' = \frac{\text{Credit\_Score\_normalized} - 0.351}{0.850 - 0.351} \in [0, 1]$$

### Profundidad del Circuito

Con reps=2:

$$\text{Depth} = 2 \times (n + (n-1) + 1) = 2 \times (8 + 7 + 1) = 32$$

**32 capas de puertas** para transformar 8 qubits. En hardware real:
- CNOT/CZ tienen **tiempos de coherencia de ~microsegundos**
- Circuito de profundidad 32 toma ~100 microsegundos
- **Ruido cuántico** se acumula rápidamente

**En simulación clásica:** Sin ruido, es determinístico.

### Cálculo de Kernel Matrix

Para N=5,000 muestras, necesitamos calcular:

$$K_{ij} = |\langle 0^8 | U_\Phi^\dagger(\mathbf{x}_i) U_\Phi(\mathbf{x}_j) | 0^8 \rangle|^2$$

5,000 muestras → 5,000 × 5,000 / 2 = 12.5 millones de kernels (por simetría).

**Tiempo estimado:**
- 1 kernel = ~1 ms (simulación Qiskit-Aer)
- 12.5M kernels = 12,500 segundos ≈ 3.5 horas (single thread)
- Con 4 threads: ~1 hora

**En hardware cuántico real (IBM Quantum):**
- Queue time: 1-24 horas (esperando turno)
- Execution time: ~segundos (pero con ruido)

---

## Ventaja Cuántica y Limitaciones

### Esperanza de Ventaja Cuántica (Quantum Advantage)

**Hipótesis:** Quantum kernel puede capturar estructuras en datos que kernel clásico no puede.

**Caso ideal:**
- Dataset tiene **estructura oculta en espacio exponencial** que ZZFeatureMap puede explorar
- Quantum kernel separa clases mejor que cualquier kernel clásico eficiente

**Para Credit Risk específicamente:**
- Relaciones **no-lineales complejas** entre características (ej: interacción Income × Credit_Score)
- ZZFeatureMap con 8 qubits mapea a espacio $\mathbb{C}^{256}$
- Potencial para descubrir patrones en conjunto de features bancarias

### Limitaciones Prácticas (CRÍTICO)

#### 1. **Ruido Cuántico** (en hardware real)

Puertas cuánticas no son perfectas:

$$\text{Error por puerta} \sim 0.1\% - 1\% \text{ (hardware actual)}$$

Con 32 capas × 8 qubits = ~256 puertas:

$$\text{Error acumulado} \sim 1 - (1 - 0.001)^{256} \approx 22\% \text{ por circuito}$$

Resultado: Ruido estadístico alto, kernel matrix perturbada → SVM menos confiable.

#### 2. **Barrera de NISQ** (Noisy Intermediate-Scale Quantum)

Computadoras cuánticas actuales (2026) tienen:
- **50-100 qubits** (pero muchos no funcionales)
- **Coherence time:** ~100-200 microsegundos
- **Error rates:** 0.1-1% por gate

Para aplicación real de QSVM:
- Necesitamos **200+ qubits sin ruido** o
- Corrección de errores (requiere ~1000 qubits físicos por 1 lógico)

**Conclusión:** Verdadera "ventaja cuántica" para QSVM aún está **5-10 años en el futuro**.

#### 3. **Escalabilidad Clásica de Simulación**

Simulación clásica de Aer simulator:
- Viable hasta **20-25 qubits** (con suficiente RAM)
- Exponencial en número de qubits

Para N=20,000 muestras:
- Kernel matrix: 400M elementos
- Si cada elemento toma 1 ms: 400,000 segundos = 5 días (!!)
- Chunking/paralelización ayuda, pero aún lento

#### 4. **Ventaja Cuántica No Probada para SVM**

Hasta hoy (2026):
- **No hay demostración clara** de que QSVM supera SVM clásico en datos reales
- Mayormente aplicaciones de juguete (toy problems) de <50 qubits
- Hipotetizado pero no validado empíricamente

### Posible Ventaja Cuántica Condicional

QSVM podría ganar si:

$$\text{AUC-ROC}_{\text{Quantum}} > \text{AUC-ROC}_{\text{Classical}} + 2\sigma$$

donde $2\sigma$ es significancia estadística.

En nuestro proyecto:
- Si Classical XGBoost logra AUC=0.94
- Quantum QSVM necesitaría AUC > 0.95+ para justificar complejidad
- **Escenario poco probable** (pero posible si dataset tiene structure cuántica)

---

## Resumen: Cuando Usar QSVM

### ✅ Cuándo QSVM Tiene Sentido

1. **Exploración académica:** Aprender sobre QML
2. **Investigación de ventaja:** Buscar casos donde quantum supera classical
3. **Hardware disponible:** Acceso a computadoras cuánticas en la nube
4. **Data con estructura oculta:** Sospechar structure no-lineal exponencial

### ❌ Cuándo NO Usar QSVM

1. **Producción hoy:** Ruido muy alto, resultados inconsistentes
2. **Performance crítico:** Classical ML (XGBoost) es más confiable
3. **Escalabilidad:** 20K muestras es demasiado grande para QSVM actual
4. **ROI:** Complejidad > Beneficio en la mayoría de casos

---

**Archivo creado:** `.copilot_agentic_workspace/documentation/QUANTUM_ML_MODEL.md`  
**Versión:** 1.0  
**Última actualización:** 2026-05-19
