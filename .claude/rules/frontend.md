---
paths:
  - "templates/**/*.html"
  - "static/**/*"
---

# Frontend

- Las plantillas del dominio heredan de `templates/base.html` y solo muestran los datos de la vista: sin sumas, sin comparaciones con el umbral, sin redondeos.
- Todo formulario lleva `{% csrf_token %}`. Lo que cambia datos va por POST.
- Los campos de formulario reutilizan `templates/autenticacion/_campo.html`.
- Textos en español. Montos con `floatformat:"0g"`.
- Un solo `<h1>` por página, `<th scope="col">` en las tablas, foco visible y `aria-label` en los botones que se repiten por fila.
- JavaScript sencillo en `static/`, sin frameworks ni dependencias. La página funciona sin JavaScript.
- Lista y formulario en la misma página; no hay pantallas de edición.
