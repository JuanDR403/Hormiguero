# Hormiguero

Gestor de gastos personales con detección de gasto hormiga y metas de ahorro.

## Estructura
- `gastos/`: backend (modelos, vistas, reglas de negocio y pruebas)
- `templates/` y `static/`: frontend
- `config/`: configuración de Django

## Instalación
```bash
python -m venv .venv
source .venv/bin/activate        # fish: source .venv/bin/activate.fish
                                 # PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
Abrir http://127.0.0.1:8000

## Pruebas
```bash
python manage.py test
```