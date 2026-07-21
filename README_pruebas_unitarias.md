# Pruebas Unitarias — ProyectoSoftwareFinal

## ¿Qué son las pruebas unitarias?

Las pruebas unitarias verifican el comportamiento de una **unidad mínima de código** (un modelo, un formulario o una vista) de forma **aislada**, sin depender de sistemas externos ni de otras partes de la aplicación.

En este proyecto se usan las herramientas integradas de Django:

- `django.test.TestCase` — clase base que levanta una base de datos en memoria para cada prueba y la destruye al terminar. Nunca toca `db.sqlite3`.
- `self.client` — cliente HTTP de pruebas que simula peticiones GET/POST sin necesitar un servidor real.
- `unittest.mock.patch` — reemplaza temporalmente una función real por un objeto controlado para aislar comportamientos.

---

## Estructura de los archivos de prueba

```
Modelo/
    ModeloLaboratorio/Laboratorios/tests.py   ← modelos + formularios de Laboratorio
    ModeloMedicamentos/Medicamentos/tests.py  ← modelos + formularios de Medicamento
    ModeloFarmacia/Farmacias/tests.py         ← modelos + formularios de Farmacia
    ModeloUsuario/Perfiles/tests.py           ← modelo de Usuario (auth de Django)
Controlador/
    tests.py                                  ← todas las vistas/controladores
```

---

## Capa 1 — Pruebas de Modelos

Verifican que los modelos se crean correctamente, sus relaciones funcionan y sus métodos retornan los valores esperados.

### `LaboratorioModelTest`

| Test | Qué verifica |
|------|-------------|
| `test_crear_laboratorio` | Se crea con `nombre` y `direccion` correctos |
| `test_str_laboratorio` | `__str__` retorna el nombre |
| `test_nombre_max_length` | `max_length` del campo `nombre` es 100 |
| `test_direccion_max_length` | `max_length` del campo `direccion` es 100 |
| `test_laboratorio_persiste_en_bd` | El objeto existe en la BD tras ser creado |
| `test_crear_multiples_laboratorios` | Múltiples laboratorios coexisten sin conflicto |

### `MedicamentoModelTest`

| Test | Qué verifica |
|------|-------------|
| `test_crear_medicamento` | Se crea con todos sus campos correctamente |
| `test_str_medicamento` | `__str__` retorna `"NombreComercial (NombreLab)"` |
| `test_cascade_delete` | Al borrar el laboratorio, el medicamento se elimina (`on_delete=CASCADE`) |
| `test_ordenamiento_default` | `Medicamento.objects.all()` viene ordenado por `nombre_comercial` |
| `test_nombre_comercial_max_length` | `max_length` del campo es 100 |
| `test_medicamento_persiste_en_bd` | El objeto existe en la BD tras ser creado |
| `test_laboratorio_fk` | El campo `laboratorio` es una `ForeignKey` al modelo `Laboratorios` |

### `FarmaciaModelTest`

| Test | Qué verifica |
|------|-------------|
| `test_crear_farmacia` | Se crea con `nombre` y `direccion` correctos |
| `test_str_farmacia` | `__str__` retorna el nombre |
| `test_relacion_many_to_many_un_laboratorio` | Puede asociarse con un laboratorio |
| `test_relacion_many_to_many_multiples_laboratorios` | Puede asociarse con varios laboratorios |
| `test_farmacia_sin_laboratorios` | Puede existir sin laboratorios asignados |
| `test_relacion_inversa_laboratorio_farmacias` | Desde un laboratorio se accede a sus farmacias via `related_name='farmacias'` |
| `test_nombre_max_length` | `max_length` del campo es 100 |
| `test_farmacia_persiste_en_bd` | El objeto existe en la BD tras ser creado |

### `UsuarioModelTest`

Usa el modelo `User` estándar de Django (`django.contrib.auth`).

