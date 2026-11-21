# Exaion & FOCUS: Data Generator Gap Analysis

*Analysis run: June 25, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** Exaion  
**Prepared:** June 25, 2026  
**Source:** Exaion billing portal; Exaion invoice system  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 29 Present, 11 Deviation, 0 Missing Mandatory, 5 Missing Conditional, 1 Missing Recommended, 11 N/A

---

## Executive Summary

Exaion is a French AI cloud provider (EDF Group subsidiary) offering NVIDIA GPU compute (H100, A100, L40S), CPU instances, and object storage, billed by the hour. Exaion's key differentiator is its carbon-neutral data centers powered by nuclear energy. GPU instance IDs are available as ResourceId. Exaion operates from French data centers (FR region). Public on-demand pricing covers most GPU families. Exaion does not offer reserved instances or savings plans. All 21 Mandatory columns have source data. Eleven columns are N/A: no CommitmentDiscount, no CapacityReservation, AvailabilityZone N/A for single-zone data centers, and tags not exposed at the billing layer.

**Recommendation:** Implement one FOCUS row per Exaion instance × billing period. ResourceId = instance ID. RegionId = "fr" (France). PricingUnit = "GPU-Hours" for GPU instances; "Instance-Hours" for CPU. ServiceCategory = "Compute".

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

**Exaion Billing Portal and Invoices**: Exaion billing is managed through a customer portal and invoices. Key fields: instance ID, GPU model, hours, hourly rate, data center, total amount.

Key characteristics:
- **GPU compute:** NVIDIA H100 (SXM and PCIe), A100, L40S instances billed per GPU-Hour. Both bare-metal and virtualized GPU configurations available.
- **CPU compute:** CPU-only instances for non-GPU workloads.
- **Object storage:** S3-compatible object storage billed per GB-Month.
- **Carbon-neutral:** All Exaion data centers run on EDF nuclear power. The carbon footprint field is a marketing differentiator, not a billing field.
- **French regulatory context:** GDPR-compliant, SecNumCloud-qualifying infrastructure. Billing in EUR.
- **No commitment pricing:** Exaion does not offer reserved instances or savings plans. All billing is on-demand.
- **Single region:** Exaion operates primarily from France. Limited multi-region.
- **Public pricing:** Exaion publishes per-GPU-Hour pricing for all major GPU families. ListUnitPrice derivable.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven. Exaion has no CommitmentDiscount constructs; all seven CommitmentDiscount columns and both CapacityReservation columns are N/A.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | Exaion source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Invoice amount per instance per billing period | Present |
| EffectiveCost | Mandatory | = BilledCost | Present |
| ListCost | Mandatory | On-demand rate × hours from Exaion pricing page | Present |
| ContractedCost | Mandatory | = ListCost for standard accounts; enterprise rates require supplementary data | Deviation |
| BillingAccountId | Mandatory | Exaion account ID | Present |
| BillingAccountName | Mandatory | Customer organization name | Present |
| BillingCurrency | Mandatory | EUR | Present |
| BillingPeriodStart | Mandatory | First day of billing month | Present |
| BillingPeriodEnd | Mandatory | Last day of billing month | Present |
| ChargePeriodStart | Mandatory | Instance start time | Present |
| ChargePeriodEnd | Mandatory | Instance stop time | Present |
| ChargeDescription | Mandatory | Derive: GPU model + instance name (e.g., "Exaion H100 SXM · my-training-node") | Deviation |
| ChargeCategory | Mandatory | Derive: "Usage" for all compute and storage | Deviation |
| ChargeClass | Mandatory (nullable) | null except for corrections | Present |
| InvoiceIssuerName | Mandatory | "Exaion SAS" | Present |
| ProviderName | Mandatory (dep. v1.3) | "Exaion" | Present |
| PublisherName | Mandatory (dep. v1.3) | "Exaion" | Present |
| ServiceName | Mandatory | "Exaion GPU Compute", "Exaion CPU Compute", "Exaion Object Storage" | Present |
| ServiceCategory | Mandatory | Derive: "Compute" for GPU/CPU instances; "Storage" for object storage | Deviation |
| PricingQuantity | Mandatory | Hours for compute; GB for storage | Present |
| PricingUnit | Mandatory | "GPU-Hours" for GPU instances; "Instance-Hours" for CPU; "GB" for object storage | Deviation |
| ConsumedQuantity | Conditional | = PricingQuantity | Present |
| ConsumedUnit | Conditional | = PricingUnit | Present |
| ListUnitPrice | Conditional | On-demand hourly rate from Exaion pricing page | Present |
| ContractedUnitPrice | Conditional | = ListUnitPrice for standard accounts; enterprise rates require supplementary data | Deviation |
| PricingCategory | Conditional | "Standard" (no commitment pricing) | Deviation |
| ChargeFrequency | Conditional | "Usage-Based" | Deviation |
| BillingAccountType | Conditional | "Enterprise" or "Direct" | Present |
| SubAccountId | Conditional | N/A: Exaion does not have a formal sub-account hierarchy | N/A |
| SubAccountName | Conditional | N/A | N/A |
| SubAccountType | Conditional | N/A | N/A |
| ResourceId | Conditional | Exaion instance ID | Present |
| ResourceName | Conditional | Instance name | Present |
| ResourceType | Conditional | GPU configuration (e.g., "H100 SXM5 80GB × 8", "A100 PCIe 80GB × 4") | Present |
| SkuId | Conditional | Exaion instance type code (e.g., "exaion-h100-sxm-8") | Present |
| Tags | Conditional | N/A: Exaion billing does not expose instance tags at the billing layer | N/A |
| PricingCurrency | Conditional | EUR | Present |
| PricingCurrencyListUnitPrice | Conditional | = ListUnitPrice | Present |
| PricingCurrencyContractedUnitPrice | Conditional | = ContractedUnitPrice; Deviation for enterprise | Deviation |
| PricingCurrencyEffectiveCost | Conditional | = EffectiveCost | Present |
| SkuMeter | Conditional | GPU model and count (e.g., "H100 SXM5 80GB × 8 GPU-Hours") | Deviation |
| SkuPriceId | Conditional | Not in billing portal | Missing: Conditional |
| SkuPriceDetails | Conditional | Not applicable | Missing: Conditional |
| RegionId | Conditional | "fr" (France) | Present |
| RegionName | Conditional | "France" | Present |
| CommitmentDiscountId | Conditional | N/A: no CommitmentDiscount construct | N/A |
| CommitmentDiscountName | Conditional | N/A | N/A |
| CommitmentDiscountType | Conditional | N/A | N/A |
| CommitmentDiscountCategory | Conditional | N/A | N/A |
| CommitmentDiscountStatus | Conditional | N/A | N/A |
| CommitmentDiscountQuantity | Conditional | N/A | N/A |
| CommitmentDiscountUnit | Conditional | N/A | N/A |
| CapacityReservationId | Conditional | N/A | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | Invoice number from Exaion billing portal | Present |
| ServiceSubcategory | Recommended | "GPU Compute", "CPU Compute", "Object Storage" | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: single-site French data centers | N/A |

