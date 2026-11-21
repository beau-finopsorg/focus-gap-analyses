# GitLab & FOCUS: Data Generator Gap Analysis

*Analysis run: June 25, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** GitLab  
**Prepared:** June 25, 2026  
**Source:** GitLab Customers Portal; GitLab invoice system  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 23 Present, 10 Deviation, 0 Missing Mandatory, 5 Missing Conditional, 1 Missing Recommended, 18 N/A

---

## Executive Summary

GitLab bills through per-seat subscriptions (Free, Premium at $29/user/month, Ultimate at $99/user/month) plus usage-based components: CI/CD compute minutes, storage overages, and GitLab Duo AI add-on seats. GitLab.com SaaS and GitLab Dedicated are the two cloud offerings; on-premises GitLab is a separate license. Groups provide a hierarchy within GitLab but do not map to a billing sub-account. All 21 Mandatory columns have source data. Eighteen columns are N/A: no resource IDs, no sub-account hierarchy, no regional billing, and no CommitmentDiscount constructs. The 10 Deviations cover ChargeCategory split, PricingUnit normalization, and pricing enrichment.

**Recommendation:** Implement two FOCUS row types: (1) seat subscription rows (ChargeCategory = "Purchase", PricingUnit = "Users") and (2) usage rows for CI/CD minutes and storage overages (ChargeCategory = "Usage", PricingUnit = "Minutes" or "GB"). GitLab Duo AI add-on seats are a third row type (ChargeCategory = "Purchase", PricingUnit = "Users", ServiceCategory = "AI and Machine Learning").

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

**GitLab Customers Portal and Invoices**: GitLab enterprise billing managed through customers.gitlab.com. Key fields: subscription tier, seat count, compute minutes used, storage GB, billing period, total amount.

Key characteristics:
- **Per-seat subscription tiers:** Premium ($29/user/month) and Ultimate ($99/user/month) include a compute minutes and storage allowance.
- **CI/CD compute minutes:** GitLab-hosted CI/CD runners billed per minute beyond the tier's included allowance. Published rate: $10/1000 minutes.
- **Storage overages:** Repository and artifact storage beyond the 10 GB free tier billed per GB-Month.
- **GitLab Duo AI:** AI-assisted coding and security add-on billed per seat per month.
- **GitLab Dedicated:** Dedicated single-tenant SaaS instance with additional infrastructure costs.
- **No sub-account hierarchy:** GitLab groups do not map to billing sub-accounts. Enterprise billing is at the subscription level.
- **No resource IDs:** License billing does not expose repository, project, or pipeline IDs at the billing layer.
- **No regional billing:** Global SaaS.
- **No CommitmentDiscount:** Subscriptions are term licenses. No per-resource reserved capacity.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven. GitLab annual subscriptions = PricingCategory "Committed". Monthly subscriptions = PricingCategory "Standard". ChargeCategory varies by row type.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | GitLab source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Invoice amount per line item | Present |
| EffectiveCost | Mandatory | Annual: = BilledCost; monthly: = BilledCost | Present |
| ListCost | Mandatory | Published tier price × seat count or per-minute rate × minutes | Present |
| ContractedCost | Mandatory | Enterprise rate × seat count; Deviation for custom enterprise pricing | Deviation |
| BillingAccountId | Mandatory | GitLab Customers Portal account ID | Present |
| BillingAccountName | Mandatory | Customer organization name | Present |
| BillingCurrency | Mandatory | USD | Present |
| BillingPeriodStart | Mandatory | First day of billing period | Present |
| BillingPeriodEnd | Mandatory | Last day of billing period | Present |
| ChargePeriodStart | Mandatory | Subscription or usage period start | Present |
| ChargePeriodEnd | Mandatory | Subscription or usage period end | Present |
| ChargeDescription | Mandatory | "GitLab Ultimate · 200 Users" or "GitLab CI/CD Compute Minutes Overage" | Present |
| ChargeCategory | Mandatory | Derive: "Purchase" for subscription and Duo seats; "Usage" for compute minutes and storage overages | Deviation |
| ChargeClass | Mandatory (nullable) | null except for corrections | Present |
| InvoiceIssuerName | Mandatory | "GitLab Inc." | Present |
| ProviderName | Mandatory (dep. v1.3) | "GitLab" | Present |
| PublisherName | Mandatory (dep. v1.3) | "GitLab" | Present |
| ServiceName | Mandatory | "GitLab Premium", "GitLab Ultimate", "GitLab Duo", "GitLab CI/CD Compute" | Present |
| ServiceCategory | Mandatory | Derive: "Developer Tools" for subscription and compute rows; "AI and Machine Learning" for GitLab Duo | Deviation |
| PricingQuantity | Mandatory | Seat count or compute minutes or storage GB | Present |
| PricingUnit | Mandatory | "Users" for seat rows; "Minutes" for compute rows; "GB" for storage rows | Deviation |
| ConsumedQuantity | Conditional | N/A for subscription rows; = PricingQuantity for usage rows | Present |
| ConsumedUnit | Conditional | N/A for subscription rows; = PricingUnit for usage rows | Present |
| ListUnitPrice | Conditional | Published per-user rate or per-minute rate from GitLab pricing page | Present |
| ContractedUnitPrice | Conditional | Enterprise discount rate; Deviation for custom pricing | Deviation |
| PricingCategory | Conditional | "Committed" for annual subscriptions; "Standard" for monthly or on-demand usage | Deviation |
| ChargeFrequency | Conditional | "Recurring" for subscriptions; "Usage-Based" for compute minutes and storage overages | Deviation |
| BillingAccountType | Conditional | "Enterprise" or "Direct" | Present |
| SubAccountId | Conditional | N/A: GitLab groups do not produce sub-account billing records | N/A |
| SubAccountName | Conditional | N/A | N/A |
| SubAccountType | Conditional | N/A | N/A |
| ResourceId | Conditional | N/A: billing does not expose repository or project IDs | N/A |
| ResourceName | Conditional | N/A | N/A |
| ResourceType | Conditional | N/A | N/A |
| SkuId | Conditional | Tier or usage dimension code (e.g., "gitlab-ultimate", "compute-minutes", "gitlab-duo") | Present |
| Tags | Conditional | N/A: no resource-level tags in subscription billing | N/A |
| PricingCurrency | Conditional | USD | Present |
| PricingCurrencyListUnitPrice | Conditional | = ListUnitPrice | Present |
| PricingCurrencyContractedUnitPrice | Conditional | = ContractedUnitPrice; Deviation for enterprise | Deviation |
| PricingCurrencyEffectiveCost | Conditional | = EffectiveCost | Present |
| SkuMeter | Conditional | "Users", "Compute Minutes", "Storage GB" | Deviation |
| SkuPriceId | Conditional | Not in billing system | Missing: Conditional |
| SkuPriceDetails | Conditional | Not applicable | Missing: Conditional |
| RegionId | Conditional | N/A: global SaaS | N/A |
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
| InvoiceId | Recommended | Invoice number from GitLab Customers Portal | Present |
| ServiceSubcategory | Recommended | "DevOps Platform", "CI/CD Compute", "AI Coding Assistant", "Source Code Management" | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: global SaaS | N/A |

