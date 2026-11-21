# Microsoft Azure and FOCUS: Conformance Gap and Adoption Roadmap

*Analysis run: July 1, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Provider and product in scope:** Microsoft Azure, via Microsoft Cost Management FOCUS exports (Cost Management "Exports" using the FOCUS template, delivered to Azure Storage).
**Prepared:** 2026-07-01
**Source analyzed:** Microsoft Cost Management FOCUS dataset schema, Microsoft's published FOCUS Conformance Summary and full Conformance Report, and the FOCUS get-started page for Microsoft Azure.
**FOCUS baseline for scoring:** v1.2 (current certification baseline). **Version shipped by the provider:** v1.2 (Microsoft labels the current dataset "FOCUS 1.2-preview").

---

## Executive summary

Microsoft Azure is an official FOCUS data generator listed on focus.finops.org/get-started. It does not have a conformance gap in the usual sense: Cost Management already emits a native FOCUS dataset, selectable as an export template, delivered daily to storage, with up to seven years of history available in FOCUS shape. The question is not whether a FOCUS export exists but which version it targets and how complete that export is.

The get-started page states Microsoft supports **v1.2** of the specification. Microsoft's own conformance documentation labels the current dataset "FOCUS 1.2-preview" and self-reports a **94% conformance score** against the FOCUS 1.2 Requirements Model. The dataset carries the FOCUS column IDs directly, uses key-value JSON tags, ISO 8601 exclusive-end dates, the billing currency for all cost columns, and human-readable display names. This is a substantially complete, FOCUS-shaped export today, not a mapping exercise.

The residual gaps are narrow and mostly conditional. They cluster in three areas: certain cost columns (`ListCost`, `ContractedCost` and their unit prices) return 0 for specific record types (EA/MCA Marketplace charges and reservation usage) and require a price-sheet join to populate; five conditional columns across three families are not emitted in the dataset (`CapacityReservationId`/`Status`, `CommitmentDiscountQuantity`/`Unit`, `SkuPriceDetails`), plus the Recommended `AvailabilityZone`, each with a documented workaround; and a set of value/format nuances (`ProviderName`/`ServiceName`/`ChargeDescription` nulls for edge record types, tags not `x_`-prefixed, `ResourceId` casing). None of these reflect data that does not exist. They reflect either data that lives in an adjacent dataset (the price sheet) or fields Microsoft has not yet surfaced in the FOCUS export.

- **Total FOCUS v1.2 columns:** 57
- **Present and conformant (all or most record types):** 42
- **Substantive Mandatory gaps:** 0 of 21 (no Mandatory column is entirely absent or unproducible; the Mandatory cost columns are populated, with edge-case zeros on specific record types)
- **Deviations and partial-population issues to fix:** 9
- **Conditional columns not yet emitted:** 5 (each with a documented workaround); plus 1 Recommended column (`AvailabilityZone`)

**RAG readiness:** Cost: Strong. Granularity: Strong. Allocation: Strong. Coverage: Strong. FOCUS shape: Strong. **Overall band: Aligned.**

**Recommendation:** Treat Azure as a shipping FOCUS v1.2 data generator. For practitioners, adopt the export as-is and apply Microsoft's documented workarounds (price-sheet joins for `ListCost`/`ContractedCost` on Marketplace and reservation records; null-handling for `PublisherName` and `ServiceName` edge cases). For Microsoft, the path forward is closing the 6% residual: surfacing the three not-yet-emitted conditional column families in the export, populating the cost columns for all record types without a price-sheet join, and advancing from "1.2-preview" to a GA v1.2 dataset, then tracking v1.3/v1.4.

---

## Part 1: The conformance gap

FOCUS (the FinOps Open Cost and Usage Specification) defines a common billing schema so cost and usage data is comparable across providers. Each column carries a feature level (Mandatory, Conditional, Recommended, Optional) that governs whether a conformant dataset must include and populate it. Conformance is judged column by column. For a provider that already ships a FOCUS export, the analysis measures how completely each column is populated and whether values and formats are valid, rather than whether a mapping exists.

### 1.1 The data source