| Test | Qué verifica |
|------|-------------|
| `test_crear_usuario` | Se crea con `username` correcto y contraseña válida |
| `test_contrasena_hasheada` | La contraseña se almacena hasheada, no en texto plano |
| `test_usuario_persiste_en_bd` | El objeto existe en la BD tras ser creado |
| `test_username_unico` | Crear dos usuarios con el mismo `username` lanza `IntegrityError` |
| `test_str_usuario` | `__str__` retorna el `username` |
| `test_usuario_activo_por_defecto` | `is_active=True` tras `create_user()` |
| `test_usuario_no_es_staff_por_defecto` | `is_staff=False` tras `create_user()` |

---

## Capa 2 — Pruebas de Formularios

Verifican la lógica de validación de los `ModelForm`. Se prueban tanto datos válidos como inválidos, y la persistencia en base de datos.

### `NuevoLaboratorioFormTest`

| Test | Qué verifica |
|------|-------------|
| `test_form_valido` | Válido con nombre y dirección |
| `test_form_nombre_vacio` | Inválido si `nombre` está vacío |
| `test_form_direccion_vacia` | Inválido si `direccion` está vacía |
| `test_form_ambos_campos_vacios` | Inválido si ambos campos están vacíos (2 errores) |
| `test_form_nombre_excede_longitud` | Inválido si `nombre` supera 200 caracteres |
| `test_form_direccion_excede_longitud` | Inválido si `direccion` supera 200 caracteres |
| `test_form_guarda_instancia` | `form.save()` crea un registro en la BD |
| `test_form_actualiza_instancia` | `form.save(instance=obj)` actualiza el registro existente |

### `MedicamentoFormTest`

| Test | Qué verifica |
|------|-------------|
| `test_form_valido` | Válido con todos los campos completos |
| `test_form_sin_nombre_comercial` | Inválido si falta `nombre_comercial` |
| `test_form_sin_nombre_farmacologico` | Inválido si falta `nombre_farmacologico` |
| `test_form_sin_componentes` | Inválido si falta `componentes` |
| `test_form_sin_laboratorio` | Inválido si no se selecciona laboratorio |
| `test_form_laboratorio_inexistente` | Inválido si el laboratorio no existe en la BD |
| `test_form_nombre_comercial_max_length` | Inválido si `nombre_comercial` supera 100 caracteres |
| `test_form_guarda_instancia` | `form.save()` crea un registro en la BD |
| `test_form_actualiza_instancia` | `form.save(instance=obj)` actualiza el registro existente |

### `FarmaciaFormTest`

| Test | Qué verifica |
|------|-------------|
| `test_form_valido_con_laboratorio` | Válido con nombre, dirección y laboratorio |
| `test_form_valido_sin_laboratorios` | El campo `laboratorios` **es requerido** (Django lo exige aunque sea M2M) |
| `test_form_valido_multiples_laboratorios` | Válido con múltiples laboratorios seleccionados |
| `test_form_sin_nombre` | Inválido si falta `nombre` |
| `test_form_sin_direccion` | Inválido si falta `direccion` |
| `test_form_nombre_max_length` | Inválido si `nombre` supera 100 caracteres |
| `test_form_laboratorio_inexistente` | Inválido si se referencia un laboratorio inexistente |
| `test_form_guarda_instancia` | `form.save(commit=False)` + `save()` + `save_m2m()` crea farmacia con laboratorios |
| `test_form_actualiza_instancia` | `form.save(instance=obj)` actualiza la farmacia existente |

---

## Capa 3 — Pruebas de Controladores (Vistas)

Verifican el comportamiento HTTP de cada vista: códigos de respuesta, contextos entregados al template, redirecciones y efectos en la base de datos. Se usa `self.client` para simular peticiones.

### `PerfilControllerTest`

