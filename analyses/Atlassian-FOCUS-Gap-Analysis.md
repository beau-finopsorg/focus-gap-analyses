# Atlassian & FOCUS: Data Generator Gap Analysis

*Analysis run: June 25, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** Atlassian  
**Prepared:** June 25, 2026  
**Source:** Atlassian invoice system; Atlassian Admin billing portal  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 22 Present, 9 Deviation, 0 Missing Mandatory, 6 Missing Conditional, 1 Missing Recommended, 19 N/A

---

## Executive Summary

Atlassian Cloud bills through per-user product subscriptions (Jira Software, Confluence, Jira Service Management, Bitbucket, Jira Product Discovery) with Standard, Premium, and Enterprise tiers. CI/CD compute minutes (Atlassian Pipelines) add a metered component for Bitbucket customers. Organizations with multiple product instances or sites may have distinct billing lines per site. All 21 Mandatory columns have source data. Nineteen columns are N/A: no resource IDs in subscription billing, no sub-account hierarchy, no regional billing, and no CommitmentDiscount constructs. The 9 Deviations cover enum derivation, cost enrichment, and multi-tier PricingUnit handling.

**Recommendation:** Implement one FOCUS row per Atlassian product × tier × billing period, plus a separate row per billing period for Pipelines compute minutes where applicable. PricingUnit = "Users" for subscription rows; "Minutes" for Pipelines rows. ChargeCategory = "Purchase" for subscriptions; "Usage" for Pipelines minutes.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

**Atlassian Admin Billing Portal and Invoices**: Enterprise billing managed through the Atlassian Admin portal and invoices. Key fields: product name, tier (Standard/Premium/Enterprise), user count, billing period, total amount. Pipelines minutes appear as separate line items for Bitbucket customers.

Key characteristics:
- **Per-user subscriptions:** Jira Software, Confluence, Jira Service Management, Bitbucket, Jira Product Discovery licensed per user per month/year.
- **Three tiers:** Standard, Premium, and Enterprise have different features and pricing. Tier must map to SkuId and ChargeDescription.
- **Pipelines (CI/CD) minutes:** Bitbucket Pipelines billed per minute of CI/CD compute. Published rate per minute on excess over free tier.
- **No sub-account hierarchy:** Atlassian billing is at the organization level; site-level cost allocation requires custom logic.
- **No resource IDs:** License billing has no resource instance IDs.
- **No regional billing:** Global SaaS.
- **Enterprise pricing:** Enterprise tier pricing is negotiated; not publicly listed.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven. N/A is a valid FOCUS state for columns the billing model genuinely does not produce.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | Atlassian source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Invoice line item total per product per tier | Present |
| EffectiveCost | Mandatory | Annual: = BilledCost; monthly: = BilledCost | Present |
| ListCost | Mandatory | Standard/Premium list price × user count; not available for Enterprise | Deviation |
| ContractedCost | Mandatory | Enterprise negotiated rate × user count; not in billing system | Deviation |
| BillingAccountId | Mandatory | Atlassian organization ID | Present |
| BillingAccountName | Mandatory | Organization name | Present |
| BillingCurrency | Mandatory | USD or regional | Present |
| BillingPeriodStart | Mandatory | First day of billing month | Present |
| BillingPeriodEnd | Mandatory | Last day of billing month | Present |
| ChargePeriodStart | Mandatory | Subscription period start | Present |
| ChargePeriodEnd | Mandatory | Subscription period end | Present |
| ChargeDescription | Mandatory | Product + tier + quantity (e.g., "Jira Software Premium · 150 Users") | Present |
| ChargeCategory | Mandatory | Derive: "Purchase" for subscriptions; "Usage" for Pipelines minutes | Deviation |
| ChargeClass | Mandatory (nullable) | null except for corrections | Present |
| InvoiceIssuerName | Mandatory | "Atlassian Pty Ltd" | Present |
| ProviderName | Mandatory (dep. v1.3) | "Atlassian" | Present |
| PublisherName | Mandatory (dep. v1.3) | "Atlassian" | Present |
| ServiceName | Mandatory | Product name: "Atlassian Jira Software", "Atlassian Confluence", "Atlassian Jira Service Management", "Atlassian Bitbucket" | Present |
| ServiceCategory | Mandatory | Derive: "Developer Tools" for Jira Software, Confluence, Bitbucket, Jira PD; "Management and Governance" for Jira Service Management | Deviation |
| PricingQuantity | Mandatory | User count or Pipelines minutes | Present |
| PricingUnit | Mandatory | "Users" for subscription rows; "Minutes" for Pipelines rows | Deviation |
| ConsumedQuantity | Conditional | N/A for subscription rows; = PricingQuantity for Pipelines rows | Present |
| ConsumedUnit | Conditional | N/A for subscription rows; "Minutes" for Pipelines rows | Present |
| ListUnitPrice | Conditional | Standard/Premium published rate; not available for Enterprise | Deviation |
| ContractedUnitPrice | Conditional | Enterprise rate; not accessible via billing system | Missing: Conditional |
| PricingCategory | Conditional | "Committed" for annual subscriptions; "Standard" for monthly | Deviation |
| ChargeFrequency | Conditional | "Recurring" for subscriptions; "Usage-Based" for Pipelines | Deviation |
| BillingAccountType | Conditional | "Enterprise" or "Direct" | Present |
| SubAccountId | Conditional | N/A: no sub-account billing hierarchy | N/A |
| SubAccountName | Conditional | N/A | N/A |
| SubAccountType | Conditional | N/A | N/A |
| ResourceId | Conditional | N/A: license billing | N/A |
| ResourceName | Conditional | N/A | N/A |
| ResourceType | Conditional | N/A | N/A |
| SkuId | Conditional | Product + tier code (e.g., "jira-software-premium", "bitbucket-pipelines-minutes") | Present |
| Tags | Conditional | N/A: no resource-level tags in subscription billing | N/A |
| PricingCurrency | Conditional | = BillingCurrency | Present |
| PricingCurrencyListUnitPrice | Conditional | = ListUnitPrice; Deviation where enterprise pricing not available | Deviation |
| PricingCurrencyContractedUnitPrice | Conditional | Missing: enterprise pricing not in billing system | Missing: Conditional |
| PricingCurrencyEffectiveCost | Conditional | = EffectiveCost | Present |
| SkuMeter | Conditional | N/A for flat subscriptions; "Pipelines Minutes" for Pipelines rows | Missing: Conditional |
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
| InvoiceId | Recommended | Invoice number from Atlassian Admin portal | Present |
| ServiceSubcategory | Recommended | Map from product: "Issue Tracking", "Team Collaboration", "IT Service Management", "Source Code Management" | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: global SaaS | N/A |