Microsoft Cost Management exposes FOCUS as a first-class export.

- **Delivery:** Cost Management "Exports" using the FOCUS dataset template, written to an Azure Storage account. Exports run on a schedule (daily) and support one-time historical backfills.
- **Granularity:** daily charge-period records, well below monthly aggregation. `ChargePeriodStart`/`ChargePeriodEnd` are ISO 8601 with exclusive end dates.
- **History:** up to seven years of data available in FOCUS format via exports.
- **Cost model:** FOCUS combines actual (billed) and amortized (effective) cost into a single dataset, which Microsoft notes yields roughly 49% fewer rows than maintaining separate actual and amortized datasets.
- **Account model:** supports Enterprise Agreement (EA) and Microsoft Customer Agreement (MCA). `BillingAccountId`/`Name` map to the billing profile for MCA; `SubAccountId`/`Name` map to the subscription. Some columns behave differently across EA and MCA (noted below).
- **Extensions:** Microsoft carries all native-schema detail not in FOCUS as `x_`-prefixed extended columns (for example `x_SkuDetails`, `x_SkuMeterCategory`), which is the FOCUS-sanctioned mechanism.
- **Key limitations:** several cost columns return 0 for specific record types and need a price-sheet join; three conditional column families are not yet emitted in the export; `InvoiceId` is not populated for EA accounts.

### 1.2 How conformance is judged

Feature levels for this analysis were taken from the verified reference table (FOCUS v1.2, 57 columns) and validated against the live FOCUS specification via the FOCUS MCP on 2026-07-01: the v1.2 column set returns 57 columns, `Provider`/`Publisher` show as deprecated in v1.3 (still present and Mandatory in v1.2), and the v1.2 additions (`BillingAccountType`, `SubAccountType`, `InvoiceId`, the pricing-currency columns) are present. The bundled cache was current; no refresh was required.

v1.2 feature-level distribution: 21 Mandatory, 32 Conditional, 4 Recommended (`AvailabilityZone`, `ChargeFrequency`, `InvoiceId`, `ServiceSubcategory`), 0 Optional.

### 1.3 Column-by-column status

Feature levels verified against the FOCUS v1.2 specification. Status reflects population in Microsoft's current FOCUS 1.2-preview dataset per Microsoft's schema and conformance documentation.

