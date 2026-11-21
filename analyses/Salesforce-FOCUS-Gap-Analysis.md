# Salesforce & FOCUS: Data Generator Gap Analysis

*Analysis run: June 25, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** Salesforce  
**Prepared:** June 25, 2026  
**Source:** Salesforce invoices; Salesforce licensing and usage reports  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 22 Present, 11 Deviation, 0 Missing Mandatory, 5 Missing Conditional, 1 Missing Recommended, 18 N/A

---

## Executive Summary

Salesforce operates two billing models within a single invoice: seat-based subscriptions (Sales Cloud, Service Cloud, Platform licenses) and metered usage (Marketing Cloud email sends, data storage overages, API calls). Each requires distinct FOCUS row logic. All 21 Mandatory columns have source data. The 11 Deviations cover ListCost and ContractedCost enrichment, EffectiveCost amortization for multi-year contracts, ChargeCategory and ServiceCategory derivation, and SubAccount mapping for multi-org customers. Eighteen columns are N/A because Salesforce SaaS billing has no per-resource IDs, no regional billing, and no commitment discount constructs.

**Recommendation:** Implement subscription rows first (seat counts, annual billing) using the same pattern as Workday. Add metered usage rows (email sends, storage overages) in Phase 2 with appropriate PricingUnit per usage type. The two row types share the same FOCUS schema.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

**Salesforce Invoices and Usage Reports**: Salesforce provides invoices through its customer billing portal. Subscription line items show product name, user count, unit price, and period. Metered usage reports are available through the Salesforce Setup menu (storage, API calls) and Marketing Cloud dashboards (email sends, contacts).

Key characteristics for FOCUS:

