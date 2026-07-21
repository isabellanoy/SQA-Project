# Pruebas de Caja Negra - Fiabilidad (Reliability)

Este documento detalla los casos de prueba de **Caja Negra** diseñados para evaluar la **Fiabilidad y Tolerancia a Fallos** de los módulos de Farmacias, Laboratorios y Medicamentos dentro del Sistema de Gestión.

## 1. Descripción General
Las pruebas de fiabilidad (reliability) buscan someter el sistema a condiciones extremas y anómalas desde la perspectiva de un cliente HTTP externo. El objetivo no es verificar flujos o "caminos felices", sino garantizar que el servidor siempre regrese una respuesta bien manejada (códigos HTTP 200, 302, 400, 404, 405) y nunca colapse con un **Error Interno del Servidor (HTTP 500)** cuando se encuentra con entradas maliciosas o inesperadas.

**Archivo de pruebas:** `Controlador/reliability_tests.py`

---

## 2. Preparación de Datos (SetUp)
Antes de ejecutar los ensayos de caja negra, el test levanta un estado inicial en la base de datos temporal:
- **Autenticación temporal**: Se crea y se loguea un usuario (`tester` / `password123`).
- **Laboratorio base**: `nombre="Lab Inicial"`, `direccion="Calle Verdadera 123"`.
- **Medicamento base**: `nombre_comercial="Medicina Base"`, asociado al laboratorio base.
- **Farmacia base**: `nombre="Farmacia Centro"`, `direccion="Calle Verdadera 123"`.

---

## 3. Escenarios de Prueba (Casos)

### 3.1. Análisis de Valores Límite Extremos y Desbordamiento
- **Método**: `test_valores_limites_extremos_desbordamiento`
- **Endpoint Objetivo**: POST a `/crear_labs/`
- **Payload Inyectado**: Un diccionario donde los campos `nombre` y `direccion` superan largamente el `max_length` definido en el modelo (5000 caracteres de longitud).
- **Criterio de Aceptación**: El backend debe rechazar la inserción por validación de formulario retornando un `200` re-renderizando con errores, o un `400` / `302`. No debe lanzar una excepción a nivel de base de datos (`DataError`) que rompa el servidor (500).

### 3.2. Tipos de Datos Inesperados (Fuzzing Básico)
- **Método**: `test_tipos_datos_inesperados_fuzzing`
- **Endpoint Objetivo**: POST a `/registro_farm/` (registrar_farmacia)
- **Payload Inyectado**: Caracteres especiales como `<script>alert("hack")</script>` en campos de texto, booleanos estructurados en diccionario (`{'invalido': True}`) donde se espera texto, y listas (`[1, 2, 3]`) donde se esperan cadenas.
- **Criterio de Aceptación**: Al igual que el caso anterior, la capa de Controladores/Formularios de Django debe neutralizar las estructuras no serializables o de tipo incorrecto (Type Mismatch) retornando respuestas válidas, previniendo el error 500.

### 3.3. Violación de Integridad Referencial
- **Método**: `test_violacion_integridad_referencial`
- **Endpoint Objetivo**: POST a `/registrar/` (registrar_medicamento)
- **Payload Inyectado**: Se intenta asignar un Medicamento a un Laboratorio proporcionando como "llave foránea" un string no numérico (`'un_string_que_no_es_id'`).
- **Criterio de Aceptación**: El ORM o el Formulario debe capturar y controlar el `ValueError` en lugar de pasarlo a la vista principal ocasionando un HTTP 500.

### 3.4. Métodos HTTP No Permitidos
- **Método**: `test_metodos_http_no_permitidos`
- **Endpoint Objetivo**: Rutas de sólo-lectura (`/lista/`) y rutas de mutación (`/editar/<id>/`).
- **Payload Inyectado**: Una solicitud `POST` a una vista que idealmente es solo lectura, y una solicitud `PUT` cruda simulada por el cliente.
- **Criterio de Aceptación**: Comprobar que enrutadores y controladores no asuman siempre la existencia de `request.POST` de forma ciega y no fallen si el tipo de consulta no es el ideal. Respuestas 200 (si lo ignora como GET) o 405 (Method No Allowed) son aceptables. 500 es inaceptable.

### 3.5. Carga Útil Incompleta o Vacía
- **Método**: `test_carga_util_incompleta_o_vacia`
- **Endpoint Objetivo**: POST a `/registrar/` (registrar_medicamento)
- **Payload Inyectado**: Diccionario completamente vacío (`{}`).
- **Criterio de Aceptación**: El código de la vista no debe colapsar por un `KeyError` al intentar leer variables fijas en crudo como `request.POST['nombre_comercial']`. Debe volver con un error formal indicando campos en ausencia.

---

## 4. Instrucciones de Ejecución

Para correr las pruebas de forma aislada, sigue estos pasos:

1. **Activar el entorno virtual** (muy importante para cargar las dependencias de Django):
   ```bash
   source venv/bin/activate
   # o en Windows: .\venv\Scripts\activate
   ```

2. **Ejecutar el test específico**:
   ```bash
   python manage.py test Controlador.reliability_tests
   ```

3. **Interpretar salida**:
   Deberás observar listados de `.` que indican el éxito de la prueba. Si alguna llegara a fallar, el reporte indicará directamente con qué estado devolvió el servidor en esa colisión (ej: AssertionError si devuelve código HTTP 500).
