# Workday & FOCUS: Data Generator Gap Analysis

*Analysis run: June 25, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** Workday  
**Prepared:** June 25, 2026  
**Source:** Workday invoice system; Workday Customer Center  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 20 Present, 8 Deviation, 0 Missing Mandatory, 7 Missing Conditional, 1 Missing Recommended, 21 N/A

---

## Executive Summary

Workday is a SaaS ERP and HCM platform sold as annual or multi-year seat-based subscriptions. Billing is per named user per subscription period; no consumption metering exists at the customer billing layer. All 21 Mandatory columns have source data. Twenty-one columns are legitimately N/A: no resource IDs, no sub-account hierarchy, no regional breakout, and no commitment discount or consumption metering constructs exist in Workday's billing model. The 8 Deviations cover EffectiveCost amortization for multi-year contracts, ListCost and ContractedCost enrichment (enterprise pricing not in invoices), and enum derivation.

**Recommendation:** The Workday FOCUS transform parallels the Nutanix pattern: map invoice fields to FOCUS, derive ChargeCategory = "Purchase" and ServiceCategory = "Management and Governance", and document 21 N/A columns as legitimately not applicable for a pure SaaS subscription model.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

**Workday Invoice System / Customer Center**: Workday does not publish a public programmatic billing API. Billing data is available through Workday's customer-facing portal and invoices. Key fields: invoice number, billing period, line items (product module, user count, unit price, total), customer information, and renewal dates.

Key characteristics for FOCUS:

- **Seat-based subscriptions:** Workday licenses are sold per named user per year. Modules (HCM, Financials, Planning, Payroll, etc.) are purchased separately. User count is the PricingQuantity; "Named Users" is the PricingUnit.
- **Enterprise pricing:** All Workday pricing is enterprise-negotiated. Workday does not publish list prices publicly. Both ListCost and ContractedCost require supplementary pricing data.
- **No consumption metering:** Workday SaaS does not generate per-transaction or per-resource billing data. The charge is fixed per seat per period regardless of platform usage.
- **No sub-account hierarchy:** Workday billing is at the enterprise customer level. Individual business units or countries are not billing sub-accounts in Workday's system.
- **No resource IDs:** Workday SaaS licenses are not associated with individual compute resources or resource instances.
- **No regional billing:** Workday is a global SaaS platform. Regional deployments (data centers) do not produce separate billing line items.
- **Annual or multi-year terms:** Standard contracts are 3 to 5 years. Annual invoicing is common; multi-year upfront payment also occurs. Multi-year contracts require EffectiveCost amortization.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven. N/A is a valid FOCUS state for columns the provider's billing model genuinely does not produce. A SaaS subscription vendor without consumption metering or resource-level billing legitimately nulls those columns.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | Workday source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Invoice line item total (subscription period amount) | Present |
| EffectiveCost | Mandatory | Annual subscriptions: = BilledCost; multi-year upfront: amortize across subscription term | Deviation |
| ListCost | Mandatory | Workday list price × user count; not in invoice; requires supplementary pricing data | Deviation |
| ContractedCost | Mandatory | Enterprise-negotiated rate × user count; not accessible via billing system | Deviation |
| BillingAccountId | Mandatory | Workday customer account ID | Present |
| BillingAccountName | Mandatory | Enterprise customer name | Present |
| BillingCurrency | Mandatory | Invoice currency (USD or regional per contract) | Present |
| BillingPeriodStart | Mandatory | Invoice period start date | Present |
| BillingPeriodEnd | Mandatory | Invoice period end date | Present |
| ChargePeriodStart | Mandatory | Subscription period start date | Present |
| ChargePeriodEnd | Mandatory | Subscription period end date | Present |
| ChargeDescription | Mandatory | Workday module name + user tier (e.g., "Workday HCM · 500 Named Users") | Present |
| ChargeCategory | Mandatory | Derive: "Purchase" for all subscription activations and renewals | Deviation |
| ChargeClass | Mandatory (nullable) | null except for correction charges | Present |
| InvoiceIssuerName | Mandatory | "Workday, Inc." | Present |
| ProviderName | Mandatory (dep. v1.3) | "Workday" | Present |
| PublisherName | Mandatory (dep. v1.3) | "Workday" | Present |
| ServiceName | Mandatory | Workday module name: "Workday HCM", "Workday Financial Management", "Workday Planning", etc. | Present |
| ServiceCategory | Mandatory | Derive: "Management and Governance" for all Workday modules | Deviation |
| PricingQuantity | Mandatory | Named user count from invoice | Present |
| PricingUnit | Mandatory | "Named Users" | Present |
| ConsumedQuantity | Conditional | N/A: Workday SaaS subscriptions have no variable consumption metering | N/A |
| ConsumedUnit | Conditional | N/A | N/A |
| ListUnitPrice | Conditional | Workday list price per user per year; not in invoice; requires supplementary data | Missing: Conditional |
| ContractedUnitPrice | Conditional | Enterprise-negotiated rate per user per year; not accessible via billing API | Missing: Conditional |
| PricingCategory | Conditional | "Committed" for all Workday subscriptions (term-based commitments) | Deviation |
| ChargeFrequency | Conditional | "Recurring" for annual invoicing; "One-Time" for multi-year upfront payments | Deviation |
| BillingAccountType | Conditional | Derive from contract tier (e.g., "Enterprise") | Present |
| SubAccountId | Conditional | N/A: Workday billing has no sub-account or business unit hierarchy | N/A |
| SubAccountName | Conditional | N/A | N/A |
| SubAccountType | Conditional | N/A | N/A |
| ResourceId | Conditional | N/A: Workday licenses are not associated with individual resource instances | N/A |
| ResourceName | Conditional | N/A | N/A |
| ResourceType | Conditional | N/A | N/A |
| SkuId | Conditional | Workday module or SKU code from invoice line item | Present |
| Tags | Conditional | N/A: Workday subscription billing does not include resource-level tags | N/A |
| PricingCurrency | Conditional | = BillingCurrency | Present |
| PricingCurrencyListUnitPrice | Conditional | = ListUnitPrice; Missing because ListUnitPrice requires supplementary data | Missing: Conditional |
| PricingCurrencyContractedUnitPrice | Conditional | = ContractedUnitPrice; Missing because enterprise pricing requires supplementary data | Missing: Conditional |
| PricingCurrencyEffectiveCost | Conditional | = EffectiveCost; Deviation because multi-year amortization logic required | Deviation |
| SkuMeter | Conditional | Not applicable; flat per-seat subscription pricing | Missing: Conditional |
| SkuPriceId | Conditional | Not in billing system | Missing: Conditional |
| SkuPriceDetails | Conditional | Not applicable (flat per-user pricing) | Missing: Conditional |
| RegionId | Conditional | N/A: Workday SaaS billing is not region-specific | N/A |
| RegionName | Conditional | N/A | N/A |
| CommitmentDiscountId | Conditional | N/A: Workday subscriptions are term-based licenses, not FOCUS CommitmentDiscount constructs | N/A |
| CommitmentDiscountName | Conditional | N/A | N/A |
| CommitmentDiscountType | Conditional | N/A | N/A |
| CommitmentDiscountCategory | Conditional | N/A | N/A |
| CommitmentDiscountStatus | Conditional | N/A | N/A |
| CommitmentDiscountQuantity | Conditional | N/A | N/A |
| CommitmentDiscountUnit | Conditional | N/A | N/A |
| CapacityReservationId | Conditional | N/A | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | Workday invoice number | Present |
| ServiceSubcategory | Recommended | No native field; map from module: "Human Capital Management", "Financial Management", "Planning" | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: global SaaS platform with no availability zone billing | N/A |