| FOCUS Column | Level | In the source? | Status |
|---|---|---|---|
| AvailabilityZone | Recommended | Not emitted (join resource details) | Missing: Recommended |
| BilledCost | Mandatory | Yes | Present |
| BillingAccountId | Mandatory | Yes (billing profile for MCA) | Present |
| BillingAccountName | Mandatory | Yes | Present |
| BillingAccountType | Conditional | Yes | Present |
| BillingCurrency | Mandatory | Yes | Present |
| BillingPeriodEnd | Mandatory | Yes (exclusive) | Present |
| BillingPeriodStart | Mandatory | Yes | Present |
| CapacityReservationId | Conditional | Not emitted (copy from x_SkuDetails) | Missing: Conditional |
| CapacityReservationStatus | Conditional | Not emitted (derive) | Missing: Conditional |
| ChargeCategory | Mandatory | Yes | Present |
| ChargeClass | Mandatory | Yes | Present |
| ChargeDescription | Mandatory | Yes (null for some edge records) | Present, deviation to fix |
| ChargeFrequency | Recommended | Yes | Present |
| ChargePeriodEnd | Mandatory | Yes (exclusive) | Present |
| ChargePeriodStart | Mandatory | Yes | Present |
| CommitmentDiscountCategory | Conditional | Yes | Present |
| CommitmentDiscountId | Conditional | Yes | Present |
| CommitmentDiscountName | Conditional | Yes | Present |
| CommitmentDiscountQuantity | Conditional | Not emitted (derive) | Missing: Conditional |
| CommitmentDiscountStatus | Conditional | Yes | Present |
| CommitmentDiscountType | Conditional | Yes | Present |
| CommitmentDiscountUnit | Conditional | Not emitted (derive) | Missing: Conditional |
| ConsumedQuantity | Conditional | Yes | Present |
| ConsumedUnit | Conditional | Yes | Present |
| ContractedCost | Mandatory | Yes (0 for Marketplace, some reservation usage) | Present, deviation to fix |
| ContractedUnitPrice | Conditional | Yes (0 for Marketplace, some reservation usage) | Present, deviation to fix |
| EffectiveCost | Mandatory | Yes | Present |
| InvoiceId | Recommended | Yes for MCA, not for EA | Present, deviation to fix |
| InvoiceIssuerName | Mandatory | Yes | Present |
| ListCost | Mandatory | Yes (0 for Marketplace, reservation usage) | Present, deviation to fix |
| ListUnitPrice | Conditional | Yes (0 for Marketplace, reservation usage) | Present, deviation to fix |
| PricingCategory | Conditional | Yes | Present |
| PricingCurrency | Conditional | Yes | Present |
| PricingCurrencyContractedUnitPrice | Conditional | Yes | Present |
| PricingCurrencyEffectiveCost | Conditional | Yes | Present |
| PricingCurrencyListUnitPrice | Conditional | Yes | Present |
| PricingQuantity | Mandatory | Yes | Present |
| PricingUnit | Mandatory | Yes | Present |
| ProviderName | Mandatory | Yes | Present |
| PublisherName | Mandatory | Yes (null for reservation/savings-plan-unused) | Present, deviation to fix |
| RegionId | Conditional | Yes | Present |
| RegionName | Conditional | Yes (cleansed to ARM) | Present |
| ResourceId | Conditional | Yes (lowercased) | Present |
| ResourceName | Conditional | Yes (casing may vary) | Present, deviation to fix |
| ResourceType | Conditional | Yes | Present |
| ServiceCategory | Mandatory | Yes (custom mapping, incomplete) | Present |
| ServiceName | Mandatory | Yes (empty for some edge records) | Present, deviation to fix |
| ServiceSubcategory | Recommended | Yes | Present |
| SkuId | Conditional | Yes (null when no price-sheet match) | Present |
| SkuMeter | Conditional | Yes | Present |
| SkuPriceDetails | Conditional | Not emitted (use x_SkuDetails) | Missing: Conditional |
| SkuPriceId | Conditional | Yes (null when no price-sheet match) | Present |
| SubAccountId | Conditional | Yes (subscription) | Present |
| SubAccountName | Conditional | Yes | Present |
| SubAccountType | Conditional | Yes | Present |
| Tags | Conditional | Yes (JSON key-value; not x_-prefixed) | Present |

**Reading the tally:** 42 of 57 columns are present and broadly conformant. 9 are present with a deviation or partial-population issue to fix. 5 conditional columns are not currently emitted in the export (each with a documented workaround). 1 Recommended column (`AvailabilityZone`) is not emitted. Zero Mandatory columns are entirely absent. The counts total 57.

### 1.4 What is solved, and what remains

**Solved (the bulk of the schema):** every Mandatory column is present and populated for the common case, including the four cost columns (`BilledCost`, `EffectiveCost`, `ListCost`, `ContractedCost`), the date/period columns, account and sub-account identity, service classification, pricing quantity/unit, and provider/publisher/invoice-issuer identity. The dataset combines billed and effective cost in one row, carries the full commitment-discount family for applied discounts, and includes the v1.2 pricing-currency columns. Tags are emitted as JSON key-value pairs. This is a mature FOCUS export.

**Remaining, and none of it is a "data does not exist" gap:**

- **Cost columns zeroed on specific record types (partial-population, not absence):** `ListCost`/`ListUnitPrice` and `ContractedCost`/`ContractedUnitPrice` return 0 for EA/MCA Marketplace charges and certain reservation usage. The data exists in the price sheet; Microsoft's documented workaround is a price-sheet join. This is the single most material item, but it is scoped to specific record types, not the whole dataset, and the values are reconcilable rather than missing.
- **Conditional columns not yet emitted (plumbing, with workarounds):** `CapacityReservationId`/`Status`, `CommitmentDiscountQuantity`/`Unit`, and `SkuPriceDetails` are not in the FOCUS 1.2-preview export. Each has a documented derivation from `x_SkuDetails` or existing quantities. `AvailabilityZone` (Recommended) is not emitted and can be joined from resource details.
- **Edge-case nulls on Mandatory columns:** `ServiceName` is empty for a handful of record types (EA Marketplace purchases, MCA reservation/savings-plan purchases, rounding adjustments, MACC shortfall, Azure credits); `ChargeDescription` is null for savings-plan-unused and non-SKU charges; `PublisherName` is null for reservation/savings-plan-unused records. All have documented substitute values.

