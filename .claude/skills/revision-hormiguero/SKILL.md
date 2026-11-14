---
name: revision-hormiguero
description: Use when reviewing a Hormiguero branch or pull request before merging. Checklist for weak tests, data isolation between users, business rules outside gastos/reglas, migrations and differences between the spec and the diff.
---

# Revisión de una rama de Hormiguero

## Cuándo usarla
Antes de abrir o aprobar un pull request. Las pruebas en verde no bastan: esta lista busca lo que las pruebas no ven.

## Antes de leer el código
```bash
git diff main...HEAD --stat
python manage.py test
python manage.py check
python manage.py makemigrations --check --dry-run
coverage run --source=gastos manage.py test
coverage report
```
Si algo falla aquí, es el primer hallazgo.

## Lista

### Pruebas
- Cada criterio de aceptación de `spec.md` tiene una prueba que lo nombra o lo cubre.
- Ninguna prueba sin aserción, ni que compruebe solo lo que ella misma preparó o solo un mock.
- Las reglas se prueban con `hoy` fijo; ninguna prueba depende del reloj sin `mock.patch`.
- Están los casos límite: el valor exacto del umbral, N y N−1 repeticiones, el día 30 y el 31, cero meses restantes, meta ya cumplida.
- En el historial, el commit `test:` va antes del `feat:` de ese código.

### Datos de cada usuario
- Toda consulta de `Gasto` o `Meta` filtra por `request.user`.
- Ver, cambiar o borrar un dato ajeno responde 404 y hay una prueba que lo demuestra.
- Los formularios no aceptan `usuario` desde el navegador.
- Toda vista del dominio tiene `login_required`; las que cambian datos, `require_POST`.

### Arquitectura
- La regla está en `gastos/reglas/` y no importa Django.
- La vista llama a la regla; no hay cálculos de negocio en la vista ni en la plantilla (sumas, comparaciones con el umbral, redondeos).
- Los montos son enteros; ningún `float` en cálculos de dinero.

### Base de datos
- No cambió ninguna migración existente; las nuevas las generó `makemigrations`.
- `db.sqlite3` y `.env` no están en el diff.

### Plantillas (si el diff las toca)
- Hereda de `base.html`, tiene `{% csrf_token %}` en cada formulario y los textos están en español.
- Aplica la skill `web-design-guidelines` a los archivos cambiados.

### Spec contra diff
- Los archivos cambiados son los del plan. Lo que sobra o falta se reporta.
- No hay dependencias nuevas sin avisar ni cambios en `requirements.txt` fuera del plan.

## Cómo se reporta
Un hallazgo por línea: `archivo:línea · severidad · qué pasa y con qué entrada · rol que corrige`. Severidad alta: datos de otro usuario, regla incorrecta o prueba que no prueba. Media: caso límite sin cubrir o diferencia con la spec. Baja: nombres, textos, estilo.

## Límites
- Quien revisa no corrige: reporta.
- Sin línea concreta no hay hallazgo; se escribe como pregunta.
