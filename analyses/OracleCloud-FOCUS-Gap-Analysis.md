# Oracle Cloud Infrastructure and FOCUS: Conformance Gap and Adoption Roadmap

*Analysis run: July 1, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Provider and product in scope:** Oracle Cloud Infrastructure (OCI), FOCUS CSV cost report.
**Prepared:** July 1, 2026.
**Source analyzed:** OCI Cost Reports documentation, FOCUS Cost Report Schema (the native-to-FOCUS mapping table published by Oracle), and the FOCUS get-started page for Oracle Cloud.
**FOCUS baseline for this analysis:** v1.2 (the current certification baseline, 57 columns). OCI ships a **FOCUS v1.0** export today (43-column release), so this report scores the shipped v1.0 dataset against the v1.2 column set and flags the v1.1 and v1.2 additions as the gap to close.

---

## Executive summary

Oracle Cloud Infrastructure is an official FOCUS data generator listed on focus.finops.org/get-started. The question here is not whether OCI produces a FOCUS dataset, it does, but which version it targets and how complete that export is against the current certification baseline.

OCI generates an industry-standard FOCUS CSV cost report automatically, at resource-level and hourly granularity, across all commercial-realm regions, alongside its proprietary cost report. The export is a genuine FOCUS dataset with FOCUS column IDs, real cost columns (BilledCost, EffectiveCost, ListCost), resource identity, sub-account attribution, and tags. That places OCI well beyond a native schema needing a from-scratch transform.

The gap is version and completeness. The get-started page states OCI supports **FOCUS v1.0**, announced June 2024. The published schema confirms a v1.0-era column set: it uses the v1.0 names `ChargeSubcategory`, `Region`, and `UsageQuantity`/`UsageUnit` rather than the v1.1-plus `ServiceSubcategory`, `RegionId`, and `ConsumedQuantity`/`ConsumedUnit`, and it omits every column FOCUS added in v1.1 and v1.2. Against the v1.2 baseline, OCI is missing the capacity-reservation family, the SKU Meter and SKU Price Details columns, the commitment-discount quantity and unit columns, and the v1.2 additions (account and sub-account Type, Invoice ID, and the pricing-currency family). A small set of present columns also carry format or mapping deviations that a v1.2 export would need to correct.

**Stat strip:** 57 FOCUS columns (v1.2 baseline). 30 present or partially present in the OCI v1.0 export. 3 of the missing-Mandatory columns are substantive, the rest are trivial or nullable. 6 present columns carry deviations to fix.

**Recommendation:** Treat OCI as a shipping FOCUS v1.0 generator with a substantially complete cost dataset, and target v1.2 for certification. The work is version uplift and deviation cleanup, not building a FOCUS export from nothing.

### Readiness (RAG)

| Dimension | Rating |
|---|---|
| Cost | Strong |
| Granularity | Strong |
| Allocation | Strong |
| Coverage | Partial |
| FOCUS shape | Partial |
| **Overall band** | **Structured** |

The band reflects the shipped v1.0 data source reviewed, not a formal certification result. OCI holds no FinOps Certified FOCUS Conformant designation on the get-started page, which lists it as a data generator supporting v1.0.

---

## Part 1: The conformance gap

### 1.1 The data source

OCI produces FOCUS CSV cost reports automatically every six hours, stored in an Oracle-owned Object Storage bucket and downloadable from the Cost and Usage Reports page in the Console, the CLI, or the API. Reports are partitioned by usage date in a year/month/day folder structure and retained for one year. FOCUS reports are available in all commercial-realm regions.

Characteristics relevant to conformance:

- **Granularity:** one row per OCI resource per hour, with usage, price, and cost. This is sub-daily, resource-level granularity, stronger than the daily minimum FOCUS assumes.
- **Cost basis:** BilledCost and EffectiveCost both map to `cost/myCost`, the cost after applicable discounts. ListCost and ListUnitPrice are supplied from list price. OCI notes BilledCost excludes taxes and may vary from the invoice amount, and that Oracle Universal Credits and overage are reflected in the billed values.
- **Corrections:** corrections arrive as new rows carrying `lineItem/isCorrection` and a `lineItem/backReferenceNo` to the amended line. The mechanic FOCUS models with ChargeClass exists in the source, though it is not surfaced as a ChargeClass column in the v1.0 export.
- **Historical data:** Oracle publishes a prebuilt function (the Cost Reports FOCUS converter) to convert historical proprietary data to FOCUS format.
- **Key limitation:** the export is anchored to FOCUS v1.0, so the v1.1 and v1.2 columns are absent, and a handful of present columns carry format or mapping issues (see 1.5).

