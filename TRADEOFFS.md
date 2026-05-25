# TRADEOFFS

1. No authenticated analyst roles.
   - I prioritized the data pipeline, normalization, and review UX over implementing RBAC and user provisioning.
   - In a full product, analyst and auditor roles would be required before deployment.

2. No PDF utility bill or OCR ingestion.
   - I treated utility portal CSV export as the realistic minimum viable source.
   - PDF bill ingestion adds significant complexity and is easier to add after the CSV path is stable.

3. No live SAP API integration.
   - I implemented SAP as a flat export ingestion because SAP projects often start with file extracts.
   - Direct SAP OData/BAPI connectivity is a real next step but not necessary to prove a realistic intake and normalization model.
