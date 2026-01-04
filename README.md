# FX Rates Data Pipeline

This project implements an end-to-end data pipeline to ingest foreign exchange
rates from the Frankfurter API and make them available for analytics in BigQuery.

## Architecture Overview

Frankfurter API → GCS (raw JSON) → BigQuery External Tables → dbt models

Raw data is stored immutably in Google Cloud Storage and materialized as
partitioned tables in BigQuery using dbt.

For a detailed explanation of design decisions, see
[docs/architecture.md](docs/architecture.md).

## Ingestion

Data is extracted from the Frankfurter API and stored as raw JSON in GCS,
partitioned by the data date provided by the API.

The ingestion process is idempotent: if data for a given date already exists,
the pipeline skips extraction to prevent duplicates.

## Transformations

### Data Modeling (dbt)
The project follows a layered modeling approach using dbt:

#### Raw
The raw layer preserves the original structure of the data extracted from the
Frankfurter API. Data is loaded into BigQuery with minimal transformation to
ensure traceability and facilitate debugging.

#### Staging
The staging layer standardizes and normalizes the raw data to prepare it for
analytical use. Key transformations include:

- Flattening the `rates` structure to one row per date and target currency
- Standardizing column names and data types
- Removing request-specific fields (e.g. `amount`) that do not represent
  intrinsic attributes of the exchange rate
- Defining a clear grain: one record per date, base currency, and target currency

Staging models are materialized as views to keep transformations lightweight and
avoid unnecessary data duplication.

#### Marts
Mart models are designed for analytical consumption. They expose clean,
business-friendly schemas and add lightweight semantic logic (e.g. flags for
latest available rates). Marts are materialized as tables for performance.

## Orchestration

The pipeline is orchestrated using Apache Airflow, running locally with Docker
Compose and the LocalExecutor.

A single DAG (`exchange_rates_pipeline`) coordinates the end-to-end workflow:

1. **Extraction**  
   A Python ingestion script fetches exchange rate data from the Frankfurter API
   and stores raw JSON files in Google Cloud Storage.

2. **Transformations**  
   dbt is executed from Airflow using `BashOperator` to build raw, staging, and
   mart models in BigQuery.

3. **Data Quality Validation**  
   dbt tests are executed as a separate task to ensure data quality before the
   pipeline completes.

The DAG is configured to run manually (`@once`) to simplify local development and
demonstration, while still reflecting a production-ready orchestration pattern.

## Infrastructure & Deployment

Airflow is run locally using Docker Compose with a custom Docker image that
extends the official Apache Airflow image to include dbt.

The project infrastructure is organized under a dedicated `docker/` directory,
keeping orchestration and container configuration separate from application and
transformation code.

Authentication to Google Cloud services is handled using Application Default
Credentials (ADC) with a service account, allowing secure access to GCS and
BigQuery without hardcoding secrets in the codebase.

## Running the Project Locally

### Prerequisites
- Docker and Docker Compose
- Google Cloud SDK
- A GCP project with access to:
  - Cloud Storage
  - BigQuery

### Setup

1. Create a service account in GCP and download a JSON key.
2. Store the key locally (outside version control) and set the environment
   variable `GOOGLE_APPLICATION_CREDENTIALS`.
3. Define required environment variables in a `.env` file (project ID, dataset,
   bucket name).

### Start Airflow

From the `docker/` directory:

```bash
docker compose up -d --build
```

Airflow will be available at:
```bash
http://localhost:8080
```

### Run the Pipeline
Trigger the exchange_rates_pipeline DAG manually from the Airflow UI.
The pipeline will execute ingestion, dbt transformations, and data quality
checks end-to-end.

## Testing

- Unit tests are implemented using pytest, with API and GCS interactions mocked.
- Data quality checks are implemented using dbt tests (not null, accepted values,
  and custom SQL tests).

## Technologies

- Python
- Apache Airflow
- Docker & Docker Compose
- Google Cloud Storage
- BigQuery
- dbt
- pytest

