# Pruebas de Integración — ProyectoSoftwareFinal

## ¿Qué son las pruebas de integración?

Las pruebas de integración verifican que **múltiples componentes del sistema funcionan correctamente juntos**. A diferencia de las pruebas unitarias (que prueban una sola pieza en aislamiento), las pruebas de integración simulan flujos reales de usuario de principio a fin:

```
Petición HTTP → URL → Controlador (vista) → Formulario → Modelo → Base de datos → Respuesta HTTP
```

**Diferencias clave frente a las pruebas unitarias:**

| Aspecto | Pruebas Unitarias | Pruebas de Integración |
|---------|-------------------|----------------------|
| Alcance | Un componente aislado | Múltiples componentes juntos |
| Mocks | Sí (para aislar dependencias) | No (todo es real) |
| BD | En memoria, datos mínimos | En memoria, flujos completos |
| Objetivo | Verificar lógica interna | Verificar flujos de usuario |
| Velocidad | Muy rápidas | Más lentas (hacen más operaciones) |

---

## Archivo de pruebas

```
Controlador/
    integration_tests.py    ← todas las pruebas de integración
```

---

## Explicación detallada por clase y test

---

### `MedicamentoCRUDIntegrationTest`

Cubre el ciclo completo de vida de un medicamento, pasando por las vistas reales en cada paso.

#### `test_ciclo_completo_medicamento`

Simula a un usuario que registra un medicamento, lo ve en la lista, lo edita y luego lo elimina.

**Pasos del flujo:**

1. `POST /registrar/` con datos válidos → debe redirigir a `/lista/`
2. Verificar que el medicamento existe en la base de datos (`assertTrue`)
3. `GET /lista/` → el medicamento debe aparecer en el contexto `medicamentos`
4. `POST /editar/<id>/` con nuevos datos → debe redirigir a `/lista/`
5. Verificar con `refresh_from_db()` que los cambios (nombre y componentes) se guardaron en BD
6. `POST /eliminar/<id>/` → debe redirigir a `/lista/`
7. Verificar que el medicamento ya no existe en BD (`assertFalse`) ni en el contexto de la lista

#### `test_registrar_medicamento_invalido_no_persiste`

Verifica que el sistema rechaza datos inválidos sin dejar rastro en la base de datos.

**Pasos del flujo:**

1. Contar los medicamentos existentes antes del POST (`count_antes`)
2. `POST /registrar/` con campos vacíos (formulario inválido — sin nombre ni laboratorio)
3. Verificar que `Medicamento.objects.count()` es igual a `count_antes` (nada se creó)

---

### `LaboratorioCRUDIntegrationTest`

Cubre la creación, modificación y el historial de un laboratorio.

#### `test_ciclo_completo_laboratorio`

Simula a un usuario que crea un laboratorio y luego modifica sus datos.

**Pasos del flujo:**

1. `POST /crear_labs/` con nombre y dirección → debe redirigir a `/labs/`
2. Verificar que el laboratorio existe en BD (`assertTrue`)
3. `GET /labs/` → el laboratorio debe aparecer en el contexto `laboratorio`
4. `POST /modificar_labs/<id>/` con nuevos datos → debe redirigir a `/labs/`
5. Verificar con `refresh_from_db()` que nombre y dirección se actualizaron en BD

#### `test_historial_refleja_medicamentos_y_farmacias`

Verifica que el historial de un laboratorio muestra correctamente todas sus entidades asociadas, cruzando tres modelos distintos.

**Pasos del flujo:**

1. Crear laboratorio, medicamento (ForeignKey al laboratorio) y farmacia (ManyToMany al laboratorio) directamente en BD
2. `GET /ver_historial/<id>/` → verificar que el contexto contiene el medicamento en `medicamentos` y la farmacia en `farmacias`

> Este test cruza tres modelos (`Laboratorios`, `Medicamento`, `Farmacia`) y verifica que la vista los une correctamente usando los filtros ORM.

#### `test_historial_laboratorio_sin_asociaciones`

Verifica el caso límite de un laboratorio recién creado sin ninguna entidad relacionada.

**Pasos del flujo:**