**Tally:** 23 Present, 10 Deviation, 0 Missing Mandatory, 5 Missing Conditional, 1 Missing Recommended, 18 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Tier, seat count, compute minutes, storage usage, public pricing, invoice numbers. All 21 Mandatory columns have source data.

**Remaining:** Enterprise ContractedCost requires supplementary data. SkuPriceId absent.

### 1.5 Deviations to Fix

**ChargeCategory:** "Purchase" for subscription and Duo seats; "Usage" for compute minutes overages and storage overages.

**PricingUnit:** "Users" for seat rows; "Minutes" for compute rows; "GB" for storage rows.

**ServiceCategory:** "Developer Tools" for subscription and compute rows; "AI and Machine Learning" for GitLab Duo.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (June 4, 2026); certify at FOCUS v1.2.

### 2.2 What Certification Requires

Contact `member-cert@finops.org` for the RFI. Document dual ChargeCategory and 18 N/A columns.

### 2.3 Phased Roadmap

**Phase 0:** Confirm GitLab Customers Portal invoice export. Pull sample invoices.

**Phase 1: Subscription transform.** Map Premium and Ultimate seat rows. ChargeCategory = "Purchase", PricingUnit = "Users".

**Phase 2: Usage rows.** Add compute minutes and storage overage rows. Add GitLab Duo AI seats.

**Phase 3: Certify.** Add ServiceSubcategory. Drop ProviderName, PublisherName (v1.4). Validate and certify.

---

## Part 3: Immediate Next Steps

1. Confirm GitLab Customers Portal invoice export access.
2. Pull sample invoices across subscription tiers and usage dimensions.
3. Implement Phase 1 subscription transform and run through FOCUS Validator.
4. Open the RFI with `member-cert@finops.org`.

---

## Confidence Summary

- **High:** GitLab invoices expose tier, seat count, and usage dimensions. Standard and Premium pricing is publicly available.
- **Moderate:** ChargeCategory split and ServiceCategory for GitLab Duo AI rows. Confirm with FinOps community.
- **Low:** Enterprise ContractedCost. Custom enterprise pricing requires supplementary data.

---

## Sources

- GitLab Customers Portal: [customers.gitlab.com](https://customers.gitlab.com)
- GitLab Pricing: [about.gitlab.com/pricing/](https://about.gitlab.com/pricing/)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