-----------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------
# FX Rates Data Pipeline – Airflow, dbt & GCP

Proyecto personal de ingeniería de datos donde diseño y ejecuto un pipeline
end-to-end para la ingesta, transformación y validación de tipos de cambio
a partir de una API pública, con foco en arquitectura, orquestación y buenas
prácticas de data engineering.

El objetivo principal del proyecto es simular un flujo real de datos analíticos,
priorizando trazabilidad, separación de responsabilidades y capacidad de
debug en entornos locales.

---

## Arquitectura General

Frankfurter API  
→ Google Cloud Storage (raw JSON, inmutable)  
→ BigQuery (modelado analítico con dbt)  
→ Consumo analítico

Los datos crudos se almacenan sin transformar en GCS y posteriormente se
modelan en BigQuery siguiendo un enfoque por capas.

---

## Ingesta de Datos

La ingesta se realiza mediante un script en Python que consulta la Frankfurter API
y persiste los resultados como archivos JSON en Google Cloud Storage,
particionados por fecha.

Características clave:
- Almacenamiento raw e inmutable
- Particionado por fecha de los datos
- Proceso idempotente: evita reingesta de fechas ya procesadas

---

## Transformaciones y Modelado (dbt)

El modelado de datos se implementa utilizando dbt, siguiendo una arquitectura
en capas:

### Raw
Replica la estructura original de la API con transformaciones mínimas.
Esta capa facilita la trazabilidad y el debugging ante errores en origen.

### Staging
Normaliza y estandariza los datos crudos para su uso analítico:
- Aplanado de estructuras anidadas (`rates`)
- Tipos de datos consistentes
- Nombres de columnas estandarizados
- Definición explícita del grain (fecha, moneda base y moneda destino)

Los modelos de staging se materializan como *views* para mantener ligereza
y evitar duplicación innecesaria.

### Marts
Capa orientada al consumo analítico, con modelos materializados como tablas
optimizadas para performance. Incluye lógica semántica ligera, como flags
para identificar los valores más recientes.

---

## Orquestación con Apache Airflow

El pipeline está orquestado con Apache Airflow y se ejecuta localmente mediante
Docker Compose usando `LocalExecutor`.

Un único DAG coordina el flujo completo:

1. **Extract**  
   Ejecución del script Python de ingesta desde Airflow.

2. **Transform**  
   Ejecución de `dbt run` para construir los modelos analíticos en BigQuery.

3. **Data Quality**  
   Ejecución de `dbt test` para validar reglas de calidad e integridad de datos.

El DAG está configurado con ejecución manual (`@once`), facilitando pruebas
locales y demostraciones sin perder realismo productivo.

---

## Infraestructura y Entorno Local

- Airflow se ejecuta en contenedores Docker
- Imagen custom que incluye dbt y dependencias necesarias
- Configuración centralizada en el directorio `docker/`
- Variables de entorno para desacoplar configuración y código

La autenticación con Google Cloud se gestiona mediante Application Default
Credentials (ADC) usando una service account, sin exponer credenciales en el repo.

---

## Ejecución Local

### Requisitos
- Docker y Docker Compose
- Proyecto activo en Google Cloud
- Acceso a:
  - Google Cloud Storage
  - BigQuery

### Pasos generales
1. Configurar variables de entorno (project, dataset, bucket)
2. Levantar Airflow con Docker Compose
3. Ejecutar el DAG manualmente desde la UI de Airflow

Airflow queda disponible en: http://localhost:8080

## Testing y Calidad

- Tests unitarios en Python con pytest (mock de API y GCS)
- Validaciones de calidad implementadas con dbt tests
  (not null, accepted values y reglas custom)

---

## Estado del Proyecto

- Arquitectura end-to-end definida
- Pipeline ejecutable en entorno local
- Flujo completo de ingesta, transformación y validación
- Iteraciones futuras enfocadas en mejoras de despliegue y automatización

---

## Tecnologías

- Python
- Apache Airflow
- dbt
- Docker & Docker Compose
- Google Cloud Storage
- BigQuery
