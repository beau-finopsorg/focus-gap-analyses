# Tencent Cloud and FOCUS: Conformance Gap and Adoption Roadmap

*Analysis run: July 1, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

Prepared: 2026-07-01
Source analyzed: Tencent Cloud FOCUS 1.0 (Preview) product documentation (updated 2025-11-27), the Tencent Cloud FOCUS 1.0 Conformance Gap Report, and the FinOps Foundation get-started page for Tencent Cloud.
FOCUS baseline for scoring: v1.2 (current certification baseline, 57 columns). Version shipped by Tencent Cloud: v1.0 (Preview).

## Executive summary

Tencent Cloud is an official FOCUS data generator listed on focus.finops.org. It ships a FOCUS-shaped billing export today: FOCUS-named columns delivered as daily or monthly files to a customer Cloud Object Storage (COS) bucket, with historical backfill and per-sub-account files. The export targets FOCUS v1.0 and is explicitly labeled Preview, and Tencent publishes its own Conformance Gap Report acknowledging that its v1.0 support does not fully align with the official v1.0 specification.

The export is real, structured, and usable. The question is completeness against a current baseline, not existence. Scored against FOCUS v1.2 (the certification baseline), the shape is strong and coverage is mid-to-high, but two gaps stand out. First, EffectiveCost is emitted empty, so amortized and commitment-adjusted spend is not represented. Second, ServiceCategory is emitted empty, which removes the highest-level cross-provider service classification. Both are Mandatory in v1.0 and in v1.2. A handful of Conditional columns are also empty (ResourceType, SkuId, SkuPriceId), and Tags ship as a JSON array of key/value objects rather than the FOCUS key-value map shape.

4-stat strip: 57 FOCUS columns (v1.2 baseline). Present or derivable: 40. Substantive Mandatory gaps: 2 of the missing Mandatory set (EffectiveCost, ServiceCategory). Deviations to fix: 1 (Tags shape).

RAG readiness: Cost Partial, Granularity Strong, Allocation Strong, Coverage Partial, FOCUS shape Strong. Overall band: Partially aligned.

Recommendation: treat Tencent Cloud as a live-but-preview FOCUS v1.0 generator. Close the two substantive Mandatory gaps (EffectiveCost, ServiceCategory), fix the Tags shape, then mature from v1.0 toward the v1.2 certification baseline.

## Part 1: The conformance gap

### 1.1 The data source

Tencent Cloud exposes FOCUS-shaped bill data through its Bill Overview console. A customer toggles bill storage on, selects a file type (daily or monthly), and Tencent writes FOCUS bill files to a nominated COS bucket on a regular basis. Historical bill data can be backfilled with a checkbox, and customers with sub-accounts can store separate sub-account bill files.

Characteristics that matter for conformance:

- Granularity: daily line items are available (file type daily or monthly). ChargePeriodStart and ChargePeriodEnd derive from usage start and end times as ISO 8601 UTC timestamps. Billing period derives from the bill month.
- Delivery: file-based to customer-owned COS storage, so a customer can ingest into a warehouse and run the FinOps Use Case Library SQL directly.
- Version and status: FOCUS v1.0, in Preview, live since January 2025. Tencent states plainly that its FOCUS 1.0 support with Tencent-specific columns has discrepancies from the official FOCUS 1.0 specification, and that unsupported fields are displayed as empty.
- Cost basis: BilledCost derives from amount before tax; ListCost from original cost (ListUnitPrice times PricingQuantity); ContractedCost from total amount after discount excluding tax, with voucher deduction folded into credit rows. EffectiveCost is emitted empty, so amortized effective cost is absent.
- Discounts and credits: negotiated and contracted discounts are reflected in ContractedCost and ContractedUnitPrice. Credits and vouchers appear via a Credit charge category. Because EffectiveCost is empty, amortization of prepaid commitments is not represented.
- Commitments: the commitment-discount columns are supported for Reserved Instances and Savings Plans only.
- Identity and allocation: ResourceId (from instance ID) and ResourceName (from instance name) are populated. BillingAccountId is the payer account, SubAccountId is the operator account, and SubAccountName is populated. Tags merge the Tencent tag and project name into a JSON array of key/value objects. Provider-specific x_ columns are added (for example x_OwnerAccountID, x_ComponentName, x_ComponentType, x_ExportTime).

### 1.2 How conformance is judged

FOCUS assigns each column a feature level: Mandatory, Conditional, Recommended, or Optional. Conformance is judged column by column against the Requirements Model. A Mandatory column must be present and populated (some are nullable only in defined cases). A Conditional column is required when the provider's business model triggers its condition and may otherwise be null-valid. Recommended columns are encouraged but do not block conformance.