**Tally:** 20 Present, 8 Deviation, 0 Missing Mandatory, 7 Missing Conditional, 1 Missing Recommended, 21 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Invoice framework is complete. Workday invoices expose customer account, module names, user counts, subscription period, and invoice numbers. The 21 N/A columns are legitimately correct for a pure SaaS subscription model.

**Remaining:** ListCost and ContractedCost require supplementary pricing data. Multi-year EffectiveCost amortization requires contract term data. Programmatic invoice access may require PDF parsing if no structured API is available.

### 1.5 Deviations to Fix

**EffectiveCost:** Annual subscriptions: = BilledCost. Multi-year upfront payments: total contract value ÷ number of subscription periods. Document amortization method.

**ListCost and ContractedCost:** Integrate Workday list price book for ListCost. ContractedCost requires the customer's negotiated rate. Both require supplementary data files.

**ChargeCategory:** All Workday charges → "Purchase" for subscription activations and renewals.

**ServiceCategory:** All Workday modules → "Management and Governance".

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (June 4, 2026); certify at FOCUS v1.2.

### 2.2 What Certification Requires

Contact `member-cert@finops.org` for the RFI. The 21 N/A columns must be documented as legitimately not applicable for a SaaS subscription model. This is a supported FOCUS state.

### 2.3 Phased Roadmap

**Phase 0:** Confirm invoice access method (Customer Center export, structured API, or PDF parsing). Pull sample invoices for one or more contract years.

**Phase 1: Core subscription transform.** Map BilledCost, ChargePeriod, BillingAccount, ServiceName (module), SkuId, PricingQuantity (users), PricingUnit, ChargeDescription, InvoiceId. Derive ChargeCategory = "Purchase" and ServiceCategory = "Management and Governance". EffectiveCost = BilledCost for annual contracts.

**Phase 2: Cost enrichment.** Integrate Workday list price book for ListCost. Add contracted rate data for ContractedCost. Implement multi-year EffectiveCost amortization.

**Phase 3: Certify.** Add ServiceSubcategory mapping per module. Drop ProviderName, PublisherName (v1.4). Validate with FOCUS Validator. Submit for certification.

### 2.4 FOCUS Use Cases Workday Customers Unlock

**After Phase 1:** Cost by Workday module. Subscription term tracking via ChargePeriodStart/End. Invoice reconciliation via InvoiceId.

**After Phase 2:** List vs. contracted vs. billed rate comparison. Multi-year contract EffectiveCost amortization for per-period cost allocation.

---

## Part 3: Immediate Next Steps

1. Identify invoice access method: Customer Center export, EDI/API, or structured PDF.
2. Pull sample invoice data covering at least one full subscription year across all active modules.
3. Obtain Workday list price book for ListCost enrichment.
4. Implement Phase 1 transform. Run through FOCUS Validator.
5. Open the RFI with `member-cert@finops.org`.

---

## Confidence Summary

- **High:** Workday invoices expose module names, user counts, subscription period, and invoice numbers. The 20 Present columns are grounded in standard invoice fields.
- **High:** The 21 N/A columns correctly reflect Workday's SaaS subscription model.
- **Moderate:** ServiceCategory mapping. "Management and Governance" covers most Workday modules, but edge cases (Workday Extend, developer tools) may need review.
- **Low:** ListCost and ContractedCost. Workday does not publish list prices; both require supplementary data.
- **Unknown:** Programmatic invoice API access. Workday does not advertise a public billing export API.

---

## Sources

- Workday Customer Center: [community.workday.com](https://community.workday.com)
- Workday Product Documentation: [docs.workday.com](https://docs.workday.com)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
