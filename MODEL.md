# MODEL

## Purpose
This data model is designed to support enterprise onboarding for ESG data ingestion, normalization, analyst review, and audit-ready approval.

## Core entities

- `Tenant`
  - Represents a single client or enterprise account.
  - Enables true multi-tenancy by isolating imported sources, batches, and normalized records.

- `Source`
  - Represents the original source system or export type: SAP fuel/procurement, utility electricity, or corporate travel.
  - Includes `source_type`, `tenant`, and optional config metadata.

- `ImportBatch`
  - Tracks each file ingest as a source-of-truth event.
  - Records filename, source type, receive timestamp, row counts, imported/failed counts, and import status.

- `NormalizedRecord`
  - The canonical normalized row used for analyst review and approval.
  - Includes source references: `tenant`, `source`, `import_batch`, and `raw_payload`.
  - Tracks raw values (`quantity`, `quantity_unit`) plus normalized values (`normalized_quantity`, `normalized_unit`).
  - Stores `emissions_kg_co2e`, `record_type`, `category`, `emission_scope`, `vendor`, and `location`.
  - Contains review state: `status`, `approved_by`, `approved_at`, `suspicious_reason`, `created_at`, and `updated_at`.

- `AuditEntry`
  - Captures approval activity and other record-level events.
  - Includes `event_type`, `created_by`, timestamp, and arbitrary JSON `data`.

## Multi-tenancy
Each record is associated with a `Tenant`. All source and import metadata is scoped to that tenant.

## Scope 1 / 2 / 3 categorization
`NormalizedRecord.emission_scope` supports explicit categories: `scope1`, `scope2`, and `scope3`.

- SAP fuel/procurement rows are treated as `scope1`.
- Utility electricity is treated as `scope2`.
- Corporate travel is treated as `scope3`.

## Source-of-truth tracking
The model tracks provenance using:
- `Source` for the source system type.
- `ImportBatch` for the uploaded file and ingestion event.
- `NormalizedRecord.raw_payload` to preserve the original row data.
- `created_at`, `updated_at`, `approved_at`, and `AuditEntry` for history and review events.

## Unit normalization
Each normalized row stores:
- `quantity` and `quantity_unit` from the raw data.
- `normalized_quantity` and `normalized_unit` for common unit handling.

Normalization rules are implemented in the ingestion layer:
- fuel quantities remain in liters when possible,
- electricity is normalized to kWh,
- travel distance is normalized to km.

## Audit trail
- `NormalizedRecord` includes approval state and timestamps.
- `AuditEntry` captures discrete actions such as approvals.
- The ingest batch and raw payload preserve the original source row.