Feature levels in this report were verified against the FOCUS Specification via the FOCUS MCP server. EffectiveCost and ServiceCategory are Mandatory in both FOCUS v1.0 and v1.2. Tencent ships v1.0; scoring below uses the v1.2 baseline of 57 columns per the analysis standard, with the version shipped noted throughout.

### 1.3 Column-by-column status (FOCUS v1.2 baseline, 57 columns)

Status legend: Present (emitted and aligned); Present, deviation to fix (emitted, wrong format or invalid value); Missing: Mandatory (required and absent, blocks conformance); Missing: Recommended (encouraged, absent); Missing: Conditional (required when the model triggers it); N/A: null valid (Conditional or Recommended column that does not apply to this model and should exist and be null).

Note on version: columns marked "v1.1+" or "v1.2 addition" did not exist in the FOCUS v1.0 that Tencent ships, so their absence from the v1.0 export is expected. They are classified here against the v1.2 baseline for the maturation path.

| FOCUS Column | Level (v1.2) | In the source? | Status |
|---|---|---|---|
| AvailabilityZone | R | No | N/A: null valid |
| BilledCost | M | Yes (amount before tax) | Present |
| BillingAccountId | M | Yes (payer account) | Present |
| BillingAccountName | M | Yes | Present |
| BillingAccountType | C (v1.2 addition) | No | Missing: Conditional |
| BillingCurrency | M | Yes | Present |
| BillingPeriodEnd | M | Yes (bill month) | Present |
| BillingPeriodStart | M | Yes (bill month) | Present |
| CapacityReservationId | C (v1.1+) | No | N/A: null valid |
| CapacityReservationStatus | C (v1.1+) | No | N/A: null valid |
| ChargeCategory | M | Yes (Usage, Purchase, Tax, Credit, Adjustment) | Present |
| ChargeClass | M | Yes (Correction or empty) | Present |
| ChargeDescription | M | Yes | Present |
| ChargeFrequency | R | Yes (One-Time, Recurring, Usage-Based) | Present |
| ChargePeriodEnd | M | Yes (usage end, ISO 8601) | Present |
| ChargePeriodStart | M | Yes (usage start, ISO 8601) | Present |
| CommitmentDiscountCategory | C | Yes (RI and SP only) | Present |
| CommitmentDiscountId | C | Yes (RI and SP only) | Present |
| CommitmentDiscountName | C | Yes (RI and SP only) | Present |
| CommitmentDiscountQuantity | C (v1.1+) | No | Missing: Conditional |
| CommitmentDiscountStatus | C | Yes (RI and SP only) | Present |
| CommitmentDiscountType | C | Partial (documented empty) | Missing: Conditional |
| CommitmentDiscountUnit | C (v1.1+) | No | Missing: Conditional |
| ConsumedQuantity | C | Yes | Present |
| ConsumedUnit | C | Yes | Present |
| ContractedCost | M | Yes (after-discount excl. tax) | Present |
| ContractedUnitPrice | C | Yes | Present |
| EffectiveCost | M | No (emitted empty) | Missing: Mandatory |
| InvoiceId | R (v1.2 addition) | No | Missing: Recommended |
| InvoiceIssuerName | M | Yes (Tencent legal entity) | Present |
| ListCost | M | Yes (original cost) | Present |
| ListUnitPrice | C | Yes | Present |
| PricingCategory | C | Yes (Standard default) | Present |
| PricingCurrency | C (v1.2 addition) | No | Missing: Conditional |
| PricingCurrencyContractedUnitPrice | C (v1.2 addition) | No | Missing: Conditional |
| PricingCurrencyEffectiveCost | C (v1.2 addition) | No | Missing: Conditional |
| PricingCurrencyListUnitPrice | C (v1.2 addition) | No | Missing: Conditional |
| PricingQuantity | M | Yes | Present |
| PricingUnit | M | Yes | Present |
| ProviderName | M | Yes (Tencent Cloud) | Present |
| PublisherName | M | Yes (Tencent Cloud) | Present |
| RegionId | C | Yes | Present |
| RegionName | C | Yes | Present |
| ResourceId | C | Yes (instance ID) | Present |
| ResourceName | C | Yes (instance name) | Present |
| ResourceType | C | No (emitted empty) | Missing: Conditional |
| ServiceCategory | M | No (emitted empty) | Missing: Mandatory |
| ServiceName | M | Yes | Present |
| ServiceSubcategory | R (v1.1+) | No | Missing: Recommended |
| SkuId | C | No (emitted empty) | Missing: Conditional |
| SkuMeter | C (v1.1+) | No | Missing: Conditional |
| SkuPriceDetails | C (v1.1+) | No | Missing: Conditional |
| SkuPriceId | C | No (emitted empty) | Missing: Conditional |
| SubAccountId | C | Yes (operator account) | Present |
| SubAccountName | C | Yes | Present |
| SubAccountType | C (v1.2 addition) | No | Missing: Conditional |
| Tags | C | Yes (JSON array of key/value objects) | Present, deviation to fix |

