# STACKIT and FOCUS: Conformance Gap and Adoption Roadmap

*Analysis run: July 6, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

Provider: STACKIT (Schwarz Digits, Schwarz Group), the European sovereign cloud.
Product in scope: STACKIT native FOCUS report (Beta) exported to Object Storage, complemented by the Cost API (v3) and Invoice Exporter API (v1).
Prepared: 2026-07-06.
Source analyzed: STACKIT public documentation (Costs and billing, FOCUS report Beta, Resource labelling, Cost Dashboard) and the downloadable STACKIT example FOCUS report (CSV, 1,000 sample rows).
FOCUS baseline for scoring: v1.2 (current certification baseline). Build target: v1.4 (latest).

STACKIT is not listed on focus.finops.org/get-started, so it is not a Supported (certified) provider. This report assesses readiness only.

## Executive summary

STACKIT already generates a native FOCUS report. The Beta export emits all 57 FOCUS v1.2 columns by column ID, plus four provider-specific `x_` extension columns for the STACKIT project and customer hierarchy. In the example dataset the four cost columns reconcile exactly (BilledCost = EffectiveCost = ListCost = ContractedCost), currency is EUR, enum values are valid, resource identity is present, and tags are emitted as a key-value object. This is a near-conformant dataset, not a from-scratch build.

The remaining work is narrow: STACKIT states GA is planned for H1/2026 and lists FOCUS conformant report certification as a planned feature. The substantive gaps are two Conditional families that STACKIT does not yet populate but that the platform hierarchy could support (SubAccount attribution) and resource naming (ResourceName is documented as planned). None of the Mandatory columns is a substantive data gap: every Mandatory column is populated in the sample.

Four-stat summary:
- 57 FOCUS columns (v1.2)
- 57 present (all emitted; some Conditional columns null pending data)
- 0 of 21 Mandatory gaps are substantive (all 21 Mandatory columns populated)
- 1 deviation to review (Tags representation, see 1.5)

Readiness (data source reviewed, not a certification result):
- Cost: Strong
- Granularity: Strong
- Allocation: Partial
- Coverage: Strong
- FOCUS shape: Strong
- Overall band: Partially aligned

Recommendation: Run the example export and a live export through the FOCUS Validator, confirm the Tags representation against the Requirements Model, populate ResourceName and the SubAccount family (or document them as null-valid for the single-billing-account model), then pursue FinOps Certified FOCUS conformance.

---

## Part 1: The conformance gap

STACKIT is unusual among the providers assessed in this series: it ships a native FOCUS report rather than a proprietary schema that must be mapped. The gap analysis therefore reads less like a mapping exercise and more like a conformance review of an existing FOCUS dataset.

### 1.1 The data source

STACKIT exposes cost and usage data through three mechanisms:

- FOCUS report (Beta): a scheduled export in FOCUS format. STACKIT states it supports FOCUS versions 1.1 and 1.2, generates the report at billing-account level, supports all Mandatory (MUST) columns, and adds STACKIT-specific columns using the `x_` prefix. Reports are delivered daily at 12:00 UTC to the customer's own S3-compatible Object Storage bucket as compressed (gzip) CSV. The customer picks daily or monthly frequency and month-to-date or day-to-date reporting.
- Cost Dashboard and Cost API (v3): a per-project, per-customer-account, and per-partner cost view with daily granularity (previous day available after 07:30 UTC), SKU-level breakdown, and quantity consumed. Data is UTC and may change during the month, so historical requests are recommended from the first of the month to the prior day.
- Invoice Exporter API (v1): list-invoices and get-invoice-details endpoints returning dates, customer details, totals, and taxes.

Granularity: daily charge records with SKU-level and resource-level detail. This satisfies the FOCUS expectation of sub-monthly charge periods.

Format: the FOCUS export is a gzip CSV keyed by billing period and creation timestamp. Currency is EUR throughout. Timestamps and periods follow the FOCUS conventions.

