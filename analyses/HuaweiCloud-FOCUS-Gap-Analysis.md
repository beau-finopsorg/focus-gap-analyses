# Huawei Cloud and FOCUS: Conformance Gap and Adoption Roadmap

*Analysis run: July 1, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Provider in scope:** Huawei Cloud (Cost Center "Cost details (FOCUS 1.0)" export to OBS)
**Prepared:** July 1, 2026
**Source analyzed:** Huawei Cloud Cost Center User Guide, "FOCUS 1.0 Field Description" (updated 2026-05-22), the companion "Export to OBS" and "Creating an OBS Export Task" pages, plus the FOCUS get-started listing for Huawei Cloud.
**FOCUS baseline for scoring:** v1.2 (the current certification baseline). **Version shipped by the provider:** v1.0.

---

## Executive summary

Huawei Cloud ships a real FOCUS export today. Its Cost Center produces a "Cost details (FOCUS 1.0)" dataset, delivered to an Object Storage Service (OBS) bucket through a scheduled export task, with FOCUS column IDs and the core cost columns already mapped from Huawei's native cost detail fields. The get-started page lists the supported version as v1.0, and Huawei publishes a full field-mapping dictionary showing how each FOCUS field is populated.

The gap is therefore about version and completeness, not existence. Measured against the v1.2 certification baseline, two things stand out. First, the export targets v1.0, so the columns added in v1.1 and v1.2 (ServiceSubcategory, the capacity-reservation family, SkuMeter, SkuPriceDetails, CommitmentDiscountQuantity/Unit, BillingAccountType, SubAccountType, InvoiceId, and the pricing-currency family) are out of scope for the current build. Second, within the v1.0 columns it does emit, Huawei's own documentation shows a set of columns that are left empty for every line item: ChargeClass, ChargeDescription (placeholder "No description"), ContractedUnitPrice, InvoiceIssuerName, ListUnitPrice, PricingCategory, PricingQuantity, PricingUnit, PublisherName, and SkuPriceId.

The strongest finding is the cost picture. All four cost columns map to real native fields: BilledCost (Original Cost), ListCost (List Price), EffectiveCost (Current Month Amortized), and ContractedCost (Original Cost). EffectiveCost drawing from an amortized field is the harder half of the cost model, and Huawei populates it. The most consequential gaps are the two Mandatory columns emitted empty: InvoiceIssuerName (Mandatory, non-nullable in v1.2) and PricingQuantity / PricingUnit (Mandatory in v1.2). PricingQuantity and PricingUnit are derivable from the ConsumedQuantity and ConsumedUnit that Huawei already emits, so they are plumbing rather than a data gap; InvoiceIssuerName is a constant the provider can populate. The one clear format deviation is Tags, emitted as a concatenated string ("Department:pc;Env:beta") rather than as key-value pairs.

**Stat strip:** 57 FOCUS columns (v1.2 baseline); 27 present and conformant; 1 of 5 Mandatory gaps is substantive; 2 deviations to fix.

**Recommendation:** Treat this as a solid v1.0 export that is strong on cost coverage and attribution but leaves several emitted columns empty and sits one baseline behind the certification target. Prioritize populating InvoiceIssuerName and PublisherName (constants), derive PricingQuantity/PricingUnit from consumed quantity, populate ChargeDescription, reshape Tags to key-value, then move the build target from v1.0 to v1.2.

---

## Part 1: The conformance gap

### 1.1 The data source

Huawei Cloud exposes FOCUS data through the Cost Center console under Cost Insights > Cost Details Export > Export to OBS. A user creates an export task, sets Content Type to "Cost details (FOCUS 1.0)," and points the task at an OBS bucket. The export is a mapping layer over Huawei's native cost detail fields (Original Cost, List Price, Current Month Amortized, Bill Type, Billing Mode, Service Type, Resource ID, and so on), each converted to a FOCUS column per a published conversion table.

Characteristics relevant to conformance:

