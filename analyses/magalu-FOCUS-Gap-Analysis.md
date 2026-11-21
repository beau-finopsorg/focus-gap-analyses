# Magalu Cloud & FOCUS: Data Generator Gap Analysis

*Analysis run: June 25, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** Magalu Cloud (magalu)  
**Prepared:** June 25, 2026  
**Source:** Magalu Cloud billing portal; Magalu Cloud API  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 28 Present, 11 Deviation, 0 Missing Mandatory, 6 Missing Conditional, 1 Missing Recommended, 11 N/A

---

## Executive Summary

Magalu Cloud is a Brazilian cloud provider (Magazine Luiza Group) offering IaaS compute (virtual machines, bare metal), object storage, block storage, databases, Kubernetes, networking, and CDN services billed by the hour or GB-Month. Billing is in Brazilian Reais (BRL). Magalu Cloud operates from Brazilian data centers (São Paulo, BR-SE region). Projects provide a sub-account grouping. Public on-demand pricing covers all products. Magalu Cloud does not have a CommitmentDiscount construct. All 21 Mandatory columns have source data. Eleven columns are N/A: no CommitmentDiscount, no CapacityReservation, and no billing-layer tag exposure. The 11 Deviations cover PricingUnit normalization, BRL billing currency handling, and enum derivation.

**Recommendation:** Implement one FOCUS row per Magalu Cloud resource × billing period. ResourceId = instance ID. SubAccountId = Project ID. RegionId = "br-se1" (São Paulo). BillingCurrency = "BRL". PricingUnit = "Instance-Hours" for compute; "GB" for storage.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

**Magalu Cloud Billing API and Portal**: Magalu Cloud billing managed through customer portal and API. Key fields: resource ID, resource type, region, project ID, hours, unit price (BRL), total (BRL), billing period.

Key characteristics:
- **Virtual machines:** General purpose and GPU-enabled instances billed per hour in BRL.
- **Bare metal:** Dedicated physical servers.
- **Object storage:** S3-compatible object storage billed per GB-Month and per request.
- **Block storage:** Persistent block volumes billed per GB-Month.
- **Managed databases:** PostgreSQL and other managed database services.
- **Kubernetes:** MKE (Magalu Kubernetes Engine) managed Kubernetes.
- **Networking:** Load balancers, VPC, and CDN.
- **BRL billing:** All Magalu Cloud billing is in Brazilian Reais. BillingCurrency = "BRL".
- **Brazilian data centers:** Magalu Cloud operates from São Paulo and other Brazilian regions. RegionId from Magalu region codes.
- **Projects:** Magalu Cloud Projects organize resources within an account. Project ID → SubAccountId.
- **Public pricing:** Magalu Cloud publishes per-unit pricing in BRL. ListUnitPrice derivable.
- **No CommitmentDiscount:** Magalu Cloud does not offer reserved instances or savings plans.
- **Brazilian tax considerations:** Brazilian invoices may include ICMS and ISS tax components. These generate separate ChargeCategory = "Tax" rows.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven. Magalu Cloud has no CommitmentDiscount constructs. Brazilian tax rows (ICMS, ISS) are separate FOCUS rows with ChargeCategory = "Tax".

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | Magalu Cloud source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Invoice amount per resource per billing period in BRL | Present |
| EffectiveCost | Mandatory | = BilledCost | Present |
| ListCost | Mandatory | On-demand rate in BRL × quantity from Magalu pricing page | Present |
| ContractedCost | Mandatory | = ListCost for direct customers; enterprise rates require supplementary data | Deviation |
| BillingAccountId | Mandatory | Magalu Cloud account ID | Present |
| BillingAccountName | Mandatory | Customer organization name | Present |
| BillingCurrency | Mandatory | "BRL" | Present |
| BillingPeriodStart | Mandatory | First day of billing month | Present |
| BillingPeriodEnd | Mandatory | Last day of billing month | Present |
| ChargePeriodStart | Mandatory | Resource start time | Present |
| ChargePeriodEnd | Mandatory | Resource stop time or period end | Present |
| ChargeDescription | Mandatory | Derive: instance type + resource name (e.g., "Magalu Cloud VM Standard 4 vCPU · my-vm") | Deviation |
| ChargeCategory | Mandatory | Derive: "Usage" for compute/storage/network; "Tax" for ICMS/ISS tax rows | Deviation |
| ChargeClass | Mandatory (nullable) | null except for corrections | Present |
| InvoiceIssuerName | Mandatory | "Magazine Luiza S.A." or "Magalu Cloud Tecnologia" | Present |
| ProviderName | Mandatory (dep. v1.3) | "Magalu Cloud" | Present |
| PublisherName | Mandatory (dep. v1.3) | "Magalu Cloud" | Present |
| ServiceName | Mandatory | "Magalu Cloud Virtual Machines", "Magalu Cloud Object Storage", "Magalu Cloud Block Storage", "Magalu Cloud Managed Database" | Present |
| ServiceCategory | Mandatory | Derive: "Compute" for VMs; "Storage" for object/block storage; "Databases" for managed DBs; "Networking" for LB/CDN | Deviation |
| PricingQuantity | Mandatory | Hours for compute; GB for storage; GB for egress | Present |
| PricingUnit | Mandatory | "Instance-Hours" for VMs; "GB" for storage and egress; "GB-Month" for block storage | Deviation |
| ConsumedQuantity | Conditional | = PricingQuantity | Present |
| ConsumedUnit | Conditional | = PricingUnit | Present |
| ListUnitPrice | Conditional | On-demand rate in BRL from Magalu pricing page | Present |
| ContractedUnitPrice | Conditional | = ListUnitPrice for direct customers; enterprise rates require supplementary data | Deviation |
| PricingCategory | Conditional | "Standard" (no commitment pricing) | Deviation |
| ChargeFrequency | Conditional | "Usage-Based" for hourly compute; "Recurring" for monthly storage | Deviation |
| BillingAccountType | Conditional | "Enterprise" or "Direct" | Present |
| SubAccountId | Conditional | Magalu Cloud Project ID | Present |
| SubAccountName | Conditional | Project name | Present |
| SubAccountType | Conditional | "Project" | Present |
| ResourceId | Conditional | Magalu Cloud resource ID (VM ID, volume ID, bucket name) | Present |
| ResourceName | Conditional | Resource name as set in portal | Present |
| ResourceType | Conditional | VM configuration, "Object Storage Bucket", "Block Storage Volume", "Managed PostgreSQL" | Present |
| SkuId | Conditional | Magalu Cloud product code | Present |
| Tags | Conditional | N/A: Magalu Cloud billing does not expose resource tags at the billing layer | N/A |
| PricingCurrency | Conditional | "BRL" | Present |
| PricingCurrencyListUnitPrice | Conditional | = ListUnitPrice in BRL | Present |
| PricingCurrencyContractedUnitPrice | Conditional | = ContractedUnitPrice; Deviation for enterprise | Deviation |
| PricingCurrencyEffectiveCost | Conditional | = EffectiveCost in BRL | Present |
| SkuMeter | Conditional | Product label (e.g., "Standard VM Instance-Hours", "Object Storage GB") | Deviation |
| SkuPriceId | Conditional | Not in billing API | Missing: Conditional |
| SkuPriceDetails | Conditional | Not applicable | Missing: Conditional |
| RegionId | Conditional | Magalu Cloud region code (e.g., "br-se1" for São Paulo) | Present |
| RegionName | Conditional | Region name (e.g., "Brazil - São Paulo") | Present |
| CommitmentDiscountId | Conditional | N/A: no CommitmentDiscount construct | N/A |
| CommitmentDiscountName | Conditional | N/A | N/A |
| CommitmentDiscountType | Conditional | N/A | N/A |
| CommitmentDiscountCategory | Conditional | N/A | N/A |
| CommitmentDiscountStatus | Conditional | N/A | N/A |
| CommitmentDiscountQuantity | Conditional | N/A | N/A |
| CommitmentDiscountUnit | Conditional | N/A | N/A |
| CapacityReservationId | Conditional | N/A | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | Invoice number (nota fiscal number) from Magalu billing portal | Present |
| ServiceSubcategory | Recommended | "Virtual Machines", "Object Storage", "Block Storage", "Managed Databases", "Kubernetes" | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: Magalu Cloud locations are single-zone | N/A |

