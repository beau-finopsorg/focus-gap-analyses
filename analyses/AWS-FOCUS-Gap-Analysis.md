# Amazon Web Services (AWS) and FOCUS: Conformance Gap Analysis

*Analysis run: July 1, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Provider in scope:** Amazon Web Services (AWS), Data Exports FOCUS 1.2 with AWS columns table (`FOCUS_1_2_AWS`)
**Prepared:** 2026-07-01
**Source analyzed:** AWS FOCUS 1.2 Data Dictionary, AWS FOCUS 1.2 Conformance Gap Report, AWS GA announcement (19 Nov 2025), and the FOCUS get-started page for AWS
**FOCUS baseline for scoring:** v1.2 (current certification baseline)
**FOCUS version AWS ships:** v1.2 (GA Nov 2025), with v1.0 still offered

---

## Executive summary

AWS is an official FOCUS data generator and ships a substantially complete FOCUS v1.2 export today. This is not a from-scratch build: the gap here is not whether an export exists but how complete it is and which spec version it tracks. AWS Data Exports delivers a native FOCUS 1.2 dataset (table `FOCUS_1_2_AWS`) to Amazon S3, in Parquet or CSV, at hourly, daily, or monthly granularity, covering the full four-cost-column structure (ListCost, ContractedCost, BilledCost, EffectiveCost), commitment discounts, capacity reservations, SKU metering, and the v1.2 pricing-currency columns.

All 57 v1.2 columns are present in the schema. AWS publishes its own Conformance Gap Report, which lists a small set of nullability and edge-case deviations rather than any missing column. The rating is Aligned against the v1.2 baseline, with a handful of documented conditional-population gaps that AWS discloses transparently.

**Stat strip:** 57 FOCUS columns (v1.2) | 57 present in schema | 0 of 21 Mandatory gaps are substantive | 11 documented deviations (nullability / edge cases)

**Readiness (RAG):** Cost: Strong | Granularity: Strong | Allocation: Strong | Coverage: Strong | FOCUS shape: Strong | **Overall band: Aligned**

**Recommendation:** Adopt the FOCUS 1.2 export as the primary AWS cost dataset. The documented deviations are conditional edge cases (certain product offerings, reserved-state capacity, minimum-charge quantities) that do not block the common allocation, reporting, and reconciliation use cases. Track AWS's move toward v1.3/v1.4 as those versions mature and Validator support lands.

---

## Part 1: The conformance gap

### 1.1 The data source

AWS exposes FOCUS data through **AWS Data Exports** in the Billing and Cost Management console (the successor delivery mechanism to the legacy Cost and Usage Report). The relevant table is **FOCUS 1.2 with AWS columns** (`FOCUS_1_2_AWS`).

Key characteristics:

- **Delivery:** exported to an Amazon S3 bucket, in Parquet or CSV (gzip/parquet), on a scheduled refresh. A CloudFormation template can automate creation and consolidate multiple accounts into one bucket, and an Athena table for querying.
- **Granularity:** configurable via the `TIME_GRANULARITY` table configuration to HOURLY, DAILY, or MONTHLY. FOCUS 1.0 supported only hourly; 1.2 adds daily and monthly. This satisfies the daily-or-finer requirement comfortably.
- **Scope:** inherits AWS Organizations consolidated billing. A management account export covers the management account plus all member accounts; a member account export covers only that account.
- **Custom columns:** three AWS proprietary columns are added, correctly prefixed: `x_Discounts`, `x_Operation`, `x_ServiceCode`. This follows the FOCUS custom-column convention.
- **Cost columns:** the full four-cost structure is present (ListCost, ContractedCost, BilledCost, EffectiveCost). Discounts, credits, Savings Plans, and Reserved Instance amortization are reflected in EffectiveCost, so the list-cost trap does not apply here: AWS produces reconciled cost columns, not list-only data.

Known limitations are documented by AWS itself in its Conformance Gap Report (see 1.5), and center on conditional nullability rather than absent data.

### 1.2 How conformance is judged

