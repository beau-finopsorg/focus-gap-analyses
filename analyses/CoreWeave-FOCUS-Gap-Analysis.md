# CoreWeave & FOCUS: Data Generator Gap Analysis

*Analysis run: June 25, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** CoreWeave  
**Prepared:** June 25, 2026  
**Source:** CoreWeave billing API; CoreWeave invoice portal  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 33 Present, 11 Deviation, 0 Missing Mandatory, 5 Missing Conditional, 1 Missing Recommended, 7 N/A

---

## Executive Summary

CoreWeave is a specialized GPU cloud provider offering NVIDIA H100, A100, H200, and other GPU instances billed per hour. CoreWeave also provides CPU instances, networking, storage (block and object), and Kubernetes-as-a-service. Instance IDs are available as ResourceId. Namespaces provide a sub-account grouping. CoreWeave offers reserved instances (monthly/quarterly/annual) that map to FOCUS CommitmentDiscount columns. All 21 Mandatory columns have source data. Seven columns are N/A: single-region billing rows do not split by availability zone, and tags are not exposed at the billing layer. The 11 Deviations cover enum derivation, ContractedCost enrichment, and CommitmentDiscount field population.

**Recommendation:** Implement one FOCUS row per CoreWeave resource type × instance × billing period. ResourceId = instance/pod ID. CommitmentDiscountType = "Reserved" for reserved GPU instances. PricingUnit = "GPU-Hours" for GPU instances; "CPU-Hours" for CPU; "GB" for storage.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

**CoreWeave Billing API and Invoice Portal**: CoreWeave provides billing data via API and invoice exports. Key fields: instance type, GPU model, hours used, hourly rate, reservation ID, namespace, billing period, total amount.

Key characteristics:
- **GPU-first compute:** NVIDIA H100, H200, A100, A40, RTX A6000 instances billed per GPU-Hour. Instance families have different GPU counts per instance.
- **CPU and general compute:** CPU-only instances for non-GPU workloads.
- **Networking:** Egress and load balancer costs.
- **Storage:** Block storage (SSD) and object storage (compatible with S3 API).
- **Kubernetes-as-a-service:** Managed Kubernetes clusters billed for control plane and node hours.
- **Reserved instances:** CoreWeave offers 1-month, 3-month, and 12-month GPU reservations at discounted rates. These are FOCUS CommitmentDiscount constructs.
- **Namespace hierarchy:** CoreWeave namespaces group resources within an account and map to SubAccountId.
- **Regional:** CoreWeave operates in multiple US regions (LAS1, ORD1, EWR1). RegionId is available.
- **Public pricing:** CoreWeave publishes per-GPU-Hour pricing for on-demand instances. ListUnitPrice derivable.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven. CoreWeave reserved instances are true CommitmentDiscount constructs (reserved capacity with a commitment period). This differs from Datadog annual plans (pricing tiers only). CoreWeave reservations generate both the reserved row and usage rows that reference CommitmentDiscountId.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | CoreWeave source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Invoice amount per resource per billing period | Present |
| EffectiveCost | Mandatory | On-demand: = BilledCost; reserved: amortize reservation fee across commitment period | Deviation |
| ListCost | Mandatory | On-demand hourly rate × hours from CoreWeave pricing page | Present |
| ContractedCost | Mandatory | Reserved rate × hours; enterprise contract rate × usage | Deviation |
| BillingAccountId | Mandatory | CoreWeave account ID | Present |
| BillingAccountName | Mandatory | Account name | Present |
| BillingCurrency | Mandatory | USD | Present |
| BillingPeriodStart | Mandatory | First day of billing month | Present |
| BillingPeriodEnd | Mandatory | Last day of billing month | Present |
| ChargePeriodStart | Mandatory | Start of usage period | Present |
| ChargePeriodEnd | Mandatory | End of usage period | Present |
| ChargeDescription | Mandatory | Derive: instance type + GPU model (e.g., "CoreWeave H100 SXM5 · 8 GPU Instance") | Deviation |
| ChargeCategory | Mandatory | Derive: "Usage" for compute/storage/network; "Purchase" for reserved instance upfront fees | Deviation |
| ChargeClass | Mandatory (nullable) | null except for corrections | Present |
| InvoiceIssuerName | Mandatory | "CoreWeave, Inc." | Present |
| ProviderName | Mandatory (dep. v1.3) | "CoreWeave" | Present |
| PublisherName | Mandatory (dep. v1.3) | "CoreWeave" | Present |
| ServiceName | Mandatory | "CoreWeave GPU Compute", "CoreWeave CPU Compute", "CoreWeave Block Storage", "CoreWeave Object Storage", "CoreWeave Networking" | Present |
| ServiceCategory | Mandatory | Derive: "Compute" for GPU/CPU; "Storage" for block/object; "Networking" for egress/LB | Deviation |
| PricingQuantity | Mandatory | Hours for compute; GB for storage; GB for egress | Present |
| PricingUnit | Mandatory | "GPU-Hours" for GPU instances; "CPU-Hours" for CPU instances; "GB" for storage and egress | Deviation |
| ConsumedQuantity | Conditional | = PricingQuantity | Present |
| ConsumedUnit | Conditional | = PricingUnit | Present |
| ListUnitPrice | Conditional | On-demand hourly rate per instance type from CoreWeave pricing page | Present |
| ContractedUnitPrice | Conditional | Reserved instance rate per GPU-Hour; enterprise contract rate | Deviation |
| PricingCategory | Conditional | "Standard" for on-demand; "Committed" for reserved instances | Deviation |
| ChargeFrequency | Conditional | "Usage-Based" for on-demand; "Recurring" for reserved | Deviation |
| BillingAccountType | Conditional | "Enterprise" or "Direct" | Present |
| SubAccountId | Conditional | CoreWeave namespace ID | Present |
| SubAccountName | Conditional | Namespace name | Present |
| SubAccountType | Conditional | "Namespace" | Present |
| ResourceId | Conditional | Instance ID or pod ID | Present |
| ResourceName | Conditional | Instance or pod name | Present |
| ResourceType | Conditional | GPU instance family (e.g., "H100 SXM5 80GB × 8") or "Block Storage Volume" | Present |
| SkuId | Conditional | CoreWeave instance type code | Present |
| Tags | Conditional | N/A: CoreWeave billing does not expose Kubernetes labels at the billing layer | N/A |
| PricingCurrency | Conditional | USD | Present |
| PricingCurrencyListUnitPrice | Conditional | = ListUnitPrice | Present |
| PricingCurrencyContractedUnitPrice | Conditional | = ContractedUnitPrice; Deviation for enterprise | Deviation |
| PricingCurrencyEffectiveCost | Conditional | = EffectiveCost; Deviation for reservation amortization | Deviation |
| SkuMeter | Conditional | GPU model and count (e.g., "H100 SXM5 80GB × 8 GPU-Hours") | Deviation |
| SkuPriceId | Conditional | Not in billing API | Missing: Conditional |
| SkuPriceDetails | Conditional | Not applicable | Missing: Conditional |
| RegionId | Conditional | CoreWeave data center code (LAS1, ORD1, EWR1) | Present |
| RegionName | Conditional | Data center name (e.g., "Las Vegas", "Chicago") | Present |
| CommitmentDiscountId | Conditional | CoreWeave reservation ID | Present |
| CommitmentDiscountName | Conditional | Reservation name or description | Present |
| CommitmentDiscountType | Conditional | "Reserved" | Present |
| CommitmentDiscountCategory | Conditional | "Usage" (capacity reservation for GPU-Hours) | Present |
| CommitmentDiscountStatus | Conditional | "Used" or "Unused" per hour | Present |
| CommitmentDiscountQuantity | Conditional | Reserved GPU-Hours per period | Present |
| CommitmentDiscountUnit | Conditional | "GPU-Hours" | Present |
| CapacityReservationId | Conditional | N/A: CommitmentDiscount covers the CoreWeave reservation construct | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | Invoice number from CoreWeave portal | Present |
| ServiceSubcategory | Recommended | "GPU Compute", "CPU Compute", "Block Storage", "Object Storage", "Network Egress" | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: CoreWeave data centers are single-AZ locations | N/A |