**Tally:** 22 Present, 9 Deviation, 0 Missing Mandatory, 6 Missing Conditional, 1 Missing Recommended, 19 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Product, tier, user count, billing period, invoice number. All 21 Mandatory columns have source data. Standard/Premium list prices are publicly available.

**Remaining:** Enterprise ContractedCost and ContractedUnitPrice require supplementary data. SkuPriceId absent.

### 1.5 Deviations to Fix

**ChargeCategory:** "Purchase" for subscription rows; "Usage" for Pipelines minutes. Build a product-type → ChargeCategory lookup.

**PricingUnit:** "Users" for subscription rows; "Minutes" for Pipelines rows.

**ServiceCategory:** "Developer Tools" for Jira Software, Confluence, Bitbucket; "Management and Governance" for Jira Service Management.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (June 4, 2026); certify at FOCUS v1.2.

### 2.2 What Certification Requires

Contact `member-cert@finops.org` for the RFI. Document N/A columns and dual ChargeCategory logic.

### 2.3 Phased Roadmap

**Phase 0:** Confirm Admin billing portal invoice export access. Pull sample invoices across all active products.

**Phase 1: Core subscription transform.** Map Jira Software and Confluence rows. Derive ChargeCategory, ServiceCategory, PricingUnit = "Users".

**Phase 2: Pipelines and Jira Service Management.** Add Pipelines minutes rows (ChargeCategory = "Usage"). Add JSM rows with ServiceCategory = "Management and Governance".

**Phase 3: Certify.** Add ServiceSubcategory. Drop ProviderName, PublisherName (v1.4). Validate and certify.

---

## Part 3: Immediate Next Steps

1. Confirm Atlassian Admin billing portal invoice export access.
2. Pull sample invoices across all active Atlassian products.
3. Implement Phase 1 subscription transform and run through FOCUS Validator.
4. Open the RFI with `member-cert@finops.org`.

---

## Confidence Summary

- **High:** Atlassian invoices expose product, tier, and user count. Standard and Premium pricing is publicly available.
- **High:** The 19 N/A columns correctly reflect the SaaS subscription model.
- **Moderate:** ServiceCategory split between "Developer Tools" and "Management and Governance". Confirm Jira Service Management mapping.
- **Low:** Enterprise ContractedCost. Enterprise tier pricing is not publicly available.

---

## Sources

- Atlassian Admin Billing: [admin.atlassian.com](https://admin.atlassian.com)
- Atlassian Pricing: [atlassian.com/software/jira/pricing](https://www.atlassian.com/software/jira/pricing)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
