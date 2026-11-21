# Adobe & FOCUS: Data Generator Gap Analysis

*Analysis run: June 25, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** Adobe  
**Prepared:** June 25, 2026  
**Source:** Adobe invoice system; Adobe Admin Console  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 21 Present, 8 Deviation, 0 Missing Mandatory, 7 Missing Conditional, 1 Missing Recommended, 20 N/A

---

## Executive Summary

Adobe bills primarily through seat-based subscriptions (Creative Cloud for Enterprise, Document Cloud, Sign) with credit-based add-ons for Adobe Stock. All billing is enterprise-negotiated; Adobe does not publish list prices for enterprise agreements. All 21 Mandatory columns have source data. Twenty columns are N/A: no resource IDs, no sub-account hierarchy, no regional billing, and no commitment discount constructs. The 8 Deviations cover ListCost/ContractedCost enrichment, EffectiveCost amortization for multi-year contracts, and enum derivation. Adobe Experience Cloud (DXP) enterprise contracts may include usage components (email sends, content views) adding complexity.

**Recommendation:** Map Adobe Creative Cloud for Enterprise invoice fields first: seat count as PricingQuantity, "Named Users" as PricingUnit, ChargeCategory = "Purchase", ServiceCategory = "Developer Tools". Add Adobe Stock (credit-based) and Experience Cloud metered usage in a follow-on pass.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

**Adobe Admin Console and Invoice System**: Adobe enterprise billing is managed through the Adobe Admin Console and invoices. Key fields: product name, user count, license period, total amount. Adobe Stock credits appear as separate line items. Experience Cloud metered usage requires integration with Adobe Analytics APIs.

Key characteristics:
- **Seat-based subscriptions:** Creative Cloud for Enterprise, Document Cloud, Adobe Sign billed per named user per year.
- **Credit-based:** Adobe Stock licensed in credit packs or credits per asset.
- **Experience Cloud:** Adobe Experience Cloud (AEM, Campaign, Analytics, Target) uses enterprise subscription pricing with usage components for some products.
- **No public pricing:** All enterprise pricing is negotiated. List and contracted costs require supplementary data.
- **No sub-account hierarchy:** Adobe billing is at the enterprise account level; team or department billing requires supplementary cost allocation logic.
- **No resource IDs:** Software licenses are not associated with resource instances.
- **No regional billing:** Global SaaS platform.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven. N/A is a valid FOCUS state for columns the provider's billing model genuinely does not produce.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | Adobe source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Invoice line item total | Present |
| EffectiveCost | Mandatory | Annual: = BilledCost; multi-year: amortize across term | Deviation |
| ListCost | Mandatory | Adobe list price × quantity; not published for enterprise; requires supplementary data | Deviation |
| ContractedCost | Mandatory | Enterprise-negotiated rate × quantity; not in billing system | Deviation |
| BillingAccountId | Mandatory | Adobe enterprise account ID | Present |
| BillingAccountName | Mandatory | Enterprise customer name | Present |
| BillingCurrency | Mandatory | Invoice currency (USD or regional) | Present |
| BillingPeriodStart | Mandatory | Invoice period start | Present |
| BillingPeriodEnd | Mandatory | Invoice period end | Present |
| ChargePeriodStart | Mandatory | Subscription period start | Present |
| ChargePeriodEnd | Mandatory | Subscription period end | Present |
| ChargeDescription | Mandatory | Product name + quantity (e.g., "Creative Cloud All Apps · 200 Named Users") | Present |
| ChargeCategory | Mandatory | Derive: "Purchase" for all subscription and credit pack charges | Deviation |
| ChargeClass | Mandatory (nullable) | null except for corrections | Present |
| InvoiceIssuerName | Mandatory | "Adobe Inc." | Present |
| ProviderName | Mandatory (dep. v1.3) | "Adobe" | Present |
| PublisherName | Mandatory (dep. v1.3) | "Adobe" | Present |
| ServiceName | Mandatory | Product name: "Adobe Creative Cloud", "Adobe Document Cloud", "Adobe Sign", "Adobe Experience Cloud" | Present |
| ServiceCategory | Mandatory | Derive: "Developer Tools" for Creative Cloud; "Management and Governance" for Document/Sign; "AI and Machine Learning" for Firefly | Deviation |
| PricingQuantity | Mandatory | Named user count or credit pack quantity | Present |
| PricingUnit | Mandatory | "Named Users" for subscriptions; "Credits" for Adobe Stock | Deviation |
| ConsumedQuantity | Conditional | N/A: no variable consumption metering for seat subscriptions; credits are pre-purchased, not metered | N/A |
| ConsumedUnit | Conditional | N/A | N/A |
| ListUnitPrice | Conditional | Not published for enterprise; requires supplementary data | Missing: Conditional |
| ContractedUnitPrice | Conditional | Enterprise rate not accessible via billing system | Missing: Conditional |
| PricingCategory | Conditional | "Committed" for all term subscriptions and credit pack purchases | Deviation |
| ChargeFrequency | Conditional | "Recurring" for annual subscriptions; "One-Time" for credit pack purchases | Deviation |
| BillingAccountType | Conditional | "Enterprise" | Present |
| SubAccountId | Conditional | N/A: no sub-account hierarchy in Adobe enterprise billing | N/A |
| SubAccountName | Conditional | N/A | N/A |
| SubAccountType | Conditional | N/A | N/A |
| ResourceId | Conditional | N/A: license billing has no resource instance IDs | N/A |
| ResourceName | Conditional | N/A | N/A |
| ResourceType | Conditional | N/A | N/A |
| SkuId | Conditional | Adobe product or SKU code from invoice | Present |
| Tags | Conditional | N/A: no resource-level tags in subscription billing | N/A |
| PricingCurrency | Conditional | = BillingCurrency | Present |
| PricingCurrencyListUnitPrice | Conditional | Missing because ListUnitPrice requires supplementary data | Missing: Conditional |
| PricingCurrencyContractedUnitPrice | Conditional | Missing because enterprise pricing requires supplementary data | Missing: Conditional |
| PricingCurrencyEffectiveCost | Conditional | = EffectiveCost; Deviation because multi-year amortization required | Deviation |
| SkuMeter | Conditional | Not applicable for flat subscription; "Credits" for Stock | Missing: Conditional |
| SkuPriceId | Conditional | Not in billing system | Missing: Conditional |
| SkuPriceDetails | Conditional | Not applicable (flat per-seat pricing) | Missing: Conditional |
| RegionId | Conditional | N/A: global SaaS | N/A |
| RegionName | Conditional | N/A | N/A |
| CommitmentDiscountId | Conditional | N/A: Adobe subscriptions are term licenses, not FOCUS CommitmentDiscount | N/A |
| CommitmentDiscountName | Conditional | N/A | N/A |
| CommitmentDiscountType | Conditional | N/A | N/A |
| CommitmentDiscountCategory | Conditional | N/A | N/A |
| CommitmentDiscountStatus | Conditional | N/A | N/A |
| CommitmentDiscountQuantity | Conditional | N/A | N/A |
| CommitmentDiscountUnit | Conditional | N/A | N/A |
| CapacityReservationId | Conditional | N/A | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | Adobe invoice number | Present |
| ServiceSubcategory | Recommended | Map from product: "Creative Tools", "Document Management", "Digital Signatures", "Marketing" | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: global SaaS | N/A |