FOCUS conformance is judged column by column. Each column carries a feature level: Mandatory (must be present and populated where applicable), Conditional (required when the provider's model triggers the condition), Recommended (encouraged), or Optional. A dataset conforms when every applicable Mandatory column is present and correctly populated, Conditional columns are present and populated where the condition applies, and values follow FOCUS types, enums, and formats.

Feature levels in this report were verified against the FOCUS v1.2 specification content-constraint tables (bundled reference stamped 2026-06-23). v1.2 has 21 Mandatory, 32 Conditional, and 4 Recommended columns.

### 1.3 Column-by-column status

Status legend: Present (emitted and aligned) / Present, deviation to fix (emitted, wrong format or nullability) / Missing: Mandatory / Missing: Recommended / Missing: Conditional / N/A: null valid.

Feature levels verified against the FOCUS v1.2 specification.

| FOCUS Column | Level | In the source? | Status |
|---|---|---|---|
| AvailabilityZone | R | Yes | Present |
| BilledCost | M | Yes | Present |
| BillingAccountId | M | Yes | Present |
| BillingAccountName | M | Yes | Present |
| BillingAccountType | C | Yes | Present |
| BillingCurrency | M | Yes | Present |
| BillingPeriodEnd | M | Yes | Present |
| BillingPeriodStart | M | Yes | Present |
| CapacityReservationId | C | Yes | Present |
| CapacityReservationStatus | C | Yes | Present, deviation to fix |
| ChargeCategory | M | Yes | Present |
| ChargeClass | M | Yes | Present |
| ChargeDescription | M | Yes | Present |
| ChargeFrequency | R | Yes | Present |
| ChargePeriodEnd | M | Yes | Present |
| ChargePeriodStart | M | Yes | Present |
| CommitmentDiscountCategory | C | Yes | Present |
| CommitmentDiscountId | C | Yes | Present |
| CommitmentDiscountName | C | Yes | Present |
| CommitmentDiscountQuantity | C | Yes | Present |
| CommitmentDiscountStatus | C | Yes | Present |
| CommitmentDiscountType | C | Yes | Present |
| CommitmentDiscountUnit | C | Yes | Present |
| ConsumedQuantity | C | Yes | Present, deviation to fix |
| ConsumedUnit | C | Yes | Present, deviation to fix |
| ContractedCost | M | Yes | Present |
| ContractedUnitPrice | C | Yes | Present, deviation to fix |
| EffectiveCost | M | Yes | Present |
| InvoiceId | R | Yes | Present |
| InvoiceIssuerName | M | Yes | Present, deviation to fix |
| ListCost | M | Yes | Present |
| ListUnitPrice | C | Yes | Present, deviation to fix |
| PricingCategory | C | Yes | Present |
| PricingCurrency | C | Yes | Present |
| PricingCurrencyContractedUnitPrice | C | Yes | Present |
| PricingCurrencyEffectiveCost | C | Yes | Present |
| PricingCurrencyListUnitPrice | C | Yes | Present |
| PricingQuantity | M | Yes | Present |
| PricingUnit | M | Yes | Present, deviation to fix |
| ProviderName | M | Yes | Present |
| PublisherName | M | Yes | Present, deviation to fix |
| RegionId | C | Yes | Present |
| RegionName | C | Yes | Present |
| ResourceId | C | Yes | Present |
| ResourceName | C | Yes | Present |
| ResourceType | C | Yes | Present |
| ServiceCategory | M | Yes | Present |
| ServiceName | M | Yes | Present |
| ServiceSubcategory | R | Yes | Present |
| SkuId | C | Yes | Present, deviation to fix |
| SkuMeter | C | Yes | Present, deviation to fix |
| SkuPriceDetails | C | Yes | Present |
| SkuPriceId | C | Yes | Present, deviation to fix |
| SubAccountId | C | Yes | Present |
| SubAccountName | C | Yes | Present |
| SubAccountType | C | Yes | Present |
| Tags | C | Yes | Present |

**Tally:** 57 of 57 columns present in the schema. No missing columns. 11 columns carry a documented deviation, all conditional nullability or edge-case population issues that AWS discloses in its own Conformance Gap Report. 0 of the 21 Mandatory columns represent a substantive data gap: the two Mandatory columns with deviations (PricingUnit, InvoiceIssuerName, PublisherName) can be null only for narrow product-offering or charge scenarios, not systematically.

### 1.4 What's solved, and what remains

**Solved (the bulk of the work):**

- The full four-cost structure. ListCost, ContractedCost, BilledCost, and EffectiveCost are all present and reconciled, with discounts, credits, Savings Plans, and Reserved Instance amortization flowing into EffectiveCost. This is the single hardest thing for a provider to get right, and AWS ships it.
- Daily and hourly granularity, configurable.
- Full allocation dimensions: ResourceId, ResourceName, ResourceType, Tags (key-value), plus SubAccountId/Name/Type for member-account attribution under consolidated billing.
- The complete v1.2 additions: BillingAccountType, SubAccountType, InvoiceId, the pricing-currency family, capacity-reservation columns, SKU Meter and SKU Price Details, and CommitmentDiscountQuantity/Unit.
- Correct FOCUS shape: PascalCase column IDs, ISO 4217 currencies, ISO 8601 periods, key-value Tags, and `x_`-prefixed custom columns.

**Remains (all conditional edge cases, none blocking):**

- A set of nullability deviations where a column may be null in scenarios FOCUS says it should not (detailed in 1.5).
- No formal FinOps Certified FOCUS designation is asserted on the get-started page; the page confirms v1.0 and v1.2 support and links AWS's own conformance report.
- Version lag against the current latest spec: AWS ships v1.2 while v1.3 (Dec 2025) and v1.4 (Jun 2026) exist. v1.2 is the certification baseline, so this is a currency question, not a conformance failure.

### 1.5 Deviations to fix

These are drawn directly from AWS's published FOCUS 1.2 Conformance Gap Report. Each is conditional: it applies only to specific line-item scenarios.

**Missing-data nullability (column may be null where FOCUS requires non-null):**

- **ContractedUnitPrice:** may be null for certain product offerings on non-correction Usage/Purchase lines.
- **ListUnitPrice:** may be null for certain product offerings on non-correction Usage/Purchase lines.
- **PricingUnit:** may be null for certain product offerings on non-correction Usage/Purchase lines.
- **SkuId:** may be null for certain product offerings on non-correction Usage/Purchase lines.
- **SkuPriceId:** may be null for certain line items where it should not be.
- **InvoiceIssuerName:** may be null for certain charges.
- **PublisherName:** may be null for certain charges.
- **CapacityReservationStatus:** may be null when a reservation is in a "reserved" state that is neither used nor unused, while CapacityReservationId is not null and ChargeCategory is Usage.

**Incorrect-data / value deviations:**

- **ConsumedQuantity:** reflects the quantity charged rather than the quantity consumed, so it can overstate usage where a minimum-charge applies (for example, a 10MB minimum per Athena query, a 10-minute minimum Glue crawler run).
- **SkuMeter:** may be null even when SkuId is null (FOCUS requires SkuMeter be null only when SkuId is null; the mismatch is the deviation).
- **ConsumedUnit:** nullability may not match ConsumedQuantity (FOCUS requires the two to align).

**Already done right:** column presence is complete, the cost quartet is reconciled, tags are key-value, currencies and timestamps follow ISO conventions, and custom columns are `x_`-prefixed.

---

## Part 2: The path forward

### 2.1 Which FOCUS version to target

AWS ships v1.2, which is the current certification baseline, so the export is aligned with what conformance is measured against today. The natural forward path is v1.3 (adds the Contract Commitment dataset and split-cost-allocation columns; deprecates Provider and Publisher) and v1.4 (removes Provider and Publisher; adds Invoice Detail and billing-period datasets for reconciliation). Validator support for v1.4 is expected later in 2026. Continuing to publish v1.2 while these mature is reasonable; the main action is to plan for the Provider/Publisher deprecation so downstream pipelines are not surprised.

### 2.2 What certification requires

FOCUS conformance for data generators runs through the FinOps Foundation. The current program is "FinOps Certified FOCUS v1.2 Conformant" (contact `member-cert@finops.org` for the RFI). Deliverables are a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report, which AWS already publishes. Membership is required to certify, though contributing to the spec is open and free, and AWS is a Steering Committee member and contributor. Open tooling supports the effort: the FOCUS Validator (checks data against the Requirements Model), the FOCUS Converter, and the FOCUS Requirements Model.

### 2.3 Phased roadmap

**Phase 0: validate what exists.** Run a representative FOCUS 1.2 export through the FOCUS Validator, spanning Usage, Purchase, Tax, Credit, and Adjustment lines plus capacity reservations and commitment discounts, to confirm the documented deviations are the only findings.

**Phase 1: close conditional nullability gaps.** Populate ContractedUnitPrice, ListUnitPrice, PricingUnit, SkuId, and SkuPriceId for the product offerings where they are currently null on non-correction Usage/Purchase lines. Ensure InvoiceIssuerName and PublisherName are populated for all charges.

**Phase 2: fix value/consistency deviations.** Align ConsumedUnit nullability with ConsumedQuantity; correct SkuMeter to be null only when SkuId is null; and document or split minimum-charge quantities so ConsumedQuantity reflects consumption rather than the charged minimum. Resolve the CapacityReservationStatus "reserved" state.

**Phase 3: pursue formal conformance.** If AWS elects to certify, submit the RFI, public sample data, and mapping alongside the existing conformance report.

**Phase 4: mature toward the latest version.** Track v1.3/v1.4, plan for the Provider/Publisher removal, and adopt the reconciliation datasets as Validator support lands.

### 2.4 FOCUS Use Cases unlocked

Because AWS ships reconciled cost columns, daily granularity, and full allocation dimensions today, the large majority of FOCUS Use Cases work immediately:

- **Available now:** cost allocation by tag, resource, service, and sub-account; effective-cost and amortized-cost reporting; commitment-discount (Savings Plans / Reserved Instance) utilization and coverage; capacity-reservation utilization; multi-currency reporting via the pricing-currency columns; and invoice reconciliation via InvoiceId (the headline v1.2 use case AWS calls out).
- **Improved after Phase 1/2:** SKU-level unit-economics analysis (depends on the unit-price and SKU columns being fully populated) and precise consumption analytics (depends on ConsumedQuantity reflecting consumption rather than charged minimums).
- **Depends on version:** split cost allocation and contract-commitment tracking arrive with a v1.3+ export.

---

## Part 3: Immediate next steps

1. Adopt the FOCUS 1.2 with AWS columns export as the primary AWS cost dataset; enable daily granularity and consolidate accounts via the CloudFormation template.
2. Run a representative export through the FOCUS Validator to confirm AWS's published gap list is the complete set for your account's usage mix.
3. Review the documented deviations against your actual services to see which apply (many will not, depending on the offerings you consume).
4. Plan pipeline handling for the Provider/Publisher deprecation ahead of any v1.3+ move.
5. If pursuing formal conformance, contact `member-cert@finops.org` for the v1.2 RFI.

---

## Confidence summary

- **AWS ships FOCUS v1.2 (and v1.0):** high confidence. Confirmed by the FOCUS get-started page and the AWS GA announcement of 19 Nov 2025.
- **Delivery, granularity, and full column presence:** high confidence, from the AWS FOCUS 1.2 Data Dictionary (Data Exports to S3; HOURLY/DAILY/MONTHLY; `FOCUS_1_2_AWS`; three `x_` columns).
- **The 11 deviations:** high confidence: they are transcribed from AWS's own published Conformance Gap Report and are conditional edge cases, not missing columns.
- **Feature levels:** high confidence, verified against the bundled v1.2 reference (stamped 2026-06-23), consistent with the live spec; v1.2 remains the certification baseline.
- **Overall band Aligned:** high confidence that AWS ships a substantially complete FOCUS v1.2 export today. This report reflects the documented data source, not a formal certification result; the get-started page does not assert a FinOps Certified FOCUS designation for AWS.
- **Column-level per-account population:** moderate confidence: which of the conditional deviations actually apply depends on the specific services an account consumes and is best confirmed by running the Validator on a real export.

---

## Sources

- FOCUS get-started page for AWS: https://focus.finops.org/get-started/aws/
- AWS FOCUS 1.2 with AWS columns Data Dictionary: https://docs.aws.amazon.com/cur/latest/userguide/table-dictionary-focus-1-2-aws.html
- AWS FOCUS 1.2 Conformance Gap Report: https://docs.aws.amazon.com/cur/latest/userguide/table-dictionary-focus-1-2-aws-conformance.html
- AWS GA announcement, "Data Exports for FOCUS 1.2 is now generally available," 19 Nov 2025: https://aws.amazon.com/blogs/aws-cloud-financial-management/data-exports-for-focus-1-2-is-now-generally-available/
- FOCUS v1.2 specification: https://focus.finops.org/focus-specification/v1-2/
- FinOps Certified FOCUS Conformant program: https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