### 1.2 How conformance is judged

FOCUS assigns each column a feature level: Mandatory, Conditional, Recommended, or Optional. A conformant dataset must include and populate every Mandatory column, must populate Conditional columns when the provider's model triggers the condition, and should supply Recommended columns. Conformance is judged column by column against the Requirements Model, so the analysis turns on getting the feature levels right for the target version.

Feature levels in the table below were taken from the verified v1.2 reference and spot-checked against the live FOCUS specification via the FOCUS MCP server on July 1, 2026. The live check confirmed the v1.0 column set is 43 columns and that the v1.2 baseline is 57, with the shared columns carrying stable levels across v1.0 through v1.2.

### 1.3 Column-by-column status

Feature levels verified against FOCUS Specification v1.2. The "In the source?" column reflects the OCI FOCUS v1.0 export as published in Oracle's schema map.

Status legend: Present (emitted and aligned); Present, deviation to fix (emitted, wrong format or invalid value); Missing: Mandatory (blocks conformance); Missing: Recommended (does not block); Missing: Conditional (required when the model triggers it); N/A: null valid (does not apply to OCI's model, column should exist and be null).

| § | FOCUS Column (v1.2) | Level | In the OCI FOCUS export? | Status |
|---|---|---|---|---|
| 3.1 | AvailabilityZone | R | Yes (`product/availabilityDomain`) | Present |
| 3.2 | BilledCost | M | Yes (`cost/myCost`) | Present |
| 3.3 | BillingAccountId | M | Yes (`cost/subscriptionId`) | Present |
| 3.4 | BillingAccountName | M | No (mapped to NONE, null) | Present, deviation to fix |
| 3.5 | BillingAccountType | C | No (v1.2 addition) | Missing: Conditional |
| 3.6 | BillingCurrency | M | Yes (`cost/currencyCode`) | Present |
| 3.7 | BillingPeriodEnd | M | Yes (derived) | Present |
| 3.8 | BillingPeriodStart | M | Yes (derived) | Present |
| 3.9 | CapacityReservationId | C | No (v1.1 addition) | N/A: null valid |
| 3.10 | CapacityReservationStatus | C | No (v1.1 addition) | N/A: null valid |
| 3.11 | ChargeCategory | M | Yes (`lineItem/isCorrection`) | Present, deviation to fix |
| 3.12 | ChargeClass | M | No (correction data exists, not surfaced) | Missing: Mandatory |
| 3.13 | ChargeDescription | M | Yes (`product/description`) | Present |
| 3.14 | ChargeFrequency | R | Yes (defaults to Usage-Based) | Present, deviation to fix |
| 3.15 | ChargePeriodEnd | M | Yes (`lineItem/intervalUsageEnd`) | Present, deviation to fix |
| 3.16 | ChargePeriodStart | M | Yes (`lineItem/intervalUsageStart`) | Present, deviation to fix |
| 3.17 | CommitmentDiscountCategory | C | No (mapped to NONE, null) | N/A: null valid |
| 3.18 | CommitmentDiscountId | C | No (mapped to NONE, null) | N/A: null valid |
| 3.19 | CommitmentDiscountName | C | No (mapped to NONE, null) | N/A: null valid |
| 3.20 | CommitmentDiscountQuantity | C | No (v1.1 addition) | N/A: null valid |
| 3.21 | CommitmentDiscountStatus | C | No (mapped to NONE, null) | N/A: null valid |
| 3.22 | CommitmentDiscountType | C | No (OCI has no reserved instances) | N/A: null valid |
| 3.23 | CommitmentDiscountUnit | C | No (v1.1 addition) | N/A: null valid |
| 3.24 | ConsumedQuantity | C | Partial (`usage/billedQuantity` as UsageQuantity) | Present, deviation to fix |
| 3.25 | ConsumedUnit | C | Partial (`cost/skuUnitDescription` as UsageUnit) | Present, deviation to fix |
| 3.26 | ContractedCost | M | No | Missing: Mandatory |
| 3.27 | ContractedUnitPrice | C | No | Missing: Conditional |
| 3.28 | EffectiveCost | M | Yes (`cost/myCost`) | Present |
| 3.29 | InvoiceId | R | No (v1.2 addition) | Missing: Recommended |
| 3.30 | InvoiceIssuerName | M | Yes (defaults to Oracle) | Present |
| 3.31 | ListCost | M | Yes (from list price) | Present |
| 3.32 | ListUnitPrice | C | Yes (from list price) | Present |
| 3.33 | PricingCategory | C | No (mapped to NONE, null) | Missing: Conditional |
| 3.34 | PricingCurrency | C | No (v1.2 addition) | Missing: Conditional |
| 3.35 | PricingCurrencyContractedUnitPrice | C | No (v1.2 addition) | N/A: null valid |
| 3.36 | PricingCurrencyEffectiveCost | C | No (v1.2 addition) | Missing: Conditional |
| 3.37 | PricingCurrencyListUnitPrice | C | No (v1.2 addition) | Missing: Conditional |
| 3.38 | PricingQuantity | M | Yes (`usage/billedQuantity`) | Present |
| 3.39 | PricingUnit | M | Yes (`cost/skuUnitDescription`) | Present |
| 3.40 | ProviderName | M | Yes (defaults to Oracle) | Present |
| 3.41 | PublisherName | M | Yes (Oracle, or third-party marketplace) | Present |
| 3.42 | RegionId | C | Partial (`product/region` as Region) | Present, deviation to fix |
| 3.43 | RegionName | C | No (single Region field only) | Missing: Conditional |
| 3.44 | ResourceId | C | Yes (`product/resourceId`) | Present |
| 3.45 | ResourceName | C | No (Oracle does not publish, null) | N/A: null valid |
| 3.46 | ResourceType | C | Yes (e.g. Storage) | Present |
| 3.47 | ServiceCategory | M | Yes (FOCUS enum) | Present |
| 3.48 | ServiceName | M | Yes (`product/service`) | Present |
| 3.49 | ServiceSubcategory | R | No (v1.0 emits ChargeSubcategory, null) | Missing: Recommended |
| 3.50 | SkuId | C | Yes (`cost/productSku`) | Present |
| 3.51 | SkuMeter | C | No (v1.1 addition) | Missing: Conditional |
| 3.52 | SkuPriceDetails | C | No (v1.1 addition) | Missing: Conditional |
| 3.53 | SkuPriceId | C | No (construct does not exist in OCI, null) | N/A: null valid |
| 3.54 | SubAccountId | C | Yes (`lineItem/TenantId`) | Present |
| 3.55 | SubAccountName | C | Yes (tenancy name) | Present |
| 3.56 | SubAccountType | C | No (v1.2 addition) | Missing: Conditional |
| 3.57 | Tags | C | Yes (`tags/`, JSON) | Present, deviation to fix |

**Reading the tally.** Of 57 v1.2 columns: 24 are Present and conformant, 6 are Present with a deviation to fix, 3 are Missing Mandatory, 2 are Missing Recommended, 9 are Missing Conditional (the condition applies to OCI's model), and 13 are N/A null-valid (Conditional or Recommended columns OCI's model does not trigger). The three missing Mandatory columns are ChargeClass, ContractedCost, and, in practice, BillingAccountName (present as a column but mapped to null). The v1.1 and v1.2 additions account for most of the Missing Conditional and N/A entries, which is expected for a v1.0 export.

### 1.4 What's solved, and what remains

**Solved (the substance is present).** The hard parts of a FOCUS dataset already exist in OCI's export: resource-level, hourly charge records; BilledCost and EffectiveCost; ListCost and ListUnitPrice; ServiceCategory as a FOCUS enum; SKU ID; sub-account attribution via tenancy; and tags. This is a working FOCUS cost dataset, not a native schema.

**Substantive gaps (real data or real reconciliation work).**

- **ContractedCost (Mandatory):** OCI supplies BilledCost, EffectiveCost, and ListCost but not ContractedCost. OCI sells commitment-based pricing through Oracle Universal Credits and Funded Allocation, so the contracted/negotiated rate is a real distinct value, not a copy of ListCost. Producing ContractedCost means reconciling the negotiated commit rate back to the usage line. This is the single most substantive gap.
- **BillingAccountName (Mandatory):** the column exists but maps to null. A conformant export must populate the billing account (subscription) name. This is substantive only insofar as the name must be sourced and joined; the identifier is already present.
- **EffectiveCost equals BilledCost:** OCI maps both to `cost/myCost`. When commitment amortization or credits apply, EffectiveCost and BilledCost can legitimately differ. Confirm whether OCI's model ever separates them; if so, EffectiveCost is a reconciliation task, not a copy.

**Trivial gaps (plumbing, derivable, or nullable).**

- **ChargeClass (Mandatory, nullable):** populated only for corrections. OCI already emits `lineItem/isCorrection` and `lineItem/backReferenceNo`, so ChargeClass is a direct derivation (set to Correction on correction rows, null otherwise).
- **The v1.1 and v1.2 additions** (BillingAccountType, SubAccountType, InvoiceId, the pricing-currency family, SkuMeter, SkuPriceDetails): these are the version-uplift columns. Several are derivable or defaultable; the pricing-currency family matters only where pricing currency differs from billing currency.

### 1.5 Deviations to fix

Present columns that carry a format, mapping, or value issue:

- **ChargeCategory mapped from `lineItem/isCorrection`:** ChargeCategory must be one of Usage, Purchase, Tax, Credit, Adjustment. Mapping it from a correction boolean cannot produce the full enum. OCI's own description mixes Usage and Adjustment values, but the source field is the wrong basis. Charge category should be derived from the line's economic nature (usage, tax, credit), with corrections carried on ChargeClass instead.
- **ChargePeriodStart and ChargePeriodEnd as epoch milliseconds:** FOCUS requires ISO 8601 timestamps with inclusive-start, exclusive-end semantics. Oracle's schema describes these as milliseconds since epoch, and its start/end descriptions appear transposed. Emit ISO 8601 and confirm the boundary semantics.
- **Tags as a JSON byte array:** FOCUS represents tags as key-value pairs. Oracle stores Tags as JSON described as a byte array. Confirm the emitted shape is proper key-value pairs, not a serialized blob or an array of bare strings.
- **RegionId carrying a Region value:** the v1.0 export has a single Region field. v1.2 splits this into RegionId and RegionName. Map the OCI region to RegionId and add RegionName.
- **ConsumedQuantity and ConsumedUnit named UsageQuantity and UsageUnit:** v1.0 used the Usage names; v1.1-plus renamed them. Rename on uplift.
- **ChargeFrequency defaulting to Usage-Based:** defaulting the whole column to one value is acceptable for a usage-only feed but understates purchases and recurring fees if those ever appear. Confirm the default holds across all charge types.

**Already done right:** FOCUS column IDs, ServiceCategory as a valid FOCUS enum, real cost columns, resource and sub-account identity, and a genuine tags column. These are the parts providers most often get wrong, and OCI has them.

---

## Part 2: The path forward

### 2.1 Which FOCUS version to target

OCI ships v1.0 today. The current certification baseline is **v1.2**, so v1.2 is the certification target. Design toward the latest ratified version (v1.4, June 2026) where cheap, but note that v1.3 deprecates and v1.4 removes ProviderName and PublisherName, which OCI currently populates. The pragmatic path is to certify at v1.2 and track v1.3/v1.4 for the Provider/Publisher removal and the reconciliation datasets.

### 2.2 What certification requires

FOCUS conformance for data generators runs through the FinOps Foundation. The program is "FinOps Certified FOCUS v1.2 Conformant" (contact member-cert@finops.org for the RFI). Membership is required for certification, though contributing to the spec is open and free. Deliverables are a conformant dataset, public sample data, a native-to-FOCUS mapping (Oracle already publishes one), and a Conformance Gap Report (this analysis is its seed). Open-source tooling: the FOCUS Validator (checks data against the Requirements Model), the FOCUS Converter (provider-native to FOCUS), and the FOCUS Requirements Model (machine-readable MUST/SHOULD/MAY rules).

### 2.3 Phased roadmap

**Phase 0: Validate what exists.** Run a current OCI FOCUS v1.0 sample through the FOCUS Validator. Confirm the v1.0 baseline, catalog the deviations objectively, and fix scope. Oracle's published schema map is the starting artifact.

**Phase 1: Close the Mandatory gaps.** Add ChargeClass (derive from `lineItem/isCorrection`). Populate BillingAccountName. Add ContractedCost by reconciling the Universal Credits/Funded Allocation commit rate to the usage line, and confirm whether EffectiveCost should diverge from BilledCost under amortization.

**Phase 2: Fix the deviations.** Re-base ChargeCategory on the line's economic nature and move corrections to ChargeClass. Emit ISO 8601 charge-period timestamps with correct inclusive/exclusive boundaries. Confirm Tags are key-value pairs. These unlock clean validation.

**Phase 3: Uplift to v1.2 columns.** Rename UsageQuantity/UsageUnit to ConsumedQuantity/ConsumedUnit and ChargeSubcategory to ServiceSubcategory. Split Region into RegionId and RegionName. Add BillingAccountType, SubAccountType, InvoiceId, the pricing-currency family (where pricing currency differs from billing currency), SkuMeter, and SkuPriceDetails.

**Phase 4: Certify and track forward.** Submit for FinOps Certified FOCUS v1.2 Conformant. Plan the Provider/Publisher removal for a later v1.3/v1.4 pass, along with the reconciliation datasets v1.4 adds.

### 2.4 FOCUS Use Cases unlocked

Because OCI already emits resource-, tag-, and hour-level data with real cost columns, most allocation, showback, anomaly-detection, and trend-reporting use cases work against the current v1.0 export today. Multi-currency allocation, which the get-started page links directly, works once the pricing-currency columns land in Phase 3. Reconciliation and actuals-versus-contracted use cases need ContractedCost from Phase 1. Commitment-utilization and capacity-reservation use cases are out of scope for OCI's model, which has no reserved instances and does not surface capacity reservations.

---

## Part 3: Immediate next steps

1. Run a live OCI FOCUS v1.0 sample through the FOCUS Validator to convert this manual pass into an objective baseline.
2. Derive and add ChargeClass from the existing correction fields; it is the cheapest Mandatory win.
3. Populate BillingAccountName from the subscription record.
4. Scope the ContractedCost reconciliation against Universal Credits and Funded Allocation, the one substantive data build.
5. Fix the ChargeCategory basis and the epoch-millisecond charge-period timestamps; these are the deviations most likely to fail validation.
6. Plan the v1.0-to-v1.2 column rename and additions as a single uplift, then submit for v1.2 certification.

---

## Confidence summary

- **FOCUS version shipped (v1.0):** high confidence. The get-started page states "Version Supported: v1.0," and Oracle's schema uses v1.0 column names (ChargeSubcategory, Region, UsageQuantity/UsageUnit) and omits all v1.1 and v1.2 additions.
- **Feature levels and column counts:** high confidence. Levels were taken from the verified v1.2 reference and spot-checked against the live FOCUS specification via the FOCUS MCP server on July 1, 2026; the live check confirmed 43 v1.0 columns and 57 v1.2 columns with stable shared levels. No cache refresh was needed.
- **Column mapping and deviations:** high confidence on presence and mapping, drawn directly from Oracle's published FOCUS Cost Report Schema table. Moderate confidence on the exact emitted format of Tags and charge-period timestamps, which the docs describe but a sample would confirm.
- **ContractedCost and EffectiveCost as substantive:** moderate to high confidence. OCI's commitment model (Universal Credits, Funded Allocation) means contracted rates are real and distinct; whether EffectiveCost ever diverges from BilledCost in practice would be confirmed by a sample.
- **Overall readiness band (Structured):** OCI ships a substantially complete FOCUS v1.0 cost export with strong cost, granularity, and allocation. The band is held below the higher tiers by the version gap to v1.2 and the format deviations, not by missing source data. This score reflects the data source reviewed, not a formal certification result.

---

## Sources

- Oracle Cloud Infrastructure documentation, Cost Reports and FOCUS Cost Report Schema: https://docs.oracle.com/en-us/iaas/Content/Billing/Concepts/costusagereportsoverview.htm
- FOCUS get-started page for Oracle Cloud: https://focus.finops.org/get-started/oracle-cloud/
- Oracle blog, Announcing FOCUS support for OCI cost reports (June 2024): https://blogs.oracle.com/cloud-infrastructure/post/announcing-focus-support-for-oci-cost-reports
- OCI FinOps Hub documentation: https://docs.oracle.com/en-us/iaas/Content/Billing/Concepts/FinOps.htm
- FOCUS Specification and Column Library: https://focus.finops.org/focus-specification/
- Feature levels verified via the FOCUS MCP server against the live specification, July 1, 2026.

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
