# Temporal & FOCUS: Data Generator Gap Analysis

*Analysis run: June 25, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** Temporal  
**Prepared:** June 25, 2026  
**Source:** Temporal Cloud Usage API; Temporal billing dashboard  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 24 Present, 10 Deviation, 0 Missing Mandatory, 5 Missing Conditional, 1 Missing Recommended, 17 N/A

---

## Executive Summary

Temporal Cloud bills by action consumption: each workflow execution, activity execution, signal, query, and child workflow counts as a billable action. Storage (active and retained workflow histories) is a second billing dimension. Namespaces are the resource-level grouping; accounts may have multiple namespaces. All 21 Mandatory columns have source data. Seventeen columns are N/A: no regional billing rows, no CommitmentDiscount constructs. The 10 Deviations cover enum derivation, PricingUnit normalization, and ContractedCost enrichment.

**Recommendation:** Implement one FOCUS row per billing dimension (actions, active storage, retained storage) × namespace × billing period. ResourceId = namespace ID. PricingUnit = "Actions" for action-based rows; "GB-Hours" for storage rows. Public pricing covers on-demand ListUnitPrice.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

**Temporal Cloud Usage API**: Returns action consumption and storage usage broken down by namespace. Key fields: namespace ID, action count, active workflow count, storage GB, billing period, total cost. Temporal publishes on-demand pricing per action and per GB of stored workflow history.

Key characteristics:
- **Action-based billing:** The primary billing unit is an "action" (workflow or activity execution, signal, query). Actions per second determines infrastructure sizing.
- **Storage billing:** Active and retained workflow histories billed per GB-Hour or GB-Month.
- **Namespace as resource:** Temporal Cloud namespaces (e.g., "payments.acme", "orders.acme") map to ResourceId.
- **Account hierarchy:** Multiple namespaces per account; no formal sub-account billing hierarchy.
- **Public pricing:** Temporal publishes per-action and per-GB rates. ListUnitPrice is derivable.
- **No regional billing rows:** Namespace regions are set at creation; billing does not split by region.
- **No CommitmentDiscount:** No per-namespace reserved capacity. Temporal Cloud does offer enterprise commitments (volume discounts) which map to PricingCategory = "Committed".

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven. Enterprise volume commitments = PricingCategory "Committed". CommitmentDiscount columns are N/A.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | Temporal source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Invoice amount per billing dimension per namespace | Present |
| EffectiveCost | Mandatory | = BilledCost | Present |
| ListCost | Mandatory | On-demand rate × quantity from Temporal pricing page | Present |
| ContractedCost | Mandatory | Enterprise commitment rate × quantity; Deviation for custom contracts | Deviation |
| BillingAccountId | Mandatory | Temporal Cloud account ID | Present |
| BillingAccountName | Mandatory | Customer organization name | Present |
| BillingCurrency | Mandatory | USD | Present |
| BillingPeriodStart | Mandatory | First day of billing month | Present |
| BillingPeriodEnd | Mandatory | Last day of billing month | Present |
| ChargePeriodStart | Mandatory | Start of usage period | Present |
| ChargePeriodEnd | Mandatory | End of usage period | Present |
| ChargeDescription | Mandatory | Derive: namespace + dimension (e.g., "Temporal Cloud Actions · payments.acme") | Deviation |
| ChargeCategory | Mandatory | Derive: "Usage" for all action and storage consumption | Deviation |
| ChargeClass | Mandatory (nullable) | null except for corrections | Present |
| InvoiceIssuerName | Mandatory | "Temporal Technologies, Inc." | Present |
| ProviderName | Mandatory (dep. v1.3) | "Temporal" | Present |
| PublisherName | Mandatory (dep. v1.3) | "Temporal" | Present |
| ServiceName | Mandatory | "Temporal Cloud Workflow Executions" or "Temporal Cloud Storage" | Present |
| ServiceCategory | Mandatory | Derive: "Developer Tools" for workflow orchestration platform | Deviation |
| PricingQuantity | Mandatory | Action count or storage GB | Present |
| PricingUnit | Mandatory | "Actions" for execution rows; "GB-Hours" for storage rows | Deviation |
| ConsumedQuantity | Conditional | = PricingQuantity | Present |
| ConsumedUnit | Conditional | = PricingUnit | Present |
| ListUnitPrice | Conditional | On-demand rate per action or per GB-Hour from Temporal pricing page | Present |
| ContractedUnitPrice | Conditional | Enterprise commitment rate; Deviation for custom contracts | Deviation |
| PricingCategory | Conditional | "Standard" for on-demand; "Committed" for enterprise volume commitments | Deviation |
| ChargeFrequency | Conditional | "Usage-Based" | Deviation |
| BillingAccountType | Conditional | "Enterprise" or "Direct" | Present |
| SubAccountId | Conditional | N/A: Temporal Cloud does not expose a formal sub-account billing hierarchy | N/A |
| SubAccountName | Conditional | N/A | N/A |
| SubAccountType | Conditional | N/A | N/A |
| ResourceId | Conditional | Temporal Cloud namespace ID | Present |
| ResourceName | Conditional | Namespace name (e.g., "payments.acme") | Present |
| ResourceType | Conditional | "Namespace" | Present |
| SkuId | Conditional | Billing dimension code (e.g., "actions", "active-storage", "retained-storage") | Present |
| Tags | Conditional | N/A: Temporal Cloud billing does not expose namespace tags at the billing layer | N/A |
| PricingCurrency | Conditional | USD | Present |
| PricingCurrencyListUnitPrice | Conditional | = ListUnitPrice | Present |
| PricingCurrencyContractedUnitPrice | Conditional | = ContractedUnitPrice; Deviation for enterprise | Deviation |
| PricingCurrencyEffectiveCost | Conditional | = EffectiveCost | Present |
| SkuMeter | Conditional | "Actions", "Active Storage GB-Hours", "Retained Storage GB-Hours" | Deviation |
| SkuPriceId | Conditional | No pricing catalog ID in billing API | Missing: Conditional |
| SkuPriceDetails | Conditional | Not applicable | Missing: Conditional |
| RegionId | Conditional | N/A: Temporal Cloud billing does not generate per-region rows | N/A |
| RegionName | Conditional | N/A | N/A |
| CommitmentDiscountId | Conditional | N/A: no per-namespace reserved capacity | N/A |
| CommitmentDiscountName | Conditional | N/A | N/A |
| CommitmentDiscountType | Conditional | N/A | N/A |
| CommitmentDiscountCategory | Conditional | N/A | N/A |
| CommitmentDiscountStatus | Conditional | N/A | N/A |
| CommitmentDiscountQuantity | Conditional | N/A | N/A |
| CommitmentDiscountUnit | Conditional | N/A | N/A |
| CapacityReservationId | Conditional | N/A | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | Invoice number from Temporal billing dashboard | Present |
| ServiceSubcategory | Recommended | "Workflow Orchestration" or "Workflow Storage" | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: no per-AZ billing | N/A |

