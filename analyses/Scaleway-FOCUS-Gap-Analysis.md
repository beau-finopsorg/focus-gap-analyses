# Scaleway & FOCUS: Data Generator Gap Analysis

*Analysis run: June 25, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** Scaleway  
**Prepared:** June 25, 2026  
**Source:** Scaleway Billing API (`GET /billing/v2beta1/invoices`); Scaleway Console  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 31 Present, 11 Deviation, 0 Missing Mandatory, 4 Missing Conditional, 1 Missing Recommended, 10 N/A

---

## Executive Summary

Scaleway is a French cloud provider (Iliad Group) offering compute, object storage, managed databases, Kubernetes, serverless functions, and IoT services billed by the hour or GB-month. Scaleway operates regions in Paris (fr-par), Amsterdam (nl-ams), and Warsaw (pl-waw), with availability zones within each region. Instance IDs are available as ResourceId. Scaleway Projects provide a sub-account grouping. Public on-demand pricing covers ListUnitPrice. Scaleway does not have a native CommitmentDiscount construct. All 21 Mandatory columns have source data. Ten columns are N/A: no CommitmentDiscount, no CapacityReservation, and no billing-layer tag exposure. The 11 Deviations cover PricingUnit normalization, enum derivation, and ContractedCost enrichment.

**Recommendation:** Implement one FOCUS row per Scaleway resource type × instance × billing period. ResourceId = instance ID. SubAccountId = Project ID. RegionId from Scaleway region codes (fr-par, nl-ams, pl-waw). AvailabilityZone from zone identifiers (fr-par-1, fr-par-2).

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

**Scaleway Billing API** (`GET /billing/v2beta1/invoices`): Returns invoice line items broken down by resource type, resource ID, project, and region. Key fields: resource ID, resource type, region, project ID, hours, unit price, total amount.

Key characteristics:
- **Per-hour compute:** DEV1, GP1, ENT1, RENDER GPU, and Elastic Metal instances billed per hour.
- **GPU compute:** NVIDIA H100 and L4 GPU instances (RENDER-S, RENDER-HM families) billed per GPU-Hour.
- **Object storage:** Scaleway Object Storage (S3-compatible) billed per GB-Month stored and GB egressed.
- **Managed databases:** PostgreSQL and MySQL managed databases billed per hour.
- **Kubernetes Kapsule:** Managed Kubernetes; worker nodes billed as instances; control plane included.
- **Serverless Functions/Containers:** Billed per invocation and per GB-Second compute.
- **IoT Hub:** Billed per device per month.
- **Projects:** Scaleway Projects group resources within an Organization. Project ID → SubAccountId.
- **Regions and zones:** Scaleway has three regions (fr-par, nl-ams, pl-waw), each with multiple AZs.
- **Public pricing:** Scaleway publishes per-unit pricing for all products in EUR and USD. ListUnitPrice derivable.
- **No CommitmentDiscount:** Scaleway does not offer reserved instances or savings plans. Long-running instances save nothing over on-demand.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven. Scaleway has no CommitmentDiscount constructs; all seven CommitmentDiscount columns and both CapacityReservation columns are N/A.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | Scaleway source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Invoice line item total per resource | Present |
| EffectiveCost | Mandatory | = BilledCost | Present |
| ListCost | Mandatory | On-demand rate × quantity from Scaleway pricing page | Present |
| ContractedCost | Mandatory | = ListCost for direct customers; enterprise contracts require supplementary data | Deviation |
| BillingAccountId | Mandatory | Scaleway Organization ID | Present |
| BillingAccountName | Mandatory | Organization name | Present |
| BillingCurrency | Mandatory | EUR (primary); USD available | Present |
| BillingPeriodStart | Mandatory | First day of billing month | Present |
| BillingPeriodEnd | Mandatory | Last day of billing month | Present |
| ChargePeriodStart | Mandatory | Start of usage period (hourly or monthly) | Present |
| ChargePeriodEnd | Mandatory | End of usage period | Present |
| ChargeDescription | Mandatory | Derive: instance type + resource name (e.g., "Scaleway GP1-M Instance · my-instance") | Deviation |
| ChargeCategory | Mandatory | Derive: "Usage" for all metered resources | Deviation |
| ChargeClass | Mandatory (nullable) | null except for corrections | Present |
| InvoiceIssuerName | Mandatory | "Scaleway SAS" | Present |
| ProviderName | Mandatory (dep. v1.3) | "Scaleway" | Present |
| PublisherName | Mandatory (dep. v1.3) | "Scaleway" | Present |
| ServiceName | Mandatory | Derive: "Scaleway Instances", "Scaleway Object Storage", "Scaleway Managed Database", "Scaleway Kubernetes Kapsule" | Present |
| ServiceCategory | Mandatory | Derive: "Compute" for instances; "Storage" for object storage; "Databases" for managed DBs; "Networking" for egress | Deviation |
| PricingQuantity | Mandatory | Hours for compute; GB for storage; count for other resources | Present |
| PricingUnit | Mandatory | "Instance-Hours" for compute; "GPU-Hours" for GPU instances; "GB" for storage; "GB" for egress | Deviation |
| ConsumedQuantity | Conditional | = PricingQuantity | Present |
| ConsumedUnit | Conditional | = PricingUnit | Present |
| ListUnitPrice | Conditional | On-demand rate from Scaleway pricing page | Present |
| ContractedUnitPrice | Conditional | = ListUnitPrice for direct customers; enterprise rates require supplementary data | Deviation |
| PricingCategory | Conditional | "Standard" (no commitment pricing available) | Deviation |
| ChargeFrequency | Conditional | "Usage-Based" for hourly; "Recurring" for monthly IoT device fees | Deviation |
| BillingAccountType | Conditional | "Enterprise" or "Direct" | Present |
| SubAccountId | Conditional | Scaleway Project ID | Present |
| SubAccountName | Conditional | Project name | Present |
| SubAccountType | Conditional | "Project" | Present |
| ResourceId | Conditional | Scaleway resource ID (instance ID, bucket name, DB ID) | Present |
| ResourceName | Conditional | Resource name as set in Scaleway Console | Present |
| ResourceType | Conditional | Instance family (e.g., "GP1-M"), "Object Storage Bucket", "Managed PostgreSQL" | Present |
| SkuId | Conditional | Scaleway product SKU (e.g., "instance_gp1m", "object_storage") | Present |
| Tags | Conditional | N/A: Scaleway resource tags are not exposed in the Billing API | N/A |
| PricingCurrency | Conditional | EUR or USD | Present |
| PricingCurrencyListUnitPrice | Conditional | = ListUnitPrice | Present |
| PricingCurrencyContractedUnitPrice | Conditional | = ContractedUnitPrice; Deviation for enterprise | Deviation |
| PricingCurrencyEffectiveCost | Conditional | = EffectiveCost | Present |
| SkuMeter | Conditional | Product family label (e.g., "GP1-M Instance-Hours", "GPU-Hours H100") | Deviation |
| SkuPriceId | Conditional | Not in Billing API | Missing: Conditional |
| SkuPriceDetails | Conditional | Not applicable | Missing: Conditional |
| RegionId | Conditional | Scaleway region code (fr-par, nl-ams, pl-waw) | Present |
| RegionName | Conditional | Region name (e.g., "France - Paris", "Netherlands - Amsterdam") | Present |
| CommitmentDiscountId | Conditional | N/A: no CommitmentDiscount construct | N/A |
| CommitmentDiscountName | Conditional | N/A | N/A |
| CommitmentDiscountType | Conditional | N/A | N/A |
| CommitmentDiscountCategory | Conditional | N/A | N/A |
| CommitmentDiscountStatus | Conditional | N/A | N/A |
| CommitmentDiscountQuantity | Conditional | N/A | N/A |
| CommitmentDiscountUnit | Conditional | N/A | N/A |
| CapacityReservationId | Conditional | N/A | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | Invoice number from Scaleway Billing API | Present |
| ServiceSubcategory | Recommended | Map from resource type: "Virtual Machines", "GPU Compute", "Object Storage", "Managed PostgreSQL" | Missing: Recommended |
| AvailabilityZone | Recommended | Scaleway zone identifier (e.g., fr-par-1, fr-par-2, nl-ams-1) | Present |

