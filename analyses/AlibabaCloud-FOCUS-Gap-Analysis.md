# Alibaba Cloud and FOCUS: Conformance Gap and Adoption Roadmap

*Analysis run: July 1, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Provider in scope:** Alibaba Cloud (Standard Bill "FOCUS 1.0 with Alibaba Cloud columns," Preview)
**Prepared:** July 1, 2026
**Source analyzed:** Alibaba Cloud User Center documentation, "Export FOCUS 1.0 with Alibaba Cloud columns (Preview) data" and the companion "FOCUS 1.0 with Alibaba Cloud columns (Preview) conformance gaps" page (both last updated July 22, 2025), plus the FOCUS get-started listing for Alibaba Cloud.
**FOCUS baseline for scoring:** v1.2 (the current certification baseline). **Version shipped by the provider:** v1.0.

---

## Executive summary

Alibaba Cloud ships a real FOCUS export today. It publishes a "Standard Bill FOCUS" dataset branded "FOCUS 1.0 with Alibaba Cloud columns (Preview)," delivered to an Object Storage Service (OSS) bucket on a monthly subscription, with the FOCUS column IDs, key-value tags, and the core cost columns already in place. The get-started page lists the supported version as v1.0, and the export is explicitly an invitational Preview.

The gap is therefore about version and completeness, not existence. Measured against the v1.2 certification baseline, two things stand out. First, the export targets v1.0, so the columns added in v1.1 and v1.2 (BillingAccountType, SubAccountType, InvoiceId, the pricing-currency family, ServiceSubcategory, capacity-reservation columns, SKU Meter and SKU Price Details, and CommitmentDiscountQuantity/Unit) are simply out of scope for the current build. Second, within the v1.0 columns it does emit, Alibaba's own documentation lists a set of columns that are null for all line items today: ChargeDescription, ConsumedQuantity, ConsumedUnit, ContractedCost, ContractedUnitPrice, SkuId, and SkuPriceId. Several of these are Mandatory in v1.2.

The single most consequential gap is ContractedCost, which is Mandatory and non-nullable in v1.2 but null for all line items in the current export. BilledCost, EffectiveCost, and ListCost are present and non-null, which is the harder half of the cost picture. The export also carries two flagged deviations: timestamps use UTC+08:00 rather than UTC, and the commitment-discount columns exist but are not populated with used or unused data.

**Stat strip:** 57 FOCUS columns (v1.2 baseline); 33 present and conformant; 5 of 8 Mandatory gaps are substantive; 2 deviations to fix.

**Recommendation:** Treat this as a mature Preview that is close on shape and cost coverage but incomplete on populated fields and one version behind the certification baseline. Prioritize populating ContractedCost, ConsumedQuantity/ConsumedUnit, and ChargeDescription, then convert timestamps to UTC, then move the build target from v1.0 to v1.2.

---

## Part 1: The conformance gap

### 1.1 The data source

Alibaba Cloud exposes FOCUS data through the Expenses and Costs console under Bills > Bill Subscription. A subscriber selects "FOCUS Billing Data" as the export type, picks a start billing month, and points the subscription at an OSS bucket and directory. Files are compressed .zip, split into parts for large months (`..._part_001.zip`), and named `{Account UID}_{Site ID}_{Bill Type}_{YYYYMM}.zip`, where Site ID 1 is the China site and 2 is the International site. The finalized file for a given month is pushed after 12:00 on the 4th day of the following month.

Characteristics relevant to conformance:

- Granularity: the export carries charge-period columns (ChargePeriodStart, ChargePeriodEnd) alongside billing-period columns, so line items are resolved below the monthly billing period. This supports charge-level analysis.
- Format: FOCUS column IDs are used directly, Tags is typed as JSON (key-value), and currency and cost columns are typed as expected.
- Alibaba-specific columns: the export appends provider columns using an `X_` prefix (X_CommodityCode, X_CommodityName, X_BillingItemCode, X_BillingItemName, X_InstanceID), which is the correct FOCUS convention for custom columns.
- Stated limitation: Alibaba documents that the export is "for analytical purposes only and can not be used as a basis for reconciliation," directing users to the official bill overview for settlement and payment. This is a material caveat for actuals-based use cases.

