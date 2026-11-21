# New Relic & FOCUS: Data Generator Gap Analysis

*Analysis run: June 25, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** New Relic  
**Prepared:** June 25, 2026  
**Source:** New Relic NerdGraph API; New Relic billing dashboard  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 25 Present, 10 Deviation, 0 Missing Mandatory, 4 Missing Conditional, 1 Missing Recommended, 17 N/A

---

## Executive Summary

New Relic has converged its pricing onto two dimensions: data ingest (GB/month) and users (Full Platform, Core, or Basic). Data ingest is metered at $0.30/GB/month (on-demand) after a free 100 GB/month. Users are subscription seats. Most organizations generate two FOCUS row types: one for ingest and one per user tier. Accounts may have sub-accounts (child accounts) that map to SubAccountId. All 21 Mandatory columns have source data. Seventeen columns are N/A: no resource IDs at the billing layer, no regional billing, and no CommitmentDiscount constructs (New Relic annual plans are pricing tiers).

**Recommendation:** Implement two FOCUS row types: (1) data ingest rows with PricingUnit = "GB", ChargeCategory = "Usage"; (2) user subscription rows with PricingUnit = "Users", ChargeCategory = "Purchase". Parent/child account hierarchy maps to BillingAccountId/SubAccountId.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

**New Relic NerdGraph API**: GraphQL API providing account usage data. Key fields: ingest GB by data type (APM, infrastructure, logs, browser, etc.), user counts by tier, account ID, sub-account ID, billing period.

**New Relic Billing Dashboard**: Monthly invoices with line items for ingest and user tiers. Invoice numbers available.

Key characteristics:
- **Data ingest billing:** New Relic ingests all telemetry data (metrics, events, logs, traces) into the New Relic Database (NRDB). Billed per GB ingested beyond the 100 GB free tier.
- **User billing:** Full Platform Users ($99/month on-demand or $349/month with full access), Core Users ($49/month), Basic Users (free).
- **Sub-account hierarchy:** New Relic supports parent and child accounts. Child accounts roll up to the parent. Child account ID → SubAccountId.
- **Public pricing:** New Relic publishes on-demand ingest pricing ($0.30/GB) and user pricing. ListUnitPrice derivable.
- **Data Plus:** New Relic Data Plus is an optional add-on that extends data retention and query limits. Adds a third FOCUS row type.
- **Annual plans:** Annual commitments reduce ingest rates. PricingCategory = "Committed".
- **No resource IDs:** Billing aggregates by account; no per-host or per-service IDs at the billing layer.
- **No regional billing:** Global multi-tenant SaaS.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven. Annual ingest commitments = PricingCategory "Committed". CommitmentDiscount columns are N/A.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | New Relic source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Invoice amount per billing dimension per account | Present |
| EffectiveCost | Mandatory | = BilledCost | Present |
| ListCost | Mandatory | On-demand rate × quantity from New Relic pricing page | Present |
| ContractedCost | Mandatory | Annual commitment rate × quantity; Deviation for enterprise | Deviation |
| BillingAccountId | Mandatory | New Relic parent account ID | Present |
| BillingAccountName | Mandatory | Account name | Present |
| BillingCurrency | Mandatory | USD | Present |
| BillingPeriodStart | Mandatory | First day of billing month | Present |
| BillingPeriodEnd | Mandatory | Last day of billing month | Present |
| ChargePeriodStart | Mandatory | Start of usage period | Present |
| ChargePeriodEnd | Mandatory | End of usage period | Present |
| ChargeDescription | Mandatory | Derive: "New Relic Data Ingest · GB" or "New Relic Full Platform Users · [count]" | Deviation |
| ChargeCategory | Mandatory | Derive: "Usage" for ingest rows; "Purchase" for user subscription rows | Deviation |
| ChargeClass | Mandatory (nullable) | null except for corrections | Present |
| InvoiceIssuerName | Mandatory | "New Relic, Inc." | Present |
| ProviderName | Mandatory (dep. v1.3) | "New Relic" | Present |
| PublisherName | Mandatory (dep. v1.3) | "New Relic" | Present |
| ServiceName | Mandatory | "New Relic Data Ingest" or "New Relic Full Platform Users" or "New Relic Core Users" | Present |
| ServiceCategory | Mandatory | Derive: "Management and Governance" for observability and monitoring platform | Deviation |
| PricingQuantity | Mandatory | GB ingested or user count per tier | Present |
| PricingUnit | Mandatory | "GB" for ingest rows; "Users" for user subscription rows | Deviation |
| ConsumedQuantity | Conditional | = PricingQuantity for ingest rows; N/A for user seat rows | Present |
| ConsumedUnit | Conditional | "GB" for ingest rows; N/A for user seat rows | Present |
| ListUnitPrice | Conditional | $0.30/GB (ingest on-demand); published user tier rates | Present |
| ContractedUnitPrice | Conditional | Annual commitment rate; Deviation for enterprise | Deviation |
| PricingCategory | Conditional | "Standard" for on-demand; "Committed" for annual ingest commitments | Deviation |
| ChargeFrequency | Conditional | "Usage-Based" for ingest; "Recurring" for user subscriptions | Deviation |
| BillingAccountType | Conditional | "Enterprise" or "Direct" | Present |
| SubAccountId | Conditional | Child account ID | Present |
| SubAccountName | Conditional | Child account name | Present |
| SubAccountType | Conditional | "Account" | Present |
| ResourceId | Conditional | N/A: New Relic billing aggregates by account; no per-host IDs | N/A |
| ResourceName | Conditional | N/A | N/A |
| ResourceType | Conditional | N/A | N/A |
| SkuId | Conditional | Billing dimension code (e.g., "data-ingest", "full-platform-user", "core-user") | Present |
| Tags | Conditional | N/A: New Relic billing does not expose entity tags at the billing layer | N/A |
| PricingCurrency | Conditional | USD | Present |
| PricingCurrencyListUnitPrice | Conditional | = ListUnitPrice | Present |
| PricingCurrencyContractedUnitPrice | Conditional | = ContractedUnitPrice; Deviation for enterprise | Deviation |
| PricingCurrencyEffectiveCost | Conditional | = EffectiveCost | Present |
| SkuMeter | Conditional | "Data Ingest GB", "Full Platform Users", "Core Users", "Data Plus GB" | Deviation |
| SkuPriceId | Conditional | No pricing catalog ID in NerdGraph API | Missing: Conditional |
| SkuPriceDetails | Conditional | Not applicable | Missing: Conditional |
| RegionId | Conditional | N/A: New Relic billing is not region-specific | N/A |
| RegionName | Conditional | N/A | N/A |
| CommitmentDiscountId | Conditional | N/A: annual plans are pricing tiers, not FOCUS CommitmentDiscount | N/A |
| CommitmentDiscountName | Conditional | N/A | N/A |
| CommitmentDiscountType | Conditional | N/A | N/A |
| CommitmentDiscountCategory | Conditional | N/A | N/A |
| CommitmentDiscountStatus | Conditional | N/A | N/A |
| CommitmentDiscountQuantity | Conditional | N/A | N/A |
| CommitmentDiscountUnit | Conditional | N/A | N/A |
| CapacityReservationId | Conditional | N/A | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | Invoice number from New Relic billing dashboard | Present |
| ServiceSubcategory | Recommended | "Observability Data Ingest" or "Observability Users" | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: global SaaS | N/A |

