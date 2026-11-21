# Dynatrace & FOCUS: Data Generator Gap Analysis

*Analysis run: June 25, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** Dynatrace  
**Prepared:** June 25, 2026  
**Source:** Dynatrace DPS Usage API; Dynatrace billing dashboard  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 27 Present, 10 Deviation, 0 Missing Mandatory, 3 Missing Conditional, 1 Missing Recommended, 16 N/A

---

## Executive Summary

Dynatrace bills through its Dynatrace Platform Subscription (DPS) model: a unified credit pool called Davis Data Units (DDUs) consumed across infrastructure monitoring, log management, application security, digital experience monitoring, and business analytics. Each capability has a DDU consumption rate. Dynatrace's Usage API provides per-capability, per-environment consumption data. All 21 Mandatory columns have source data. Sixteen columns are N/A: no per-resource IDs at the billing layer, no regional billing, and no commitment discount constructs (DPS commitments are pricing tiers, not FOCUS CommitmentDiscounts).

**Recommendation:** Implement one FOCUS row per Dynatrace capability × environment × billing period. PricingUnit = "Davis Data Units" across all capabilities; SkuMeter = capability name (e.g., "Infrastructure Monitoring DDUs"). Public on-demand DDU rates cover ListUnitPrice; enterprise DPS commitment rates require supplementary pricing.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

**Dynatrace Usage API**: Returns daily DDU consumption broken down by capability and by environment. Environments map to SubAccountId. Key capabilities: Infrastructure Monitoring, Log Management and Analytics, Application Security, Digital Experience Monitoring, Business Analytics, Synthetic Monitoring.

Key characteristics:
- **Unified credit model:** All Dynatrace capabilities consume DDUs from a shared pool. One PricingUnit spans all rows.
- **Environment hierarchy:** Dynatrace deployments use environments (e.g., dev, staging, prod). These map to SubAccountId/SubAccountName.
- **Public on-demand pricing:** Dynatrace publishes per-DDU on-demand rates for all major capabilities. ListUnitPrice is derivable.
- **DPS commitments:** Customers commit to a DDU pool annually. This is PricingCategory = "Committed", not a FOCUS CommitmentDiscount.
- **No resource IDs:** Billing aggregates by capability; no per-host or per-service IDs at the billing layer.
- **No regional billing:** Dynatrace is a global SaaS platform. Data residency options exist but do not create separate billing line items.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven. DPS annual commitments map to PricingCategory = "Committed". CommitmentDiscount columns are N/A.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | Dynatrace source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Invoice amount per capability per billing period | Present |
| EffectiveCost | Mandatory | = BilledCost (no prepaid amortization at DDU level) | Present |
| ListCost | Mandatory | On-demand DDU rate × DDU quantity from pricing page | Present |
| ContractedCost | Mandatory | DPS commitment rate × quantity; not in Usage API for enterprise | Deviation |
| BillingAccountId | Mandatory | Dynatrace tenant ID | Present |
| BillingAccountName | Mandatory | Customer organization name | Present |
| BillingCurrency | Mandatory | USD or EUR | Present |
| BillingPeriodStart | Mandatory | First day of billing month | Present |
| BillingPeriodEnd | Mandatory | Last day of billing month | Present |
| ChargePeriodStart | Mandatory | Start of usage period | Present |
| ChargePeriodEnd | Mandatory | End of usage period | Present |
| ChargeDescription | Mandatory | Derive: capability name + unit (e.g., "Dynatrace Infrastructure Monitoring · Davis Data Units") | Deviation |
| ChargeCategory | Mandatory | Derive: "Usage" for all DDU consumption | Deviation |
| ChargeClass | Mandatory (nullable) | null except for corrections | Present |
| InvoiceIssuerName | Mandatory | "Dynatrace LLC" | Present |
| ProviderName | Mandatory (dep. v1.3) | "Dynatrace" | Present |
| PublisherName | Mandatory (dep. v1.3) | "Dynatrace" | Present |
| ServiceName | Mandatory | Derive: "Dynatrace Infrastructure Monitoring", "Dynatrace Log Management", "Dynatrace Application Security", etc. | Present |
| ServiceCategory | Mandatory | Derive: "Management and Governance" for observability and security capabilities | Deviation |
| PricingQuantity | Mandatory | DDU quantity consumed per capability per period | Present |
| PricingUnit | Mandatory | "Davis Data Units" across all capabilities | Deviation |
| ConsumedQuantity | Conditional | = PricingQuantity (DDUs consumed) | Present |
| ConsumedUnit | Conditional | "Davis Data Units" | Present |
| ListUnitPrice | Conditional | On-demand DDU rate per capability from Dynatrace pricing page | Present |
| ContractedUnitPrice | Conditional | DPS commitment rate per DDU; Deviation for enterprise accounts | Deviation |
| PricingCategory | Conditional | "Standard" for on-demand; "Committed" for DPS commitment | Deviation |
| ChargeFrequency | Conditional | "Usage-Based" | Deviation |
| BillingAccountType | Conditional | "Enterprise" or "Direct" | Present |
| SubAccountId | Conditional | Dynatrace environment ID | Present |
| SubAccountName | Conditional | Environment name (e.g., "production", "staging") | Present |
| SubAccountType | Conditional | "Environment" | Present |
| ResourceId | Conditional | N/A: DDU billing does not expose per-host or per-service IDs | N/A |
| ResourceName | Conditional | N/A | N/A |
| ResourceType | Conditional | N/A | N/A |
| SkuId | Conditional | Dynatrace capability code (e.g., "infra_monitoring", "log_analytics") | Present |
| Tags | Conditional | N/A: Dynatrace billing does not expose resource tags at the billing layer | N/A |
| PricingCurrency | Conditional | USD or EUR | Present |
| PricingCurrencyListUnitPrice | Conditional | = ListUnitPrice | Present |
| PricingCurrencyContractedUnitPrice | Conditional | = ContractedUnitPrice; Deviation for enterprise rates | Deviation |
| PricingCurrencyEffectiveCost | Conditional | = EffectiveCost | Present |
| SkuMeter | Conditional | Capability name (e.g., "Infrastructure Monitoring DDUs", "Log Analytics DDUs") | Deviation |
| SkuPriceId | Conditional | No pricing catalog ID in Dynatrace Usage API | Missing: Conditional |
| SkuPriceDetails | Conditional | Not applicable (flat per-DDU pricing per capability) | Missing: Conditional |
| RegionId | Conditional | N/A: Dynatrace billing is not region-specific | N/A |
| RegionName | Conditional | N/A | N/A |
| CommitmentDiscountId | Conditional | N/A: DPS commitments are pricing tiers, not FOCUS CommitmentDiscount | N/A |
| CommitmentDiscountName | Conditional | N/A | N/A |
| CommitmentDiscountType | Conditional | N/A | N/A |
| CommitmentDiscountCategory | Conditional | N/A | N/A |
| CommitmentDiscountStatus | Conditional | N/A | N/A |
| CommitmentDiscountQuantity | Conditional | N/A | N/A |
| CommitmentDiscountUnit | Conditional | N/A | N/A |
| CapacityReservationId | Conditional | N/A | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | Invoice number from Dynatrace billing dashboard | Present |
| ServiceSubcategory | Recommended | Map from capability: "Infrastructure Monitoring", "Log Management", "Application Security", "Digital Experience" | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: global SaaS with no per-zone billing | N/A |

