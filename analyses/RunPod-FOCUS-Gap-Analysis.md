# RunPod & FOCUS: Data Generator Gap Analysis

*Analysis run: June 25, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** RunPod  
**Prepared:** June 25, 2026  
**Source:** RunPod GraphQL API; RunPod billing dashboard  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 30 Present, 11 Deviation, 0 Missing Mandatory, 5 Missing Conditional, 1 Missing Recommended, 10 N/A

---

## Executive Summary

RunPod is a GPU cloud marketplace offering Secure Cloud (dedicated GPU instances in Tier 3/4 data centers) and Community Cloud (lower-cost peer-supplied GPUs) billed by the second. Serverless GPU endpoints are a third model billed per request plus compute. Pod IDs are available as ResourceId. RunPod does not have a sub-account hierarchy by default but supports team accounts. All 21 Mandatory columns have source data. Ten columns are N/A: no CommitmentDiscount, no CapacityReservation, and no billing-layer tag exposure. The 11 Deviations cover PricingUnit normalization, enum derivation, and pricing.

**Recommendation:** Implement one FOCUS row per RunPod pod × billing period (GPU-Hour or second-level granularity). ResourceId = pod ID. ServiceCategory = "Compute". PricingUnit = "GPU-Hours" for GPU pods; "CPU-Hours" for CPU-only pods; "Requests" for serverless endpoints.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

**RunPod GraphQL API**: Returns pod billing data. Key fields: pod ID, pod name, GPU type, hours used, cost per hour, total cost, data center. RunPod billing dashboard provides invoice-level summaries.

Key characteristics:
- **Secure Cloud:** Dedicated NVIDIA GPU instances (H100 SXM, H100 PCIe, A100, A40, RTX 4090, etc.) in Tier 3/4 data centers. Per-second billing.
- **Community Cloud:** Lower-cost GPUs from community providers. Same per-second model. Slightly higher volatility in availability.
- **Serverless GPU:** RunPod Serverless provides on-demand GPU endpoints billed per second of compute plus per request. Billed per "worker-second."
- **Network storage:** Volume storage billed per GB-Hour.
- **Pod IDs:** Each running pod has a unique ID. Available as ResourceId.
- **Data center:** RunPod operates globally (US, EU, AU). Data center code maps to RegionId.
- **No team sub-accounts:** RunPod accounts are individual. Team billing requires supplementary organization; no formal sub-account hierarchy.
- **Public pricing:** RunPod publishes per-GPU-Hour pricing for all available GPU types. ListUnitPrice derivable from the pricing catalog.
- **No CommitmentDiscount:** RunPod has no reserved instances or savings plans. All billing is on-demand.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven. RunPod has no CommitmentDiscount constructs; all seven CommitmentDiscount columns and both CapacityReservation columns are N/A.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | RunPod source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Invoice amount per pod per billing period | Present |
| EffectiveCost | Mandatory | = BilledCost | Present |
| ListCost | Mandatory | On-demand GPU rate × hours from RunPod pricing page | Present |
| ContractedCost | Mandatory | = ListCost (no negotiated pricing for standard accounts; enterprise rates require supplementary data) | Deviation |
| BillingAccountId | Mandatory | RunPod account ID | Present |
| BillingAccountName | Mandatory | Account email or organization name | Present |
| BillingCurrency | Mandatory | USD | Present |
| BillingPeriodStart | Mandatory | First day of billing period | Present |
| BillingPeriodEnd | Mandatory | Last day of billing period | Present |
| ChargePeriodStart | Mandatory | Pod start time (second-level precision) | Present |
| ChargePeriodEnd | Mandatory | Pod stop time | Present |
| ChargeDescription | Mandatory | Derive: GPU type + pod name (e.g., "RunPod H100 SXM · my-training-pod") | Deviation |
| ChargeCategory | Mandatory | Derive: "Usage" for all compute and storage | Deviation |
| ChargeClass | Mandatory (nullable) | null except for corrections | Present |
| InvoiceIssuerName | Mandatory | "RunPod, Inc." | Present |
| ProviderName | Mandatory (dep. v1.3) | "RunPod" | Present |
| PublisherName | Mandatory (dep. v1.3) | "RunPod" | Present |
| ServiceName | Mandatory | "RunPod Secure Cloud", "RunPod Community Cloud", "RunPod Serverless", "RunPod Network Storage" | Present |
| ServiceCategory | Mandatory | Derive: "Compute" for GPU/CPU pods and serverless; "Storage" for network volumes | Deviation |
| PricingQuantity | Mandatory | GPU-Hours (or seconds converted to hours) for pods; requests for serverless | Present |
| PricingUnit | Mandatory | "GPU-Hours" for GPU pods; "CPU-Hours" for CPU pods; "Worker-Seconds" for serverless; "GB-Hours" for storage | Deviation |
| ConsumedQuantity | Conditional | = PricingQuantity | Present |
| ConsumedUnit | Conditional | = PricingUnit | Present |
| ListUnitPrice | Conditional | On-demand rate per GPU-Hour from RunPod pricing catalog | Present |
| ContractedUnitPrice | Conditional | = ListUnitPrice for standard accounts; enterprise rates require supplementary data | Deviation |
| PricingCategory | Conditional | "Standard" (no commitment pricing available) | Deviation |
| ChargeFrequency | Conditional | "Usage-Based" | Deviation |
| BillingAccountType | Conditional | "Direct" or "Enterprise" | Present |
| SubAccountId | Conditional | N/A: RunPod does not have a formal sub-account hierarchy | N/A |
| SubAccountName | Conditional | N/A | N/A |
| SubAccountType | Conditional | N/A | N/A |
| ResourceId | Conditional | RunPod pod ID | Present |
| ResourceName | Conditional | Pod name as set in RunPod dashboard | Present |
| ResourceType | Conditional | GPU type (e.g., "NVIDIA H100 SXM5 80GB", "NVIDIA RTX 4090") | Present |
| SkuId | Conditional | RunPod GPU tier code (e.g., "secure_h100_sxm", "community_rtx4090") | Present |
| Tags | Conditional | N/A: RunPod billing does not expose pod labels at the billing layer | N/A |
| PricingCurrency | Conditional | USD | Present |
| PricingCurrencyListUnitPrice | Conditional | = ListUnitPrice | Present |
| PricingCurrencyContractedUnitPrice | Conditional | = ContractedUnitPrice; Deviation for enterprise | Deviation |
| PricingCurrencyEffectiveCost | Conditional | = EffectiveCost | Present |
| SkuMeter | Conditional | GPU type label (e.g., "H100 SXM5 GPU-Hours", "RTX 4090 GPU-Hours") | Deviation |
| SkuPriceId | Conditional | Not in GraphQL API | Missing: Conditional |
| SkuPriceDetails | Conditional | Not applicable | Missing: Conditional |
| RegionId | Conditional | RunPod data center code (e.g., US-TX-3, EU-NO-1) | Present |
| RegionName | Conditional | Data center location name | Present |
| CommitmentDiscountId | Conditional | N/A: no CommitmentDiscount construct | N/A |
| CommitmentDiscountName | Conditional | N/A | N/A |
| CommitmentDiscountType | Conditional | N/A | N/A |
| CommitmentDiscountCategory | Conditional | N/A | N/A |
| CommitmentDiscountStatus | Conditional | N/A | N/A |
| CommitmentDiscountQuantity | Conditional | N/A | N/A |
| CommitmentDiscountUnit | Conditional | N/A | N/A |
| CapacityReservationId | Conditional | N/A | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | Invoice number from RunPod billing dashboard | Present |
| ServiceSubcategory | Recommended | "Secure GPU Cloud", "Community GPU Cloud", "Serverless GPU", "Network Storage" | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: RunPod data centers are single-AZ locations | N/A |