- **Mixed billing model:** Subscription (per user per year for CRM, Platform) and metered usage (per email send for Marketing Cloud, per GB overage for storage, per API call for some integrations).
- **Multi-org customers:** Large enterprises may have multiple Salesforce orgs (instances). Each org represents a potential SubAccount; org IDs are available in licensing records.
- **Enterprise pricing:** Salesforce does not publish list prices publicly for most products (excluding some standard editions). Both ListCost and ContractedCost require supplementary pricing data.
- **Agentforce / Einstein:** Newer AI features (Agentforce conversations, Einstein Copilot) are metered per conversation or per query, adding a third usage dimension.
- **AppExchange add-ons:** Third-party AppExchange products billed through Salesforce invoices have distinct product names and pricing.
- **No resource IDs:** Salesforce SaaS billing has no per-resource instance IDs.
- **No regional billing:** Salesforce is a global SaaS platform; regional instances do not produce separate billing line items.
- **No commitment discounts:** Salesforce subscriptions are term licenses, not FOCUS CommitmentDiscount constructs.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven. For mixed billing models, columns that apply to some row types but not others are Conditional. Columns that never apply to any Salesforce billing row type are N/A.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | Salesforce source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Invoice line item total | Present |
| EffectiveCost | Mandatory | Annual: = BilledCost; multi-year upfront: amortize across subscription term | Deviation |
| ListCost | Mandatory | Salesforce does not publish list prices for most products; requires supplementary pricing data | Deviation |
| ContractedCost | Mandatory | Enterprise-negotiated rate × quantity; not accessible via billing system | Deviation |
| BillingAccountId | Mandatory | Salesforce account ID from invoice | Present |
| BillingAccountName | Mandatory | Customer company name | Present |
| BillingCurrency | Mandatory | Invoice currency (USD or regional) | Present |
| BillingPeriodStart | Mandatory | Invoice period start | Present |
| BillingPeriodEnd | Mandatory | Invoice period end | Present |
| ChargePeriodStart | Mandatory | Subscription or usage period start | Present |
| ChargePeriodEnd | Mandatory | Subscription or usage period end | Present |
| ChargeDescription | Mandatory | Product name + quantity or usage type (e.g., "Sales Cloud Enterprise · 100 Users") | Present |
| ChargeCategory | Mandatory | Derive: "Purchase" for subscription; "Usage" for metered email sends, storage, API calls | Deviation |
| ChargeClass | Mandatory (nullable) | null except for corrections | Present |
| InvoiceIssuerName | Mandatory | "Salesforce, Inc." | Present |
| ProviderName | Mandatory (dep. v1.3) | "Salesforce" | Present |
| PublisherName | Mandatory (dep. v1.3) | "Salesforce" | Present |
| ServiceName | Mandatory | Salesforce product name: "Sales Cloud", "Service Cloud", "Marketing Cloud", "Salesforce Platform" | Present |
| ServiceCategory | Mandatory | Derive: "Management and Governance" for CRM/Platform; "AI and Machine Learning" for Einstein/Agentforce; "Developer Tools" for Heroku | Deviation |
| PricingQuantity | Mandatory | User count for subscriptions; email sends, GB, or API calls for metered usage | Present |
| PricingUnit | Mandatory | "Named Users" for subscriptions; "Email Sends", "GB", "API Calls" for metered usage | Deviation |
| ConsumedQuantity | Conditional | = PricingQuantity for metered usage rows; null for subscription rows | Deviation |
| ConsumedUnit | Conditional | = PricingUnit for metered usage rows; null for subscription rows | Deviation |
| ListUnitPrice | Conditional | Salesforce list price per user or per usage unit; not published for most products | Missing: Conditional |
| ContractedUnitPrice | Conditional | Enterprise-negotiated rate per user or per usage unit; not in billing system | Missing: Conditional |
| PricingCategory | Conditional | "Committed" for subscription; "Standard" for metered usage | Deviation |
| ChargeFrequency | Conditional | "Recurring" for annual invoicing; "Usage-Based" for metered usage rows | Deviation |
| BillingAccountType | Conditional | Derive from Salesforce contract tier (e.g., "Enterprise") | Present |
| SubAccountId | Conditional | Salesforce org ID for multi-org customers; null for single-org customers | Deviation |
| SubAccountName | Conditional | Org display name for multi-org customers | Deviation |
| SubAccountType | Conditional | "Org" for multi-org customers | Deviation |
| ResourceId | Conditional | N/A: Salesforce SaaS billing has no per-resource instance IDs | N/A |
| ResourceName | Conditional | N/A | N/A |
| ResourceType | Conditional | N/A | N/A |
| SkuId | Conditional | Salesforce product code or SKU from invoice line item | Present |
| Tags | Conditional | N/A: Salesforce billing does not include resource-level tags | N/A |
| PricingCurrency | Conditional | = BillingCurrency | Present |
| PricingCurrencyListUnitPrice | Conditional | Missing because ListUnitPrice requires supplementary data | Missing: Conditional |
| PricingCurrencyContractedUnitPrice | Conditional | Missing because enterprise pricing requires supplementary data | Missing: Conditional |
| PricingCurrencyEffectiveCost | Conditional | = EffectiveCost; Deviation because multi-year amortization required | Deviation |
| SkuMeter | Conditional | Derive: "Named Users" for subscription; "Email Sends", "GB", "API Calls" for metered | Deviation |
| SkuPriceId | Conditional | Not in billing system | Missing: Conditional |
| SkuPriceDetails | Conditional | Not applicable for flat per-unit pricing | N/A |
| RegionId | Conditional | N/A: global SaaS, billing is not region-specific | N/A |
| RegionName | Conditional | N/A | N/A |
| CommitmentDiscountId | Conditional | N/A: Salesforce subscriptions are term licenses, not FOCUS CommitmentDiscount | N/A |
| CommitmentDiscountName | Conditional | N/A | N/A |
| CommitmentDiscountType | Conditional | N/A | N/A |
| CommitmentDiscountCategory | Conditional | N/A | N/A |
| CommitmentDiscountStatus | Conditional | N/A | N/A |
| CommitmentDiscountQuantity | Conditional | N/A | N/A |
| CommitmentDiscountUnit | Conditional | N/A | N/A |
| CapacityReservationId | Conditional | N/A | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | Salesforce invoice number | Present |
| ServiceSubcategory | Recommended | Map from product: "CRM", "Marketing Automation", "AI", "Developer Tools" | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: global SaaS with no availability zone billing | N/A |