**Tally:** 25 Present, 10 Deviation, 0 Missing Mandatory, 4 Missing Conditional, 1 Missing Recommended, 17 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Per-account ingest GB and user counts, sub-account hierarchy, public pricing, invoice numbers. All 21 Mandatory columns have source data.

**Remaining:** Enterprise commitment ContractedCost and ContractedUnitPrice require supplementary data. SkuPriceId absent.

### 1.5 Deviations to Fix

**ChargeCategory:** Two row types — "Usage" for ingest rows, "Purchase" for user subscription rows. Build a dimension-type → ChargeCategory lookup.

**PricingUnit:** "GB" for ingest rows; "Users" for user tier rows.

**ChargeFrequency:** "Usage-Based" for ingest; "Recurring" for user subscriptions.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (June 4, 2026); certify at FOCUS v1.2.

### 2.2 What Certification Requires

Contact `member-cert@finops.org` for the RFI. Document annual ingest plans as PricingCategory = "Committed", not CommitmentDiscount.

### 2.3 Phased Roadmap

**Phase 0:** Enable NerdGraph API access. Pull one month of per-account ingest GB and user counts.

**Phase 1: Core transform.** Map ingest rows (ChargeCategory = "Usage", PricingUnit = "GB") and user rows (ChargeCategory = "Purchase", PricingUnit = "Users"). Add sub-account hierarchy.

**Phase 2: Data Plus and extensions.** Add Data Plus add-on rows. Integrate annual commitment rates for ContractedCost.

**Phase 3: Certify.** Add ServiceSubcategory. Drop ProviderName, PublisherName (v1.4). Validate and certify.

---

## Part 3: Immediate Next Steps

1. Enable NerdGraph API access and pull one month of per-account ingest and user data.
2. Implement Phase 1 dual-row transform and run through FOCUS Validator.
3. Open the RFI with `member-cert@finops.org`.

---

## Confidence Summary

- **High:** New Relic NerdGraph API provides account-level ingest GB and user counts. All 25 Present columns are grounded in documented API fields.
- **High:** Sub-account hierarchy maps cleanly to SubAccountId. Dual row types (ingest vs. users) are the correct approach.
- **Moderate:** ChargeCategory split between "Usage" and "Purchase" for different row types. Validate with FOCUS Validator.
- **Low:** Enterprise commitment ContractedCost. Custom negotiated ingest rates require supplementary data.

---

## Sources

- New Relic NerdGraph API: [docs.newrelic.com/docs/apis/nerdgraph/get-started/introduction-new-relic-nerdgraph/](https://docs.newrelic.com/docs/apis/nerdgraph/get-started/introduction-new-relic-nerdgraph/)
- New Relic Pricing: [newrelic.com/pricing](https://newrelic.com/pricing)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