| Test | Qué verifica |
|------|-------------|
| `test_home_get` | `GET /` retorna 200 |
| `test_signup_get` | `GET /signup/` retorna 200 con `formUser` en contexto |
| `test_signup_post_contrasenas_no_coinciden` | Muestra el error `"contraseñas no coinciden"` |
| `test_signup_post_exitoso` | Redirige a `/perfiles/` tras crear usuario _(usa mock)_ |
| `test_signup_post_usuario_duplicado` | Muestra el error `"usuario ya existe"` _(usa mock)_ |
| `test_perfiles_get` | `GET /perfiles/` retorna 200 con `users` en contexto |
| `test_signin_get` | `GET /signin/` retorna 200 con `form` en contexto |
| `test_signin_post_credenciales_validas` | Login exitoso redirige a `/perfiles/` |
| `test_signin_post_credenciales_invalidas` | Muestra el error `"Usuario o contraseña incorrectas"` |
| `test_signout` | `GET /logout/` cierra sesión y redirige a `/` |

> **Nota sobre el mock en signup:** La vista llama a `User.objects.create_user()` con el parámetro `alergias=` que no existe en el modelo estándar de Django. Se usa `unittest.mock.patch` para aislar este comportamiento.

### `MedicamentoControllerTest`

| Test | Qué verifica |
|------|-------------|
| `test_lista_medicamentos_get` | `GET /lista/` retorna 200 con `medicamentos` en contexto |
| `test_registrar_medicamento_get` | `GET /registrar/` retorna 200 con formulario vacío |
| `test_registrar_medicamento_post_valido` | `POST` válido crea medicamento y redirige a `/lista/` |
| `test_registrar_medicamento_post_invalido` | `POST` vacío retorna 200 con errores en el formulario |
| `test_editar_medicamento_get` | `GET /editar/<id>/` retorna 200 con medicamento precargado |
| `test_editar_medicamento_get_404` | `GET /editar/9999/` retorna 404 |
| `test_editar_medicamento_post_valido` | `POST` válido actualiza el medicamento y redirige |
| `test_eliminar_medicamento_get` | `GET /eliminar/<id>/` retorna 200 (pantalla de confirmación) |
| `test_eliminar_medicamento_post` | `POST` elimina el medicamento de la BD y redirige |

### `LaboratorioControllerTest`

| Test | Qué verifica |
|------|-------------|
| `test_labs_get` | `GET /labs/` retorna 200 con `laboratorio` en contexto |
| `test_crear_labs_get` | `GET /crear_labs/` retorna 200 con formulario vacío |
| `test_crear_labs_post_valido` | `POST` válido crea laboratorio y redirige a `/labs/` |
| `test_modificar_labs_get` | `GET /modificar_labs/<id>/` retorna 200 con formulario precargado |
| `test_modificar_labs_get_404` | `GET /modificar_labs/9999/` retorna 404 |
| `test_modificar_labs_post_valido` | `POST` válido actualiza laboratorio y redirige a `/labs/` |
| `test_ver_historial` | `GET /ver_historial/<id>/` retorna 200 con `laboratorio`, `medicamentos` y `farmacias` |
| `test_ver_historial_404` | `GET /ver_historial/9999/` retorna 404 |

### `FarmaciaControllerTest`

| Test | Qué verifica |
|------|-------------|
| `test_lista_farmacias_get` | `GET /lista_farm/` retorna 200 con `farmacias`, `laboratorios` y `medicamentos` |
| `test_lista_farmacias_orden_alfabetico` | `?orden=alfabetico` ordena por `nombre` ascendente |
| `test_lista_farmacias_orden_reciente` | `?orden=reciente` ordena por `-id` (más nuevo primero) |
| `test_registrar_farmacia_get` | `GET /registro_farm/` retorna 200 con formulario vacío |
| `test_registrar_farmacia_post_valido` | `POST` válido crea farmacia y redirige a la lista |
| `test_registrar_farmacia_post_invalido` | `POST` vacío retorna 200 con errores en el formulario |
| `test_modificar_farmacia_get` | `GET /farmacias/modificar/<id>/` retorna 200 con formulario precargado |
| `test_modificar_farmacia_get_404` | `GET /farmacias/modificar/9999/` retorna 404 |
| `test_modificar_farmacia_post_valido` | `POST` válido actualiza farmacia y redirige a la lista |

