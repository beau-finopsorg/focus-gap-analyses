# Vultr & FOCUS: Data Generator Gap Analysis

*Analysis run: June 25, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** Vultr  
**Prepared:** June 25, 2026  
**Source:** Vultr Billing API (`GET /v2/billing`); Vultr account portal  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 31 Present, 11 Deviation, 0 Missing Mandatory, 4 Missing Conditional, 1 Missing Recommended, 10 N/A

---

## Executive Summary

Vultr is a US-based cloud provider offering compute (cloud instances, bare metal, GPU), block storage, object storage, managed databases, Kubernetes, load balancers, and CDN across 32 global locations. Instances are billed by the hour (or monthly for some bare metal). Instance IDs are available as ResourceId. Vultr does not have a sub-account project hierarchy; all resources are under a single account. Public on-demand pricing covers all products. No CommitmentDiscount construct exists. All 21 Mandatory columns have source data. Ten columns are N/A: no sub-account hierarchy, no CommitmentDiscount, no CapacityReservation, and no billing-layer tags.

**Recommendation:** Implement one FOCUS row per Vultr resource type × instance × billing period. ResourceId = instance ID. RegionId from Vultr location codes (ewr, lax, fra, sgp, etc.). AvailabilityZone N/A (Vultr locations are single-zone). PricingUnit = "Instance-Hours" for compute; "GB" for storage and egress.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

**Vultr Billing API** (`GET /v2/billing`): Returns billing history with line items per resource. Key fields: instance ID, instance type, location, hours, rate per hour, total, billing period.

Key characteristics:
- **Cloud instances:** High-performance (AMD/Intel), high-frequency, and optimized cloud compute billed per hour or monthly.
- **Bare metal:** Single-tenant servers billed per hour or monthly.
- **GPU instances:** NVIDIA A16, A40, A100 GPU instances billed per hour.
- **Block storage:** Persistent block storage volumes billed per GB-Month.
- **Object storage:** S3-compatible object storage (Vultr Object Storage) billed per GB-Month plus egress.
- **Managed databases:** PostgreSQL, MySQL, Redis managed databases billed per hour.
- **Kubernetes:** VKE (Vultr Kubernetes Engine) with worker node billing as instances; control plane free.
- **CDN:** Bandwidth-based billing per GB.
- **32 global locations:** Vultr operates across Americas, Europe, Asia, and Australia. Location codes map to RegionId.
- **Public pricing:** Vultr publishes per-hour pricing for all instance types. ListUnitPrice derivable.
- **No CommitmentDiscount:** Vultr has no reserved instances or savings plans.
- **No project hierarchy:** All Vultr resources are under a single account. No sub-account grouping.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven. Vultr has no CommitmentDiscount constructs; all seven CommitmentDiscount columns and both CapacityReservation columns are N/A.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | Vultr source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Invoice amount per resource per billing period | Present |
| EffectiveCost | Mandatory | = BilledCost | Present |
| ListCost | Mandatory | On-demand hourly rate × hours from Vultr pricing page | Present |
| ContractedCost | Mandatory | = ListCost for standard accounts; enterprise rates require supplementary data | Deviation |
| BillingAccountId | Mandatory | Vultr account ID | Present |
| BillingAccountName | Mandatory | Account email | Present |
| BillingCurrency | Mandatory | USD | Present |
| BillingPeriodStart | Mandatory | First day of billing month | Present |
| BillingPeriodEnd | Mandatory | Last day of billing month | Present |
| ChargePeriodStart | Mandatory | Instance creation or period start | Present |
| ChargePeriodEnd | Mandatory | Instance deletion or period end | Present |
| ChargeDescription | Mandatory | Derive: instance type + location (e.g., "Vultr High-Performance AMD 2 vCPU · New Jersey") | Deviation |
| ChargeCategory | Mandatory | Derive: "Usage" for all metered resources | Deviation |
| ChargeClass | Mandatory (nullable) | null except for corrections | Present |
| InvoiceIssuerName | Mandatory | "Vultr Holdings Corp." | Present |
| ProviderName | Mandatory (dep. v1.3) | "Vultr" | Present |
| PublisherName | Mandatory (dep. v1.3) | "Vultr" | Present |
| ServiceName | Mandatory | "Vultr Cloud Instance", "Vultr Bare Metal", "Vultr GPU", "Vultr Block Storage", "Vultr Object Storage", "Vultr Managed Database" | Present |
| ServiceCategory | Mandatory | Derive: "Compute" for instances; "Storage" for block/object; "Databases" for managed DBs; "Networking" for CDN/egress | Deviation |
| PricingQuantity | Mandatory | Hours for compute; GB for storage and egress | Present |
| PricingUnit | Mandatory | "Instance-Hours" for cloud and bare metal compute; "GPU-Hours" for GPU instances; "GB" for storage and egress | Deviation |
| ConsumedQuantity | Conditional | = PricingQuantity | Present |
| ConsumedUnit | Conditional | = PricingUnit | Present |
| ListUnitPrice | Conditional | On-demand hourly rate from Vultr pricing page | Present |
| ContractedUnitPrice | Conditional | = ListUnitPrice for standard accounts; enterprise rates require supplementary data | Deviation |
| PricingCategory | Conditional | "Standard" (no commitment pricing) | Deviation |
| ChargeFrequency | Conditional | "Usage-Based" | Deviation |
| BillingAccountType | Conditional | "Direct" or "Enterprise" | Present |
| SubAccountId | Conditional | N/A: Vultr has no project or sub-account hierarchy | N/A |
| SubAccountName | Conditional | N/A | N/A |
| SubAccountType | Conditional | N/A | N/A |
| ResourceId | Conditional | Vultr instance ID or volume/bucket ID | Present |
| ResourceName | Conditional | Instance label or resource name | Present |
| ResourceType | Conditional | Instance plan (e.g., "vc2-2c-4gb", "vbm-4c-32gb", "vcg-a40-2c") | Present |
| SkuId | Conditional | Vultr plan code (e.g., "vc2-2c-4gb") | Present |
| Tags | Conditional | N/A: Vultr billing does not expose resource tags at the billing layer | N/A |
| PricingCurrency | Conditional | USD | Present |
| PricingCurrencyListUnitPrice | Conditional | = ListUnitPrice | Present |
| PricingCurrencyContractedUnitPrice | Conditional | = ContractedUnitPrice; Deviation for enterprise | Deviation |
| PricingCurrencyEffectiveCost | Conditional | = EffectiveCost | Present |
| SkuMeter | Conditional | Instance plan label (e.g., "High-Performance AMD 2 vCPU Instance-Hours") | Deviation |
| SkuPriceId | Conditional | Not in Billing API | Missing: Conditional |
| SkuPriceDetails | Conditional | Not applicable | Missing: Conditional |
| RegionId | Conditional | Vultr location code (ewr, lax, fra, sgp, syd, etc.) | Present |
| RegionName | Conditional | Location name (e.g., "New Jersey", "Los Angeles", "Frankfurt") | Present |
| CommitmentDiscountId | Conditional | N/A: no CommitmentDiscount construct | N/A |
| CommitmentDiscountName | Conditional | N/A | N/A |
| CommitmentDiscountType | Conditional | N/A | N/A |
| CommitmentDiscountCategory | Conditional | N/A | N/A |
| CommitmentDiscountStatus | Conditional | N/A | N/A |
| CommitmentDiscountQuantity | Conditional | N/A | N/A |
| CommitmentDiscountUnit | Conditional | N/A | N/A |
| CapacityReservationId | Conditional | N/A | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | Invoice number from Vultr account portal | Present |
| ServiceSubcategory | Recommended | "Virtual Machines", "Bare Metal", "GPU Compute", "Block Storage", "Object Storage", "Managed Databases" | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: Vultr locations are single-zone | N/A |