Key limitations observed:
- Scope is a single billing account per customer account today, so multi-account roll-up is not yet exercised.
- SubAccount columns are present but null in the sample; the project or folder hierarchy is carried in `x_` columns rather than the FOCUS SubAccount family.
- ResourceName is present but empty in the sample; STACKIT documents it as a planned addition.
- The Beta status means the schema may still change before GA.

### 1.2 How conformance is judged

FOCUS assigns every column a feature level: Mandatory (must be present and populated where applicable), Conditional (required when the provider's model triggers the condition), Recommended (encouraged), or Optional. Conformance is judged column by column against the Content Constraints in the specification and, objectively, by the FOCUS Validator against the machine-readable Requirements Model.

Feature levels in this report were verified against the FOCUS v1.2 specification. Custom, provider-specific columns are permitted when prefixed `x_`, which STACKIT uses correctly.

### 1.3 Column-by-column status

Status legend:
- Present: emitted and aligned.
- Present, deviation to fix: emitted, wrong format or invalid value.
- Missing: Mandatory: required and absent (blocks conformance).
- Missing: Recommended: encouraged, absent (does not block conformance).
- Missing: Conditional: required when the model triggers the condition, absent and the condition applies.
- N/A: null valid: Conditional or Recommended column that does not apply to STACKIT's model; present and null.

Feature levels verified against the FOCUS Specification v1.2.

| FOCUS Column | Level | In the source? | Status |
|---|---|---|---|
| AvailabilityZone | Recommended | Present, null in sample (AZ-level billing exists) | N/A: null valid |
| BilledCost | Mandatory | Yes (0.021783, EUR) | Present |
| BillingAccountId | Mandatory | Yes | Present |
| BillingAccountName | Mandatory | Yes | Present |
| BillingAccountType | Conditional | Yes ("Billing Account") | Present |
| BillingCurrency | Mandatory | Yes (EUR) | Present |
| BillingPeriodEnd | Mandatory | Yes | Present |
| BillingPeriodStart | Mandatory | Yes | Present |
| CapacityReservationId | Conditional | Present, null (no capacity reservations) | N/A: null valid |
| CapacityReservationStatus | Conditional | Present, null | N/A: null valid |
| ChargeCategory | Mandatory | Yes ("Usage", valid enum) | Present |
| ChargeClass | Mandatory | Present, null (correction-only) | Present |
| ChargeDescription | Mandatory | Yes | Present |
| ChargeFrequency | Recommended | Yes ("Usage-Based", valid enum) | Present |
| ChargePeriodEnd | Mandatory | Yes | Present |
| ChargePeriodStart | Mandatory | Yes | Present |
| CommitmentDiscountCategory | Conditional | Present, null (no commitments) | N/A: null valid |
| CommitmentDiscountId | Conditional | Present, null | N/A: null valid |
| CommitmentDiscountName | Conditional | Present, null | N/A: null valid |
| CommitmentDiscountQuantity | Conditional | Present, null | N/A: null valid |
| CommitmentDiscountStatus | Conditional | Present, null | N/A: null valid |
| CommitmentDiscountType | Conditional | Present, null | N/A: null valid |
| CommitmentDiscountUnit | Conditional | Present, null | N/A: null valid |
| ConsumedQuantity | Conditional | Yes (240, "Gigabyte Hours") | Present |
| ConsumedUnit | Conditional | Yes ("Gigabyte Hours") | Present |
| ContractedCost | Mandatory | Yes (0.021783) | Present |
| ContractedUnitPrice | Conditional | Yes | Present |
| EffectiveCost | Mandatory | Yes (0.021783) | Present |
| InvoiceId | Recommended | Yes ("1004002901") | Present |
| InvoiceIssuerName | Mandatory | Yes ("STACKIT GmbH & Co KG") | Present |
| ListCost | Mandatory | Yes (0.021783) | Present |
| ListUnitPrice | Conditional | Yes | Present |
| PricingCategory | Conditional | Yes | Present |
| PricingCurrency | Conditional | Yes (EUR) | Present |
| PricingCurrencyContractedUnitPrice | Conditional | Yes | Present |
| PricingCurrencyEffectiveCost | Conditional | Yes | Present |
| PricingCurrencyListUnitPrice | Conditional | Yes | Present |
| PricingQuantity | Mandatory | Yes (240, "Gigabyte Hours") | Present |
| PricingUnit | Mandatory | Yes ("Gigabyte Hours") | Present |
| ProviderName | Mandatory (deprecated v1.3, removed v1.4) | Yes ("STACKIT GmbH & Co KG") | Present |
| PublisherName | Mandatory (deprecated v1.3, removed v1.4) | Yes ("STACKIT GmbH & Co KG") | Present |
| RegionId | Conditional | Yes ("eu01") | Present |
| RegionName | Conditional | Yes ("eu01") | Present |
| ResourceId | Conditional | Yes (resource UUID + component) | Present |
| ResourceName | Conditional | Present, empty in sample (documented as planned) | Missing: Conditional |
| ResourceType | Conditional | Yes ("Storage") | Present |
| ServiceCategory | Mandatory | Yes ("Storage", valid enum) | Present |
| ServiceName | Mandatory | Yes | Present |
| ServiceSubcategory | Recommended | Yes ("Block Storage") | Present |
| SkuId | Conditional | Yes ("ST-0065901") | Present |
| SkuMeter | Conditional | Present, empty in sample | Missing: Conditional |
| SkuPriceDetails | Conditional | Present | Present |
| SkuPriceId | Conditional | Present | Present |
| SubAccountId | Conditional | Present, null in sample | Missing: Conditional |
| SubAccountName | Conditional | Present, null in sample | Missing: Conditional |
| SubAccountType | Conditional | Present, null in sample | Missing: Conditional |
| Tags | Conditional | Yes (key-value object) | Present, deviation to review |

Reading the tally: all 21 Mandatory columns are present and populated, and none is a substantive data gap. All four Recommended columns (AvailabilityZone, ChargeFrequency, InvoiceId, ServiceSubcategory) are present, with AvailabilityZone null-valid for the sampled resource. Of the 32 Conditional columns, most are present and populated; the commitment-discount and capacity-reservation families are correctly null (STACKIT sells no commitment-based discounts or capacity reservations in this dataset); and a small set (ResourceName, SubAccount family, SkuMeter) is present but empty where the platform could supply data. One column, Tags, carries a representation worth confirming against the Requirements Model.

### 1.4 What's solved, and what remains

Solved:
- The cost columns. This is the finding that matters most. In the sample, BilledCost = EffectiveCost = ListCost = ContractedCost = 0.021783 EUR. STACKIT is pay-as-you-go with hourly metering and no commitment discounts, credits, or amortization in this dataset, so list, billed, effective, and contracted cost legitimately coincide. This is the benign case of equal cost columns, not the list-cost trap: there is no downstream invoice-time adjustment layer that the daily feed is failing to reconcile.
- Granularity. Daily charge records at SKU and resource level.
- FOCUS shape. Column IDs are correct, currency is ISO 4217 EUR, enum values sampled are valid (ChargeCategory "Usage", ChargeFrequency "Usage-Based", ServiceCategory "Storage"), and extension columns use the `x_` prefix.
- Coverage. Every Mandatory column populated and most applicable Conditional columns populated.

Remaining (all narrow, none blocking on cost):
- ResourceName: present but empty; STACKIT documents it as planned. This is the clearest substantive-but-small gap: the data exists in the platform and simply is not yet mapped into the export.
- SubAccount family (SubAccountId, SubAccountName, SubAccountType): present but null. STACKIT's allocation hierarchy (organization, folder, project) is currently carried in `x_ProjectId`, `x_ProjectName`, `x_CustomerAccountId`, and `x_CustomerAccountName` rather than in the FOCUS SubAccount columns. Deciding whether the STACKIT project maps to SubAccount is a modeling choice, not a missing-data problem.
- SkuMeter: present but empty in the sample; populate where a meter distinguishes SKU price points.

### 1.5 Deviations to review

- Tags: the export emits tags as a JSON object, correctly CSV-quoted, for example `{"team":"compliant-coders","department":"IT","product-id":"hello-world-app"}`. FOCUS represents tags as key-value pairs, and a JSON object of user labels is an accepted representation. Confirm against the Requirements Model that the serialization (a single JSON object string in the Tags column) matches the expected key-value structure, and that STACKIT-applied versus user-applied tag handling follows the current guidance. This is a representation check, not a known error.

What is already done right: correct column IDs, EUR currency, valid enums, resource identity, daily periods, and disciplined use of the `x_` prefix for the four extension columns. This is the shape a conformant dataset should have.

---

## Part 2: The path forward

### 2.1 Which FOCUS version to target

STACKIT supports v1.1 and v1.2 today and lists FOCUS 1.3 adoption as planned. Baseline conformance work against v1.2, which is the current certification baseline. Design toward v1.4: in v1.3 the ProviderName and Publisher columns are deprecated (removed in v1.4), and v1.4 adds Invoice Detail and billing-period datasets for reconciliation. Because STACKIT already ships InvoiceId in the export, the move to v1.4 reconciliation datasets is a natural next step rather than a rebuild.

### 2.2 What certification requires

FOCUS conformance for data generators runs through the FinOps Foundation. The badge has historically been "FinOps Certified FOCUS v1.2 Conformant"; confirm the current badge version against the program page before finalizing. Contact member-cert@finops.org for the RFI. Membership is required for certification, though contributing to the spec is open and free. Deliverables are a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report (this analysis is its seed). Tooling: the FOCUS Validator (checks data against the Requirements Model), the FOCUS Converter, and the FOCUS Requirements Model. STACKIT already publishes a downloadable example FOCUS report, which covers part of the public-sample-data deliverable.

### 2.3 Phased roadmap

Phase 0: validate what exists. Run the published example export and a live export through the FOCUS Validator against v1.2. Confirm scope, version, and the Tags representation against the Requirements Model. This is low effort because the dataset is already FOCUS-shaped.

Phase 1: close the small Conditional gaps. Populate ResourceName (documented as planned), decide and implement the SubAccount mapping for the STACKIT project or folder hierarchy (or document those columns as null-valid for the single-billing-account model), and populate SkuMeter where applicable.

Phase 2: confirm and lock representations. Resolve the Tags serialization question, confirm enum coverage across all ServiceCategory and ChargeCategory values the catalog can emit, and validate that periods are inclusive-start, exclusive-end.

Phase 3: exit Beta and certify. Reach GA (planned H1/2026), then pursue FinOps Certified FOCUS conformance with a conformant dataset, public sample, native-to-FOCUS mapping, and this gap report.

Phase 4: mature toward v1.4. Adopt v1.3 (dropping the deprecated ProviderName and Publisher path), then v1.4, adding the Invoice Detail and billing-period datasets for reconciliation. Re-certify against the then-current baseline.

### 2.4 FOCUS Use Cases unlocked

Available now, because daily, resource-level, SKU-level, EUR cost data with valid enums already exists:
- Analyze costs by service name.
- Analyze service costs by region.
- Analyze service costs month over month.
- Analyze resource costs by SKU.
- Analyze costs of components of a resource (the STACKIT price-component model maps directly).
- Compare resource usage month over month.
- Identify anomalous daily spending (by resource or project, adapted for the single-account model).
- Analyze tag coverage (once the Tags representation is confirmed).
- Determine Effective Savings Rate (trivially zero today, since effective equals list; the query still runs).

Unlocked by Phase 1 allocation work:
- Analyze cost per compute service for a subaccount and Analyze service costs by subaccount, once the STACKIT project or folder hierarchy is mapped to the SubAccount family (today these run against the `x_Project` columns instead).
- Compare billed cost per subaccount to budget.

Out of scope for STACKIT's current model:
- Commitment-discount coverage, effective-cost breakdown, and savings-rate-by-commitment use cases: STACKIT sells no commitment-based discounts in this dataset, so the commitment-discount family is null-valid.
- Capacity-reservation analysis: no capacity reservations in this dataset.
- Multi-currency allocation: STACKIT bills in EUR only.

---

## Part 3: Immediate next steps

1. Run the published example FOCUS report and a live export through the FOCUS Validator against v1.2 and record the results.
2. Confirm the Tags representation and the SubAccount versus `x_Project` modeling choice against the FOCUS Requirements Model.
3. Populate ResourceName in the export (documented as planned) and decide the SubAccount mapping.
4. On reaching GA, contact member-cert@finops.org for the FinOps Certified FOCUS RFI and assemble the four certification deliverables.
5. Plan the v1.3 then v1.4 migration, retiring the deprecated ProviderName and Publisher path and adding the reconciliation datasets.

---

## Confidence summary

- STACKIT emits a native FOCUS report supporting v1.1 and v1.2, at billing-account level, delivered daily to Object Storage as gzip CSV: high confidence, from STACKIT documentation and the downloadable example export.
- All 57 v1.2 columns present plus four `x_` extension columns; all 21 Mandatory columns populated in the sample: high confidence, verified directly against the example CSV header and sample rows.
- Cost columns reconcile (BilledCost = EffectiveCost = ListCost = ContractedCost) and this is the benign equal-cost case, not the list-cost trap: high confidence for the sampled pay-as-you-go usage; medium confidence that no product line anywhere introduces credits or adjustments that would separate the cost columns, since the sample is limited to usage rows.
- ResourceName, SubAccount family, and SkuMeter are present but empty in the sample: high confidence from the sample; ResourceName is documented by STACKIT as planned.
- Tags representation (JSON object) is an accepted key-value form pending a Requirements Model confirmation: medium confidence, flagged for validation rather than asserted conformant.
- Feature levels verified against the bundled v1.2 reference; the bundled table's SPEC_VERSIONS_AS_OF stamp (2026-06-23) was cross-checked against the live FOCUS spec pages (v1.2 current certification baseline, v1.4 latest, ratified 2026-06-04) and matched, so no refresh was required.
- STACKIT is not a Supported (certified) provider on focus.finops.org/get-started as of the prepared date: high confidence.
- Not a formal certification result. This score reflects the data source reviewed.

## Sources

- STACKIT docs, Understand cloud costs and billing: https://docs.stackit.cloud/platform/cost-and-billing/
- STACKIT docs, FOCUS report (Beta): https://docs.stackit.cloud/platform/cost-and-billing/focus/
- STACKIT example FOCUS report (CSV): https://docs.stackit.cloud/platform/cost-and-billing/focus/ (Example FOCUS report download)
- STACKIT docs, Download FOCUS reports from Object Storage: https://docs.stackit.cloud/platform/cost-and-billing/how-tos/download-focus-report-from-object-storage/
- STACKIT docs, Resource labelling: https://docs.stackit.cloud/platform/cost-and-billing/labels/
- STACKIT docs, Cost Dashboard and Cost API (v3): https://docs.stackit.cloud/platform/cost-and-billing/cost-dashboard/
- STACKIT docs, Retrieve invoices (Invoice Exporter API v1): https://docs.stackit.cloud/platform/cost-and-billing/how-tos/retrieve-stackit-invoices/
- STACKIT pricing: https://stackit.com/en/prices/cloud
- FOCUS Specification: https://focus.finops.org/focus-specification/
- FinOps Foundation FOCUS: https://focus.finops.org/

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
