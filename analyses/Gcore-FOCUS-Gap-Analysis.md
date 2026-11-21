# Gcore Edge Cloud and FOCUS: Compliance Gap and Adoption Roadmap

*Analysis run: June 30, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

Prepared: 2026-06-30
Source analyzed: Gcore Cloud Cost Report and Reservation Cost Report (Detailed CSV, Summary/Totals CSV), Cost Reports API, and Cloud Billing documentation.
FOCUS baseline: v1.2 (certification baseline). Build target: v1.4 (latest ratified, 2026-06-04).

## Executive summary

Gcore's Cost Report is a resource-level, sub-monthly usage feed with a strong allocation backbone: it carries a resource name, UUID, resource type, region, project, key-value tags, usage quantity with a consumption unit, per-resource cost, and currency. That gives Gcore a head start on the columns that FOCUS uses for identity and attribution. The dataset is not yet FOCUS-shaped (native column names, no FOCUS enums, no FOCUS column IDs), and the central work is a cost reconciliation problem, not a missing-data problem.

The single most important finding is the split between two reports. The Cost Report values every resource at Pay-As-You-Go (PAYG) list rates and explicitly does not apply commit discounts. The Reservation Cost Report carries the commit and overcommit costs that produce the customer's actual (effective) spend, but only as monthly aggregates with no per-resource breakdown. So `ListCost` is readily available at resource grain, while `EffectiveCost` and `ContractedCost` are a substantive reconciliation gap: producing them at line grain means allocating commit discounts from the reservation report back onto the PAYG usage lines.

- Total FOCUS columns (v1.2): 57
- Already present (mappable from the source, including format fixes): 22
- Substantive Mandatory gaps: 3 of 13 missing Mandatory columns
- Deviations to fix on present columns: 7

Recommendation: target v1.2 for the certification baseline and build toward v1.4. Phase 1 should resolve the cost columns by reconciling the Reservation Cost Report against the resource-level Cost Report, then add the trivial Mandatory plumbing (`ChargeCategory`, `ChargeClass`, billing/charge period bounds, `ServiceCategory`, `InvoiceIssuerName`). The allocation and granularity foundations are already in good shape.

RAG readiness: Cost Partial, Granularity Strong, Allocation Strong, Coverage Partial, FOCUS shape Partial. Overall band: Not yet aligned (per public docs).

## Part 1: The conformance gap

### 1.1 The data source

Gcore Edge Cloud exposes cost and usage through two reports, both viewable in the control panel, downloadable as CSV, and reachable through the Cost Reports API.

