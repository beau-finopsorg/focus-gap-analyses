# Redis Cloud and FOCUS: Conformance Gap Analysis

*Analysis run: July 1, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Provider:** Redis (Redis Cloud)
**Product in scope:** Redis Cloud FOCUS cost report (REST API `POST /cost-report`)
**Prepared:** 2026-07-01
**Source analyzed:** Redis Cloud REST API documentation, "Generate FOCUS-compliant cost report" (field-level schema)
**FOCUS baseline:** v1.2 (current certification baseline)
**Status:** Redis is a Supported FOCUS data generator (an export has been provided to the FinOps Foundation). This analysis assesses the completeness of that v1.2 export. Supported is distinct from FinOps Certified FOCUS Conformant, which is earned after submitting a Conformance Gap Report.

---

## Executive summary

Redis Cloud publishes a FOCUS cost report through its REST API, and it is a genuinely strong export. The full effective-cost family is present: `ListCost`, `ContractedCost`, `BilledCost`, and `EffectiveCost` are all emitted as distinct values, along with `ListUnitPrice` and `ContractedUnitPrice`. That is the hardest part of FOCUS to get right, and Redis Cloud has done it. Tags arrive as a proper key-value map, resources and regions are identified, and the cost columns are shaped with FOCUS column IDs out of the box.

The remaining gaps are narrow and mostly structural rather than data problems. Three Mandatory columns are not documented in the export (`ProviderName`, `InvoiceIssuerName`, `ChargeClass`), and none of the three is a genuine data gap: two are fixed literals and the third is a nullable correction flag. A handful of enum and format deviations need tightening, chiefly a `ChargeCategory` set that omits `Credit` even though coupon credits exist, a `ChargeFrequency` hardwired to `Recurring`, and a `BillingAccountType` populated with the non-enum literal `Redis Cloud`.

**Stat strip:** 57 FOCUS columns (v1.2). 35 present. 3 of 3 Mandatory gaps are trivial (fixed literals or a nullable flag). 4 deviations to fix.

**Recommendation:** Add the three trivial Mandatory columns, correct the `ChargeCategory` and `ChargeFrequency` enums, and confirm charge-record granularity. The export is close to a clean v1.2 conformant dataset and is a sound basis for a Conformance Gap Report submission.

### Readiness (RAG)

| Dimension | Rating |
|---|---|
| Cost | Strong |
| Granularity | Partial |
| Allocation | Partial |
| Coverage | Strong |
| FOCUS shape | Strong |
| **Overall band** | **Near-ready** |

---

## Part 1: The conformance gap

Redis Cloud already emits a FOCUS-shaped dataset. This section walks what it exposes, how conformance is judged, and where the export sits column by column.

### 1.1 The data source

Redis Cloud generates a cost report on demand through three REST API calls: `POST /cost-report` (with a `startDate`, `endDate`, and optional filters), a task poll on `GET /tasks/{taskId}`, and a download from `GET /cost-report/{costReportId}`. Output is CSV or JSON. A date range of up to 40 days is supported per report.

Characteristics relevant to FOCUS:

- **FOCUS-native field names:** The report uses FOCUS column IDs directly (`BilledCost`, `EffectiveCost`, `ServiceCategory`, and so on), drawn from the FOCUS column library. No native-to-FOCUS renaming transform is needed.
- **Charge periods:** `ChargePeriodStart` and `ChargePeriodEnd` can differ from the billing period when a resource is created or deleted mid-period, so the report can carry sub-billing-period records. The report is described as breaking down costs per subscription and database by month, so day-level charge records are not clearly asserted.
- **Currency:** Always USD, emitted in both `BillingCurrency` and `PricingCurrency`.
- **Tags:** User-defined tags emit as a JSON `Map<String, String>`, the correct FOCUS key-value shape.
- **Filters:** The report can be filtered by subscription, database, subscription type, region, and tag, but subscription and database identity appear through `ResourceId` and `ResourceType` rather than through the FOCUS SubAccount columns.
- **Discounts and credits:** Contractual (negotiated) discounts flow into `ContractedCost`, and `EffectiveCost` is described as the true cost after all discounts, credits, and adjustments. Coupon credits exist as a separate account mechanism.

