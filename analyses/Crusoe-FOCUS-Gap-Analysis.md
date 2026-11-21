# Crusoe & FOCUS: Data Generator Gap Analysis

*Analysis run: June 25, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** Crusoe  
**Prepared:** June 25, 2026  
**Source:** Crusoe Cloud API; Crusoe billing portal  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 34 Present, 11 Deviation, 0 Missing Mandatory, 5 Missing Conditional, 1 Missing Recommended, 6 N/A

---

## Executive Summary

Crusoe Cloud is an AI-focused GPU cloud provider with per-hour instance billing, public pricing, and project-based account organization. Its billing model closely parallels Lambda's. All 21 Mandatory columns have source data. The 11 Deviations cover reserved instance EffectiveCost amortization, ContractedCost for enterprise accounts, ChargeCategory and ServiceCategory derivation, and CommitmentDiscountStatus logic. Six columns are N/A: CapacityReservation (reserved instances are CommitmentDiscount) and AvailabilityZone (Crusoe has single-zone data centers in most regions). Five Missing Conditional columns are in the SKU price catalog family.

**Recommendation:** Crusoe's simple billing model makes FOCUS conformance a single-phase implementation after confirming API access. The public pricing page provides ListCost without supplementary data. Start with on-demand compute and expand to reserved instances in a follow-on pass.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

**Crusoe Cloud API**: Crusoe exposes billing and resource management through its cloud API. Instance records include GPU type, start/end time, region, project assignment, and per-hour pricing. The billing API provides monthly usage records with cost per instance.

**Crusoe Pricing Page**: Crusoe publishes per-GPU-type hourly rates for on-demand instances and per-year rates for reserved instances.