- Granularity: the export carries charge-period columns (ChargePeriodStart, ChargePeriodEnd) drawn from native Start Time and End Time fields, so line items resolve to daily (24-hour) blocks below the monthly billing period. Amortized costs for yearly/monthly subscriptions are attributed to the amortization day. This supports charge-level and daily analysis.
- Timestamps: native GMT+08:00 values are converted to UTC with a trailing `Z` (for example, native `2025-03-20 00:00:00 GMT+08:00` becomes `2025-03-19T16:00:00Z`). This is correct FOCUS behavior, so no timestamp deviation applies.
- Currency: BillingCurrency defaults to USD.
- Attribution: the export carries SubAccountId/SubAccountName (from Linked Account) for consolidated-billing sub-accounts, and Huawei's enterprise-project construct is surfaced through the custom columns x_EnterpriseId and x_EnterpriseName. Cost categories are surfaced through x_CostUnit, and split-billing items through x_SplitItem.
- Custom columns: Huawei appends provider columns with an `x_` prefix (x_CostUnit, x_EnterpriseId, x_EnterpriseName, x_SplitItem), which is the correct FOCUS convention for custom columns.

### 1.2 How conformance is judged

FOCUS assigns every column a feature level: Mandatory (must be present and populated per its rules), Conditional (required when the provider's business model triggers the condition), Recommended (encouraged), or Optional. Conformance is judged column by column against the Requirements Model, which encodes the MUST, SHOULD, and MAY rules. A dataset conforms to a version when every Mandatory column is present and correctly populated and every applicable Conditional column is present.

Feature levels in this report are taken from the verified v1.2 reference and were spot-checked against the live FOCUS specification. v1.2 defines 57 columns: 21 Mandatory, 32 Conditional, and 4 Recommended (AvailabilityZone, ChargeFrequency, InvoiceId, ServiceSubcategory).

Because Huawei ships a v1.0 export, some v1.2 Mandatory and Conditional columns did not exist in the version it built to. Those are marked as version-scope gaps in the table below, distinct from columns Huawei emits but leaves empty.

### 1.3 Column-by-column status (v1.2 baseline)

Status legend: Present (emitted and aligned); Present, deviation (emitted, wrong format or value); Missing: Mandatory (required, absent or empty); Missing: Recommended; Missing: Conditional (applies but absent); N/A: null valid (Conditional/Recommended that does not apply, should exist and be null).

| # | FOCUS Column | Level (v1.2) | In the source? | Status |
|---|---|---|---|---|
| 3.1 | AvailabilityZone | R | Yes (from AZ) | Present |
| 3.2 | BilledCost | M | Yes (Original Cost) | Present |
| 3.3 | BillingAccountId | M | Yes (derived from PayerAccount) | Present |
| 3.4 | BillingAccountName | M | Yes (PayerAccount Name) | Present |
| 3.5 | BillingAccountType | C | No (added in v1.2) | Missing: Conditional |
| 3.6 | BillingCurrency | M | Yes (default USD) | Present |
| 3.7 | BillingPeriodEnd | M | Yes (from Month, UTC) | Present |
| 3.8 | BillingPeriodStart | M | Yes (from Month, UTC) | Present |
| 3.9 | CapacityReservationId | C | No (added in v1.1) | N/A: null valid |
| 3.10 | CapacityReservationStatus | C | No (added in v1.1) | N/A: null valid |
| 3.11 | ChargeCategory | M | Yes (from Bill Type) | Present |
| 3.12 | ChargeClass | M | Emitted empty (nullable) | Present |
| 3.13 | ChargeDescription | M | Emitted with placeholder "No description" | Present, deviation |
| 3.14 | ChargeFrequency | R | Yes (from Billing Mode) | Present |
| 3.15 | ChargePeriodEnd | M | Yes (End Time, UTC) | Present |
| 3.16 | ChargePeriodStart | M | Yes (Start Time, UTC) | Present |
| 3.17 | CommitmentDiscountCategory | C | Yes (from Billing Mode) | Present |
| 3.18 | CommitmentDiscountId | C | Yes (RI/SP/package ID) | Present |
| 3.19 | CommitmentDiscountName | C | Yes (RI/SP/package name) | Present |
| 3.20 | CommitmentDiscountQuantity | C | No (added in v1.1) | Missing: Conditional |
| 3.21 | CommitmentDiscountStatus | C | Yes (Used/Unused from Bill Type) | Present |
| 3.22 | CommitmentDiscountType | C | Yes (from Billing Mode) | Present |
| 3.23 | CommitmentDiscountUnit | C | No (added in v1.1) | Missing: Conditional |
| 3.24 | ConsumedQuantity | C | Yes (Usage) | Present |
| 3.25 | ConsumedUnit | C | Yes (Usage Unit) | Present |
| 3.26 | ContractedCost | M | Yes (Original Cost) | Present |
| 3.27 | ContractedUnitPrice | C | Emitted empty | Missing: Conditional |
| 3.28 | EffectiveCost | M | Yes (Current Month Amortized) | Present |
| 3.29 | InvoiceId | R | No (added in v1.2) | Missing: Recommended |
| 3.30 | InvoiceIssuerName | M | Emitted empty | Missing: Mandatory |
| 3.31 | ListCost | M | Yes (List Price) | Present |
| 3.32 | ListUnitPrice | C | Emitted empty | Missing: Conditional |
| 3.33 | PricingCategory | C | Emitted empty | Missing: Conditional |
| 3.34 | PricingCurrency | C | No (added in v1.2) | Missing: Conditional |
| 3.35 | PricingCurrencyContractedUnitPrice | C | No (added in v1.2) | Missing: Conditional |
| 3.36 | PricingCurrencyEffectiveCost | C | No (added in v1.2) | Missing: Conditional |
| 3.37 | PricingCurrencyListUnitPrice | C | No (added in v1.2) | Missing: Conditional |
| 3.38 | PricingQuantity | M | Emitted empty | Missing: Mandatory |
| 3.39 | PricingUnit | M | Emitted empty | Missing: Mandatory |
| 3.40 | ProviderName | M | Yes ("Huawei Cloud") | Present |
| 3.41 | PublisherName | M | Emitted empty | Missing: Mandatory |
| 3.42 | RegionId | C | Yes (Region Code) | Present |
| 3.43 | RegionName | C | Yes (Region) | Present |
| 3.44 | ResourceId | C | Yes (Resource ID) | Present |
| 3.45 | ResourceName | C | Yes (Resource Name) | Present |
| 3.46 | ResourceType | C | Yes (Resource Type) | Present |
| 3.47 | ServiceCategory | M | Yes (from Service Type) | Present, deviation |
| 3.48 | ServiceName | M | Yes (Service Type) | Present |
| 3.49 | ServiceSubcategory | R | No (added in v1.1) | Missing: Recommended |
| 3.50 | SkuId | C | Yes (Specification Code) | Present |
| 3.51 | SkuMeter | C | No (added in v1.1) | Missing: Conditional |
| 3.52 | SkuPriceDetails | C | No (added in v1.1) | Missing: Conditional |
| 3.53 | SkuPriceId | C | Emitted empty | Missing: Conditional |
| 3.54 | SubAccountId | C | Yes (from Linked Account) | Present |
| 3.55 | SubAccountName | C | Yes (Linked Account) | Present |
| 3.56 | SubAccountType | C | No (added in v1.2) | Missing: Conditional |
| 3.57 | Tags | C | Yes, but concatenated string | Present, deviation |

**Reading the tally:** 27 columns Present and conformant. Five Mandatory columns fall short of the v1.2 rules. Four are emitted empty (InvoiceIssuerName, PricingQuantity, PricingUnit, PublisherName), and one carries a placeholder value (ChargeDescription = "No description," counted as a deviation rather than a hard Mandatory gap). Of these, only InvoiceIssuerName plus PricingQuantity/PricingUnit are absent Mandatory data, and of those, PricingQuantity/PricingUnit are derivable from consumed quantity, so just one Mandatory gap (InvoiceIssuerName, a constant) is genuinely absent and non-derivable. The Conditional gaps split into columns Huawei emits but leaves empty (ContractedUnitPrice, ListUnitPrice, PricingCategory, SkuPriceId) and columns that did not exist in v1.0 (CommitmentDiscountQuantity/Unit, SkuMeter, SkuPriceDetails, the pricing-currency family, BillingAccountType, SubAccountType). Two Conditional columns are correctly N/A (the capacity-reservation family, which Huawei's model does not surface and which postdates v1.0).

### 1.4 What is solved, and what remains

**Solved (the hard parts):**

- All four cost columns map to real native fields: BilledCost (Original Cost), ListCost (List Price), EffectiveCost (Current Month Amortized), and ContractedCost (Original Cost). Populating EffectiveCost from an amortized field is the difficult half of the cost model, and Huawei does it.
- Account and attribution identity is in place: BillingAccountId/Name, SubAccountId/Name (linked accounts), ResourceId/Name/Type, RegionId/Name, and AvailabilityZone. Enterprise projects and cost categories are surfaced through `x_` custom columns. This is a strong allocation foundation.
- The commitment-discount family is populated (Category, Id, Name, Status, Type) from Huawei's RI, savings-plan, and resource-package model, including Used/Unused status. That is more commitment coverage than many v1.0 exports carry.
- Service classification (ServiceCategory, ServiceName), charge classification (ChargeCategory, ChargeFrequency), consumed quantity/unit, and SkuId are present.
- Timestamps are correctly converted to UTC, and custom columns use the `x_` prefix.

**Substantive gaps (real data not currently in the export):**

- InvoiceIssuerName (Mandatory, non-nullable): emitted empty. This is the one genuinely absent Mandatory value that is not derivable from another column, though it is a constant (the Huawei Cloud selling entity) rather than per-line data.

**Trivial or version-scope gaps (plumbing, not a data problem):**

- PricingQuantity and PricingUnit (Mandatory): emitted empty, but derivable from ConsumedQuantity and ConsumedUnit for flat-rate usage. For tiered or blended pricing, PricingQuantity must be computed against the rate basis rather than copied from consumption, so those SKUs need proper computation rather than a straight copy.
- PublisherName (Mandatory): emitted empty, populated with a constant (for first-party Huawei services, the same value as ProviderName; for Marketplace items, the seller).
- ChargeDescription (Mandatory): a static placeholder "No description" today. Huawei can populate it from existing service and specification text.
- ContractedUnitPrice, ListUnitPrice, PricingCategory, SkuPriceId (Conditional): emitted empty; derivable from Huawei's existing price and specification data.
- The v1.1 and v1.2 columns absent from this v1.0 build (ServiceSubcategory, capacity-reservation family, SkuMeter, SkuPriceDetails, CommitmentDiscountQuantity/Unit, BillingAccountType, SubAccountType, InvoiceId, pricing-currency family) are version-scope, addressed by moving the build target to v1.2.

### 1.5 Deviations to fix

- Tags format: Huawei emits Tags as a single concatenated string ("Department:pc;Env:beta") combining cost tags and resource tags. FOCUS represents Tags as key-value pairs (a JSON object), not a delimited string. This is the primary format deviation.
- ChargeDescription value: a constant placeholder "No description" is emitted for all rows. The column is present but does not carry a meaningful description, so it should be populated from Huawei's service and specification text.
- ServiceCategory values: the conversion maps Huawei's Service Type to FOCUS categories, but the documentation's example maps ECS to "Computing." The FOCUS v1.2 allowed value is "Compute." The mapping should be validated against the FOCUS ServiceCategory enum so emitted values are valid members.

Done right already: timestamps are converted to UTC with a `Z` suffix, custom columns use the `x_` prefix, currency uses a standard code (USD), and the commitment-discount enums (Used/Unused, Spend/Usage) follow FOCUS values.

---

## Part 2: The path forward

### 2.1 Which FOCUS version to target

Huawei ships v1.0 today. The certification baseline is v1.2, and the latest ratified version is v1.4. The pragmatic path is to close the v1.0 population and deviation gaps first (they apply regardless of version), then advance the build target to v1.2 to align with the certification baseline, picking up the v1.1 and v1.2 columns along the way. Designing toward v1.2 now avoids reworking the schema twice.

### 2.2 What certification requires

FOCUS conformance for data generators runs through the FinOps Foundation. The current program is "FinOps Certified FOCUS v1.2 Conformant"; the RFI contact is member-cert@finops.org. Membership is required for certification, though contributing to the spec is open and free. Deliverables are a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report (this analysis is a seed for that). Open tooling supports the work: the FOCUS Validator (checks data against the Requirements Model), the FOCUS Converter (provider-native to FOCUS), and the machine-readable FOCUS Requirements Model. The get-started listing describes Huawei Cloud as a Supported provider at v1.0; it does not assert a formal FinOps Certified FOCUS Conformant designation.

### 2.3 Phased roadmap

**Phase 0: Validate what exists.** Run a sample export through the FOCUS Validator against v1.0 to establish a baseline, and confirm which columns are empty-for-all versus conditionally empty. Confirm scope with stakeholders.

**Phase 1: Close the Mandatory data gaps.** Populate InvoiceIssuerName and PublisherName (constants). Derive PricingQuantity and PricingUnit from ConsumedQuantity/ConsumedUnit for flat-rate SKUs, and compute them against the rate basis for tiered/blended SKUs. Populate ChargeDescription from existing service and specification text. This clears the Mandatory column set for v1.0.

**Phase 2: Fix the deviations.** Reshape Tags from the concatenated string into FOCUS key-value pairs. Validate the ServiceCategory mapping against the FOCUS enum (for example, "Compute" not "Computing").

**Phase 3: Round out Conditional columns within v1.0 scope.** Populate ContractedUnitPrice, ListUnitPrice, PricingCategory, and SkuPriceId from Huawei's existing price and specification data.

**Phase 4: Advance the build target to v1.2 and certify.** Add the v1.1 and v1.2 columns (ServiceSubcategory, capacity-reservation family where applicable, SkuMeter, SkuPriceDetails, CommitmentDiscountQuantity/Unit, BillingAccountType, SubAccountType, InvoiceId, pricing-currency family), re-validate against v1.2, and pursue the FinOps Certified FOCUS v1.2 Conformant program.

### 2.4 FOCUS Use Cases unlocked

- Available now (resource-, region-, sub-account-, and charge-period data plus all four cost columns and populated commitment discounts exist): cost allocation by sub-account and enterprise project, service and region spend breakdowns, effective-cost and amortized-cost trending, commitment-discount coverage and utilization reporting, and cross-provider normalization for multi-cloud reporting.
- Unlocked by Phase 1: pricing-rate and unit-economics analysis (needs PricingQuantity/PricingUnit) and invoice-issuer attribution.
- Unlocked by Phase 2: tag-based allocation at scale (needs key-value Tags) and reliable service-category rollups (needs valid enum values).
- Out of scope until Phase 4 or by model: capacity-reservation reporting and SKU Meter / SKU Price Details analysis (not in the v1.0 build). Pricing-currency reporting depends on the v1.2 pricing-currency family.

---

## Part 3: Immediate next steps

1. Run a current sample export through the FOCUS Validator (v1.0) to confirm the empty-for-all column set and establish a measured baseline.
2. Populate the Mandatory constants (InvoiceIssuerName, PublisherName) and derive PricingQuantity/PricingUnit from consumed quantity.
3. Reshape Tags into FOCUS key-value pairs and validate the ServiceCategory mapping against the FOCUS enum.
4. Populate ChargeDescription from existing service/specification text.
5. Decide the target version (recommend v1.2) and map the v1.1/v1.2 additions to Huawei's native billing model, then engage member-cert@finops.org on the v1.2 conformance RFI.

---

## Confidence summary

- Version shipped (v1.0) and Supported status: high confidence. The get-started page lists v1.0, and Huawei's own documentation titles the feature "FOCUS 1.0 Field Description" and "Cost details (FOCUS 1.0)."
- Delivery mechanism (OBS export task from Cost Center) and daily charge-period granularity: high confidence, taken directly from Huawei's export guide.
- The empty-for-all set (ChargeClass, ChargeDescription placeholder, ContractedUnitPrice, InvoiceIssuerName, ListUnitPrice, PricingCategory, PricingQuantity, PricingUnit, PublisherName, SkuPriceId): high confidence, taken directly from Huawei's published field-conversion table, which states each is "Displayed as empty" or a fixed placeholder.
- The Tags concatenated-string deviation and the ServiceCategory "Computing" example: high confidence, quoted from the field table.
- Present classifications for populated columns (cost columns, attribution identity, commitment-discount family): solid confidence, based on the documented conversion logic rather than an inspected sample file. A Validator run on a live sample is the objective arbiter.
- Feature levels: verified against the bundled v1.2 reference (stamp 2026-06-23) and spot-checked against the live spec on this date. No cache refresh required.
- Substantive-versus-trivial calls and the RAG score reflect the documented data source, not a Validator run on a live sample.
- Overall data quality for this analysis: solid. Huawei publishes a complete field-by-field conversion dictionary, which is unusually clear source material.

## Sources

- FOCUS get-started listing, Huawei Cloud: https://focus.finops.org/get-started/
- Huawei Cloud Cost Center, "FOCUS 1.0 Field Description": https://support.huaweicloud.com/intl/en-us/usermanual-cost/costcenter_000002_03_07.html
- Huawei Cloud Cost Center, "Export to OBS": https://support.huaweicloud.com/intl/en-us/usermanual-cost/costcenter_000002_0302.html
- Huawei Cloud Cost Center, "Creating an OBS Export Task": https://support.huaweicloud.com/intl/en-us/usermanual-cost/costcenter_000002_03_04.html
- FOCUS Specification: https://focus.finops.org/focus-specification/
- FinOps Certified FOCUS Conformant program: https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