**Tally:** 31 Present, 11 Deviation, 0 Missing Mandatory, 4 Missing Conditional, 1 Missing Recommended, 10 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Instance IDs, location codes, resource types, public pricing, invoice numbers. All 21 Mandatory columns have source data.

**Remaining:** Enterprise ContractedCost requires supplementary data. SkuPriceId absent. No sub-account hierarchy.

### 1.5 Deviations to Fix

**PricingUnit:** "Instance-Hours" for cloud compute; "GPU-Hours" for GPU instances; "GB" for storage and egress.

**ChargeCategory:** "Usage" for all metered resources.

**ServiceCategory:** "Compute" for instances; "Storage" for block and object storage; "Databases" for managed databases; "Networking" for CDN and egress.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (June 4, 2026); certify at FOCUS v1.2.

### 2.2 What Certification Requires

Contact `member-cert@finops.org` for the RFI. Document no CommitmentDiscount and no sub-account hierarchy.

### 2.3 Phased Roadmap

**Phase 0:** Enable Vultr Billing API access. Pull one month of per-resource billing data.

**Phase 1: Compute transform.** Map cloud instance rows. Derive ChargeCategory, ServiceCategory, PricingUnit, RegionId, ResourceId.

**Phase 2: Storage, databases, and networking.** Add remaining resource types.

**Phase 3: Certify.** Add ServiceSubcategory. Drop ProviderName, PublisherName (v1.4). Validate and certify.

---

## Part 3: Immediate Next Steps

1. Enable Vultr Billing API (`GET /v2/billing`) access.
2. Pull one month of per-resource billing data across all active products.
3. Implement Phase 1 compute transform and run through FOCUS Validator.
4. Open the RFI with `member-cert@finops.org`.

---

## Confidence Summary

- **High:** Vultr Billing API provides instance-level data with location codes and resource types. All 31 Present columns are grounded in documented API fields.
- **High:** Instance ID maps to ResourceId. Location codes map to RegionId. No sub-account hierarchy is correct.
- **Moderate:** PricingUnit normalization across compute, storage, and networking product families.
- **Low:** Enterprise ContractedCost. Custom pricing requires supplementary data.

---

## Sources

- Vultr API Documentation: [www.vultr.com/api/#tag/billing](https://www.vultr.com/api/#tag/billing)
- Vultr Pricing: [vultr.com/pricing/](https://www.vultr.com/pricing/)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