**Tally:** 22 Present, 11 Deviation, 0 Missing Mandatory, 5 Missing Conditional, 1 Missing Recommended, 18 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Invoice framework is complete. Salesforce invoices expose product names, user counts, usage quantities (for metered products), billing period, and invoice numbers. All 21 Mandatory columns have source data.

**Remaining:** ListCost and ContractedCost require supplementary pricing data. Multi-org SubAccount mapping requires org ID lookup. EffectiveCost amortization for multi-year contracts requires contract term data.

### 1.5 Deviations to Fix

**ChargeCategory:** Subscription products → "Purchase"; metered usage (email sends, storage, API calls) → "Usage"; promotional credits → "Credit".

**SubAccount for multi-org customers:** Map Salesforce org ID → SubAccountId and org name → SubAccountName. Single-org customers: SubAccount = null.

**PricingUnit and ConsumedQuantity:** Subscription rows: PricingUnit = "Named Users", ConsumedQuantity = null. Metered usage rows: PricingUnit = usage unit ("Email Sends", "GB", etc.), ConsumedQuantity = PricingQuantity.

**ServiceCategory:** CRM, Service Cloud, Platform → "Management and Governance"; Einstein, Agentforce → "AI and Machine Learning"; Heroku → "Developer Tools".

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (June 4, 2026); certify at FOCUS v1.2.

### 2.2 What Certification Requires

Contact `member-cert@finops.org` for the RFI. The mixed billing model (subscription + metered usage) must be documented in the conformance gap report.

### 2.3 Phased Roadmap

**Phase 0:** Confirm invoice and usage report access. Pull sample data for subscription and metered usage rows.

**Phase 1: Subscription rows.** Map seat-based products. Derive ChargeCategory = "Purchase", ServiceCategory per product, PricingUnit = "Named Users".

**Phase 2: Metered usage rows.** Add Marketing Cloud, storage, API call rows with appropriate PricingUnit. Implement ConsumedQuantity for usage rows. Add multi-org SubAccount mapping.

**Phase 3: Certify.** Integrate supplementary pricing data for ListCost. Add ServiceSubcategory. Validate and certify.

### 2.4 FOCUS Use Cases Salesforce Customers Unlock

**After Phase 1:** Cost by Salesforce product family. Subscription term tracking. Invoice reconciliation.

**After Phase 2:** Subscription vs. metered usage cost comparison. Marketing Cloud send volume cost analysis. Multi-org cost allocation via SubAccount.

---

## Part 3: Immediate Next Steps

1. Confirm invoice and usage report access via Salesforce billing portal.
2. Identify all active Salesforce products: subscriptions and metered usage types.
3. Implement Phase 1 subscription transform. Run through FOCUS Validator.
4. Design multi-org SubAccount mapping logic (org ID lookup).
5. Open the RFI with `member-cert@finops.org`.

---

## Confidence Summary

- **High:** Salesforce invoices expose product names, user counts, and billing period. Subscription columns are well-sourced.
- **Moderate:** Metered usage row mapping. Marketing Cloud send volumes and storage overages require separate usage report integration.
- **Moderate:** SubAccount (org) mapping for multi-org customers. Requires org ID enrichment from Salesforce licensing records.
- **Low:** ListCost and ContractedCost. Salesforce does not publish list prices for most products.

---

## Sources

- Salesforce Billing Documentation: [help.salesforce.com](https://help.salesforce.com)
- Salesforce Marketing Cloud: [help.salesforce.com/articleView?id=mc](https://help.salesforce.com)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
