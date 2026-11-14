---
name: sdd-hormiguero
description: Use when starting or continuing a feature in Hormiguero with spec-driven development. Defines the folder, the three files (spec, plan, tasks), the evidence file and the branch and commit order for each spec.
---

# Desarrollo guiado por especificaciones en Hormiguero

## Cuándo usarla
Al empezar una funcionalidad nueva o al retomar una spec a medias. No usamos Spec Kit: esta es la estructura propia del proyecto.

## Carpeta
Cada spec vive en `specs/NNN-tema/`, con `NNN` de tres dígitos y consecutivo (`001-gasto-hormiga`). Contiene cuatro archivos.

### `spec.md` · qué y por qué
```markdown
# Spec NNN · Título

## Problema
Qué necesita el usuario y por qué. Dos o tres frases.

## Alcance
- Incluye: ...
- No incluye: ...

## Criterios de aceptación
- CA1. Dado ..., cuando ..., entonces ...
- CA2. ...

## Decisiones tomadas
Las que respondió el desarrollador, con su respuesta.
```
Cada criterio se puede comprobar con una prueba. «Funciona bien» no es un criterio; «con 3 compras de 4.000 en 30 días se marca como hormiga» sí.

### `plan.md` · cómo
```markdown
# Plan NNN · Título

## Decisiones técnicas
Regla pura, modelo, vista, URL, plantilla. Qué se reutiliza.

## Archivos
- Nuevos: ...
- Modificados: ...
- No se tocan: ...

## Pruebas
| Prueba | Criterio | Comprueba |

## Verificación
Comandos y resultado esperado.
```

### `tareas.md` · pasos
```markdown
# Tareas NNN

- [ ] T1 · probador · pruebas de la regla (CA1, CA2)
- [ ] T2 · implementador-backend · regla en gastos/reglas/
- [ ] T3 · implementador-frontend · plantilla
- [ ] T4 · revisor · revisión del diff
```
Cada tarea nombra el rol que la hace y los criterios que cubre. Se marca `[x]` solo cuando hay evidencia.

### `evidencia.md` · lo que pasó
Salida de las pruebas en rojo, salida en verde, hallazgos del revisor con lo que se hizo con cada uno, y enlace al pull request. Se copia la salida real; no se resume ni se escribe de memoria.

## Orden de trabajo
1. Spec, plan y tareas. El desarrollador los aprueba antes de escribir código.
2. Rama `feat/<tema>` desde `main` actualizado. Una rama y un pull request por spec.
3. Commits en este orden, para que el TDD se vea en el historial:
   1. `docs: spec NNN <tema>`
   2. `test: ...` (pruebas en rojo)
   3. `feat: ...` (código en verde; uno por backend y otro por frontend)
   4. `fix: ...` si la revisión pidió cambios
   5. `docs: evidencia de la spec NNN`
4. El desarrollador hace el push y abre el pull request. Otro integrante lo revisa. Se fusiona con CI en verde.

## Límites
- La spec no cambia a escondidas: si al implementar cambia el alcance, se edita `spec.md` y se anota el motivo en `evidencia.md`.
- No se marca una tarea sin su evidencia.
- No se empieza la spec siguiente con la anterior sin fusionar, salvo que no dependan entre sí.
