# ServiceNow & FOCUS: Data Generator Gap Analysis

*Analysis run: June 25, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** ServiceNow  
**Prepared:** June 25, 2026  
**Source:** ServiceNow invoice system; Customer Success Portal  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 20 Present, 8 Deviation, 0 Missing Mandatory, 7 Missing Conditional, 1 Missing Recommended, 21 N/A

---

## Executive Summary

ServiceNow bills through annual enterprise subscriptions: per-named-user licenses for IT Service Management (ITSM), IT Operations Management (ITOM), Strategic Portfolio Management (SPM), HR Service Delivery, and Customer Service Management (CSM). Pricing is entirely enterprise-negotiated; no public list prices exist for enterprise agreements. All 21 Mandatory columns have source data. Twenty-one columns are N/A, correctly reflecting a subscription SaaS model with no resource IDs, no sub-account hierarchy, and no consumption metering. The 8 Deviations cover cost enrichment and enum derivation.

**Recommendation:** Map ServiceNow invoice line items: PricingQuantity = named user count, PricingUnit = "Named Users", ChargeCategory = "Purchase", ServiceCategory = "Management and Governance". Each ServiceNow product module is a separate FOCUS row. Enterprise list prices require supplementary data from the ServiceNow sales system.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

**ServiceNow Customer Success Portal and Invoices**: Enterprise billing managed through invoices and the Customer Success Portal. Key fields: product module name, user count, license period, contract term, total amount. Some enterprise agreements include usage-based components (compute requests, AI credits) as separate line items.

Key characteristics:
- **Per-named-user subscriptions:** ITSM, ITOM, SPM, HRSD, CSM licensed per named user per year.
- **Module-based:** Each ServiceNow application is a separate subscription line item.
- **No public pricing:** ServiceNow does not publish enterprise list prices. List and contracted costs require supplementary data.
- **No sub-account hierarchy:** ServiceNow billing is at the enterprise account level; instance-level allocation requires custom logic.
- **No resource IDs:** SaaS platform; no instance-level resource billing.
- **No regional billing:** Global multi-tenant SaaS (instances may be region-specific but do not produce separate billing records).
- **Usage components:** Some enterprise agreements include AI credits or compute-request-based usage as add-ons.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven. N/A is a valid FOCUS state for columns the billing model genuinely does not produce.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | ServiceNow source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Invoice line item total per product module | Present |
| EffectiveCost | Mandatory | Annual: = BilledCost; multi-year: amortize across term | Deviation |
| ListCost | Mandatory | ServiceNow list price × user count; not published for enterprise | Deviation |
| ContractedCost | Mandatory | Enterprise rate × user count; not in billing system | Deviation |
| BillingAccountId | Mandatory | ServiceNow enterprise account ID | Present |
| BillingAccountName | Mandatory | Customer organization name | Present |
| BillingCurrency | Mandatory | Invoice currency | Present |
| BillingPeriodStart | Mandatory | Invoice period start | Present |
| BillingPeriodEnd | Mandatory | Invoice period end | Present |
| ChargePeriodStart | Mandatory | Subscription period start | Present |
| ChargePeriodEnd | Mandatory | Subscription period end | Present |
| ChargeDescription | Mandatory | Product module + user count (e.g., "ServiceNow ITSM Professional · 500 Named Users") | Present |
| ChargeCategory | Mandatory | Derive: "Purchase" for all subscription charges | Deviation |
| ChargeClass | Mandatory (nullable) | null except for corrections | Present |
| InvoiceIssuerName | Mandatory | "ServiceNow, Inc." | Present |
| ProviderName | Mandatory (dep. v1.3) | "ServiceNow" | Present |
| PublisherName | Mandatory (dep. v1.3) | "ServiceNow" | Present |
| ServiceName | Mandatory | Product module: "ServiceNow ITSM", "ServiceNow ITOM", "ServiceNow SPM", "ServiceNow HRSD" | Present |
| ServiceCategory | Mandatory | Derive: "Management and Governance" for all ITSM/ITOM/SPM; "AI and Machine Learning" for Now Assist AI add-ons | Deviation |
| PricingQuantity | Mandatory | Named user count per module | Present |
| PricingUnit | Mandatory | "Named Users" for all module subscriptions | Deviation |
| ConsumedQuantity | Conditional | N/A: no variable consumption metering for seat licenses | N/A |
| ConsumedUnit | Conditional | N/A | N/A |
| ListUnitPrice | Conditional | Not published for enterprise; requires supplementary data | Missing: Conditional |
| ContractedUnitPrice | Conditional | Enterprise rate; not accessible via billing system | Missing: Conditional |
| PricingCategory | Conditional | "Committed" for all annual/multi-year subscriptions | Deviation |
| ChargeFrequency | Conditional | "Recurring" for annual subscriptions | Deviation |
| BillingAccountType | Conditional | "Enterprise" | Present |
| SubAccountId | Conditional | N/A: no sub-account billing hierarchy | N/A |
| SubAccountName | Conditional | N/A | N/A |
| SubAccountType | Conditional | N/A | N/A |
| ResourceId | Conditional | N/A: SaaS platform | N/A |
| ResourceName | Conditional | N/A | N/A |
| ResourceType | Conditional | N/A | N/A |
| SkuId | Conditional | ServiceNow product SKU from invoice | Present |
| Tags | Conditional | N/A: no resource-level tags in subscription billing | N/A |
| PricingCurrency | Conditional | = BillingCurrency | Present |
| PricingCurrencyListUnitPrice | Conditional | Missing: requires supplementary data | Missing: Conditional |
| PricingCurrencyContractedUnitPrice | Conditional | Missing: enterprise pricing not in billing system | Missing: Conditional |
| PricingCurrencyEffectiveCost | Conditional | = EffectiveCost; Deviation for multi-year amortization | Deviation |
| SkuMeter | Conditional | Not applicable for flat user subscriptions | Missing: Conditional |
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
| InvoiceId | Recommended | ServiceNow invoice number | Present |
| ServiceSubcategory | Recommended | Map from module: "IT Service Management", "IT Operations Management", "HR Service Delivery", "Customer Service" | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: global SaaS | N/A |