Tally against the v1.2 baseline: 33 Present, 1 Present with a deviation to fix (Tags), 2 Missing Mandatory (EffectiveCost, ServiceCategory), 2 Missing Recommended (InvoiceId, ServiceSubcategory), 14 Missing Conditional, 5 N/A null valid (AvailabilityZone, CapacityReservationId, CapacityReservationStatus). Present plus deviation plus derivable-trivial reaches 40 of 57.

### 1.4 What is solved, and what remains

Solved and substantial: Tencent already emits the account and billing-period spine (BillingAccountId, BillingAccountName, BillingCurrency, BillingPeriodStart and End), the charge spine at daily granularity (ChargePeriodStart and End, ChargeCategory, ChargeClass, ChargeDescription, ChargeFrequency), three of the four cost columns (BilledCost, ListCost, ContractedCost), the pricing quantity and unit pair, service name, region, resource identity, sub-account attribution, tags, and RI and SP commitment-discount identity. This is a genuine FOCUS dataset, not a from-scratch build.

Substantive gaps (real data that does not exist in the export):

- EffectiveCost (Mandatory): emitted empty. Producing it requires amortizing prepaid RI and SP purchases across the eligible usage lines and distributing recurring commitment fees. This is the classic amortization reconciliation, not a copy of another column, so it is substantive.
- ServiceCategory (Mandatory): emitted empty. This requires mapping each Tencent service to a single FOCUS service-category value. It is a finite mapping exercise per service, more plumbing than missing data, but today the column carries no value so it blocks conformance.

Trivial or derivable adds: the commitment-discount quantity and unit and the SKU meter and price-detail columns are v1.1 or later concepts that do not exist in a v1.0 export; they arrive as part of moving to a later version. The v1.2-addition Conditional columns (BillingAccountType, SubAccountType, PricingCurrency and its price companions) are new-version plumbing. ResourceType, SkuId, and SkuPriceId are Conditional columns that Tencent has data to populate for many services; wiring them is plumbing rather than a data gap.

### 1.5 Deviations to fix

Tags: FOCUS represents tags as key-value pairs (a map). Tencent emits a JSON array of key/value objects, for example `[{"key":"GameProject","value":"SuperMario"},{"key":"teamid","value":"Group001"}]`. The data is correct; the shape needs to be normalized to the FOCUS map representation so downstream tooling reads it as tags rather than as an opaque array.

Done right and worth noting: currency codes, ISO 8601 timestamps with inclusive-start and exclusive-end periods, valid ChargeCategory enum members (Usage, Purchase, Tax, Credit, Adjustment), valid ChargeFrequency members (One-Time, Recurring, Usage-Based), ChargeClass used correctly for corrections, and provider-specific columns correctly prefixed x_.

## Part 2: The path forward

### 2.1 Which FOCUS version to target

Tencent ships FOCUS v1.0 (Preview). The current certification baseline is FOCUS v1.2. The sensible path is to first make v1.0 fully conformant by closing the two Mandatory gaps and the Tags deviation, then mature toward v1.2 for the certification baseline, and design with v1.3 and v1.4 in mind (v1.3 deprecates Provider and Publisher; v1.4 removes them and adds invoice-detail and billing-period datasets for reconciliation).

### 2.2 What certification requires

FOCUS conformance for data generators runs through the FinOps Foundation. The current badge has historically been "FinOps Certified FOCUS v1.2 Conformant." The get-started page does not state that Tencent Cloud holds a formal FinOps FOCUS certification; it lists Tencent as a data generator with a v1.0 Preview export and a self-published Conformance Gap Report. Certification deliverables are a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report (which Tencent has already started). Membership is required for certification; contributing to the spec is open and free. Contact member-cert@finops.org for the RFI. Open tooling: the FOCUS Validator (checks data against the Requirements Model), the FOCUS Converter (provider-native to FOCUS), and the FOCUS Requirements Model.

### 2.3 Phased roadmap

Phase 0: validate what exists. Run current daily and monthly COS exports through the FOCUS Validator against v1.0, confirm scope and the Preview caveats, and reconcile the published Conformance Gap Report against Validator output.

