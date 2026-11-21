# VMware & FOCUS: Data Generator Gap Analysis

*Analysis run: June 25, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** VMware (Broadcom)  
**Prepared:** June 25, 2026  
**Source:** Broadcom/VMware invoice system; My VMware portal; VMware vCloud API  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 19 Present, 8 Deviation, 0 Missing Mandatory, 8 Missing Conditional, 1 Missing Recommended, 21 N/A

---

## Executive Summary

VMware, now a Broadcom subsidiary, bills through enterprise subscription licenses for vSphere, vSAN, NSX, vCenter, Horizon, and VMware Cloud Foundation (VCF). Since Broadcom's acquisition in 2023, pricing has shifted to mandatory VCF bundles billed per core. All pricing is enterprise-negotiated. Cloud-hosted VMware (VMware Cloud on AWS, Azure VMware Solution) is billed through the respective hyperscaler and is out of scope here. All 21 Mandatory columns have source data from VMware invoices. Twenty-one columns are N/A: no resource IDs, no sub-account hierarchy, no consumption metering, and no CommitmentDiscount constructs. The 8 Deviations cover cost enrichment and enum derivation.

**Recommendation:** Map VMware VCF or individual product subscription invoice fields: PricingQuantity = core count or socket count, PricingUnit = "Cores" or "Sockets", ChargeCategory = "Purchase", ServiceCategory = "Management and Governance". All pricing requires supplementary data from the Broadcom contract system.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

**Broadcom/VMware Invoice and My VMware Portal**: Enterprise billing managed through invoices and the My VMware/Broadcom portal. Key fields: product name (vSphere, vSAN, NSX, VCF), license quantity (cores or sockets), license period, support tier, total amount.

Key characteristics:
- **Core/socket-based subscriptions:** Post-acquisition, VMware Cloud Foundation is billed per core. Legacy products (vSphere, vSAN, NSX) were per-socket or per-VM.
- **Enterprise pricing only:** All VMware/Broadcom enterprise pricing is negotiated. No public list prices exist for enterprise agreements.
- **No sub-account hierarchy:** VMware billing is at the enterprise account level. vCenter server groups and clusters do not appear in billing records.
- **No resource IDs:** License billing has no resource instance IDs.
- **No regional billing:** Licenses are global; no per-region billing rows.
- **No metered consumption:** Unlike AWS or Azure, VMware licenses are not billed by actual utilization.
- **Support and subscription:** Software subscription and support (SnS) appears as separate line items.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven. VMware subscription licenses follow the same pattern as Workday or ServiceNow: SaaS/software subscription with no metered components, no resource IDs, and no CommitmentDiscount constructs.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | VMware source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Invoice line item total per product | Present |
| EffectiveCost | Mandatory | Annual: = BilledCost; multi-year: amortize across term | Deviation |
| ListCost | Mandatory | VMware list price × quantity; not published for enterprise | Deviation |
| ContractedCost | Mandatory | Enterprise contract rate × quantity; not in billing system | Deviation |
| BillingAccountId | Mandatory | Broadcom enterprise account ID | Present |
| BillingAccountName | Mandatory | Customer organization name | Present |
| BillingCurrency | Mandatory | Invoice currency | Present |
| BillingPeriodStart | Mandatory | Invoice period start | Present |
| BillingPeriodEnd | Mandatory | Invoice period end | Present |
| ChargePeriodStart | Mandatory | Subscription period start | Present |
| ChargePeriodEnd | Mandatory | Subscription period end | Present |
| ChargeDescription | Mandatory | Product name + quantity (e.g., "VMware Cloud Foundation · 500 Cores") | Present |
| ChargeCategory | Mandatory | Derive: "Purchase" for all subscription charges | Deviation |
| ChargeClass | Mandatory (nullable) | null except for corrections | Present |
| InvoiceIssuerName | Mandatory | "Broadcom Inc." | Present |
| ProviderName | Mandatory (dep. v1.3) | "VMware" | Present |
| PublisherName | Mandatory (dep. v1.3) | "Broadcom" | Present |
| ServiceName | Mandatory | Product name: "VMware Cloud Foundation", "VMware vSphere", "VMware vSAN", "VMware NSX", "VMware Horizon" | Present |
| ServiceCategory | Mandatory | Derive: "Management and Governance" for virtualization platform; "Compute" for vSphere compute | Deviation |
| PricingQuantity | Mandatory | Core count or socket count | Present |
| PricingUnit | Mandatory | "Cores" (VCF and post-acquisition products); "Sockets" (legacy vSphere) | Deviation |
| ConsumedQuantity | Conditional | N/A: no variable consumption metering | N/A |
| ConsumedUnit | Conditional | N/A | N/A |
| ListUnitPrice | Conditional | Not published for enterprise; requires supplementary data | Missing: Conditional |
| ContractedUnitPrice | Conditional | Enterprise rate; not accessible via billing system | Missing: Conditional |
| PricingCategory | Conditional | "Committed" for all term subscriptions | Deviation |
| ChargeFrequency | Conditional | "Recurring" | Deviation |
| BillingAccountType | Conditional | "Enterprise" | Present |
| SubAccountId | Conditional | N/A: no sub-account billing hierarchy | N/A |
| SubAccountName | Conditional | N/A | N/A |
| SubAccountType | Conditional | N/A | N/A |
| ResourceId | Conditional | N/A: license billing has no resource instance IDs | N/A |
| ResourceName | Conditional | N/A | N/A |
| ResourceType | Conditional | N/A | N/A |
| SkuId | Conditional | VMware product SKU from invoice | Present |
| Tags | Conditional | N/A: no resource-level tags in subscription billing | N/A |
| PricingCurrency | Conditional | = BillingCurrency | Present |
| PricingCurrencyListUnitPrice | Conditional | Missing: requires supplementary data | Missing: Conditional |
| PricingCurrencyContractedUnitPrice | Conditional | Missing: enterprise pricing not in billing system | Missing: Conditional |
| PricingCurrencyEffectiveCost | Conditional | = EffectiveCost; Deviation for multi-year | Deviation |
| SkuMeter | Conditional | Not applicable for flat core subscriptions | Missing: Conditional |
| SkuPriceId | Conditional | Not in billing system | Missing: Conditional |
| SkuPriceDetails | Conditional | Not applicable | Missing: Conditional |
| RegionId | Conditional | N/A: global software licenses | N/A |
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
| ServiceSubcategory | Recommended | Map from product: "Server Virtualization", "Software-Defined Networking", "HCI Storage", "Virtual Desktop" | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: global software licenses | N/A |