**Tally:** 31 Present, 11 Deviation, 0 Missing Mandatory, 4 Missing Conditional, 1 Missing Recommended, 10 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Per-resource instance IDs, regions, availability zones, projects, public pricing, invoice numbers. All 21 Mandatory columns have source data.

**Remaining:** SkuPriceId absent. Enterprise ContractedCost requires supplementary data.

### 1.5 Deviations to Fix

**PricingUnit:** "Instance-Hours" for CPU instances; "GPU-Hours" for GPU instances; "GB" for object storage and egress; "GB-Month" for block storage.

**ChargeCategory:** "Usage" for all metered resources. "Credit" for credits.

**ServiceCategory:** "Compute" for instances; "Storage" for object storage and block storage; "Databases" for managed databases; "Networking" for load balancers and egress.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (June 4, 2026); certify at FOCUS v1.2.

### 2.2 What Certification Requires

Contact `member-cert@finops.org` for the RFI. Document no CommitmentDiscount as correct for Scaleway's pricing model.

### 2.3 Phased Roadmap

**Phase 0:** Enable Scaleway Billing API access. Pull one month of per-resource invoice data.

**Phase 1: Compute transform.** Map instance rows. Derive ChargeCategory, ServiceCategory, PricingUnit, RegionId, AvailabilityZone, ResourceId, SubAccount.

**Phase 2: Storage, database, and networking.** Add object storage, managed database, and egress rows.

**Phase 3: GPU, serverless, and IoT.** Add GPU compute and serverless rows. Add ServiceSubcategory.

**Phase 4: Certify.** Drop ProviderName, PublisherName (v1.4). Validate and certify.

---

## Part 3: Immediate Next Steps

1. Enable Scaleway Billing API (`GET /billing/v2beta1/invoices`) access.
2. Pull one month of per-resource invoice data across all active products.
3. Implement Phase 1 compute transform and run through FOCUS Validator.
4. Open the RFI with `member-cert@finops.org`.

---

## Confidence Summary

- **High:** Scaleway Billing API provides resource-level cost data with region and AZ. All 31 Present columns are grounded in documented API fields.
- **High:** Project ID maps to SubAccountId. Region and AZ are natively available.
- **Moderate:** PricingUnit normalization across compute, storage, and serverless product families.
- **Low:** Enterprise ContractedCost. Custom negotiated rates require supplementary data.

---

## Sources

- Scaleway Billing API: [developers.scaleway.com/en/products/billing](https://developers.scaleway.com/en/products/billing)
- Scaleway Pricing: [scaleway.com/en/pricing/](https://www.scaleway.com/en/pricing/)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