**Tally:** 27 Present, 10 Deviation, 0 Missing Mandatory, 3 Missing Conditional, 1 Missing Recommended, 16 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Per-capability DDU usage, environment hierarchy, billing period, on-demand pricing, invoice numbers. All 21 Mandatory columns have source data.

**Remaining:** Enterprise DPS commitment rates require supplementary pricing data. SkuPriceId and SkuPriceDetails absent. Missing: Conditional (3).

### 1.5 Deviations to Fix

**PricingUnit:** "Davis Data Units" across all capabilities. SkuMeter differentiates by capability (e.g., "Infrastructure Monitoring DDUs").

**ChargeCategory:** "Usage" for all DDU consumption. Credit adjustments → "Credit".

**ServiceCategory:** "Management and Governance" for all observability, security, and analytics capabilities.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (June 4, 2026); certify at FOCUS v1.2.

### 2.2 What Certification Requires

Contact `member-cert@finops.org` for the RFI. Document DPS commitments as PricingCategory = "Committed", not CommitmentDiscount.

### 2.3 Phased Roadmap

**Phase 0:** Enable Dynatrace Usage API access. Pull one month of per-capability, per-environment DDU consumption.

**Phase 1: Core DDU transform.** Map Infrastructure Monitoring and Log Management rows. Derive ChargeCategory, ServiceName, PricingUnit = "Davis Data Units", SkuMeter, PricingCategory. Add environment SubAccount mapping.

**Phase 2: Full capability portfolio.** Extend to all active capabilities. Integrate DPS commitment rates for ContractedCost.

**Phase 3: Certify.** Add ServiceSubcategory. Drop ProviderName, PublisherName (v1.4). Validate and certify.

### 2.4 FOCUS Use Cases Dynatrace Customers Unlock

**After Phase 1:** Per-capability DDU cost by environment. On-demand vs. DPS commitment rate comparison. Infrastructure + log management cost by team.

**After Phase 2:** Full observability portfolio cost by capability. ServiceSubcategory-level cost allocation. Cross-capability DDU efficiency.

---

## Part 3: Immediate Next Steps

1. Enable Dynatrace Usage API access and pull one month of per-capability, per-environment DDU data.
2. Build a capability → SkuMeter mapping table from Dynatrace's DDU taxonomy.
3. Implement Phase 1 transform (Infrastructure Monitoring + Log Management) and run through FOCUS Validator.
4. Identify DPS commitment rate for PricingCategory derivation.
5. Open the RFI with `member-cert@finops.org`.

---

## Confidence Summary

- **High:** Dynatrace Usage API provides DDU consumption by capability and environment. All 27 Present columns are grounded in documented API fields.
- **High:** Environment hierarchy maps cleanly to SubAccountId.
- **Moderate:** DPS commitment rate derivation for ContractedCost.
- **Low:** Enterprise ContractedCost. Custom negotiated rates require supplementary data.

---

## Sources

- Dynatrace DPS Usage: [docs.dynatrace.com/docs/platform/davis-data-units](https://docs.dynatrace.com/docs/platform/davis-data-units)
- Dynatrace Pricing: [dynatrace.com/pricing](https://www.dynatrace.com/pricing/)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