**Tally:** 24 Present, 10 Deviation, 0 Missing Mandatory, 5 Missing Conditional, 1 Missing Recommended, 17 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Per-namespace action counts and storage GB, public on-demand pricing, namespace ResourceId, invoice numbers. All 21 Mandatory columns have source data.

**Remaining:** Enterprise commitment ContractedCost requires supplementary data. SkuPriceId absent. No SubAccount hierarchy.

### 1.5 Deviations to Fix

**PricingUnit:** "Actions" for workflow/activity execution rows; "GB-Hours" for active and retained storage rows.

**ChargeCategory:** "Usage" for all action and storage consumption.

**ServiceCategory:** "Developer Tools" for workflow orchestration platform.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (June 4, 2026); certify at FOCUS v1.2.

### 2.2 What Certification Requires

Contact `member-cert@finops.org` for the RFI. Document enterprise volume commitments as PricingCategory = "Committed".

### 2.3 Phased Roadmap

**Phase 0:** Enable Temporal Cloud billing API access. Pull one month of per-namespace action and storage data.

**Phase 1: Core actions transform.** Map action consumption rows per namespace. Derive ChargeCategory, ServiceCategory, PricingUnit = "Actions", ResourceId = namespace ID.

**Phase 2: Storage rows.** Add active and retained storage rows with PricingUnit = "GB-Hours".

**Phase 3: Certify.** Add ServiceSubcategory. Drop ProviderName, PublisherName (v1.4). Validate and certify.

---

## Part 3: Immediate Next Steps

1. Enable Temporal Cloud billing API access and pull one month of per-namespace data.
2. Implement Phase 1 actions transform and run through FOCUS Validator.
3. Open the RFI with `member-cert@finops.org`.

---

## Confidence Summary

- **High:** Temporal Cloud billing provides namespace-level action counts and storage usage. All 24 Present columns are grounded in documented billing fields.
- **High:** Namespace ID maps cleanly to ResourceId. No SubAccount hierarchy is correct.
- **Moderate:** ServiceCategory = "Developer Tools". Workflow orchestration does not fit neatly into standard cloud service categories; confirm with FinOps community.
- **Low:** Enterprise ContractedCost. Custom commitment rates require supplementary data.

---

## Sources

- Temporal Cloud Pricing: [temporal.io/cloud/pricing](https://temporal.io/cloud/pricing)
- Temporal Cloud Documentation: [docs.temporal.io/cloud](https://docs.temporal.io/cloud)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
