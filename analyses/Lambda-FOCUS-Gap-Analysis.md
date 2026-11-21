# Lambda & FOCUS: Data Generator Gap Analysis

*Analysis run: June 25, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** Lambda (Lambda Labs)  
**Prepared:** June 25, 2026  
**Source:** Lambda Cloud API v1; Lambda billing portal  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 35 Present, 11 Deviation, 0 Missing Mandatory, 5 Missing Conditional, 1 Missing Recommended, 5 N/A

---

## Executive Summary

Lambda's GPU cloud billing model maps cleanly to FOCUS. Per-hour on-demand pricing with public rate cards and per-instance resource metadata gives Lambda a strong structural baseline. All 21 Mandatory columns have source data; the 11 Deviations cover cost enrichment for reserved instances and enum derivation. The five Missing Conditional columns are all in the SKU price detail family, which requires a pricing catalog integration Lambda does not currently surface via its billing API. Five columns are legitimately N/A: SubAccount (Lambda has no sub-account hierarchy) and CapacityReservation (reserved instances map to CommitmentDiscount, not CapacityReservation).

**Recommendation:** Start with the on-demand compute transform. Lambda's hourly billing, public pricing, and per-instance IDs make a conformant dataset achievable in one phase. Add reserved instance amortization (CommitmentDiscount) and CommitmentDiscountStatus logic in a second pass.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

**Lambda Cloud API v1** (`https://cloud.lambdalabs.com/api/v1`): The primary billing and resource management API. Endpoints include `/instance-types` (catalog with per-hour pricing per GPU type), `/instances` (running instances with type, region, start time), and `/billing` (usage records). Key fields: `instance_type`, `name`, `region_name`, `start_time`, `end_time`, `price_cents_per_hour`.

**Lambda Billing Portal / Invoices**: Provides monthly invoice data with line items per instance or reservation. InvoiceId, total amount, and billing period are available.

**Reserved Instances**: Lambda offers 1-year GPU reservations. These map to CommitmentDiscount in FOCUS. The reservation ID, GPU type, and term are available via the reservations API endpoint.