Key characteristics for FOCUS:
- **Per-hour billing:** Clean PricingQuantity (hours) and PricingUnit ("Hours") for every on-demand compute charge row.
- **Public pricing:** Crusoe publishes per-GPU-type hourly rates; ListCost is derivable without API integration.
- **Project hierarchy:** Crusoe organizes resources within Projects, which maps to FOCUS SubAccountId and SubAccountName.
- **Regions:** Crusoe operates data centers in multiple US and EU locations.
- **Tags:** Crusoe supports instance-level metadata and tags.
- **Reserved instances:** Crusoe offers 1-year and multi-year GPU reservations mapping to CommitmentDiscount.
- **Storage:** Crusoe persistent volumes are billed per GB per month.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven. Each column carries a feature level: Mandatory (must exist and be populated where applicable), Conditional (populated when the provider's model triggers the condition, otherwise null), or Recommended.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | Crusoe source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Invoice line item amount | Present |
| EffectiveCost | Mandatory | On-demand: = BilledCost; reserved: amortize reservation commitment across usage hours | Deviation |
| ListCost | Mandatory | Public rate × PricingQuantity from Crusoe pricing page | Present |
| ContractedCost | Mandatory | = ListCost for standard accounts; enterprise custom pricing not exposed via API | Deviation |
| BillingAccountId | Mandatory | Crusoe organization account ID | Present |
| BillingAccountName | Mandatory | Organization name from Crusoe account | Present |
| BillingCurrency | Mandatory | USD | Present |
| BillingPeriodStart | Mandatory | First day of billing month | Present |
| BillingPeriodEnd | Mandatory | Last day of billing month | Present |
| ChargePeriodStart | Mandatory | Instance start time for on-demand; reservation period start for reserved | Present |
| ChargePeriodEnd | Mandatory | Instance end time (or period end if still running); reservation period end | Present |
| ChargeDescription | Mandatory | GPU type + instance label (e.g., "1x NVIDIA H100 SXM5") or volume name | Present |
| ChargeCategory | Mandatory | Derive: "Usage" for on-demand compute and storage; "Purchase" for reserved instance commitments | Deviation |
| ChargeClass | Mandatory (nullable) | null except for correction charges | Present |
| InvoiceIssuerName | Mandatory | "Crusoe Energy Systems LLC" | Present |
| ProviderName | Mandatory (dep. v1.3) | "Crusoe" | Present |
| PublisherName | Mandatory (dep. v1.3) | "Crusoe" | Present |
| ServiceName | Mandatory | "Crusoe Cloud Compute" for GPU instances; "Crusoe Cloud Storage" for volumes | Present |
| ServiceCategory | Mandatory | "Compute" for GPU instances; "Storage" for volumes | Deviation |
| PricingQuantity | Mandatory | Hours for compute; GB for storage | Present |
| PricingUnit | Mandatory | "Hours" for compute; "GB-Month" for storage | Present |
| ConsumedQuantity | Conditional | = PricingQuantity | Present |
| ConsumedUnit | Conditional | = PricingUnit | Present |
| ListUnitPrice | Conditional | Public rate from Crusoe pricing page per GPU type per hour | Present |
| ContractedUnitPrice | Conditional | = ListUnitPrice for standard accounts; enterprise custom rates not exposed | Deviation |
| PricingCategory | Conditional | Derive: "Standard" for on-demand; "Committed" for reserved instances | Deviation |
| ChargeFrequency | Conditional | Derive: "Usage-Based" for on-demand; "Recurring" for reserved instance monthly payments | Deviation |
| BillingAccountType | Conditional | Derive from account plan (PAYG or Enterprise) | Present |
| SubAccountId | Conditional | Crusoe Project ID | Present |
| SubAccountName | Conditional | Crusoe Project name | Present |
| SubAccountType | Conditional | "Project" | Present |
| ResourceId | Conditional | Crusoe instance ID (UUID) | Present |
| ResourceName | Conditional | Instance name from API | Present |
| ResourceType | Conditional | GPU instance type (e.g., "h100-sxm-80gb-1") | Present |
| SkuId | Conditional | Instance type identifier | Present |
| Tags | Conditional | Instance tags from Crusoe API; parse to FOCUS key-value format | Deviation |
| PricingCurrency | Conditional | USD | Present |
| PricingCurrencyListUnitPrice | Conditional | = ListUnitPrice (USD only) | Present |
| PricingCurrencyContractedUnitPrice | Conditional | = ContractedUnitPrice; Deviation because enterprise rate requires supplementary data | Deviation |
| PricingCurrencyEffectiveCost | Conditional | = EffectiveCost; Deviation because reserved instance amortization logic is required | Deviation |
| SkuMeter | Conditional | Not exposed in billing API | Missing: Conditional |
| SkuPriceId | Conditional | Pricing plan rate identifier not exposed in billing API | Missing: Conditional |
| SkuPriceDetails | Conditional | Not applicable (Crusoe uses flat per-hour rates) | Missing: Conditional |
| RegionId | Conditional | Crusoe region code (e.g., "us-east-1", "us-west-2") | Present |
| RegionName | Conditional | Crusoe region display name | Present |
| CommitmentDiscountId | Conditional | Crusoe reservation ID | Present |
| CommitmentDiscountName | Conditional | Reservation display name | Present |
| CommitmentDiscountType | Conditional | "Reserved" | Present |
| CommitmentDiscountCategory | Conditional | "Usage" | Present |
| CommitmentDiscountStatus | Conditional | Derive: "Used" when reserved capacity is running; "Unused" when idle | Deviation |
| CommitmentDiscountQuantity | Conditional | Per-charge commitment quantity not exposed in billing API | Missing: Conditional |
| CommitmentDiscountUnit | Conditional | Same | Missing: Conditional |
| CapacityReservationId | Conditional | N/A: Crusoe reserved instances are modeled as CommitmentDiscount | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | Crusoe invoice number from billing portal | Present |
| ServiceSubcategory | Recommended | No native field; "GPU Compute" and "Block Storage" as subcategories | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: Crusoe operates single-zone data centers in most regions | N/A |

**Tally:** 34 Present, 11 Deviation, 0 Missing Mandatory, 5 Missing Conditional, 1 Missing Recommended, 6 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Per-hour GPU billing with public pricing, project hierarchy, per-instance resource IDs, region data, and reserved instance commitment metadata. All 21 Mandatory columns have source data.

**Remaining:** CommitmentDiscountStatus requires cross-referencing reservation records with instance run records. Enterprise ContractedCost requires supplementary pricing data. SkuMeter and SkuPriceId are absent from the billing API.

### 1.5 Deviations to Fix

**EffectiveCost:** On-demand: = BilledCost. Reserved: amortize monthly reservation payment across usage hours (or days) during the reservation term.

**ChargeCategory:** On-demand compute and storage → "Usage"; reserved instance payments → "Purchase"; credit adjustments → "Credit".

**ServiceCategory:** GPU compute instances → "Compute"; Crusoe volumes → "Storage".

**CommitmentDiscountStatus:** Cross-reference reservation records with instance run records per billing period. Active reserved instance → "Used"; idle reservation period → "Unused".

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (June 4, 2026); certify at FOCUS v1.2. ProviderName and PublisherName are deprecated in v1.3 and removed in v1.4.

### 2.2 What Certification Requires

Contact `member-cert@finops.org` for the RFI. Crusoe's 0 Missing Mandatory makes certification achievable after Phase 1.

### 2.3 Phased Roadmap

**Phase 0:** Confirm Crusoe Cloud API access. Pull a sample monthly billing dataset for on-demand and reserved instances. Verify field availability for instance type, project, region, start/end time, and reservation identifiers.

**Phase 1: Core transform.** Map BilledCost, ListCost (public rate card), ChargePeriod, SubAccount (project), ResourceId/Name/Type, RegionId/Name, SkuId, PricingQuantity/Unit, ServiceName, ChargeCategory, InvoiceId. Derive ServiceCategory. Delivers conformant output for 34 Present columns.

**Phase 2: Reserved instance enrichment.** Add CommitmentDiscount columns. Implement CommitmentDiscountStatus via cross-reference of reservation and instance run records. Implement EffectiveCost amortization. Add Tags.

**Phase 3: Certify.** Add ServiceSubcategory. Drop ProviderName, PublisherName (v1.4). Validate with FOCUS Validator. Submit for certification.

### 2.4 FOCUS Use Cases Crusoe Customers Unlock

**After Phase 1:** Per-instance cost tracking by GPU type and project. Regional cost comparison. List rate vs. billed cost verification. Storage cost by volume.

**After Phase 2:** Reserved vs. on-demand cost comparison. CommitmentDiscount utilization analysis (CommitmentDiscountStatus = "Unused" identifies idle reservations).

---

## Part 3: Immediate Next Steps

1. Access the Crusoe Cloud API and pull a full sample billing dataset including on-demand, reserved, and storage charges.
2. Build a programmatic rate card from the Crusoe pricing page mapping GPU instance type → ListUnitPrice per hour.
3. Implement the on-demand compute transform (Phase 1) and run through the FOCUS Validator.
4. Design the CommitmentDiscountStatus logic for reserved instances.
5. Open the RFI with `member-cert@finops.org` once Phase 1 data is validator-clean.

---

## Confidence Summary

- **High:** Crusoe's per-hour billing with per-instance GPU type, start/end time, and public rate card gives a complete structural foundation. The 34 Present columns are grounded in Crusoe's API and public pricing.
- **High:** Crusoe project hierarchy maps cleanly to FOCUS SubAccountId and SubAccountName.
- **Moderate:** CommitmentDiscountStatus derivation. Requires cross-referencing reservation and instance run records per billing period.
- **Low:** SkuMeter, SkuPriceId, SkuPriceDetails. Crusoe does not expose a pricing catalog ID structure in its billing API.

---

## Sources

- Crusoe Cloud: [crusoe.ai](https://crusoe.ai)
- Crusoe Cloud API Documentation: [docs.crusoecloud.com](https://docs.crusoecloud.com)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