The Cost Report is the primary resource-level feed. Each row describes a billable resource over a selected period and carries: Service (resource type name), UUID (resource identifier; some resources such as IP addresses have none), Feature (a billing identifier combining resource type, configuration, region, and pricing model), Tags (user tags plus system-generated tags), Service_name (the resource's display name), Region_id and Region_name, Project_id and Project_name, First_seen and Last_seen (when the resource began and stopped generating cost), Period_from and Period_to (the selected reporting window), Units (the consumption unit, for example gbminutes, minutes, MLS, bytes, GBS), Value (the usage quantity), Error, Cost, Currency, Attached_to, and Port_id. The report can be filtered by project, region, resource type, and consumption period (up to one month), and can include deleted projects and regions.

Granularity is the dataset's strength. Resources are metered per minute, costs are stated per resource, and First_seen/Last_seen plus the selectable period give sub-monthly time bounds. The documentation notes that the last hour may be incomplete, which is consistent with a near-real-time meter rather than a monthly invoice snapshot.

The key limitation is cost basis. The Cost Report values everything at PAYG rates and states plainly that, if the account has active commitments, "the prices shown in this report won't reflect your actual costs because commit discounts are not applied." Actual cost lives in the separate Reservation Cost Report, which accounts for commitments but shows only aggregated monthly data per resource type and region (Commit value, Commit cost, Overcommit cost, Total cost), with no per-resource rows.

Billing context: all clients are on a PAYG plan billed per minute; currency is EUR or USD depending on the account's provider entity; charges are deducted in threshold portions against a prepaid balance or payment method; invoices are available in the control panel. Projects act as the sub-account-level grouping within a billing account.

### 1.2 How conformance is judged

FOCUS assigns every column a feature level: Mandatory (must be present and populated), Conditional (required when the provider's model triggers the condition), Recommended (encouraged), or Optional. Conformance is judged column by column against the spec's Content Constraints and the machine-readable Requirements Model. A dataset conforms when every Mandatory column is present and correctly populated, every applicable Conditional column is handled, and present columns use the correct types, FOCUS enum values, and key-value tag format. Feature levels in this report were verified against the FOCUS v1.2 specification rather than recalled from memory.

### 1.3 Column-by-column status

Feature levels verified against the FOCUS Specification v1.2. Status legend: Present (emitted and aligned); Present, deviation to fix (emitted, wrong format or invalid value); Missing: Mandatory (required, absent, blocks conformance); Missing: Recommended (encouraged, absent); Missing: Conditional (required when the model triggers it, absent); N/A: null valid (does not apply to Gcore's model, should exist and be null).

| FOCUS Column | Level | In the source? | Status |
|---|---|---|---|
| AvailabilityZone | R | No (regions only, no zones) | N/A: null valid |
| BilledCost | M | Partial (PAYG cost in Cost Report; actual cost split into Reservation report) | Missing: Mandatory |
| BillingAccountId | M | Implicit (account context, not a Cost Report column) | Missing: Mandatory |
| BillingAccountName | M | Implicit (account context) | Missing: Mandatory |
| BillingAccountType | C | No | Missing: Conditional |
| BillingCurrency | M | Currency | Present, deviation to fix |
| BillingPeriodEnd | M | No (Period_to is a query window, not a billing period) | Missing: Mandatory |
| BillingPeriodStart | M | No (Period_from is a query window) | Missing: Mandatory |
| CapacityReservationId | C | No | N/A: null valid |
| CapacityReservationStatus | C | No | N/A: null valid |
| ChargeCategory | M | No (derivable: Usage vs reservation commit/overcommit) | Missing: Mandatory |
| ChargeClass | M | No (nullable; populate on corrections via Error field) | Missing: Mandatory |
| ChargeDescription | M | Service_name / Feature | Present, deviation to fix |
| ChargeFrequency | R | No | Missing: Recommended |
| ChargePeriodEnd | M | Last_seen / Period_to | Present, deviation to fix |
| ChargePeriodStart | M | First_seen / Period_from | Present, deviation to fix |
| CommitmentDiscountCategory | C | Partial (Reservation Cost Report) | Missing: Conditional |
| CommitmentDiscountId | C | Partial (Reservation Cost Report) | Missing: Conditional |
| CommitmentDiscountName | C | Partial (Reservation Cost Report) | Missing: Conditional |
| CommitmentDiscountQuantity | C | Commit value (Reservation report) | Missing: Conditional |
| CommitmentDiscountStatus | C | Partial (commit vs overcommit usage) | Missing: Conditional |
| CommitmentDiscountType | C | Partial (Reservation Cost Report) | Missing: Conditional |
| CommitmentDiscountUnit | C | Units (Reservation report) | Missing: Conditional |
| ConsumedQuantity | C | Value | Present |
| ConsumedUnit | C | Units | Present |
| ContractedCost | M | Partial (commit cost in Reservation report) | Missing: Mandatory |
| ContractedUnitPrice | C | No | Missing: Conditional |
| EffectiveCost | M | Partial (requires reconciling commit discounts to usage lines) | Missing: Mandatory |
| InvoiceId | R | No (invoices exist; not in the usage feed) | Missing: Recommended |
| InvoiceIssuerName | M | No (constant: Gcore entity) | Missing: Mandatory |
| ListCost | M | Cost (PAYG rate) | Present |
| ListUnitPrice | C | Derivable (Cost / Value for flat-rate SKUs) | Missing: Conditional |
| PricingCategory | C | No (PAYG; commit on Reservation report) | Missing: Conditional |
| PricingCurrency | C | Currency | Present, deviation to fix |
| PricingCurrencyContractedUnitPrice | C | No | Missing: Conditional |
| PricingCurrencyEffectiveCost | C | No | Missing: Conditional |
| PricingCurrencyListUnitPrice | C | No | Missing: Conditional |
| PricingQuantity | M | Value (derivable for flat-rate SKUs) | Present |
| PricingUnit | M | Units | Present |
| ProviderName | M | No (constant: Gcore) | Missing: Mandatory |
| PublisherName | M | No (constant: Gcore) | Missing: Mandatory |
| RegionId | C | Region_id | Present |
| RegionName | C | Region_name | Present |
| ResourceId | C | UUID | Present |
| ResourceName | C | Service_name | Present |
| ResourceType | C | Service / Feature | Present |
| ServiceCategory | M | No (derivable from resource type) | Missing: Mandatory |
| ServiceName | M | Service / Feature | Present, deviation to fix |
| ServiceSubcategory | R | No | Missing: Recommended |
| SkuId | C | Feature | Present |
| SkuMeter | C | Units / Feature | Present |
| SkuPriceDetails | C | No | Missing: Conditional |
| SkuPriceId | C | Feature | Present |
| SubAccountId | C | Project_id | Present |
| SubAccountName | C | Project_name | Present |
| SubAccountType | C | No | Missing: Conditional |
| Tags | C | Tags | Present, deviation to fix |

Reading the tally: of 57 v1.2 columns, 22 map from the source (15 clean and 7 present with deviations to fix), 13 Mandatory columns are missing (3 of them substantive, 10 trivial or constant), 3 Recommended are missing, 16 Conditional are missing because the condition applies, and 3 Conditional columns are N/A because Gcore's model does not trigger them. Counting: 15 clean present + 7 deviation + 13 Missing: Mandatory + 3 Missing: Recommended + 16 Missing: Conditional + 3 N/A = 57.

### 1.4 What's solved, and what remains

Already in good shape: the allocation and granularity foundations. Resource identity (`ResourceId` from UUID, `ResourceName` from Service_name, `ResourceType` from Service/Feature), region (`RegionId`, `RegionName`), project as sub-account (`SubAccountId`, `SubAccountName`), usage (`ConsumedQuantity`, `ConsumedUnit`, `PricingQuantity`, `PricingUnit`), SKU identifiers from Feature (`SkuId`, `SkuMeter`, `SkuPriceId`), and `ListCost` from the PAYG Cost figure all map cleanly. This is a meaningful starting position.

Substantive gaps (real data that requires work to produce):

- `EffectiveCost` and `ContractedCost`: the actual, commitment-aware cost does not exist at resource grain. The Cost Report is PAYG list only; commit and overcommit costs live in the monthly-aggregate Reservation Cost Report. Producing per-line effective and contracted cost requires allocating reservation discounts back onto the usage lines. This is the list-cost trap in its classic form: discounts genuinely exist but are applied in a separate report, so the cost columns are substantive, not a copy of `ListCost`.
- `BilledCost`: what the customer is actually charged after commit discounts and threshold-based balance deductions. As with `EffectiveCost`, it cannot be read off the PAYG Cost Report and must be reconciled from the commitment and invoice layer.

Trivial gaps (Mandatory but mechanical to add):

- `ProviderName` and `PublisherName`: constants ("Gcore"). Note these are deprecated in v1.3 and removed in v1.4, so they are baseline-only plumbing.
- `InvoiceIssuerName`: a constant (the Gcore billing entity).
- `ServiceCategory`: derivable by mapping each resource type to a FOCUS `ServiceCategory` enum value (Compute, Storage, Networking, AI and Machine Learning for GPU/IPU, and so on).
- `ChargeCategory`: derivable (Usage for metered consumption; commit and overcommit lines from the Reservation report map to Usage or Purchase per FOCUS rules).
- `ChargeClass`: nullable; populate "Correction" only when a line corrects a prior charge (the Error field is a candidate signal).
- `BillingAccountId` and `BillingAccountName`: present implicitly in account context but not as Cost Report columns; they must be stamped onto every row.
- `BillingPeriodStart` and `BillingPeriodEnd`: the calendar billing period bounds, distinct from the query window (Period_from/Period_to) and the resource lifespan (First_seen/Last_seen).

### 1.5 Deviations to fix

These columns carry the right data in a shape FOCUS would reject:

- `Tags`: the source mixes user tags and system-generated tags in a Tags column. FOCUS requires key-value pairs. Confirm the export emits structured key-value pairs rather than a flat string or array, and split system tags into `x_`-prefixed custom columns if they are not true resource tags.
- `BillingCurrency` and `PricingCurrency`: Currency must be a single ISO 4217 three-letter code (EUR or USD). Confirm the export uses the code, not a symbol or word.
- `ChargePeriodStart` and `ChargePeriodEnd`: First_seen/Last_seen (or Period_from/Period_to) must be emitted as ISO 8601 timestamps with inclusive-start, exclusive-end semantics, mapped to the charge period rather than the query window.
- `ChargeDescription` and `ServiceName`: Service_name and Feature carry the content, but FOCUS expects `ServiceName` to be the service offering and `ChargeDescription` to be a human-readable line summary. Separate the two cleanly rather than reusing one native field for both.

Done right already: the resource, region, project, usage, and SKU columns map without transformation beyond renaming, which is the bulk of the allocation surface.

## Part 2: The path forward

### 2.1 Which FOCUS version to target

Baseline to v1.2, the current certification baseline, and build toward v1.4 (ratified 2026-06-04). Two version notes matter for Gcore. First, `ProviderName` and `PublisherName` are Mandatory in v1.2, deprecated in v1.3, and removed in v1.4, so treat them as baseline-only and do not invest in them for the long term. Second, v1.4 adds Invoice Detail and billing-period datasets aimed at reconciliation, which align well with Gcore's two-report structure and would give the commit and invoice layer a native home. Validator support for v1.4 is expected later in 2026; v1.3 is supported today.

### 2.2 What certification requires

FOCUS conformance for data generators runs through the FinOps Foundation under the "FinOps Certified FOCUS v1.2 Conformant" program (contact member-cert@finops.org for the RFI). Membership is required for certification, though contributing to the spec is open and free. The deliverables are a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report, which this analysis seeds. Open-source tooling supports the work: the FOCUS Validator (checks data against the Requirements Model), the FOCUS Converter (provider-native to FOCUS), and the FOCUS Requirements Model (machine-readable MUST/SHOULD/MAY rules).

### 2.3 Phased roadmap

Phase 0, validate what exists: run a sample of the Detailed Cost Report CSV through the FOCUS Validator after a first-pass rename, and confirm scope (Cost Report plus Reservation Cost Report) and target version.

Phase 1, close the Mandatory gaps. The headline work is cost reconciliation: join the monthly Reservation Cost Report (commit cost, overcommit cost, commit value) to the resource-level PAYG Cost Report to produce `EffectiveCost`, `ContractedCost`, and `BilledCost` at line grain. In parallel, add the trivial Mandatory plumbing: stamp `BillingAccountId`/`BillingAccountName`, `ProviderName`/`PublisherName`, and `InvoiceIssuerName` constants; derive `ServiceCategory` from resource type; derive `ChargeCategory`; carry `ChargeClass` (nullable); and emit true `BillingPeriodStart`/`BillingPeriodEnd`.

Phase 2, fix deviations: structure `Tags` as key-value pairs, normalize currency to ISO 4217, emit ISO 8601 charge periods with correct interval semantics, and separate `ChargeDescription` from `ServiceName`.

Phase 3, round out Conditional and Recommended columns: surface the commitment-discount family (`CommitmentDiscountId`, `Name`, `Type`, `Category`, `Status`, `Quantity`, `Unit`) by promoting Reservation Cost Report data to line level; add `ListUnitPrice` and `PricingCategory`; add `BillingAccountType`/`SubAccountType`; and add the Recommended `ChargeFrequency`, `InvoiceId`, and `ServiceSubcategory`.

Phase 4, mature toward v1.4: drop the deprecated `ProviderName`/`PublisherName`, adopt the Invoice Detail and billing-period datasets to formalize the commit/invoice layer, and certify or re-certify.

### 2.4 FOCUS Use Cases unlocked

Unlocked as soon as the dataset is renamed and validated (Phase 0 to 1), because resource, tag, project, and sub-monthly data already exist: cost reporting and visualization by service and region; allocation and showback by project (as sub-account) and by tag; resource-level usage and rightsizing analysis; and anomaly detection on daily cost movement.

Unlocked once the cost columns are reconciled (Phase 1 to 2): effective-cost and actuals-based reporting; budgeting and variance against real spend; commitment utilization and coverage analysis (drawing on the Reservation Cost Report); and invoice reconciliation once billing-period datasets land.

Out of scope for Gcore's current model: capacity-reservation use cases beyond the commit/reservation mechanic Gcore already offers, and any use case requiring a marketplace publisher distinct from the provider, since Gcore is both provider and publisher.

## Part 3: Immediate next steps

1. Pull a representative Detailed Cost Report CSV and a matching Reservation Cost Report for an account that holds active commitments, so the reconciliation logic is exercised against real overcommit lines.
2. Draft the native-to-FOCUS column mapping from the table in section 1.3, recording the rename and the derivation rule for each Mandatory column.
3. Design the cost reconciliation that allocates commit and overcommit costs from the monthly Reservation report onto the resource-level PAYG lines to yield `EffectiveCost`, `ContractedCost`, and `BilledCost`.
4. Run the first-pass output through the FOCUS Validator and triage failures by feature level.
5. Contact member-cert@finops.org for the RFI if pursuing the "FinOps Certified FOCUS v1.2 Conformant" designation.

## Confidence summary

- Source field set (Cost Report and Reservation Cost Report columns): high confidence, taken directly from current Gcore Cloud documentation.
- The cost split (PAYG list in the Cost Report, commit/effective cost only in the monthly Reservation report) and its classification as a substantive gap: high confidence, stated explicitly in Gcore's documentation.
- Granularity (per-minute metering, resource-level rows, sub-monthly periods): high confidence.
- Feature levels for all 57 v1.2 columns: high confidence; verified against the FOCUS v1.2 specification via the FOCUS column reference, cross-checked against the live FOCUS column set on 2026-06-30 (57 columns confirmed; `ProviderName`/`PublisherName` deprecated v1.3, removed v1.4; bundled table current as of 2026-06-23, no refresh required).
- Exact CSV value formats (tag structure, currency representation, timestamp format): medium confidence; the column meanings are documented but the literal serialization should be confirmed against a real export before the deviation fixes are finalized.
- Mapping of `Feature` to the SKU column family and `Project` to sub-account: medium-high confidence; `Feature` bundles type, configuration, region, and pricing model, so it may need decomposition rather than a single mapping.
- Overall readiness band (Emerging): medium-high confidence; reflects the data source reviewed, not a formal certification result.

## Sources

- Gcore Docs, Cost reports: https://gcore.com/docs/cloud/getting-started/view-statistics-on-expenses
- Gcore Docs, Billing: https://gcore.com/docs/cloud/billing
- Gcore Cost Reports API: https://gcore.com/docs/api-reference/cloud (Cost-Reports tag)
- FOCUS Specification v1.2: https://focus.finops.org/focus-specification/v1-2/
- FOCUS column reference and Requirements Model: https://focus.finops.org/
- FinOps Foundation FOCUS conformance program: member-cert@finops.org

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
