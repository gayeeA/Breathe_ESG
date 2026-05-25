# SOURCES

## SAP fuel/procurement
- Real-world format: enterprise SAP exports often come as flat CSV/Excel files generated from SAP BW or SAP GUI reports.
- What I learned: SAP headers are not stable; some clients use German labels like `Buchungsdatum`, while others use English labels like `Posting Date`.
- Sample data shape:
  - `Posting Date`, `Material Description`, `Plant Code`, `Quantity`, `UoM`, `Vendor`, `CO2 Emissions`
- Why it is realistic: fuel procurement rows in SAP are typically tied to plant/plant codes, include quantities and units, and may or may not include explicit CO2 values.
- What would break in a real deployment:
  - missing or highly customized SAP report columns,
  - delivery of data as Excel rather than CSV,
  - line-item splits across purchase orders and cost centers.

## Utility electricity
- Real-world format: utility portal exports typically provide meter-level billing periods and kWh usage in CSV.
- What I learned: billing periods often span non-calendar months and raw rows include meter/account identifiers plus usage and cost.
- Sample data shape:
  - `Billing Start`, `Billing End`, `Meter ID`, `Usage (kWh)`, `Account Number`, `Cost`
- Why it is realistic: facilities teams commonly upload meter-based CSV billing summaries for electricity reconciliation.
- What would break in a real deployment:
  - alternative pricing structures with demand or tiered charges,
  - CSVs localized with different delimiters,
  - meter-level data split into separate files.

## Corporate travel
- Real-world format: corporate travel exports from Concur/Navan come as expense rows with categories, dates, distances, and origin/destination metadata.
- What I learned: travel categories matter because flights, hotels, and ground transport use different emission factors.
- Sample data shape:
  - `Expense Type`, `Trip Start`, `Trip End`, `Origin`, `Destination`, `Distance`, `Amount`, `Currency`
- Why it is realistic: approving travel emissions typically requires review of travel rows and flags when distance or trip dates are missing.
- What would break in a real deployment:
  - missing distance fields,
  - origin/destination values that require airport lookup,
  - split itineraries or multi-leg travel rows.