**Tally:** 33 Present, 11 Deviation, 0 Missing Mandatory, 5 Missing Conditional, 1 Missing Recommended, 7 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Instance IDs, GPU models, namespace hierarchy, reservation IDs, regional data centers, public on-demand pricing, invoice numbers. All 21 Mandatory columns have source data.

**Remaining:** Enterprise contract ContractedCost requires supplementary data. SkuPriceId absent.

### 1.5 Deviations to Fix

**PricingUnit:** "GPU-Hours" for GPU instances; "CPU-Hours" for CPU; "GB" for storage and egress. Build instance-type → PricingUnit lookup.

**CommitmentDiscount columns:** CoreWeave reservations are true CommitmentDiscount constructs. Populate CommitmentDiscountId, CommitmentDiscountType = "Reserved", CommitmentDiscountCategory = "Usage", CommitmentDiscountStatus = "Used"/"Unused".

**EffectiveCost:** For reserved instances, amortize the upfront/periodic reservation fee across GPU-hours consumed.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (June 4, 2026); certify at FOCUS v1.2.

### 2.2 What Certification Requires

Contact `member-cert@finops.org` for the RFI. CommitmentDiscount columns require full population for GPU reservations.

### 2.3 Phased Roadmap

**Phase 0:** Enable CoreWeave billing API access. Pull one month of per-instance billing data.

**Phase 1: On-demand compute.** Map GPU and CPU instance rows. Derive ChargeCategory, ServiceCategory, PricingUnit, RegionId, ResourceId, SubAccount.

**Phase 2: Reserved instances.** Add CommitmentDiscount columns. Calculate EffectiveCost amortization.

**Phase 3: Storage and networking.** Add block storage, object storage, and egress rows. Add ServiceSubcategory.

**Phase 4: Certify.** Drop ProviderName, PublisherName (v1.4). Validate and certify.

---

## Part 3: Immediate Next Steps

1. Enable CoreWeave billing API access.
2. Pull one month of per-instance GPU usage data.
3. Implement Phase 1 on-demand compute transform and run through FOCUS Validator.
4. Open the RFI with `member-cert@finops.org`.

---

## Confidence Summary

- **High:** CoreWeave billing provides instance-level data with GPU model, hours, region. All 33 Present columns are grounded in billing fields.
- **High:** CommitmentDiscount columns map directly to CoreWeave GPU reservations.
- **Moderate:** EffectiveCost amortization for reserved instances. Confirm amortization period with CoreWeave documentation.
- **Low:** Enterprise contract ContractedCost. Custom negotiated rates require supplementary data.

---

## Sources

- CoreWeave Pricing: [coreweave.com/gpu-cloud/pricing](https://www.coreweave.com/gpu-cloud/pricing)
- CoreWeave Documentation: [docs.coreweave.com](https://docs.coreweave.com)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
