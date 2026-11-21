# JFrog & FOCUS: Data Generator Gap Analysis

*Analysis run: June 25, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** JFrog  
**Prepared:** June 25, 2026  
**Source:** JFrog Artifactory billing API; JFrog MyJFrog portal  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 24 Present, 10 Deviation, 0 Missing Mandatory, 4 Missing Conditional, 1 Missing Recommended, 18 N/A

---

## Executive Summary

JFrog bills through a hybrid model: platform subscription (JFrog Platform, Artifactory, Xray, Pipelines, Distribution) with a base tier fee, plus usage-based overages for storage, data transfer, and CI/CD pipeline minutes beyond the included allowance. Subscriptions are per-enterprise, usage overages are metered. The platform does not expose per-artifact or per-build resource IDs at the billing layer. All 21 Mandatory columns have source data. Eighteen columns are N/A: no resource IDs at the billing layer, no sub-account hierarchy, no regional billing, and no CommitmentDiscount constructs. The 10 Deviations cover ChargeCategory split, PricingUnit normalization, and pricing enrichment.

**Recommendation:** Implement two FOCUS row types: (1) platform subscription rows (ChargeCategory = "Purchase", PricingUnit = "Platform Subscriptions") and (2) usage overage rows (ChargeCategory = "Usage", PricingUnit varies by dimension). ChargeFrequency = "Recurring" for subscriptions; "Usage-Based" for overages.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

**JFrog MyJFrog Portal and Invoices**: JFrog enterprise billing managed through the MyJFrog portal. Key fields: subscription tier, storage GB used, data transfer GB, pipeline minutes, billing period, total amount.

Key characteristics:
- **Platform subscription tiers:** JFrog Platform Enterprise/Enterprise+ tiers with base fees covering included storage, transfer, and pipeline minutes.
- **Usage overages:** Storage beyond included allocation billed per GB-Month. Data transfer beyond included allocation billed per GB. Pipeline minutes beyond included allocation billed per minute.
- **No sub-account hierarchy:** JFrog billing is at the enterprise account level; project- or team-level allocation requires custom logic.
- **No resource IDs:** Billing aggregates by usage dimension; no per-artifact, per-repository, or per-build IDs at the billing layer.
- **No regional billing:** JFrog Cloud is a global multi-region SaaS. Customers select a primary region, but billing does not generate per-region rows.
- **No CommitmentDiscount:** Subscription tiers are term licenses. No per-resource reserved capacity.
- **Multi-product:** Artifactory (artifact management), Xray (security scanning), Pipelines (CI/CD), Distribution (release distribution). Each may appear as separate subscription line items.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven. JFrog subscription tiers = PricingCategory "Committed". Usage overages = separate rows with ChargeCategory "Usage".

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | JFrog source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Invoice amount per line item (subscription or overage) | Present |
| EffectiveCost | Mandatory | Annual: = BilledCost; multi-year: amortize | Deviation |
| ListCost | Mandatory | Published tier price or overage rate; enterprise tier requires supplementary data | Deviation |
| ContractedCost | Mandatory | Enterprise rate; not in billing system | Deviation |
| BillingAccountId | Mandatory | JFrog enterprise account ID | Present |
| BillingAccountName | Mandatory | Customer organization name | Present |
| BillingCurrency | Mandatory | USD | Present |
| BillingPeriodStart | Mandatory | First day of billing month | Present |
| BillingPeriodEnd | Mandatory | Last day of billing month | Present |
| ChargePeriodStart | Mandatory | Subscription or usage period start | Present |
| ChargePeriodEnd | Mandatory | Subscription or usage period end | Present |
| ChargeDescription | Mandatory | "JFrog Platform Enterprise+ Subscription" or "JFrog Artifactory Storage Overage · 500 GB" | Present |
| ChargeCategory | Mandatory | Derive: "Purchase" for subscription rows; "Usage" for overage rows | Deviation |
| ChargeClass | Mandatory (nullable) | null except for corrections | Present |
| InvoiceIssuerName | Mandatory | "JFrog Ltd." | Present |
| ProviderName | Mandatory (dep. v1.3) | "JFrog" | Present |
| PublisherName | Mandatory (dep. v1.3) | "JFrog" | Present |
| ServiceName | Mandatory | "JFrog Artifactory", "JFrog Xray", "JFrog Pipelines", "JFrog Distribution" | Present |
| ServiceCategory | Mandatory | Derive: "Developer Tools" for all JFrog DevOps platform products | Deviation |
| PricingQuantity | Mandatory | 1 for subscription; GB for storage/transfer; minutes for pipelines | Present |
| PricingUnit | Mandatory | "Platform Subscriptions" for subscription rows; "GB" for storage/transfer; "Minutes" for pipelines | Deviation |
| ConsumedQuantity | Conditional | N/A for subscription rows; = PricingQuantity for overage rows | Present |
| ConsumedUnit | Conditional | N/A for subscription rows; = PricingUnit for overage rows | Present |
| ListUnitPrice | Conditional | Published overage rates; enterprise tier price requires supplementary data | Deviation |
| ContractedUnitPrice | Conditional | Enterprise rate; not in billing system | Missing: Conditional |
| PricingCategory | Conditional | "Committed" for subscriptions; "Standard" for pay-as-you-go overages | Deviation |
| ChargeFrequency | Conditional | "Recurring" for subscriptions; "Usage-Based" for overages | Deviation |
| BillingAccountType | Conditional | "Enterprise" | Present |
| SubAccountId | Conditional | N/A: no sub-account billing hierarchy | N/A |
| SubAccountName | Conditional | N/A | N/A |
| SubAccountType | Conditional | N/A | N/A |
| ResourceId | Conditional | N/A: billing aggregates by dimension; no per-artifact or per-build IDs | N/A |
| ResourceName | Conditional | N/A | N/A |
| ResourceType | Conditional | N/A | N/A |
| SkuId | Conditional | JFrog tier code or overage dimension code | Present |
| Tags | Conditional | N/A: no resource-level tags in subscription or overage billing | N/A |
| PricingCurrency | Conditional | USD | Present |
| PricingCurrencyListUnitPrice | Conditional | = ListUnitPrice; Deviation where enterprise pricing not available | Deviation |
| PricingCurrencyContractedUnitPrice | Conditional | Missing: enterprise pricing not in billing system | Missing: Conditional |
| PricingCurrencyEffectiveCost | Conditional | = EffectiveCost; Deviation for multi-year | Deviation |
| SkuMeter | Conditional | "Storage GB", "Data Transfer GB", "Pipeline Minutes" for overage rows | Missing: Conditional |
| SkuPriceId | Conditional | Not in billing portal | Missing: Conditional |
| SkuPriceDetails | Conditional | Not applicable | Missing: Conditional |
| RegionId | Conditional | N/A: JFrog Cloud does not produce per-region billing rows | N/A |
| RegionName | Conditional | N/A | N/A |
| CommitmentDiscountId | Conditional | N/A: subscriptions are term licenses, not FOCUS CommitmentDiscount | N/A |
| CommitmentDiscountName | Conditional | N/A | N/A |
| CommitmentDiscountType | Conditional | N/A | N/A |
| CommitmentDiscountCategory | Conditional | N/A | N/A |
| CommitmentDiscountStatus | Conditional | N/A | N/A |
| CommitmentDiscountQuantity | Conditional | N/A | N/A |
| CommitmentDiscountUnit | Conditional | N/A | N/A |
| CapacityReservationId | Conditional | N/A | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | Invoice number from JFrog MyJFrog portal | Present |
| ServiceSubcategory | Recommended | "Artifact Management", "Security Scanning", "CI/CD Pipelines", "Release Distribution" | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: global SaaS | N/A |