### 1.5 Deviations to fix

- **Cost zeros on Marketplace and reservation records:** populate `ListCost`, `ListUnitPrice`, `ContractedCost`, `ContractedUnitPrice` for all record types so no price-sheet join is required.
- **`PublisherName` nulls:** default to "Microsoft" for reservation, reservation purchase, and savings-plan-unused records.
- **`ServiceName` empties:** fill from `PublisherName` or `x_SkuMeterSubcategory` for the affected record types.
- **`ChargeDescription` nulls:** provide a computed description for savings-plan-unused and non-SKU charges.
- **`InvoiceId` on EA:** not populated for Enterprise Agreement accounts (Recommended column; present for MCA).
- **`ResourceName` casing:** may not match original case; lowercase for consistent grouping.
- **Tags not `x_`-prefixed:** provider-specified tags are emitted without the `x_` prefix that FOCUS expects for provider-defined tag keys.
- **`SkuPriceId` non-uniqueness:** does not always identify a single price and has no direct price-sheet equivalent; documented join keys are provided.

**Already done right:** FOCUS column IDs used natively, JSON key-value tags, ISO 8601 exclusive-end dates, billing currency for all costs, ARM-consistent region names, `x_`-prefixed extension columns, actual and amortized cost combined in a single dataset.

---

## Part 2: The path forward

### 2.1 Which FOCUS version to target

Microsoft ships v1.2 today (labeled "1.2-preview"). The current certification baseline is v1.2, so the shipped version matches the baseline. The build target for maturation is v1.3 (ratified 2025-12-05, which deprecates `Provider`/`Publisher` and adds the Contract Commitment dataset and split-cost allocation) and v1.4 (ratified 2026-06-04, which removes `Provider`/`Publisher` and adds Invoice Detail and billing-period datasets). Microsoft should first move the v1.2 dataset from preview to GA, then track v1.3/v1.4.

### 2.2 What certification requires

FOCUS conformance for data generators runs through the FinOps Foundation. The current badge is "FinOps Certified FOCUS v1.2 Conformant." The get-started page lists Microsoft Azure as a data generator and links to Microsoft's own conformance summary and full report; it does not, on that page, assert a formal FinOps certification designation, so none is claimed here. The deliverables for the program are a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report. Microsoft already publishes the mapping-equivalent (the FOCUS dataset schema and convert/mapping guides) and its own Conformance Summary and full Conformance Report, which is exactly the seed artifact the program expects. Contact for the RFI is member-cert@finops.org; membership is required for certification, though contributing to the spec is open and free. Tooling: the FOCUS Validator (checks data against the Requirements Model), the FOCUS Converter, and the machine-readable FOCUS Requirements Model.

### 2.3 Phased roadmap

**Phase 0: Validate what exists.** Run a representative export (spanning EA and MCA, usage plus reservation plus savings-plan plus Marketplace records) through the FOCUS Validator against the v1.2 Requirements Model to confirm Microsoft's self-reported 94% and catch anything the manual pass missed.

**Phase 1: Close the cost-column zeros.** Populate `ListCost`/`ListUnitPrice` and `ContractedCost`/`ContractedUnitPrice` directly in the FOCUS export for Marketplace and reservation records so consumers do not need a price-sheet join. This is the highest-value residual item.

**Phase 2: Emit the not-yet-included conditional columns.** Add `CapacityReservationId`/`Status`, `CommitmentDiscountQuantity`/`Unit`, and `SkuPriceDetails` to the export, sourced from the same `x_SkuDetails` data the documented workarounds already use.

