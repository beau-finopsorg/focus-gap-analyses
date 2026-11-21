# Vantage & FOCUS: Data Generator Gap Analysis

*Analysis run: June 25, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** Vantage  
**Prepared:** June 25, 2026  
**Source:** Vantage invoice system; Vantage account billing dashboard  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 20 Present, 8 Deviation, 0 Missing Mandatory, 7 Missing Conditional, 1 Missing Recommended, 21 N/A

---

## Executive Summary

Vantage is a FinOps cost visibility platform billed as a SaaS subscription: flat monthly tiers or enterprise agreements priced as a percentage of cloud spend managed. All billing is at the platform level; there are no resource IDs, no sub-account hierarchy, and no consumption metering of customer infrastructure. All 21 Mandatory columns have source data. Twenty-one columns are N/A, correctly reflecting a subscription SaaS model. The 8 Deviations cover ListCost/ContractedCost enrichment, enum derivation, and multi-year EffectiveCost amortization.

**Recommendation:** Map Vantage subscription invoice fields: PricingQuantity = "1" (platform seat), PricingUnit = "Platform Subscriptions", ChargeCategory = "Purchase", ServiceCategory = "Management and Governance". Enterprise percentage-of-spend contracts require supplementary pricing data for ListCost and ContractedCost.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

**Vantage Invoice and Billing Dashboard**: Vantage billing is managed through invoices and the customer billing portal. Key fields: subscription tier, billing period, platform fee. Enterprise contracts may include usage-based fees as a percentage of cloud spend managed.

Key characteristics:
- **Subscription tiers:** Vantage charges flat monthly fees (Free, Pro, Enterprise) or percentage-of-cloud-spend for enterprise accounts.
- **No resource IDs:** Vantage is a cost visibility SaaS; the billing record covers the platform subscription, not customer infrastructure resources.
- **No sub-account hierarchy:** Vantage billing is at the organization level; workspace-level cost allocation is a product feature, not a billing hierarchy.
- **No regional billing:** Global SaaS platform.
- **Enterprise pricing:** Custom enterprise contracts are negotiated and not reflected in the billing system.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven. N/A is a valid FOCUS state for columns the provider's billing model genuinely does not produce.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | Vantage source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Invoice line item total | Present |
| EffectiveCost | Mandatory | Annual: = BilledCost; multi-year or % contracts: amortize | Deviation |
| ListCost | Mandatory | Published tier price; not available for enterprise % contracts | Deviation |
| ContractedCost | Mandatory | Enterprise contract rate; not in billing system | Deviation |
| BillingAccountId | Mandatory | Vantage organization ID | Present |
| BillingAccountName | Mandatory | Customer organization name | Present |
| BillingCurrency | Mandatory | USD | Present |
| BillingPeriodStart | Mandatory | First day of billing month | Present |
| BillingPeriodEnd | Mandatory | Last day of billing month | Present |
| ChargePeriodStart | Mandatory | Subscription period start | Present |
| ChargePeriodEnd | Mandatory | Subscription period end | Present |
| ChargeDescription | Mandatory | "Vantage [Tier] Subscription" | Present |
| ChargeCategory | Mandatory | Derive: "Purchase" for all subscription charges | Deviation |
| ChargeClass | Mandatory (nullable) | null except for corrections | Present |
| InvoiceIssuerName | Mandatory | "Vantage Inc." | Present |
| ProviderName | Mandatory (dep. v1.3) | "Vantage" | Present |
| PublisherName | Mandatory (dep. v1.3) | "Vantage" | Present |
| ServiceName | Mandatory | "Vantage Cloud Cost Management" | Present |
| ServiceCategory | Mandatory | Derive: "Management and Governance" | Deviation |
| PricingQuantity | Mandatory | 1 (platform subscription) or cloud spend managed (for % contracts) | Present |
| PricingUnit | Mandatory | "Platform Subscriptions" for flat tier; "Dollars of Cloud Spend" for % contracts | Deviation |
| ConsumedQuantity | Conditional | N/A: no metered consumption | N/A |
| ConsumedUnit | Conditional | N/A | N/A |
| ListUnitPrice | Conditional | Published tier price; missing for enterprise % contracts | Missing: Conditional |
| ContractedUnitPrice | Conditional | Enterprise rate; not in billing system | Missing: Conditional |
| PricingCategory | Conditional | "Committed" for annual; "Standard" for monthly | Deviation |
| ChargeFrequency | Conditional | "Recurring" | Deviation |
| BillingAccountType | Conditional | "Enterprise" or "Direct" | Present |
| SubAccountId | Conditional | N/A: no sub-account billing hierarchy | N/A |
| SubAccountName | Conditional | N/A | N/A |
| SubAccountType | Conditional | N/A | N/A |
| ResourceId | Conditional | N/A: SaaS platform subscription | N/A |
| ResourceName | Conditional | N/A | N/A |
| ResourceType | Conditional | N/A | N/A |
| SkuId | Conditional | Vantage tier code (e.g., "vantage-pro", "vantage-enterprise") | Present |
| Tags | Conditional | N/A: no resource-level tags in subscription billing | N/A |
| PricingCurrency | Conditional | USD | Present |
| PricingCurrencyListUnitPrice | Conditional | Missing: requires supplementary data for enterprise | Missing: Conditional |
| PricingCurrencyContractedUnitPrice | Conditional | Missing: enterprise pricing not in billing system | Missing: Conditional |
| PricingCurrencyEffectiveCost | Conditional | = EffectiveCost; Deviation for % contracts | Deviation |
| SkuMeter | Conditional | N/A for flat subscription; "Dollars of Cloud Spend" for % contracts | Missing: Conditional |
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
| InvoiceId | Recommended | Invoice number from billing portal | Present |
| ServiceSubcategory | Recommended | "Cloud Cost Management" | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: global SaaS | N/A |