1. Crear laboratorio vacío en BD (sin medicamentos ni farmacias)
2. `GET /ver_historial/<id>/` → verificar que `medicamentos.count() == 0` y `farmacias.count() == 0`

---

### `FarmaciaCRUDIntegrationTest`

Cubre el registro, modificación y los distintos órdenes de la lista, incluyendo la relación ManyToMany con laboratorios.

#### `test_ciclo_completo_farmacia`

Simula registrar una farmacia con un laboratorio y luego editarla para agregar un segundo laboratorio.

**Pasos del flujo:**

1. `POST /registro_farm/` con nombre, dirección y `laboratorios=[lab1]` → redirige a lista
2. Verificar en BD que la farmacia existe y que `farmacia.laboratorios.all()` contiene `lab1`
3. `GET /lista_farm/` → la farmacia aparece en el contexto `farmacias`
4. `POST /farmacias/modificar/<id>/` con `laboratorios=[lab1, lab2]` → redirige a lista
5. Verificar que `farmacia.laboratorios.count() == 2` y que `lab2` fue agregado correctamente

#### `test_lista_farmacias_tres_ordenes`

Verifica que el parámetro `?orden=` produce resultados distintos y correctos para los tres modos disponibles.

**Pasos del flujo:**

1. Crear 3 farmacias con nombres fuera de orden alfabético ("Zebra", "Alfa", "Medio")
2. `GET /lista_farm/?orden=alfabetico` → la primera debe ser "Alfa Farmacia" y la última "Zebra Farmacia"
3. `GET /lista_farm/?orden=reciente` → la primera debe ser la de mayor `id` (más reciente)
4. `GET /lista_farm/` sin parámetro → debe retornar las 3 farmacias (sin orden exigido)

---

### `RelacionesEntidadesIntegrationTest`

Verifica que las relaciones entre los tres modelos principales se comportan correctamente de extremo a extremo.

#### `test_eliminacion_laboratorio_elimina_medicamentos_en_cascada`

Verifica que `on_delete=CASCADE` funciona correctamente y que la vista refleja el estado actualizado de la BD.

**Pasos del flujo:**

1. Crear laboratorio y 2 medicamentos asociados a él
2. `GET /lista/` → verificar que ambos medicamentos aparecen en el contexto
3. Eliminar el laboratorio con `lab.delete()` (dispara el CASCADE en BD)
4. Verificar que los medicamentos ya no existen en BD (`assertFalse` para cada uno)
5. `GET /lista/` → verificar que el contexto `medicamentos` tiene `count() == 0`

> No existe una vista de eliminación de laboratorios en el proyecto, por eso la eliminación se hace directamente por ORM. Lo que se integra aquí es el comportamiento de la BD + la vista de medicamentos.

#### `test_farmacia_visible_en_historial_de_sus_laboratorios`

Verifica que una relación ManyToMany se refleja correctamente en ambas direcciones del historial.

**Pasos del flujo:**

1. Crear 2 laboratorios y 1 farmacia, luego asociarla a ambos con `farmacia.laboratorios.add(lab1, lab2)`
2. `GET /ver_historial/<lab1.pk>/` → la farmacia debe estar en el contexto `farmacias`
3. `GET /ver_historial/<lab2.pk>/` → la farmacia también debe estar en el contexto `farmacias`

#### `test_lista_farmacias_incluye_contexto_completo`

Verifica que la vista de lista entrega todos los datos auxiliares que el template necesita para mostrar filtros.

**Pasos del flujo:**

1. Crear laboratorio, medicamento asociado y farmacia asociada al laboratorio
2. `GET /lista_farm/` → verificar que el contexto contiene `farmacias`, `laboratorios` y `medicamentos`

---

### `AutenticacionIntegrationTest`

Verifica el flujo completo de autenticación sin ningún mock — todas las llamadas pasan por Django Auth real.

#### `test_flujo_signin_perfiles_signout`

Simula el ciclo completo de una sesión de usuario desde login hasta logout.

**Pasos del flujo:**

1. `POST /signin/` con credenciales correctas → redirige a `/perfiles/`
2. `GET /perfiles/` → el usuario autenticado aparece en el contexto `users`, `is_authenticated == True`
3. `GET /logout/` → redirige a `/`
4. `GET /` → verificar que `request.user.is_authenticated == False` (sesión destruida)