### 1.2 How conformance is judged

FOCUS assigns every column a feature level: Mandatory (must be present and populated), Conditional (required when the provider's business model triggers the condition), Recommended, or Optional. Conformance is judged column by column against the FOCUS Requirements Model. A dataset is conformant when every Mandatory column is present and correctly typed, every applicable Conditional column is populated, and values honor FOCUS allowed-value sets and formats.

Feature levels in this report were taken from the verified v1.2 reference and spot-checked live against the FOCUS specification (`ContractedCost` Mandatory, `ChargeClass` Mandatory-nullable) on 2026-07-01. No newer ratified baseline supersedes v1.2 for the current certification badge.

### 1.3 Column-by-column status

Legend: Present; Present, deviation to fix; Missing: Mandatory; Missing: Recommended; Missing: Conditional; N/A: null valid.

| FOCUS Column | Level | In the source? | Status |
|---|---|---|---|
| AvailabilityZone | R | No | Missing: Recommended |
| BilledCost | M | `BilledCost` | Present |
| BillingAccountId | M | `BillingAccountId` | Present |
| BillingAccountName | M | `BillingAccountName` | Present |
| BillingAccountType | C | `BillingAccountType` (`Redis Cloud`) | Present, deviation to fix |
| BillingCurrency | M | `BillingCurrency` (USD) | Present |
| BillingPeriodEnd | M | `BillingPeriodEnd` | Present |
| BillingPeriodStart | M | `BillingPeriodStart` | Present |
| CapacityReservationId | C | No | N/A: null valid |
| CapacityReservationStatus | C | No | N/A: null valid |
| ChargeCategory | M | `ChargeCategory` (no `Credit`) | Present, deviation to fix |
| ChargeClass | M | No | Missing: Mandatory |
| ChargeDescription | M | `ChargeDescription` | Present |
| ChargeFrequency | R | `ChargeFrequency` (always `Recurring`) | Present, deviation to fix |
| ChargePeriodEnd | M | `ChargePeriodEnd` | Present |
| ChargePeriodStart | M | `ChargePeriodStart` | Present |
| CommitmentDiscountCategory | C | No | N/A: null valid |
| CommitmentDiscountId | C | No | N/A: null valid |
| CommitmentDiscountName | C | No | N/A: null valid |
| CommitmentDiscountQuantity | C | No | N/A: null valid |
| CommitmentDiscountStatus | C | No | N/A: null valid |
| CommitmentDiscountType | C | No | N/A: null valid |
| CommitmentDiscountUnit | C | No | N/A: null valid |
| ConsumedQuantity | C | `ConsumedQuantity` | Present |
| ConsumedUnit | C | `ConsumedUnit` | Present |
| ContractedCost | M | `ContractedCost` | Present |
| ContractedUnitPrice | C | `ContractedUnitPrice` | Present |
| EffectiveCost | M | `EffectiveCost` | Present |
| InvoiceId | R | No | Missing: Recommended |
| InvoiceIssuerName | M | No | Missing: Mandatory |
| ListCost | M | `ListCost` | Present |
| ListUnitPrice | C | `ListUnitPrice` | Present |
| PricingCategory | C | `PricingCategory` (`Standard`) | Present |
| PricingCurrency | C | `PricingCurrency` (USD) | Present |
| PricingCurrencyContractedUnitPrice | C | No | N/A: null valid |
| PricingCurrencyEffectiveCost | C | No | N/A: null valid |
| PricingCurrencyListUnitPrice | C | No | N/A: null valid |
| PricingQuantity | M | `PricingQuantity` | Present |
| PricingUnit | M | `PricingUnit` | Present |
| ProviderName | M | No | Missing: Mandatory |
| PublisherName | M | `PublisherName` (`redis.io`) | Present |
| RegionId | C | `RegionId` | Present |
| RegionName | C | `RegionName` | Present |
| ResourceId | C | `ResourceId` | Present |
| ResourceName | C | `ResourceName` | Present |
| ResourceType | C | `ResourceType` | Present |
| ServiceCategory | M | `ServiceCategory` (`Databases`) | Present |
| ServiceName | M | `ServiceName` | Present |
| ServiceSubcategory | R | `ServiceSubcategory` (`Caching`) | Present |
| SkuId | C | No | Missing: Conditional |
| SkuMeter | C | No | Missing: Conditional |
| SkuPriceDetails | C | `SkuPriceDetails` | Present |
| SkuPriceId | C | No | Missing: Conditional |
| SubAccountId | C | No | Missing: Conditional |
| SubAccountName | C | No | Missing: Conditional |
| SubAccountType | C | No | N/A: null valid |
| Tags | C | `Tags` (key-value map) | Present |

**Reading the tally:** Of 57 v1.2 columns, 35 are Present (4 of them carrying a deviation), 3 Mandatory are missing, 2 Recommended are missing, 6 Conditional are missing where the model plausibly triggers them (SKU identifiers and sub-account attribution), and 11 Conditional or Recommended are legitimately N/A (commitment-discount family, capacity reservations, pricing-currency conversions that collapse because billing and pricing are both USD).

### 1.4 What is solved, and what remains

**Solved (the substantive work):** The cost columns are the load-bearing part of any FOCUS dataset, and Redis Cloud emits the full set as distinct values, not copies. `ListCost` is list price, `ContractedCost` reflects negotiated discounts, and `EffectiveCost` is the true cost after all discounts, credits, and adjustments. This is not the common list-cost-only trap: discounts and credits are reconciled into the export rather than deferred to a separate invoice. Resource and region identity, consumed quantity and unit, pricing quantity and unit, tags, and SKU price details are all present and correctly shaped.

**The three Mandatory gaps are trivial, not substantive:**

- `ProviderName`: a fixed literal. Redis is both provider and publisher; `PublisherName` already emits `redis.io`, so `ProviderName` is a one-line add.
- `InvoiceIssuerName`: a fixed literal (Redis is the invoice issuer for direct billing; a marketplace reseller where applicable).
- `ChargeClass`: Mandatory but nullable, populated only to flag corrections to a previously invoiced period. Adding the column and leaving it null on normal charges satisfies the requirement.

No missing Mandatory column represents data that does not exist in the source. This is plumbing.

**Conditional gaps worth closing:** `SubAccountId` and `SubAccountName` would let subscription or database roll up as a FOCUS sub-account rather than only as a resource, which improves allocation. `SkuId`, `SkuMeter`, and `SkuPriceId` would round out SKU-level price transparency alongside the `SkuPriceDetails` already emitted.

### 1.5 Deviations to fix

- `ChargeCategory`: The documented set is `Usage`, `Purchase`, `Tax`, `Adjustment`. FOCUS also defines `Credit`, and Redis Cloud has a coupon-credit mechanism. Credit-bearing rows should carry `ChargeCategory: Credit`, not be folded into `Adjustment`.
- `ChargeFrequency`: Hardwired to `Recurring`. FOCUS allows `One-Time`, `Recurring`, and `Usage-Based`. One-time purchases and usage-metered charges (Pro hourly consumption reads as usage-based) should map to the matching value rather than all being labeled recurring.
- `BillingAccountType`: Populated with the literal `Redis Cloud`. `BillingAccountType` expects a value describing the account structure; a vendor product name is not a conformant value for this column.
- `ChargeFrequency` and granularity: The report is described as a per-month breakdown by subscription and database. Confirm whether charge records are day-level or monthly, since sub-monthly records materially raise the granularity rating and unlock time-series use cases.

**Already done right:** FOCUS column IDs used natively, tags as a key-value map, ISO 4217 currency, ISO 8601 inclusive-start and exclusive-end periods, the full distinct-value cost family, and a valid `ServiceCategory` (`Databases`).

---

## Part 2: The path forward

### 2.1 Which FOCUS version to target

Baseline the build against v1.2, the current certification badge version. The three trivial Mandatory adds and the enum fixes bring the export to a clean v1.2 dataset. When targeting v1.3+ later, note that `Provider` and `Publisher` are deprecated in v1.3 and removed in v1.4, so the `ProviderName` add should be treated as v1.2-scoped.

### 2.2 What certification requires

FOCUS conformance for data generators runs through the FinOps Foundation. Redis is already listed as a Supported data generator; the Conformant designation is earned by submitting a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report (this analysis is its seed). Membership is required for certification; contributing to the spec is open and free. Contact `member-cert@finops.org` for the RFI. Validate output with the open-source FOCUS Validator against the Requirements Model.

### 2.3 Phased roadmap

**Phase 0: Validate what exists.** Run a real cost report (CSV and JSON) through the FOCUS Validator to confirm types and turn up any deviations not visible in the documentation. Confirm charge-record granularity.

**Phase 1: Close the trivial Mandatory gaps.** Add `ProviderName` (`redis.io`), `InvoiceIssuerName`, and `ChargeClass` (nullable). This alone clears the Mandatory column requirement.

**Phase 2: Fix the deviations.** Add `Credit` to `ChargeCategory` for coupon-credit rows, map `ChargeFrequency` to `One-Time` / `Recurring` / `Usage-Based` correctly, and populate `BillingAccountType` with a conformant value.

**Phase 3: Round out Conditional columns.** Add `SubAccountId` and `SubAccountName` for subscription or database attribution, and `SkuId` / `SkuMeter` / `SkuPriceId` for full SKU transparency.

**Phase 4: Mature toward the latest version.** Track v1.3/v1.4, drop `Provider`/`Publisher` when moving past v1.2, and pursue the Conformant designation.

### 2.4 FOCUS Use Cases unlocked

- **Available today:** effective-cost and savings reporting (`Determine Effective Savings Rate`, `Discount Effectiveness by Service`), spend-by-service and by-region allocation, tag-based cost allocation, and cash-vs-accrual comparison, all supported by the present cost family and dimensions.
- **Unlocked by Phase 3:** sub-account chargeback and showback once `SubAccountId`/`SubAccountName` exist.
- **Unlocked by Phase 1/2:** corrections reporting (`Report corrections for a previously invoiced billing period`) once `ChargeClass` is present, and accurate credit reporting once `ChargeCategory: Credit` is emitted.
- **Out of scope for this model:** commitment-discount and capacity-reservation use cases; Redis Cloud sells neither, so that column family is correctly N/A.

---

## Part 3: Immediate next steps

1. Run a live cost report through the FOCUS Validator and record the deviations it flags.
2. Add the three trivial Mandatory columns: `ProviderName`, `InvoiceIssuerName`, `ChargeClass`.
3. Correct the `ChargeCategory` (add `Credit`) and `ChargeFrequency` (three valid values) enums.
4. Replace the `BillingAccountType` literal with a conformant value.
5. Confirm charge-record granularity, and decide whether to expose `SubAccountId`/`SubAccountName`.
6. Engage `member-cert@finops.org` on the Conformant RFI when the dataset validates clean.

---

## Confidence summary

- **Data source (high):** The Redis Cloud documentation lists the FOCUS export field by field, so the per-column mapping rests on published schema rather than inference. Data quality for this analysis is solid.
- **Cost columns present and distinct (high):** The four cost columns and both unit-price columns are individually documented with distinct definitions.
- **Missing Mandatory columns are trivial (high):** `ProviderName` and `InvoiceIssuerName` are fixed literals; `ChargeClass` is nullable. None is a data gap.
- **Deviations (high for the documented enums; medium for granularity):** The `ChargeCategory`, `ChargeFrequency`, and `BillingAccountType` deviations are visible in the documentation. Whether charge records are day-level or monthly is not fully resolved in the docs and should be confirmed against a live report.
- **Conditional SKU/sub-account gaps (medium):** Classified as missing because the model plausibly supports them; a live report may reveal partial population not shown in the field tables.
- **Feature levels (high):** Verified against the bundled v1.2 reference and spot-checked live against the FOCUS specification on 2026-07-01.

---

## Sources

- Redis Cloud REST API, "Generate FOCUS-compliant cost report": https://redis.io/docs/latest/operate/rc/api/examples/generate-cost-report/
- Redis Cloud, "Billing & payments": https://redis.io/docs/latest/operate/rc/billing-and-payments/
- FOCUS Specification v1.2: https://focus.finops.org/focus-specification/v1-2/
- FOCUS column library: https://focus.finops.org/focus-columns/
- FOCUS Validator and Requirements Model: https://focus.finops.org/

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