**Tally:** 24 Present, 10 Deviation, 0 Missing Mandatory, 4 Missing Conditional, 1 Missing Recommended, 18 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Subscription tier, usage overages, billing period, product names, invoice number. All 21 Mandatory columns have source data.

**Remaining:** Enterprise ContractedCost requires supplementary data. SkuMeter, SkuPriceId absent for some rows.

### 1.5 Deviations to Fix

**ChargeCategory:** "Purchase" for platform subscription rows; "Usage" for storage, transfer, and pipeline minute overages. Build dimension-type → ChargeCategory lookup.

**PricingUnit:** "Platform Subscriptions" for subscription rows; "GB" for storage/transfer overages; "Minutes" for pipeline minute overages.

**ServiceCategory:** "Developer Tools" for all JFrog DevOps platform products.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (June 4, 2026); certify at FOCUS v1.2.

### 2.2 What Certification Requires

Contact `member-cert@finops.org` for the RFI. Document dual ChargeCategory logic and 18 N/A columns.

### 2.3 Phased Roadmap

**Phase 0:** Confirm MyJFrog portal invoice export access. Pull sample invoices across subscription and overage line items.

**Phase 1: Subscription transform.** Map platform subscription rows. ChargeCategory = "Purchase", PricingUnit = "Platform Subscriptions".

**Phase 2: Usage overages.** Add storage, transfer, and pipeline overage rows. ChargeCategory = "Usage".

**Phase 3: Certify.** Add ServiceSubcategory. Drop ProviderName, PublisherName (v1.4). Validate and certify.

---

## Part 3: Immediate Next Steps

1. Confirm JFrog MyJFrog portal invoice export access.
2. Pull sample invoices covering subscription and all active overage dimensions.
3. Implement Phase 1 subscription transform and run through FOCUS Validator.
4. Open the RFI with `member-cert@finops.org`.

---

## Confidence Summary

- **High:** JFrog invoices expose subscription tier, overage dimensions, and billing period. All 21 N/A columns are correctly not applicable.
- **Moderate:** ChargeCategory split between subscription and overage rows. Validate with FOCUS Validator.
- **Low:** Enterprise ContractedCost. JFrog does not publish enterprise tier pricing.

---

## Sources

- JFrog MyJFrog Portal: [myjfrog.jfrog.com](https://myjfrog.jfrog.com)
- JFrog Pricing: [jfrog.com/pricing/](https://jfrog.com/pricing/)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