**Phase 3: Fix value and format deviations.** Backfill `PublisherName`, `ServiceName`, and `ChargeDescription` for the edge record types; add `x_` prefixing to provider tags; populate `InvoiceId` for EA where feasible; normalize `ResourceName` casing.

**Phase 4: Mature the version and certify.** Move v1.2 from preview to GA, submit for the FinOps Certified FOCUS v1.2 Conformant program, then track v1.3 (drop `Provider`/`Publisher`, add Contract Commitment and split allocation) and v1.4.

### 2.4 FOCUS Use Cases unlocked

Because Azure already emits day-level, resource- and tag-attributed FOCUS data with the full cost family, most FOCUS Use Cases work today: cost allocation by tag, subscription, and service; anomaly detection; commitment-discount utilization and coverage (via the commitment family and `CommitmentDiscountStatus`); effective-vs-billed reconciliation; and multi-currency reporting (via the pricing-currency columns). Use cases needing the not-yet-emitted columns wait on Phase 2: capacity-reservation utilization (needs `CapacityReservationId`/`Status`) and commitment-discount normalized-quantity analysis (needs `CommitmentDiscountQuantity`/`Unit`). List-price savings analysis on Marketplace and reservation records is fully clean only after Phase 1.

---

## Part 3: Immediate next steps

1. Adopt the export as-is: create a Cost Management export using the FOCUS template to Azure Storage; it is a shipping v1.2 dataset.
2. Apply Microsoft's documented workarounds for the known gaps (price-sheet joins for zeroed cost columns; null substitutions for `PublisherName`/`ServiceName`/`ChargeDescription`).
3. Run a representative sample through the FOCUS Validator to confirm the 94% conformance figure in your own tenant.
4. For Microsoft: prioritize populating the cost columns for all record types and emitting the three not-yet-included conditional column families, then move v1.2 from preview to GA.

---

## Confidence summary

- **Version shipped (v1.2):** high confidence. The get-started page states "Version Supported: v1.2" and Microsoft's conformance documentation is written against the FOCUS 1.2 specification.
- **"1.2-preview" label and 94% self-reported conformance:** high confidence, quoted directly from Microsoft's FOCUS Conformance Summary (last updated 2026-02-11).
- **Column-by-column population statuses:** high confidence for the columns named in Microsoft's conformance summary; medium confidence for columns marked simply "Present," which are inferred from the FOCUS dataset schema and the What-is-FOCUS overview rather than a row-level validation run.
- **Feature levels:** high confidence. Verified against the live FOCUS v1.2 column set via the FOCUS MCP on 2026-07-01; bundled cache (stamp 2026-06-23) was current, no refresh required.
- **No formal certification asserted:** the get-started page does not state a FinOps Certified FOCUS designation for Azure, so none is claimed. The "Conformant" readiness band reflects the shipping FOCUS export reviewed, not a formal certification result.
- **Overall verdict (Conformant band):** high confidence that Azure ships a substantially complete FOCUS v1.2 export today; the residual gaps are narrow, mostly conditional, and each is documented with a workaround.

---

## Sources

- FOCUS get-started page for Microsoft Azure: https://focus.finops.org/get-started/microsoft/
- Microsoft, "What is FOCUS?" overview: https://learn.microsoft.com/en-us/cloud-computing/finops/focus/what-is-focus
- Microsoft FOCUS Conformance Summary (94% score, 1.2-preview): https://learn.microsoft.com/en-us/cloud-computing/finops/focus/conformance-summary
- Microsoft FOCUS full Conformance Report: https://learn.microsoft.com/en-us/cloud-computing/finops/focus/conformance-full-report
- Microsoft Cost Management FOCUS dataset schema: https://learn.microsoft.com/en-us/azure/cost-management-billing/dataset-schema/cost-usage-details-focus
- Cost Management exports tutorial (FOCUS template): https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/tutorial-improved-exports
- FOCUS Specification (column set and feature levels, v1.2): https://focus.finops.org/focus-specification/v1-2/
- FOCUS Column Library via FOCUS MCP (verified 2026-07-01)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