---

## Resumen de cobertura

| Capa | Clases de prueba | Tests |
|------|-----------------|-------|
| Modelos | 4 | 28 |

---

## Preparación de Datos (SetUp)
En las pruebas unitarias de modelos, formularios y vistas (`Controlador/tests.py`), la preparación de datos (`setUp`) se mantiene al mínimo necesario para aislar la prueba. Dependiendo del caso de prueba, los datos provienen de constructores simulados desde cero (hardcodeados dentro del propio caso de prueba) durante la fase de validación inicial (`setUp`). Generalmente implica:
- Crear registros aislados requeridos para las llaves foráneas. Ejemplo: se crea un registro de `Laboratorios` para poder pasarlo en la creación de un `Medicamento`.
- Crear el registro primario modificado o inspeccionado. Ejemplo: la prueba `test_modificar_labs_post_valido` primero genera y guarda un Laboratorio (`self.laboratorio`) antes de intentar modificarlo a través del `self.client`.
- Crear usuarios en los test de la vista autenticada usando el método `User.objects.create_user`.
| Formularios | 3 | 26 |
| Controladores | 4 | 36 |
| **Total** | **11** | **90** |

---

## Cómo ejecutar las pruebas

### 0. Primera vez — configurar el entorno

El proyecto incluye un `requirements.txt`. Solo necesitas hacer esto una vez:

```bash
# Crear el entorno virtual dentro del proyecto
python -m venv venv

# Activarlo (Linux/macOS)
source venv/bin/activate

# Activarlo (Windows)
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 1. Activar el entorno virtual

Desde la raíz del proyecto, antes de correr cualquier test:

```bash
# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

Este paso se necesita una sola vez por sesión de terminal.

### 2. Ejecutar todas las pruebas

```bash
python manage.py test \
  Modelo.ModeloLaboratorio.Laboratorios.tests \
  Modelo.ModeloMedicamentos.Medicamentos.tests \
  Modelo.ModeloFarmacia.Farmacias.tests \
  Modelo.ModeloUsuario.Perfiles.tests \
  Controlador.tests \
  --verbosity=2
```

### 3. Ejecutar una capa específica

```bash
# Solo pruebas de Medicamentos (modelos + formularios)
python manage.py test Modelo.ModeloMedicamentos.Medicamentos.tests --verbosity=2

# Solo pruebas de controladores
python manage.py test Controlador.tests --verbosity=2
```

### 4. Ejecutar una clase específica

```bash
python manage.py test Controlador.tests.MedicamentoControllerTest --verbosity=2
python manage.py test Modelo.ModeloFarmacia.Farmacias.tests.FarmaciaFormTest --verbosity=2
```

### 5. Ejecutar un test individual

```bash
python manage.py test Controlador.tests.FarmaciaControllerTest.test_lista_farmacias_orden_alfabetico
python manage.py test Modelo.ModeloMedicamentos.Medicamentos.tests.MedicamentoModelTest.test_cascade_delete
```

### Resultado esperado

```
Ran 90 tests in X.XXXs

OK
```

---

## Notas técnicas

- **Base de datos de prueba:** Django crea una BD en memoria para cada ejecución. No se modifica `db.sqlite3` en ningún momento.
- **Aislamiento:** cada método `test_*` parte de un estado limpio. `setUp()` se ejecuta antes de cada test y sus datos se descartan al terminar.
- **Corrección aplicada:** `Super/settings.py` fue corregido para que Django encuentre los templates ubicados en `Vista/*/Templates/`. La configuración original apuntaba a una carpeta inexistente.