Characteristics relevant to FOCUS:
- Per-hour billing for on-demand: clean PricingQuantity (hours) and PricingUnit ("Hours") for every on-demand charge row.
- Public pricing: Lambda publishes per-GPU-type hourly rates at lambdalabs.com/service/gpu-cloud/pricing. ListUnitPrice is derivable from the public rate card.
- Flat account structure: Lambda has no sub-account or resource group hierarchy. BillingAccountId is the Lambda organization or user account.
- Regions: Lambda data centers are named (US-East-1, US-West-1, etc.) with human-readable display names.
- Tags: Lambda supports instance-level tags via the API; tag data is available on instance records.
- Storage: Lambda Filesystems are billed per GB per month, with PricingQuantity in GB and PricingUnit in "GB-Month".

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven. Each column carries a feature level: Mandatory (must exist and be populated where applicable), Conditional (must exist; populated when the provider's model triggers the condition, otherwise null), or Recommended. A conformant dataset presents the full column set under FOCUS column IDs, populates every Mandatory column, satisfies Conditional columns where applicable, and uses the correct types and allowed values.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | Lambda source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Invoice line item amount (on-demand: hours × rate; reserved: monthly payment) | Present |
| EffectiveCost | Mandatory | On-demand: = BilledCost; reserved instances: amortize reservation upfront/monthly commitment across usage hours | Deviation |
| ListCost | Mandatory | Public rate × PricingQuantity from lambdalabs.com pricing page; = BilledCost for on-demand PAYG | Present |
| ContractedCost | Mandatory | = ListCost for standard accounts; enterprise custom pricing not exposed via API | Deviation |
| BillingAccountId | Mandatory | Lambda organization or user account ID | Present |
| BillingAccountName | Mandatory | Organization or user name from Lambda account | Present |
| BillingCurrency | Mandatory | USD | Present |
| BillingPeriodStart | Mandatory | First day of billing month | Present |
| BillingPeriodEnd | Mandatory | Last day of billing month | Present |
| ChargePeriodStart | Mandatory | Instance `start_time` for on-demand; reservation period start for reserved | Present |
| ChargePeriodEnd | Mandatory | Instance `end_time` (or billing period end if still running) for on-demand; reservation period end for reserved | Present |
| ChargeDescription | Mandatory | Instance type + GPU label (e.g., "1x NVIDIA H100 SXM5 80GB") or filesystem name | Present |
| ChargeCategory | Mandatory | Derive: "Usage" for on-demand compute and storage; "Purchase" for reserved instance commitments | Deviation |
| ChargeClass | Mandatory (nullable) | null except for correction charges | Present |
| InvoiceIssuerName | Mandatory | "Lambda Labs, Inc." | Present |
| ProviderName | Mandatory (dep. v1.3) | "Lambda" | Present |
| PublisherName | Mandatory (dep. v1.3) | "Lambda" | Present |
| ServiceName | Mandatory | "Lambda GPU Cloud" for compute; "Lambda Filesystems" for storage | Present |
| ServiceCategory | Mandatory | "Compute" for GPU instances; "Storage" for filesystems | Deviation |
| PricingQuantity | Mandatory | Hours for compute (on-demand duration); GB for storage (monthly GB usage) | Present |
| PricingUnit | Mandatory | "Hours" for compute; "GB-Month" for storage | Present |
| ConsumedQuantity | Conditional | = PricingQuantity (Lambda charges for actual time used; no rateability adjustment) | Present |
| ConsumedUnit | Conditional | = PricingUnit | Present |
| ListUnitPrice | Conditional | Public rate from Lambda pricing page per GPU type per hour (e.g., H100 SXM5: $2.49/hr) | Present |
| ContractedUnitPrice | Conditional | = ListUnitPrice for standard accounts; enterprise custom rates not exposed | Deviation |
| PricingCategory | Conditional | Derive: "Standard" for on-demand; "Committed" for reserved instances | Deviation |
| ChargeFrequency | Conditional | Derive: "Usage-Based" for on-demand compute (charged per actual hour); "Recurring" for reserved instance monthly payments | Deviation |
| BillingAccountType | Conditional | Derive from account plan (PAYG or Enterprise) | Present |
| SubAccountId | Conditional | N/A: Lambda has no sub-account or project hierarchy | N/A |
| SubAccountName | Conditional | N/A | N/A |
| SubAccountType | Conditional | N/A | N/A |
| ResourceId | Conditional | Lambda instance ID (UUID) | Present |
| ResourceName | Conditional | Instance name from API or display label | Present |
| ResourceType | Conditional | GPU instance type (e.g., "gpu_1x_h100_sxm5", "gpu_8x_a100") | Present |
| SkuId | Conditional | Instance type identifier from `instance_type` field | Present |
| Tags | Conditional | Instance tags available from the Lambda instances API; parse to FOCUS key-value format | Deviation |
| PricingCurrency | Conditional | USD | Present |
| PricingCurrencyListUnitPrice | Conditional | = ListUnitPrice (Lambda invoices in USD; no currency conversion) | Present |
| PricingCurrencyContractedUnitPrice | Conditional | = ContractedUnitPrice; Deviation because ContractedUnitPrice requires enterprise rate data for custom accounts | Deviation |
| PricingCurrencyEffectiveCost | Conditional | = EffectiveCost; Deviation because reserved instance amortization logic is required | Deviation |
| SkuMeter | Conditional | Not exposed in billing API; instance type identifies the compute unit but no separate SkuMeter display label is published | Missing: Conditional |
| SkuPriceId | Conditional | Pricing plan rate identifier not exposed in billing API | Missing: Conditional |
| SkuPriceDetails | Conditional | Tier pricing details not applicable (Lambda uses flat per-hour rates); field not exposed | Missing: Conditional |
| RegionId | Conditional | Lambda region code (e.g., "us-east-1", "us-west-2", "europe-central-1") | Present |
| RegionName | Conditional | Lambda region display name (e.g., "US East", "US West", "Europe Central") | Present |
| CommitmentDiscountId | Conditional | Lambda reservation ID | Present |
| CommitmentDiscountName | Conditional | Reservation display name or GPU type + term label | Present |
| CommitmentDiscountType | Conditional | "Reserved" | Present |
| CommitmentDiscountCategory | Conditional | "Usage" (Lambda reservations are capacity commitments, not spend commitments) | Present |
| CommitmentDiscountStatus | Conditional | Derive: "Used" when reserved capacity is running; "Unused" when reserved capacity has no running instance during a billing period | Deviation |
| CommitmentDiscountQuantity | Conditional | Per-charge commitment quantity not exposed in billing API | Missing: Conditional |
| CommitmentDiscountUnit | Conditional | Same | Missing: Conditional |
| CapacityReservationId | Conditional | N/A: Lambda reserved instances are modeled as CommitmentDiscount, not as a separate CapacityReservation construct | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | Lambda invoice number from billing portal | Present |
| ServiceSubcategory | Recommended | No native field; would require mapping "GPU Compute" and "Filesystem Storage" as subcategories | Missing: Recommended |
| AvailabilityZone | Recommended | Lambda zone-level data present for some regions (e.g., "us-east-1a"); not all regions expose zone granularity | Present |

**Tally:** 35 Present, 11 Deviation, 0 Missing Mandatory, 5 Missing Conditional, 1 Missing Recommended, 5 N/A

### 1.4 What Is Solved, and What Remains

**Solved**

Lambda's billing model is the most straightforward possible for FOCUS: per-hour compute with public pricing and per-instance resource IDs. All 21 Mandatory columns have source data. ListCost is derivable from the public rate card without API integration (the pricing page is publicly accessible and stable). ResourceId, ResourceName, and ResourceType are present for every compute charge row. RegionId and RegionName are available and well-structured. The CommitmentDiscount family is populated for reserved instances.

**Remaining**

CommitmentDiscountStatus requires logic to determine whether a reserved instance was actively running (Used) or idle (Unused) during each billing period. The Lambda billing API provides reservation records but not per-period utilization status; this requires cross-referencing instance run records with the reservation term.

The five Missing Conditional columns (SkuMeter, SkuPriceId, SkuPriceDetails, CommitmentDiscountQuantity, CommitmentDiscountUnit) are absent from the Lambda billing API. Lambda's pricing model is simple enough that SkuPriceDetails (tiered pricing) is not applicable; the main gap is SkuMeter and SkuPriceId for the SKU catalog link.

### 1.5 Deviations to Fix

**EffectiveCost for reserved instances**  
For on-demand compute, EffectiveCost = BilledCost. For reserved instances, FOCUS requires EffectiveCost to reflect the amortized daily cost of the commitment allocated to each usage period. Compute: monthly reservation payment ÷ days in the month × days the instance ran. For unused reservation days, EffectiveCost for those rows = the amortized daily reservation cost (even though no instance ran).

**ChargeCategory**  
Derive: on-demand compute and storage → "Usage"; reserved instance payments → "Purchase"; credit adjustments → "Credit". Build from charge type in the Lambda invoice API.

**ServiceCategory**  
Lambda does not emit a FOCUS-aligned service category. Map: GPU compute instances → "Compute"; Lambda Filesystems → "Storage". This is a simple two-value mapping.

**CommitmentDiscountStatus**  
Cross-reference Lambda reservation records with instance run records per billing period. If the reserved instance had an active running instance during the period → "Used". If the reservation was active but no instance was running → "Unused". Lambda may need to expose a utilization endpoint for this to be computed without joining separate API calls.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (released June 4, 2026); certify at FOCUS v1.2. ProviderName and PublisherName are deprecated in v1.3 and removed in v1.4.

### 2.2 What Certification Requires

Contact `member-cert@finops.org` for the RFI. Deliverables: conformant dataset under FOCUS column IDs, sample data passing the FOCUS Validator, documented native-to-FOCUS mapping, and a Conformance Gap Report. Lambda's 0 Missing Mandatory makes certification achievable after Phase 1.

### 2.3 Phased Roadmap

**Phase 0: Validate and scope**  
Confirm billing API access. Pull a sample monthly dataset for on-demand and reserved instances. Verify that `start_time`, `end_time`, and `price_cents_per_hour` are available per instance record. Open the RFI with `member-cert@finops.org`.

**Phase 1: Core transform (on-demand)**  
Build the on-demand compute transform. Map BilledCost, ListCost (from public rate card), ChargePeriod, ResourceId/Name/Type, RegionId/Name, SkuId, PricingQuantity/Unit, ServiceName, ChargeCategory/Description, InvoiceId, AvailabilityZone. Derive ServiceCategory = "Compute". Add Filesystem storage rows with PricingUnit = "GB-Month". This delivers a conformant dataset with 0 Missing Mandatory.

**Phase 2: Reserved instance enrichment**  
Add CommitmentDiscount columns from reservation records (Id, Name, Type, Category). Implement CommitmentDiscountStatus via cross-reference of reservation and instance run records. Implement EffectiveCost amortization for reserved charges. Add PricingCategory = "Committed" and ChargeFrequency = "Recurring" for reserved rows.

**Phase 3: Finalize and certify**  
Add Tags from instance tag API. Add ServiceSubcategory mapping. Drop ProviderName and PublisherName (v1.4). Validate with FOCUS Validator. Submit for certification.

### 2.4 FOCUS Use Cases Lambda Customers Unlock

**After Phase 1 (on-demand core transform):**
- Per-instance cost tracking and attribution by GPU type.
- Regional cost comparison across Lambda data centers.
- Public list rate vs. actual billed cost comparison (verifying standard vs. custom pricing).
- Storage cost by filesystem.

**After Phase 2 (reserved instance enrichment):**
- Reserved vs. on-demand cost comparison.
- CommitmentDiscount utilization analysis: identify idle reservation periods (CommitmentDiscountStatus = "Unused").
- EffectiveCost-based cost allocation that amortizes commitment purchases.

**Out of scope for Lambda's model:**  
Sub-account cost allocation (Lambda has no sub-account hierarchy). Capacity reservation analysis (reserved instances are CommitmentDiscount). Availability-zone analysis for regions that do not expose zone granularity.

---

## Part 3: Immediate Next Steps

1. Access the Lambda Cloud API and pull a full sample billing dataset for one month including on-demand instances, reserved instances, and filesystem charges. Confirm field availability for `instance_type`, `region_name`, `start_time`, `end_time`, and reservation identifiers.
2. Download the current Lambda pricing page and build a programmatic rate card mapping GPU instance type → ListUnitPrice per hour.
3. Implement the on-demand compute transform (Phase 1), run it through the FOCUS Validator, and iterate to a clean pass.
4. Design the CommitmentDiscountStatus logic: determine whether the Lambda API exposes per-period reservation utilization directly, or whether it must be derived from cross-referencing instance run records with reservation terms.
5. Open the RFI with `member-cert@finops.org` once Phase 1 sample data is validator-clean.

---

## Confidence Summary

- **High:** Lambda's on-demand billing records expose per-instance GPU type, start/end time, and hourly rate. The 35 Present columns are grounded in the Lambda Cloud API v1 and the public pricing page.
- **High:** Lambda's public pricing page provides a stable, per-GPU-type rate card. ListCost derivation is a simple multiplication: hours × published hourly rate per instance type.
- **High:** Lambda instance tags are available via the instances API. Tag parsing to FOCUS key-value format is a straightforward string operation.
- **Moderate:** CommitmentDiscountStatus derivation. The logic requires cross-referencing reservation records with instance run records per billing period. This is feasible but requires Lambda to expose the necessary data per period, which may require API calls to multiple endpoints.
- **Low:** SkuMeter, SkuPriceId, SkuPriceDetails. Lambda does not expose a pricing catalog ID structure in its billing API. These columns are likely to remain Missing unless Lambda adds a pricing catalog API endpoint.

---

## Sources

- Lambda Cloud API Documentation: [docs.lambdalabs.com](https://docs.lambdalabs.com/on-demand-cloud/cloud-api)
- Lambda GPU Pricing: [lambdalabs.com/service/gpu-cloud/pricing](https://lambdalabs.com/service/gpu-cloud/pricing)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