**Tally:** 30 Present, 11 Deviation, 0 Missing Mandatory, 5 Missing Conditional, 1 Missing Recommended, 10 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Pod IDs, GPU types, data center locations, per-second billing, public pricing. All 21 Mandatory columns have source data.

**Remaining:** Enterprise ContractedCost requires supplementary data. SkuPriceId absent. No sub-account hierarchy.

### 1.5 Deviations to Fix

**PricingUnit:** "GPU-Hours" for GPU pods (convert seconds to hours); "Worker-Seconds" for serverless; "GB-Hours" for network storage.

**ChargeCategory:** "Usage" for all compute and storage rows.

**ServiceCategory:** "Compute" for GPU/CPU pods and serverless endpoints; "Storage" for network volumes.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (June 4, 2026); certify at FOCUS v1.2.

### 2.2 What Certification Requires

Contact `member-cert@finops.org` for the RFI. Document no CommitmentDiscount as correct. Document no sub-account hierarchy.

### 2.3 Phased Roadmap

**Phase 0:** Enable RunPod GraphQL API access. Pull one month of pod billing data.

**Phase 1: Secure Cloud pods.** Map GPU pod rows: ChargeCategory, ServiceCategory, PricingUnit = "GPU-Hours", ResourceId = pod ID, RegionId.

**Phase 2: Community Cloud and serverless.** Add Community Cloud rows and Serverless endpoint rows.

**Phase 3: Storage and certify.** Add network storage rows. Add ServiceSubcategory. Drop ProviderName, PublisherName (v1.4). Validate and certify.

---

## Part 3: Immediate Next Steps

1. Enable RunPod GraphQL API access and pull one month of pod billing data.
2. Implement Phase 1 Secure Cloud transform and run through FOCUS Validator.
3. Open the RFI with `member-cert@finops.org`.

---

## Confidence Summary

- **High:** RunPod GraphQL API provides pod-level billing with GPU type, hours, and data center. All 30 Present columns are grounded in documented API fields.
- **High:** Pod ID maps cleanly to ResourceId. No sub-account hierarchy is correct for RunPod's single-account model.
- **Moderate:** PricingUnit for serverless. "Worker-Seconds" is the logical unit; confirm with FOCUS community.
- **Low:** Enterprise ContractedCost. Custom pricing requires supplementary data.

---

## Sources

- RunPod GraphQL API: [docs.runpod.io/docs/graphql-basics](https://docs.runpod.io/docs/graphql-basics)
- RunPod Pricing: [runpod.io/gpu-cloud](https://www.runpod.io/gpu-cloud)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
