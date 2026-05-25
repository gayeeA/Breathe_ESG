# DECISIONS

## Ingestion approach
All three sources are implemented as file uploads.
This is realistic for enterprise onboarding because clients often deliver exports from SAP, utility portals, and travel platforms as CSVs before API integrations are built.

## SAP fuel/procurement
- Chose a flat-file CSV-style SAP export rather than a SOAP or BAPI integration.
- Justification: CSV exports are the most practical initial onboarding path when enterprise data is inconsistent and clients are still identifying which reports they can share.
- Handled:
  - German-style and English headers via flexible column matching.
  - Inconsistent units by preserving `quantity_unit` and normalizing values for review.
  - Plant codes as opaque `location` values, since lookups are often separate from initial ingestion.
- Ignored:
  - full IDoc field mapping,
  - SAP OData/BAPI connectivity,
  - purchase-order reconciliation.

## Utility electricity
- Chose portal CSV export ingestion.
- Justification: facility teams usually export utility bills to CSV when direct utility APIs are not available, and CSV can preserve billing periods and usage metadata.
- Handled:
  - billing start/end dates,
  - usage in kWh,
  - meter or account identifiers,
  - non-calendar billing periods.
- Ignored:
  - PDF bill OCR,
  - tariff/price structure parsing,
  - demand charges and load-profile detail.

## Corporate travel
- Chose a travel export format like Concur/Navan expense reports.
- Justification: corporate travel platforms commonly provide CSV exports that include expense categories, dates, airport codes, and distances.
- Handled:
  - flights, hotels, and ground transport as distinct categories,
  - distance-based emission estimation,
  - fallback from origin/destination when explicit distance is missing.
- Ignored:
  - full airport-to-airport routing,
  - per-seat-class flight factor detail,
  - hotel night-stay reconstructions.

## Review UX
- Built a dashboard that surfaces pending normalized rows, suspicious flags, and approve actions.
- Focused on a minimal analyst workflow rather than a full audit portal.

## What I would ask the PM
- Which tenant identification method should be authoritative for production (URL path, auth token, or upload metadata)?
- Do they want source imports locked after approval, or should analysts be able to correct and reprocess rows?
- Should travel emissions be derived using distance-only heuristics or should we also accept platform-specific factors from the export?
