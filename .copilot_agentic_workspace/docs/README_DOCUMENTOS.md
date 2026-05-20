# Documentos LaTeX Educativos
## Material de Estudio para Equipos del Banco

Dos documentos detallados y accesibles que explican los algoritmos de análisis de riesgo crediticio sin necesidad de expertise avanzada.

---

## 📄 Documentos

### 1. **XGBoost_Explicativo.tex**
**Título:** XGBoost para Análisis de Riesgo Crediticio - Guía Explicativa Paso a Paso

**Contenido:**
- ✓ Conceptos fundamentales (árboles de decisión)
- ✓ El truco de XGBoost (múltiples árboles débiles)
- ✓ Flujo de datos paso a paso
- ✓ Normalización de datos
- ✓ Ingeniería de características
- ✓ Ejemplo numérico completo (Cliente de Alto Riesgo)
- ✓ Métricas de desempeño
- ✓ Umbral óptimo (11.6%)
- ✓ Ventajas del modelo
- ✓ Glosario de términos

**Público objetivo:** Personal del banco sin expertise en ML  
**Nivel:** Principiante  
**Páginas:** ~15

---

### 2. **QSVM_Cuantico_Explicativo.tex**
**Título:** QSVM Cuántico para Análisis de Riesgo Crediticio - Guía Didáctica Completa

**Contenido:**
- ✓ Introducción a computación cuántica (analogías claras)
- ✓ **PARTE 1: PCA Completo**
  - ¿Qué es PCA?
  - Cómo funciona matemáticamente (simplificado)
  - Reducción de 18 → 8 dimensiones
  - Interpretación de componentes principales

- ✓ **PARTE 2: Computación Cuántica**
  - ¿Qué es un qubit?
  - Superposición y poder exponencial
  - Circuitos cuánticos (ZZFeatureMap)
  - Profundidad del circuito

- ✓ **PARTE 3: Matriz de Kernel Cuántico**
  - Concepto de kernel (similitud)
  - Fidelidad cuántica
  - Construcción de K_train y K_test
  - Ventaja cuántica en separabilidad

- ✓ **PARTE 4: SVM**
  - ¿Qué es SVM?
  - SVM con kernel cuántico
  - Support vectors

- ✓ **PARTE 5: Ejemplo Completo**
  - Flujo de datos completo
  - Paso a paso con números reales
  - Decisión final

- ✓ **PARTE 6: Cliente de Alto Riesgo**
  - Comparación con cliente de bajo riesgo

- ✓ Desempeño del modelo
- ✓ Comparación XGBoost vs QSVM
- ✓ Glosario completo

**Público objetivo:** Personal del banco interesado en ML cuántico  
**Nivel:** Principiante (sin conocimiento previo de cuántica)  
**Páginas:** ~25

---

## 🔨 Cómo Compilar

### Opción 1: TeX Live (Windows)

**Instalar:**
```powershell
# Descargar TeX Live desde:
# https://mirror.ctan.org/systems/texlive/tlnet/install-tl-windows.exe

# O si tienes chocolatey:
choco install texlive
```

**Compilar:**
```powershell
cd docs

# XGBoost
pdflatex XGBoost_Explicativo.tex
pdflatex XGBoost_Explicativo.tex  # Ejecutar dos veces para referencias

# QSVM
pdflatex QSVM_Cuantico_Explicativo.tex
pdflatex QSVM_Cuantico_Explicativo.tex
```

### Opción 2: Overleaf Online (Recomendado)

1. Ir a https://www.overleaf.com
2. Crear proyecto nuevo
3. Copiar contenido del archivo .tex
4. Compilar automáticamente
5. Descargar PDF

### Opción 3: VS Code + LaTeX Extension

1. Instalar extensión: "LaTeX Workshop" (James Yu)
2. Abrir archivo .tex
3. Presionar `Ctrl+Shift+P` → "LaTeX: Build"
4. Ver PDF en preview

---

## 📊 Estructura de Cada Documento

Ambos documentos siguen estructura similar:

```
1. Portada
2. Abstract (Resumen)
3. Tabla de Contenidos
4. Secciones temáticas
   - Introducción
   - Conceptos fundamentales
   - Teoría
   - Ejemplos numéricos
   - Métricas
5. Conclusión
6. Glosario
7. Apéndices (si aplica)
```

---

## 🎯 Cómo Usar Estos Documentos

### Para Capacitación
1. **Sesión 1:** Distribuir XGBoost_Explicativo.tex
   - Leer Secciones 1-3 (30 min)
   - Discutir ejemplos (15 min)

2. **Sesión 2:** Distribuir QSVM_Cuantico_Explicativo.tex
   - Leer Secciones 1-2 sobre PCA (30 min)
   - Leer Secciones 3-4 sobre cuántica (30 min)
   - Leer Sección 5 ejemplo completo (20 min)

### Para Auto-Estudio
- Leer a propio ritmo
- Usar glosario si hay términos desconocidos
- Revisar ejemplos numéricos
- Hacer preguntas al equipo técnico

### Para Presentaciones
- Usar diagramas del documento en PowerPoint
- Mostrar ejemplos numéricos a stakeholders
- Destacar métricas de desempeño

---

## 📋 Contenido de Ejemplos

### XGBoost Document
- **Cliente 1:** Perfil de bajo riesgo (35 años, $50k ingreso)
- **Cliente 3:** Perfil de alto riesgo (45 años, $25k ingreso, historial de impago)

### QSVM Document
- **Cliente 1:** Mismos datos que XGBoost para comparación
- **Cliente 3:** Mismo cliente para ver diferentes perspectivas

---

## 🔍 Características Especiales

### XGBoost Document
- ✓ Diagrama de árbol de decisión
- ✓ Tabla de características ingenierizadas
- ✓ Matriz de costo-beneficio
- ✓ Gráfico de umbral óptimo conceptual

### QSVM Document
- ✓ Analogías accesibles (moneda girando, bibliotecas)
- ✓ Diagramas de circuitos cuánticos (simplificados)
- ✓ Tablas de varianza explicada por componentes PCA
- ✓ Matrices de kernel ejemplares
- ✓ Tabla comparativa XGBoost vs QSVM

---

## 🛠️ Personalizando los Documentos

### Cambiar Institución
Buscar y reemplazar:
```latex
\author{Material Educativo - Departamento de Riesgo}
```

Por:
```latex
\author{Material Educativo - Banco XYZ - Departamento de Riesgo}
```

### Agregar Logos
Después de `\maketitle`:
```latex
\vspace{1cm}
\includegraphics[width=3cm]{logo_banco.png}
```

### Cambiar Colores
En el preámbulo:
```latex
\definecolor{bancocolor}{RGB}{0, 51, 102}  % Azul
```

---

## ✅ Checklist de Compilación

- [ ] LaTeX instalado (o Overleaf cuenta)
- [ ] Archivo .tex descargado
- [ ] Verificar caracteres especiales (ñ, acentos) se ven correctamente
- [ ] Tabla de contenidos generada
- [ ] Glosario aparece al final
- [ ] Todos los ejemplos son legibles
- [ ] PDF generado sin errores
- [ ] Hipervínculos funcionan

---

## 📞 Soporte

Si hay problemas con compilación:

1. **Error: "Missing package"**
   - Instalar package faltante o usar Overleaf

2. **Error: "Encoding"**
   - Verificar que archivo está en UTF-8
   - Usar `\usepackage[utf-8]{inputenc}`

3. **PDF no se genera**
   - Verificar sintaxis LaTeX
   - Ver línea específica del error
   - Buscar el error en Google + "LaTeX"

---

## 📚 Recursos Adicionales

- **LaTeX Tutorial:** https://www.overleaf.com/learn
- **Qiskit (Computación Cuántica):** https://qiskit.org
- **Scikit-Learn (ML):** https://scikit-learn.org
- **XGBoost Docs:** https://xgboost.readthedocs.io

---

**Versión:** 1.0  
**Última Actualización:** Mayo 20, 2026  
**Formato:** LaTeX + PDF  
**Licencia:** Uso interno - Banco