#### `test_credenciales_invalidas_no_autentican`

Verifica que una contraseña incorrecta no abre sesión ni redirige a páginas internas.

**Pasos del flujo:**

1. `POST /signin/` con contraseña incorrecta → retorna 200 (no redirige a `/perfiles/`)
2. La respuesta contiene el texto `"Usuario o contraseña incorrectas"`
3. `request.user.is_authenticated == False`

#### `test_multiples_usuarios_visibles_en_perfiles`

Verifica que la vista de perfiles refleja todos los usuarios del sistema en tiempo real.

**Pasos del flujo:**

1. El `setUp` crea 1 usuario; este test crea 2 adicionales (total: 3 en BD)
2. `GET /perfiles/` → `response.context['users'].count() == 3`

---

## Resumen de cobertura

| Clase | Tests |
|-------|-------|
| `MedicamentoCRUDIntegrationTest` | 2 |
| `LaboratorioCRUDIntegrationTest` | 3 |
| `FarmaciaCRUDIntegrationTest` | 2 |
| `RelacionesEntidadesIntegrationTest` | 3 |
| `AutenticacionIntegrationTest` | 3 |
| **Total** | **13** |

---

## Paso a paso para ejecutar las pruebas

### Prerrequisitos

Tener el entorno virtual creado e instaladas las dependencias. Si aún no lo hiciste:

```bash
python -m venv venv
pip install -r requirements.txt
```

### Paso 1 — Posicionarse en la raíz del proyecto

```bash
cd /ruta/a/ProyectoSoftwareFinal
```

### Paso 2 — Activar el entorno virtual

```bash
# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

Sabrás que está activo porque el prompt muestra `(venv)`.

### Paso 3 — Ejecutar las pruebas

**Solo pruebas de integración:**

```bash
python manage.py test Controlador.integration_tests --verbosity=2
```

**Una clase específica:**

```bash
python manage.py test Controlador.integration_tests.MedicamentoCRUDIntegrationTest --verbosity=2
python manage.py test Controlador.integration_tests.AutenticacionIntegrationTest --verbosity=2
```

**Un test individual:**

```bash
python manage.py test Controlador.integration_tests.LaboratorioCRUDIntegrationTest.test_historial_refleja_medicamentos_y_farmacias
python manage.py test Controlador.integration_tests.RelacionesEntidadesIntegrationTest.test_eliminacion_laboratorio_elimina_medicamentos_en_cascada
```

**Suite completa — unitarias + integración (103 tests):**

```bash
python manage.py test \
  Modelo.ModeloLaboratorio.Laboratorios.tests \
  Modelo.ModeloMedicamentos.Medicamentos.tests \
  Modelo.ModeloFarmacia.Farmacias.tests \
  Modelo.ModeloUsuario.Perfiles.tests \
  Controlador.tests \
  Controlador.integration_tests \
  --verbosity=2
```

### Paso 4 — Interpretar el resultado

```
Ran 13 tests in 1.570s

OK
```

- `OK` — todos los tests pasaron.
- `FAILED (failures=N)` — N tests fallaron; se muestra el nombre del test, el traceback y la aserción que no se cumplió.
- `ERROR` — ocurrió una excepción inesperada durante la ejecución del test.

---

## Notas técnicas

- **Sin mocks:** todas las llamadas son reales; no se reemplaza ningún componente por un objeto simulado. Si hay un bug en el controlador, el modelo o la BD, el test lo detectará.
- **Base de datos en memoria:** se usa una BD SQLite en memoria que se crea limpia antes de cada test y se destruye al terminar. No afecta `db.sqlite3`.
- **`assertRedirects`:** verifica que la vista retorna un código 302 y que la URL de destino es la correcta, confirmando que el flujo se completó exitosamente.
- **`refresh_from_db()`:** recarga el objeto desde la BD para confirmar que los cambios persistieron realmente, no solo en la memoria de Python.
- **`response.wsgi_request.user`:** permite inspeccionar el estado de autenticación del usuario después de una petición, sin necesidad de hacer otra solicitud.
- **`response.context`:** contiene el diccionario de variables que el controlador pasó al template, lo que permite verificar qué datos recibe la vista sin parsear HTML.