**Tally:** 29 Present, 11 Deviation, 0 Missing Mandatory, 5 Missing Conditional, 1 Missing Recommended, 11 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Instance IDs, GPU models, French region, public pricing, invoice numbers. All 21 Mandatory columns have source data.

**Remaining:** Enterprise ContractedCost requires supplementary data. SkuPriceId absent. No sub-account hierarchy.

### 1.5 Deviations to Fix

**PricingUnit:** "GPU-Hours" for GPU instances; "Instance-Hours" for CPU instances; "GB" for object storage and egress.

**ChargeCategory:** "Usage" for all compute and storage rows.

**ServiceCategory:** "Compute" for GPU/CPU instances; "Storage" for object storage.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (June 4, 2026); certify at FOCUS v1.2.

### 2.2 What Certification Requires

Contact `member-cert@finops.org` for the RFI. Document no CommitmentDiscount and French-only region.

### 2.3 Phased Roadmap

**Phase 0:** Enable Exaion billing portal access. Pull one month of per-instance billing data.

**Phase 1: GPU compute.** Map H100 and A100 instance rows. Derive ChargeCategory, ServiceCategory, PricingUnit = "GPU-Hours", ResourceId, RegionId = "fr".

**Phase 2: CPU compute and storage.** Add CPU instances and object storage rows.

**Phase 3: Certify.** Add ServiceSubcategory. Drop ProviderName, PublisherName (v1.4). Validate and certify.

---

## Part 3: Immediate Next Steps

1. Enable Exaion billing portal access and pull one month of instance data.
2. Implement Phase 1 GPU compute transform and run through FOCUS Validator.
3. Open the RFI with `member-cert@finops.org`.

---

## Confidence Summary

- **High:** Exaion billing provides instance-level data with GPU model, hours, and region. All 29 Present columns are grounded in billing fields.
- **High:** Instance ID maps to ResourceId. French region is single-region; no AZ is correct.
- **Moderate:** PricingUnit normalization for CPU vs. GPU instances.
- **Low:** Enterprise ContractedCost. Custom pricing requires supplementary data.

---

## Sources

- Exaion Cloud: [exaion.com](https://www.exaion.com)
- Exaion Pricing: [exaion.com/en/pricing](https://www.exaion.com/en/pricing)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