**Tally:** 28 Present, 11 Deviation, 0 Missing Mandatory, 6 Missing Conditional, 1 Missing Recommended, 11 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Resource IDs, project hierarchy, Brazilian region, BRL pricing, invoice numbers. All 21 Mandatory columns have source data.

**Remaining:** Enterprise ContractedCost requires supplementary data. SkuPriceId absent. Brazilian tax rows require ChargeCategory = "Tax" handling.

### 1.5 Deviations to Fix

**PricingUnit:** "Instance-Hours" for VMs; "GB" for object storage and egress; "GB-Month" for block storage.

**ChargeCategory:** "Usage" for compute/storage/network; "Tax" for ICMS and ISS tax line items on Brazilian invoices (nota fiscal).

**BillingCurrency:** BRL. Ensure all cost fields use BRL values. No FX conversion at the FOCUS level; report in the billing currency.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (June 4, 2026); certify at FOCUS v1.2.

### 2.2 What Certification Requires

Contact `member-cert@finops.org` for the RFI. Document BRL billing and Brazilian tax row handling. Confirm ChargeCategory = "Tax" is the correct mapping for nota fiscal tax components.

### 2.3 Phased Roadmap

**Phase 0:** Enable Magalu Cloud billing API access. Pull one month of per-resource billing data.

**Phase 1: VM compute.** Map VM rows. Derive ChargeCategory, ServiceCategory, PricingUnit = "Instance-Hours", ResourceId, SubAccount = Project, RegionId = "br-se1".

**Phase 2: Storage, databases, and networking.** Add object storage, block storage, managed databases, and networking rows.

**Phase 3: Tax rows.** Add ICMS/ISS tax rows with ChargeCategory = "Tax".

**Phase 4: Certify.** Add ServiceSubcategory. Drop ProviderName, PublisherName (v1.4). Validate and certify.

---

## Part 3: Immediate Next Steps

1. Enable Magalu Cloud billing API access and pull one month of per-resource billing data.
2. Implement Phase 1 VM compute transform and run through FOCUS Validator.
3. Clarify Brazilian tax row handling (ChargeCategory = "Tax") with the FOCUS community.
4. Open the RFI with `member-cert@finops.org`.

---

## Confidence Summary

- **High:** Magalu Cloud billing provides resource-level data with project hierarchy and Brazilian region. All 28 Present columns are grounded in billing fields.
- **High:** Project ID maps to SubAccountId. BRL currency is straightforward.
- **Moderate:** Brazilian tax row handling. ChargeCategory = "Tax" is the FOCUS mechanism; confirm nota fiscal component mapping.
- **Low:** Enterprise ContractedCost. Custom pricing requires supplementary data.

---

## Sources

- Magalu Cloud Documentation: [docs.magalu.cloud](https://docs.magalu.cloud)
- Magalu Cloud Pricing: [magalu.cloud/precos](https://magalu.cloud/precos)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