**Tally:** 20 Present, 8 Deviation, 0 Missing Mandatory, 7 Missing Conditional, 1 Missing Recommended, 21 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Invoice fields for tier, billing period, invoice number. All 21 Mandatory columns have source data. The 21 N/A columns correctly reflect the SaaS subscription model.

**Remaining:** Enterprise % contracts require supplementary data for ListCost, ContractedCost, ListUnitPrice, ContractedUnitPrice. SkuPriceId absent.

### 1.5 Deviations to Fix

**ChargeCategory:** "Purchase" for all subscription and platform charges.

**ServiceCategory:** "Management and Governance" for cost visibility and FinOps tooling.

**PricingUnit:** "Platform Subscriptions" for flat-fee tiers. "Dollars of Cloud Spend" for percentage-based enterprise contracts.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (June 4, 2026); certify at FOCUS v1.2.

### 2.2 What Certification Requires

Contact `member-cert@finops.org` for the RFI. The 21 N/A columns must be documented as legitimately not applicable for a SaaS subscription model.

### 2.3 Phased Roadmap

**Phase 0:** Confirm invoice export access. Pull sample invoices across tiers.

**Phase 1: Core subscription transform.** Map flat-tier subscription rows. Derive ChargeCategory, ServiceCategory, PricingUnit = "Platform Subscriptions".

**Phase 2: Enterprise % contracts.** Handle percentage-of-spend PricingUnit. Integrate supplementary pricing data for ListCost, ContractedCost.

**Phase 3: Certify.** Add ServiceSubcategory. Drop ProviderName, PublisherName (v1.4). Validate and certify.

### 2.4 FOCUS Use Cases Vantage Customers Unlock

**After Phase 1:** Vantage platform cost as a FOCUS row alongside the cloud provider costs Vantage manages. FinOps tooling cost allocation.

---

## Part 3: Immediate Next Steps

1. Confirm invoice export or API access from the Vantage billing portal.
2. Pull sample invoices covering flat-tier and enterprise contracts.
3. Implement Phase 1 subscription transform and run through FOCUS Validator.
4. Open the RFI with `member-cert@finops.org`.

---

## Confidence Summary

- **High:** Vantage invoices expose tier, billing period, and totals. The 21 N/A columns correctly reflect the SaaS model.
- **Moderate:** PricingUnit for enterprise % contracts. "Dollars of Cloud Spend" is the logical choice; confirm with FinOps community.
- **Low:** ListCost and ContractedCost for enterprise % contracts. These require supplementary pricing data.

---

## Sources

- Vantage Pricing: [vantage.sh/pricing](https://www.vantage.sh/pricing)
- Vantage Documentation: [docs.vantage.sh](https://docs.vantage.sh)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
