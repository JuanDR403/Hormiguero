# Tareas 002

- [x] T1 · probador · pruebas de la vista y la página en `gastos/tests/test_vista_hormiga.py` (CA1–CA14); confirmar rojo (21 de 22 en rojo; la que pasa es una guarda de regresión, ver evidencia)
- [x] T2 · implementador-backend · vista `hormiga` en `gastos/views.py` y ruta en `gastos/urls.py` (CA1–CA9, CA11 contexto, CA14); confirmar que solo fallan las pruebas que renderizan la plantilla
- [x] T3 · implementador-frontend · plantilla `templates/gastos/hormiga.html` y enlace en `templates/base.html` (CA3, CA6, CA9–CA13 en HTML); confirmar verde de toda la suite
- [x] T4 · revisor · revisión del diff contra `main` y la spec (dos vueltas: 3 hallazgos menores en la primera y 1 en la segunda, todos corregidos; `aria-current` descartado, ver evidencia)
- [x] T5 · probador · corrección de la revisión: fijar el día en las pruebas de CA8 (hallazgo 1), afinar CA11 (hallazgo 2) y prueba en rojo de CA15 (hallazgo 3)
- [x] T6 · implementador-backend · `categoria_nombre` tolerante a códigos desconocidos (CA15, hallazgo 3)
- [x] T7 · probador · corrección de la revisión, vuelta 2: parche de `timezone.localdate` con fecha fija (hallazgo nuevo 1)