**Tally:** 19 Present, 8 Deviation, 0 Missing Mandatory, 8 Missing Conditional, 1 Missing Recommended, 21 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Invoice fields for product names, core/socket counts, subscription period, invoice number. All 21 Mandatory columns have source data. The 21 N/A columns correctly reflect on-premises software license billing.

**Remaining:** All pricing data requires supplementary sources. Eight Missing: Conditional columns require pricing catalog data not available from invoices.

### 1.5 Deviations to Fix

**PricingUnit:** "Cores" for VCF and post-acquisition bundles; "Sockets" for legacy vSphere licenses.

**ChargeCategory:** "Purchase" for all subscription and support charges. "Credit" for credits/adjustments.

**ServiceCategory:** "Management and Governance" for VCF and vCenter; "Compute" for vSphere standalone; "Networking" for NSX.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (June 4, 2026); certify at FOCUS v1.2.

### 2.2 What Certification Requires

Contact `member-cert@finops.org` for the RFI. Document 21 N/A columns as legitimately not applicable for on-premises software license billing.

### 2.3 Phased Roadmap

**Phase 0:** Confirm Broadcom portal invoice export access. Pull sample invoices across all VMware products.

**Phase 1: VCF core subscription transform.** Map VCF rows. Derive ChargeCategory, ServiceCategory, PricingUnit = "Cores".

**Phase 2: Legacy product rows.** Add vSphere, vSAN, NSX, Horizon rows with appropriate PricingUnit.

**Phase 3: Certify.** Add ServiceSubcategory. Drop ProviderName, PublisherName (v1.4). Validate and certify.

---

## Part 3: Immediate Next Steps

1. Confirm Broadcom portal invoice export access.
2. Pull sample invoices covering VCF and legacy VMware products.
3. Implement Phase 1 VCF transform and run through FOCUS Validator.
4. Open the RFI with `member-cert@finops.org`.

---

## Confidence Summary

- **High:** VMware invoices expose product names and core/socket counts. The 21 N/A columns correctly reflect the license model.
- **Moderate:** ServiceCategory split across product families. VCF as "Management and Governance" vs. "Compute" is non-obvious; confirm with FinOps community.
- **Low:** All pricing data. Broadcom does not publish enterprise list prices.

---

## Sources

- Broadcom/VMware Licensing: [broadcom.com/support/licensing](https://www.broadcom.com/support/licensing)
- My VMware Portal: [my.vmware.com](https://my.vmware.com)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