Phase 1: close the substantive Mandatory gaps. Populate EffectiveCost by amortizing RI and SP prepaids and distributing recurring commitment fees to eligible usage lines. Populate ServiceCategory by mapping every Tencent service to a single FOCUS service-category value. This is the phase that unlocks the most conformance value.

Phase 2: fix the deviation. Normalize Tags from the JSON array of key/value objects to the FOCUS key-value map shape.

Phase 3: round out applicable Conditional and Recommended columns. Wire ResourceType, SkuId, and SkuPriceId where Tencent has the data; add InvoiceId and ServiceSubcategory.

Phase 4: mature to the certification baseline. Move from v1.0 to v1.2, adding the v1.1 columns (ServiceSubcategory, SKU meter and price details, commitment quantity and unit) and the v1.2 columns (account and sub-account Type, Invoice ID, pricing-currency family), then pursue certification and plan for v1.3 and v1.4 deltas.

### 2.4 FOCUS Use Cases unlocked

Unlocked as soon as the day-level, resource-level, tag-level data is ingested (already available): report costs by service (via ServiceName), analyze service costs by region, analyze cost per compute service for a sub-account, report service costs by a provider's sub-account, and identify anomalous daily spending by sub-account and region. Tag-based allocation works once the Tags shape is normalized in Phase 2.

Unlocked by Phase 1: report effective cost of compute, determine effective savings rate, forecast amortized costs month over month, and analyze capacity reservations and commitment burn-down, all of which depend on EffectiveCost. Cross-provider and category reporting (report costs by service category, report spending across billing periods by service category) unlocks once ServiceCategory is populated.

Out of scope for the current model: capacity-reservation use cases are moot until Tencent adopts the v1.1 capacity-reservation columns; full commitment analytics beyond RI and SP is limited by the RI-and-SP-only commitment support; invoice-detail reconciliation use cases depend on the v1.4 datasets.

## Part 3: Immediate next steps

1. Run a current daily COS export through the FOCUS Validator against v1.0 and record the delta versus Tencent's published Conformance Gap Report.
2. Scope the EffectiveCost amortization logic for RI and SP prepaids and recurring commitment fees.
3. Build the Tencent-service to FOCUS ServiceCategory mapping table (one category per service).
4. Normalize the Tags output to the FOCUS key-value map shape.
5. Decide the target version step (v1.0 fully conformant first, then v1.2) and open the certification RFI with member-cert@finops.org.

## Confidence summary

- Version shipped and Preview status: high confidence. Stated on the FinOps get-started page and Tencent's product documentation (v1.0, Preview, since January 2025).
- Delivery mechanism (COS, daily/monthly, historical backfill, sub-account files): high confidence, from the get-started page and Tencent product doc.
- Column-level support (which columns are populated versus emitted empty): solid confidence for the items drawn from Tencent's product-doc support matrix (EffectiveCost, ServiceCategory, ResourceType, SkuId, SkuPriceId empty; Tags JSON array shape; RI-and-SP-only commitments). The dedicated Conformance Gap Report page could not be rendered directly (JavaScript-rendered); its substance is corroborated by the product doc support matrix, which enumerates the same gaps.
- Feature levels: high confidence. Verified against the FOCUS Specification via the FOCUS MCP server; EffectiveCost and ServiceCategory confirmed Mandatory in v1.0 and v1.2. The v1.2 baseline table was validated (SPEC_VERSIONS_AS_OF 2026-06-23); v1.0 exposes 43 columns per the MCP, and columns marked v1.1+ or v1.2-addition are correctly treated as expected absences in a v1.0 export.
- Overall readiness band (Structured): moderate-to-high confidence. A live, FOCUS-shaped, daily, resource-and-tag-level export with strong shape, held back from a higher band by two empty Mandatory columns and the Preview status. This score reflects the data source reviewed, not a formal FinOps certification result.
- Certification status: the get-started page does not assert that Tencent Cloud holds a formal FinOps FOCUS certification. No certification is claimed here.

## Sources

- FinOps Foundation, Get started with FOCUS from Tencent Cloud: https://focus.finops.org/get-started/tencent-cloud/
- Tencent Cloud, FOCUS 1.0 product documentation: https://www.tencentcloud.com/document/product/555/67495
- Tencent Cloud, FOCUS 1.0 Conformance Gap Report: https://www.tencentcloud.com/document/product/555/67496
- FOCUS Specification and Column Library (feature levels verified via FOCUS MCP server): https://focus.finops.org/focus-specification/
- FOCUS Validator: https://focus.finops.org/focus-validator/

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