### 1.2 How conformance is judged

FOCUS assigns every column a feature level: Mandatory (must be present and populated per its rules), Conditional (required when the provider's business model triggers the condition), Recommended (encouraged), or Optional. Conformance is judged column by column against the Requirements Model, which encodes the MUST, SHOULD, and MAY rules. A dataset conforms to a version when every Mandatory column is present and correctly populated and every applicable Conditional column is present.

Feature levels in this report are taken from the verified v1.2 reference and were spot-checked against the live FOCUS specification. v1.2 defines 57 columns: 21 Mandatory, 32 Conditional, and 4 Recommended (AvailabilityZone, ChargeFrequency, InvoiceId, ServiceSubcategory).

Because Alibaba ships a v1.0 export, some v1.2 Mandatory and Conditional columns did not exist in the version it built to. Those are marked as version-scope gaps in the table below, distinct from columns Alibaba emits but leaves null.

### 1.3 Column-by-column status (v1.2 baseline)

Status legend: Present (emitted and aligned); Present, deviation (emitted, wrong format or value); Missing: Mandatory (required, absent or null); Missing: Recommended; Missing: Conditional (applies but absent); N/A: null valid (Conditional/Recommended that does not apply, should exist and be null).

| # | FOCUS Column | Level (v1.2) | In the source? | Status |
|---|---|---|---|---|
| 3.1 | AvailabilityZone | R | Yes | Present |
| 3.2 | BilledCost | M | Yes, non-null | Present |
| 3.3 | BillingAccountId | M | Yes | Present |
| 3.4 | BillingAccountName | M | Yes | Present |
| 3.5 | BillingAccountType | C | No (added in v1.2) | Missing: Conditional |
| 3.6 | BillingCurrency | M | Yes | Present |
| 3.7 | BillingPeriodEnd | M | Yes | Present, deviation |
| 3.8 | BillingPeriodStart | M | Yes | Present, deviation |
| 3.9 | CapacityReservationId | C | No (added in v1.1) | N/A: null valid |
| 3.10 | CapacityReservationStatus | C | No (added in v1.1) | N/A: null valid |
| 3.11 | ChargeCategory | M | Yes | Present |
| 3.12 | ChargeClass | M | Yes (nullable) | Present |
| 3.13 | ChargeDescription | M | Emitted but null for all rows | Missing: Mandatory |
| 3.14 | ChargeFrequency | R | Yes | Present |
| 3.15 | ChargePeriodEnd | M | Yes | Present, deviation |
| 3.16 | ChargePeriodStart | M | Yes | Present, deviation |
| 3.17 | CommitmentDiscountCategory | C | Emitted, not populated | Missing: Conditional |
| 3.18 | CommitmentDiscountId | C | Emitted, not populated | Missing: Conditional |
| 3.19 | CommitmentDiscountName | C | Emitted, not populated | Missing: Conditional |
| 3.20 | CommitmentDiscountQuantity | C | No (added in v1.1) | Missing: Conditional |
| 3.21 | CommitmentDiscountStatus | C | Emitted, not populated | Missing: Conditional |
| 3.22 | CommitmentDiscountType | C | Emitted, not populated | Missing: Conditional |
| 3.23 | CommitmentDiscountUnit | C | No (added in v1.1) | Missing: Conditional |
| 3.24 | ConsumedQuantity | C | Emitted but null for all rows | Missing: Conditional |
| 3.25 | ConsumedUnit | C | Emitted but null for all rows | Missing: Conditional |
| 3.26 | ContractedCost | M | Emitted but null for all rows | Missing: Mandatory |
| 3.27 | ContractedUnitPrice | C | Emitted but null for all rows | Missing: Conditional |
| 3.28 | EffectiveCost | M | Yes, non-null | Present |
| 3.29 | InvoiceId | R | No (added in v1.2) | Missing: Recommended |
| 3.30 | InvoiceIssuerName | M | Yes | Present |
| 3.31 | ListCost | M | Yes, non-null | Present |
| 3.32 | ListUnitPrice | C | Yes (nullable in some scenarios) | Present |
| 3.33 | PricingCategory | C | Yes | Present |
| 3.34 | PricingCurrency | C | No (added in v1.2) | Missing: Conditional |
| 3.35 | PricingCurrencyContractedUnitPrice | C | No (added in v1.2) | Missing: Conditional |
| 3.36 | PricingCurrencyEffectiveCost | C | No (added in v1.2) | Missing: Conditional |
| 3.37 | PricingCurrencyListUnitPrice | C | No (added in v1.2) | Missing: Conditional |
| 3.38 | PricingQuantity | M | Yes | Present |
| 3.39 | PricingUnit | M | Yes (nullable in some scenarios) | Present |
| 3.40 | ProviderName | M | Yes | Present |
| 3.41 | PublisherName | M | Yes | Present |
| 3.42 | RegionId | C | Yes | Present |
| 3.43 | RegionName | C | Yes | Present |
| 3.44 | ResourceId | C | Yes (nullable for some offerings) | Present |
| 3.45 | ResourceName | C | Yes | Present |
| 3.46 | ResourceType | C | Yes (nullable for some offerings) | Present |
| 3.47 | ServiceCategory | M | Yes | Present |
| 3.48 | ServiceName | M | Yes | Present |
| 3.49 | ServiceSubcategory | R | No (added in v1.1) | Missing: Recommended |
| 3.50 | SkuId | C | Emitted but null for all rows | Missing: Conditional |
| 3.51 | SkuMeter | C | No (added in v1.1) | Missing: Conditional |
| 3.52 | SkuPriceDetails | C | No (added in v1.1) | Missing: Conditional |
| 3.53 | SkuPriceId | C | Emitted but null for all rows | Missing: Conditional |
| 3.54 | SubAccountId | C | Yes | Present |
| 3.55 | SubAccountName | C | Yes | Present |
| 3.56 | SubAccountType | C | No (added in v1.2) | Missing: Conditional |
| 3.57 | Tags | C | Yes (JSON key-value) | Present |

**Reading the tally:** 33 columns Present and conformant. 8 Mandatory columns fall short of the v1.2 rules: 6 through timestamp deviations (BillingPeriodStart/End, ChargePeriodStart/End) that carry correct data in a near-correct shape, plus ChargeDescription and ContractedCost, which are null for all line items. Counting distinct Mandatory columns that need data or a fix: ChargeDescription and ContractedCost are the two data gaps, and the four timestamp columns are a single systematic deviation. The Conditional gaps split into columns Alibaba emits but leaves null (ConsumedQuantity, ConsumedUnit, ContractedUnitPrice, SkuId, SkuPriceId, and the commitment-discount family) and columns that did not exist in v1.0 (the pricing-currency family, SubAccountType, BillingAccountType, SKU Meter/Price Details, CommitmentDiscountQuantity/Unit).

### 1.4 What is solved, and what remains

**Solved (the hard parts):**

- Three of four cost columns are present and non-null: BilledCost, EffectiveCost, and ListCost. Getting EffectiveCost right (amortized, after discounts) is the difficult half of the cost model, and Alibaba populates it.
- Account and attribution identity is in place: BillingAccountId/Name, SubAccountId/Name, ResourceId/Name/Type, RegionId/Name, AvailabilityZone, and key-value Tags. This is a strong allocation foundation.
- Service classification (ServiceCategory, ServiceName), charge classification (ChargeCategory, ChargeClass, ChargeFrequency), and pricing quantity/unit are present.
- FOCUS shape is correct: FOCUS column IDs, JSON key-value tags, and `X_`-prefixed custom columns.

**Substantive gaps (real data not currently in the export):**

- ContractedCost (Mandatory): null for all line items. This is the one Mandatory cost column missing, and it requires surfacing negotiated/contracted pricing back to each line.
- ConsumedQuantity and ConsumedUnit (Conditional): null for all line items, though Alibaba clearly supports usage measurement, so the condition applies.
- ContractedUnitPrice (Conditional): null for all line items.
- Commitment-discount population: the columns exist but do not carry used/unused data for RI and resource-plan discounts, so amortized commitment analysis is not yet possible from this export.

**Trivial or version-scope gaps (plumbing, not a data problem):**

- ChargeDescription (Mandatory, nullable-tolerant in practice) is a text field Alibaba can populate from existing commodity/billing-item names it already emits in `X_` columns.
- SkuId and SkuPriceId (Conditional) map to Alibaba's existing commodity/billing-item identifiers.
- The v1.1 and v1.2 columns absent from this v1.0 build (BillingAccountType, SubAccountType, InvoiceId, pricing-currency family, ServiceSubcategory, SKU Meter/Price Details, capacity-reservation family, CommitmentDiscountQuantity/Unit) are version-scope, addressed by moving the build target to v1.2.

The reconciliation caveat matters here. Alibaba states the export is for analysis, not reconciliation. That signals BilledCost/EffectiveCost on this feed may not tie exactly to the settled invoice, so any actuals-based use should reconcile against the official bill.

### 1.5 Deviations to fix

- Timestamp time zone: BillingPeriodStart/End and ChargePeriodStart/End are emitted in ISO 8601 but with UTC+08:00 offsets (for example, `2025-05-01T00:00:00+08:00`). FOCUS requires date/time values in UTC. This is a straightforward conversion.
- Commitment-discount population: the commitment-discount columns are present but not populated with used or unused rows, so they do not yet meet the Conditional requirement for a provider that supports commitment discounts.

Done right already: Tags is JSON key-value (not an array of bare strings), custom columns use the `X_` prefix, and currency uses standard codes.

---

## Part 2: The path forward

### 2.1 Which FOCUS version to target

Alibaba ships v1.0 today. The certification baseline is v1.2, and the latest ratified version is v1.4. The pragmatic path is to close the v1.0 population and deviation gaps first (they apply regardless of version), then advance the build target to v1.2 to align with the certification baseline, picking up the v1.1 and v1.2 columns along the way. Designing toward v1.2 now avoids reworking the schema twice.

### 2.2 What certification requires

FOCUS conformance for data generators runs through the FinOps Foundation. The current program is "FinOps Certified FOCUS v1.2 Conformant"; the RFI contact is member-cert@finops.org. Membership is required for certification, though contributing to the spec is open and free. Deliverables are a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report (this analysis is a seed for that). Open tooling supports the work: the FOCUS Validator (checks data against the Requirements Model), the FOCUS Converter (provider-native to FOCUS), and the machine-readable FOCUS Requirements Model. The get-started listing does not assert a formal certification for Alibaba Cloud; it lists the supported version as v1.0.

### 2.3 Phased roadmap

**Phase 0: Validate what exists.** Run a sample export through the FOCUS Validator against v1.0 to establish a baseline, and confirm which columns are null-for-all versus conditionally null. Confirm scope and the reconciliation caveat with stakeholders.

**Phase 1: Close the substantive Mandatory and near-Mandatory data gaps.** Populate ContractedCost (Mandatory), ConsumedQuantity and ConsumedUnit, and ContractedUnitPrice. Populate ChargeDescription from existing commodity/billing-item text. This unlocks the bulk of allocation and usage analysis.

**Phase 2: Fix the deviations.** Convert all four timestamp columns to UTC. Populate the commitment-discount columns with used/unused rows for RI and resource plans, or document why the condition does not apply where it genuinely does not.

**Phase 3: Round out Conditional and Recommended columns within v1.0 scope.** Populate SkuId and SkuPriceId from Alibaba's commodity/billing-item identifiers.

**Phase 4: Advance the build target to v1.2 and certify.** Add the v1.1 and v1.2 columns (BillingAccountType, SubAccountType, InvoiceId, pricing-currency family, ServiceSubcategory, SKU Meter/Price Details, capacity-reservation columns, CommitmentDiscountQuantity/Unit), re-validate against v1.2, and pursue the FinOps Certified FOCUS v1.2 Conformant program.

### 2.4 FOCUS Use Cases unlocked

- Available now (resource-, tag-, region-, and charge-period data plus BilledCost/EffectiveCost/ListCost exist): cost allocation by tag and sub-account, service and region spend breakdowns, effective-cost trending, and cross-provider normalization for multi-cloud reporting.
- Unlocked by Phase 1: usage-normalized efficiency analysis (needs ConsumedQuantity/Unit) and contracted-rate analysis (needs ContractedCost/ContractedUnitPrice).
- Unlocked by Phase 2: commitment-discount coverage and utilization reporting (needs populated commitment-discount rows), and any time-zone-sensitive daily reconciliation (needs UTC timestamps).
- Out of scope until Phase 4 or by model: capacity-reservation reporting and SKU Meter/Price Details analysis (not in the v1.0 build). Invoice-accurate reconciliation is limited by the provider's stated "analysis only" caveat and should reconcile against the official bill.

---

## Part 3: Immediate next steps

1. Run a current sample export through the FOCUS Validator (v1.0) to confirm the null-for-all column set and establish a measured baseline.
2. Scope Phase 1: populate ContractedCost, ConsumedQuantity/ConsumedUnit, ContractedUnitPrice, and ChargeDescription.
3. Convert the four timestamp columns from UTC+08:00 to UTC.
4. Decide the target version (recommend v1.2) and map the v1.1/v1.2 additions to Alibaba's native billing model.
5. Engage member-cert@finops.org to understand the v1.2 conformance RFI and deliverables.

---

## Confidence summary

- Version shipped (v1.0) and Preview status: high confidence. The get-started page lists "Version Supported: v1.0," and Alibaba's own docs title the feature "FOCUS 1.0 with Alibaba Cloud columns (Preview)."
- Delivery mechanism (OSS subscription, monthly, zip, finalized after the 4th): high confidence, taken directly from Alibaba's export guide.
- The null-for-all and deviation lists (ChargeDescription, ConsumedQuantity/Unit, ContractedCost, ContractedUnitPrice, SkuId, SkuPriceId null; UTC+08:00 timestamps; unpopulated commitment discounts): high confidence, taken directly from Alibaba's published conformance-gaps page.
- Present/Conditional classifications for columns Alibaba lists as populated (RegionId/Name, ResourceId/Name/Type, PricingCategory, SubAccountId/Name, Tags): solid confidence, based on the documented column list and descriptions rather than an inspected sample file.
- Feature levels: verified against the bundled v1.2 reference and spot-checked against the live spec on this date (ChargeClass Mandatory/nullable, ChargeFrequency Recommended confirmed). No cache refresh required.
- Substantive-versus-trivial calls and the RAG score reflect the documented data source, not a Validator run on a live sample; a Validator pass in Phase 0 is the objective arbiter.
- Overall data quality for this analysis: solid. Alibaba publishes both a column dictionary and an explicit conformance-gaps page, which is unusually complete source material.

## Sources

- FOCUS get-started listing, Alibaba Cloud: https://focus.finops.org/get-started/alibaba-cloud/
- Alibaba Cloud, "Export FOCUS 1.0 with Alibaba Cloud columns (Preview) data": https://www.alibabacloud.com/help/en/user-center/export-alibaba-cloud-standard-billing-focus
- Alibaba Cloud, "FOCUS 1.0 with Alibaba Cloud columns (Preview) conformance gaps": https://www.alibabacloud.com/help/en/user-center/alibaba-cloud-focus-1-0-preview-field-differences
- FinOps Foundation, "Building a FOCUS Data Export Pipeline for Alibaba Cloud": https://www.finops.org/assets/building-a-focus-data-export-pipeline-for-alibaba-cloud/
- FOCUS Specification: https://focus.finops.org/focus-specification/
- FinOps Certified FOCUS Conformant program: https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
