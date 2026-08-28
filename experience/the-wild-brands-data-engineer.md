---
company: "The Wild Brands"
role: "Data Engineer"
employment_type: ""
location: "Chile - México"
start: "2023-11"
end: "2025-06"
---

# Data Engineer — The Wild Brands

## Scope

Diseñó desde cero la arquitectura de datos compartida por WildLama Chile y WildFoods Chile y México, atendiendo a cerca de 150 usuarios y definiendo lineamientos de escalabilidad, gobierno y control de costos.

## Achievements

- Diseñó un Data Lake en GCP con ambientes productivos y de prueba para cada empresa y país, organizado en capas raw, stage y share, más un proyecto compute por ambiente.
- Modeló en dbt la capa de transformación y reglas de negocio, incluido el modelo de mayor tamaño de la organización, con más de 200 entidades.
- Implementó ingestas batch desde SAP HANA vía ODBC, Odoo, Airbyte y fuentes personalizadas.
- Integró los datos de Shopify mediante consultas GraphQL personalizadas para los procesos batch y procesó sus webhooks con Pub/Sub y Dataflow, alineando ambos flujos con el mismo modelo de datos.
- Desarrolló en Go una API desplegada en Cloud Run para recibir el inventario del sistema de bodega cada 15 minutos.
- Implementó una reconciliación de pagos entre las transacciones recibidas en terminales POS y los registros contables de ingreso en las cuentas de la compañía.
- Desarrolló pipelines de GitHub Actions y gestionó toda la infraestructura mediante Terraform.
- Creó modelos semánticos y los primeros paneles oficiales en Looker; además, desarrolló una herramienta para convertir definiciones de dbt en modelos de Looker y rediseñó su arquitectura para simplificar el conector sin alterar el modelo estrella ni las reglas de negocio.
- Implementó paneles FinOps para analizar el gasto en GCP y gestionó accesos mediante grupos de Google para simplificar la asignación de roles.

## Responsibilities

- Organizó GCP en seis carpetas lógicas —producción y prueba para cada empresa y país— con proyectos raw, stage, share y compute en cada una.
- Centralizó en la capa compute Cloud Composer, Artifact Registry, Cloud Run y los procesos de Dataflow; configuró una red propia y una IP pública estática para conectarse con sistemas legados.
- Coordinó conversaciones con distintos partners para la contratación de Looker, acompañó a los primeros usuarios y lideró integrantes más junior a medida que creció el equipo.
- Continuó apoyando a la compañía como freelance a tiempo parcial después de finalizar el rol.

## Skills

- GCP, BigQuery, Cloud Storage, dbt, Airflow, Cloud Composer, Terraform, GitHub Actions, Airbyte, GraphQL, Pub/Sub, Dataflow, Cloud Functions, Cloud Run, Go, SAP HANA, ODBC, Shopify, Odoo, EDI, Looker, IAM, FinOps y arquitectura de Data Lake.
