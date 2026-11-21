# CloudHealth (Broadcom) & FOCUS: Data Generator Gap Analysis

*Analysis run: June 25, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** CloudHealth by VMware (Broadcom)  
**Prepared:** June 25, 2026  
**Source:** CloudHealth invoice system; Broadcom billing portal  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 19 Present, 8 Deviation, 0 Missing Mandatory, 8 Missing Conditional, 1 Missing Recommended, 21 N/A

---

## Executive Summary

CloudHealth by VMware (now a Broadcom product) is a FinOps and cloud management platform billed as an enterprise SaaS subscription, typically priced as a percentage of the cloud spend managed or as a flat annual license. Since Broadcom's acquisition of VMware in 2023, CloudHealth pricing and packaging has been bundled into Broadcom's VMware portfolio offerings. All billing is enterprise-negotiated. All 21 Mandatory columns have source data. Twenty-one columns are N/A, correctly reflecting a SaaS subscription model with no resource IDs, no sub-account hierarchy, no consumption metering, and no CommitmentDiscount constructs. The 8 Deviations cover cost enrichment and enum derivation.

**Recommendation:** Map CloudHealth subscription invoice fields: PricingQuantity = "1" (platform subscription) or cloud spend managed, PricingUnit = "Platform Subscriptions" or "Dollars of Cloud Spend", ChargeCategory = "Purchase", ServiceCategory = "Management and Governance". All pricing requires supplementary data from the Broadcom contract system.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

**Broadcom/CloudHealth Invoice and Billing Portal**: CloudHealth enterprise billing managed through invoices and the Broadcom customer portal. Key fields: product name ("CloudHealth by VMware"), subscription tier or cloud-spend-managed commitment, billing period, total amount. Some legacy contracts may include usage-based fees tied to cloud spend under management.

Key characteristics:
- **SaaS subscription:** CloudHealth billed as a flat annual enterprise license or as a percentage of cloud spend managed.
- **Broadcom bundle:** Post-acquisition, CloudHealth may appear as part of VMware Cloud Foundation or Broadcom portfolio bundles.
- **No sub-account hierarchy:** CloudHealth billing is at the enterprise account level. Perspective-level or business group cost allocation is a product feature, not a billing hierarchy.
- **No resource IDs:** SaaS platform; no instance-level resource billing.
- **No regional billing:** Global SaaS.
- **No consumption metering:** Unlike Datadog or New Relic, CloudHealth does not generate per-resource metered billing rows. The platform fee is flat.
- **No CommitmentDiscount:** Platform subscriptions are term licenses.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven. CloudHealth follows the same pattern as other FinOps platform SaaS subscriptions (Vantage, Apptio). N/A is a valid FOCUS state for the 21 columns the billing model does not produce.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | CloudHealth source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Invoice line item total | Present |
| EffectiveCost | Mandatory | Annual: = BilledCost; multi-year: amortize across term | Deviation |
| ListCost | Mandatory | CloudHealth list price; not published for enterprise | Deviation |
| ContractedCost | Mandatory | Enterprise contract rate; not in billing system | Deviation |
| BillingAccountId | Mandatory | Broadcom enterprise account ID | Present |
| BillingAccountName | Mandatory | Customer organization name | Present |
| BillingCurrency | Mandatory | USD | Present |
| BillingPeriodStart | Mandatory | Invoice period start | Present |
| BillingPeriodEnd | Mandatory | Invoice period end | Present |
| ChargePeriodStart | Mandatory | Subscription period start | Present |
| ChargePeriodEnd | Mandatory | Subscription period end | Present |
| ChargeDescription | Mandatory | "CloudHealth by VMware Enterprise Platform Subscription" | Present |
| ChargeCategory | Mandatory | Derive: "Purchase" for all subscription charges | Deviation |
| ChargeClass | Mandatory (nullable) | null except for corrections | Present |
| InvoiceIssuerName | Mandatory | "Broadcom Inc." | Present |
| ProviderName | Mandatory (dep. v1.3) | "CloudHealth" | Present |
| PublisherName | Mandatory (dep. v1.3) | "Broadcom" | Present |
| ServiceName | Mandatory | "CloudHealth by VMware" | Present |
| ServiceCategory | Mandatory | Derive: "Management and Governance" for cloud cost management platform | Deviation |
| PricingQuantity | Mandatory | 1 (platform) or cloud spend managed (for % contracts) | Present |
| PricingUnit | Mandatory | "Platform Subscriptions" for flat; "Dollars of Cloud Spend" for % contracts | Deviation |
| ConsumedQuantity | Conditional | N/A: no variable consumption metering | N/A |
| ConsumedUnit | Conditional | N/A | N/A |
| ListUnitPrice | Conditional | Not published for enterprise | Missing: Conditional |
| ContractedUnitPrice | Conditional | Enterprise rate; not in billing system | Missing: Conditional |
| PricingCategory | Conditional | "Committed" for annual subscriptions | Deviation |
| ChargeFrequency | Conditional | "Recurring" | Deviation |
| BillingAccountType | Conditional | "Enterprise" | Present |
| SubAccountId | Conditional | N/A: no sub-account billing hierarchy | N/A |
| SubAccountName | Conditional | N/A | N/A |
| SubAccountType | Conditional | N/A | N/A |
| ResourceId | Conditional | N/A: SaaS platform subscription | N/A |
| ResourceName | Conditional | N/A | N/A |
| ResourceType | Conditional | N/A | N/A |
| SkuId | Conditional | CloudHealth product SKU from invoice | Present |
| Tags | Conditional | N/A: no resource-level tags in subscription billing | N/A |
| PricingCurrency | Conditional | USD | Present |
| PricingCurrencyListUnitPrice | Conditional | Missing: enterprise pricing not publicly available | Missing: Conditional |
| PricingCurrencyContractedUnitPrice | Conditional | Missing: enterprise pricing not in billing system | Missing: Conditional |
| PricingCurrencyEffectiveCost | Conditional | = EffectiveCost; Deviation for multi-year | Deviation |
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
| InvoiceId | Recommended | Invoice number from Broadcom portal | Present |
| ServiceSubcategory | Recommended | "Cloud Cost Management" | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: global SaaS | N/A |