**Tally:** 21 Present, 8 Deviation, 0 Missing Mandatory, 7 Missing Conditional, 1 Missing Recommended, 20 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Invoice fields for product names, user counts, subscription period, and invoice numbers. All 21 Mandatory columns have source data.

**Remaining:** List and contracted pricing require supplementary data. SkuMeter is absent for subscription rows; present only for credit-based products.

### 1.5 Deviations to Fix

**ChargeCategory:** All Adobe subscriptions and credit packs → "Purchase". Refunds/credits → "Credit".

**PricingUnit:** Subscriptions → "Named Users"; Adobe Stock → "Credits".

**ServiceCategory:** Creative Cloud → "Developer Tools"; Document Cloud, Sign → "Management and Governance"; Firefly, Sensei AI → "AI and Machine Learning".

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (June 4, 2026); certify at FOCUS v1.2.

### 2.2 What Certification Requires

Contact `member-cert@finops.org` for the RFI. The 20 N/A columns must be documented as legitimately not applicable for a SaaS subscription model.

### 2.3 Phased Roadmap

**Phase 0:** Confirm Admin Console invoice export or API access. Pull sample invoices across all active Adobe products.

**Phase 1: Core subscription transform.** Map Creative Cloud for Enterprise and Document Cloud rows. Derive ChargeCategory = "Purchase", ServiceCategory, PricingUnit = "Named Users".

**Phase 2: Stock and Experience Cloud.** Add Adobe Stock rows with PricingUnit = "Credits". Integrate Experience Cloud metered usage where applicable.

**Phase 3: Certify.** Add ServiceSubcategory mapping. Drop ProviderName, PublisherName (v1.4). Validate and certify.

### 2.4 FOCUS Use Cases Adobe Customers Unlock

**After Phase 1:** Cost by Adobe product family. Subscription term tracking. Invoice reconciliation via InvoiceId.

**After Phase 2:** Creative vs. Document vs. Experience Cloud cost allocation. Adobe Stock credit spend tracking.

---

## Part 3: Immediate Next Steps

1. Confirm Adobe Admin Console invoice export or billing API access.
2. Pull sample invoices covering all active Adobe enterprise products.
3. Implement Phase 1 subscription transform. Run through FOCUS Validator.
4. Open the RFI with `member-cert@finops.org`.

---

## Confidence Summary

- **High:** Adobe invoices expose product names, user counts, and billing period. The 21 Present columns are grounded in standard invoice fields.
- **High:** The 20 N/A columns correctly reflect Adobe's SaaS subscription model.
- **Moderate:** ServiceCategory mapping. "Developer Tools" for Creative Cloud is non-obvious; confirm with FinOps team.
- **Low:** ListCost and ContractedCost. Adobe does not publish enterprise list prices.

---

## Sources

- Adobe Admin Console: [adminconsole.adobe.com](https://adminconsole.adobe.com)
- Adobe Value Incentive Plan Documentation: [helpx.adobe.com/enterprise](https://helpx.adobe.com/enterprise)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