**Tally:** 20 Present, 8 Deviation, 0 Missing Mandatory, 7 Missing Conditional, 1 Missing Recommended, 21 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Invoice fields for module names, user counts, subscription period. All 21 Mandatory columns have source data. The 21 N/A columns correctly reflect the SaaS subscription model.

**Remaining:** List and contracted pricing require supplementary data. SkuMeter, SkuPriceId absent.

### 1.5 Deviations to Fix

**ChargeCategory:** "Purchase" for all subscription and AI credit charges. "Credit" for refunds.

**PricingUnit:** "Named Users" for module subscriptions. "AI Credits" for Now Assist usage add-ons.

**ServiceCategory:** "Management and Governance" for ITSM/ITOM/SPM/HRSD/CSM. "AI and Machine Learning" for Now Assist AI add-ons.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (June 4, 2026); certify at FOCUS v1.2.

### 2.2 What Certification Requires

Contact `member-cert@finops.org` for the RFI. Document N/A columns as legitimately not applicable for SaaS subscription model.

### 2.3 Phased Roadmap

**Phase 0:** Confirm Customer Success Portal invoice export access. Pull sample invoices across all active modules.

**Phase 1: Core ITSM/ITOM transform.** Map module subscription rows. Derive ChargeCategory, ServiceCategory, PricingUnit = "Named Users".

**Phase 2: AI and usage add-ons.** Add Now Assist AI credit rows with PricingUnit = "AI Credits" and ChargeFrequency = "Usage-Based".

**Phase 3: Certify.** Add ServiceSubcategory. Drop ProviderName, PublisherName (v1.4). Validate and certify.

---

## Part 3: Immediate Next Steps

1. Confirm ServiceNow Customer Success Portal invoice export or API access.
2. Pull sample invoices across all active ServiceNow modules.
3. Implement Phase 1 ITSM subscription transform and run through FOCUS Validator.
4. Open the RFI with `member-cert@finops.org`.

---

## Confidence Summary

- **High:** ServiceNow invoices expose module names, user counts, and subscription period. All 21 N/A columns correctly reflect the SaaS model.
- **Moderate:** ServiceCategory mapping. "Management and Governance" is correct for ITSM; confirm for Now Assist AI rows.
- **Low:** ListCost and ContractedCost. ServiceNow does not publish enterprise list prices.

---

## Sources

- ServiceNow Customer Success Portal: [support.servicenow.com](https://support.servicenow.com)
- ServiceNow Product Documentation: [docs.servicenow.com](https://docs.servicenow.com)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