**Tally:** 19 Present, 8 Deviation, 0 Missing Mandatory, 8 Missing Conditional, 1 Missing Recommended, 21 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Invoice fields for subscription, billing period, invoice number. All 21 Mandatory columns have source data. The 21 N/A columns correctly reflect the SaaS subscription model.

**Remaining:** All pricing requires supplementary contract data. Eight Missing: Conditional columns cannot be populated from the billing system alone.

### 1.5 Deviations to Fix

**ChargeCategory:** "Purchase" for all subscription and platform charges.

**PricingUnit:** "Platform Subscriptions" for flat-fee tiers; "Dollars of Cloud Spend" for percentage-of-spend contracts.

**ServiceCategory:** "Management and Governance" for cloud cost management platform.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (June 4, 2026); certify at FOCUS v1.2.

### 2.2 What Certification Requires

Contact `member-cert@finops.org` for the RFI. Document 21 N/A columns as legitimately not applicable for SaaS subscription billing.

### 2.3 Phased Roadmap

**Phase 0:** Confirm Broadcom portal invoice export access. Pull sample invoices.

**Phase 1: Subscription transform.** Map CloudHealth subscription rows. Derive ChargeCategory, ServiceCategory, PricingUnit.

**Phase 2: Pricing enrichment.** Integrate supplementary data from Broadcom contracts for ListCost, ContractedCost.

**Phase 3: Certify.** Add ServiceSubcategory = "Cloud Cost Management". Drop ProviderName, PublisherName (v1.4). Validate and certify.

---

## Part 3: Immediate Next Steps

1. Confirm Broadcom portal invoice export access.
2. Pull sample invoices for all active CloudHealth subscription agreements.
3. Implement Phase 1 subscription transform and run through FOCUS Validator.
4. Open the RFI with `member-cert@finops.org`.

---

## Confidence Summary

- **High:** CloudHealth invoices expose subscription terms, billing period, and totals. The 21 N/A columns correctly reflect the SaaS model.
- **Moderate:** PricingUnit for percentage-of-spend contracts. "Dollars of Cloud Spend" is the logical choice; confirm with FinOps community.
- **Low:** ListCost and ContractedCost. Broadcom does not publish CloudHealth enterprise pricing.

---

## Sources

- CloudHealth by VMware: [vmware.com/products/cloudhealth.html](https://www.vmware.com/products/cloudhealth.html)
- Broadcom Support: [broadcom.com/support](https://www.broadcom.com/support)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
