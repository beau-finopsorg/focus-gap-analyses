# Nutanix & FOCUS: Data Generator Gap Analysis

*Analysis run: June 25, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** Nutanix  
**Prepared:** June 25, 2026  
**Source:** Nutanix invoice system; Nutanix Customer Portal  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 20 Present, 8 Deviation, 0 Missing Mandatory, 7 Missing Conditional, 1 Missing Recommended, 21 N/A

---

## Executive Summary

Nutanix is primarily a software subscription vendor. Its billing model is term-based license subscriptions billed annually or multi-year, based on node count, capacity (TiB), or Nutanix Consumption Units (NCUs). This model limits FOCUS applicability: 21 columns are legitimately N/A because software licenses have no resource-level IDs, no sub-account hierarchy, no regional breakout, and no consumption metering. All 21 Mandatory columns have source data. The 8 Deviations cover cost enrichment (list and contracted pricing, multi-year amortization) and enum derivation. Seven Missing Conditional columns are in the SKU price catalog and unit price families.

**Recommendation:** The short path to conformance is mapping the 20 Present columns into FOCUS shape and addressing the 8 Deviations. The resulting dataset will have 21 null Conditional/Recommended columns (all legitimately N/A for a pure software subscription). Document those nulls in the conformance gap report as N/A, not as gaps.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

**Nutanix Customer Portal / Invoice API**: Nutanix does not publish a public billing API with full programmatic access. Billing data is available through the Nutanix Customer Portal (my.nutanix.com), which provides invoice history, license entitlements, and subscription details. Key fields: invoice number, billing period, line items (product name, quantity, unit, list price, contracted price, total), customer information.

**Nutanix License Manager**: License entitlements are tracked in the Nutanix License Manager, which provides SKU, term, node/TiB/NCU quantities, and expiration dates.

Key characteristics for FOCUS:
- **Term-based subscriptions:** Nutanix licenses are sold as 1, 3, or 5-year subscriptions. Annual invoicing is the norm; multi-year contracts may be invoiced upfront or annually.
- **License units:** The billing unit varies by product: nodes (for cluster-based licensing), TiB (for storage-based licensing), or NCUs (Nutanix Consumption Units, a normalized unit for some products). These map to PricingQuantity and PricingUnit.
- **No consumption metering:** Nutanix software does not generate per-transaction or per-resource billing data. There is no equivalent to cloud API call counts or storage byte-hours.
- **Enterprise pricing:** Nutanix pricing is entirely enterprise-negotiated. MSRP (list prices) exists in Nutanix's price book but is not accessible via a programmatic API.
- **No sub-account hierarchy:** Nutanix customer accounts are flat; there is no sub-account or project hierarchy in the billing system.
- **No resource-level IDs:** Nutanix licenses are associated with a cluster or site, not with individual virtual machines, volumes, or other cloud-native resource types.
- **Regions:** Nutanix on-premises software licenses are not region-specific in the billing context. Nutanix Cloud Clusters (NC2) runs on AWS/Azure; the underlying cloud charges flow through the cloud provider, not through Nutanix's billing.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven. Each column carries a feature level: Mandatory (must exist and be populated where applicable), Conditional (must exist; populated when the provider's model triggers the condition, otherwise null), or Recommended. Columns are N/A when the provider's billing model genuinely does not produce the data (e.g., a software subscription vendor has no resource-level IDs). N/A is a valid FOCUS state, not a gap.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | Nutanix source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Invoice line item total (subscription period amount) | Present |
| EffectiveCost | Mandatory | Multi-year pre-paid contracts require amortization of upfront payment across billing periods; annual subscriptions: = BilledCost | Deviation |
| ListCost | Mandatory | Nutanix MSRP × PricingQuantity; MSRP exists in price book but not accessible via API; requires supplementary price book data | Deviation |
| ContractedCost | Mandatory | Enterprise-negotiated rate × PricingQuantity; not accessible via billing API | Deviation |
| BillingAccountId | Mandatory | Nutanix customer account ID from Customer Portal | Present |
| BillingAccountName | Mandatory | Customer company name | Present |
| BillingCurrency | Mandatory | Invoice currency (USD, EUR, or regional per contract) | Present |
| BillingPeriodStart | Mandatory | Invoice period start date | Present |
| BillingPeriodEnd | Mandatory | Invoice period end date | Present |
| ChargePeriodStart | Mandatory | Subscription period start date | Present |
| ChargePeriodEnd | Mandatory | Subscription period end date | Present |
| ChargeDescription | Mandatory | Product name + SKU description (e.g., "Nutanix Cloud Infrastructure Ultimate - 3 Nodes") | Present |
| ChargeCategory | Mandatory | Derive: "Purchase" for new subscription activations; "Recurring" maps to "Usage" in FOCUS? No - use "Purchase" for subscription renewals. Subscriptions are "Purchase" in FOCUS. | Deviation |
| ChargeClass | Mandatory (nullable) | null except for correction charges | Present |
| InvoiceIssuerName | Mandatory | "Nutanix, Inc." | Present |
| ProviderName | Mandatory (dep. v1.3) | "Nutanix" | Present |
| PublisherName | Mandatory (dep. v1.3) | "Nutanix" | Present |
| ServiceName | Mandatory | Nutanix product name (e.g., "Nutanix Cloud Infrastructure", "Nutanix Unified Storage", "Nutanix Data Services") | Present |
| ServiceCategory | Mandatory | Map Nutanix products: NCI, NCP → "Compute"; Nutanix Unified Storage → "Storage"; Nutanix Flow → "Networking"; Nutanix Era/Data Services → "Databases" | Deviation |
| PricingQuantity | Mandatory | License quantity: number of nodes, TiB of capacity, or NCU count from invoice | Present |
| PricingUnit | Mandatory | License unit: "Nodes", "TiB", or "NCU" per product | Present |
| ConsumedQuantity | Conditional | N/A: Nutanix software subscriptions have no variable consumption metering; quantity is fixed at subscription time | N/A |
| ConsumedUnit | Conditional | N/A | N/A |
| ListUnitPrice | Conditional | Nutanix MSRP per license unit; not exposed via billing API | Missing: Conditional |
| ContractedUnitPrice | Conditional | Enterprise-negotiated rate per license unit; not accessible via billing API | Missing: Conditional |
| PricingCategory | Conditional | "Committed" for all Nutanix subscriptions (term-based commitments) | Deviation |
| ChargeFrequency | Conditional | "Recurring" for annual subscription renewals; "One-Time" for multi-year upfront payments | Deviation |
| BillingAccountType | Conditional | Derive from Nutanix customer tier (e.g., "Enterprise") | Present |
| SubAccountId | Conditional | N/A: Nutanix billing has no sub-account or project hierarchy | N/A |
| SubAccountName | Conditional | N/A | N/A |
| SubAccountType | Conditional | N/A | N/A |
| ResourceId | Conditional | N/A: Nutanix licenses are associated with a cluster or site, not with individual resource instances | N/A |
| ResourceName | Conditional | N/A | N/A |
| ResourceType | Conditional | N/A | N/A |
| SkuId | Conditional | Nutanix part number (e.g., "SW-NCI-ULT-3N-1Y") from invoice or License Manager | Present |
| Tags | Conditional | N/A: Nutanix software license billing data does not include resource-level tags | N/A |
| PricingCurrency | Conditional | = BillingCurrency | Present |
| PricingCurrencyListUnitPrice | Conditional | = ListUnitPrice; Missing because ListUnitPrice requires supplementary data | Missing: Conditional |
| PricingCurrencyContractedUnitPrice | Conditional | = ContractedUnitPrice; Missing because ContractedUnitPrice requires enterprise pricing data | Missing: Conditional |
| PricingCurrencyEffectiveCost | Conditional | = EffectiveCost; Deviation because multi-year amortization logic is required | Deviation |
| SkuMeter | Conditional | Not exposed; Nutanix licenses do not have a metered dimension separate from the license SKU | Missing: Conditional |
| SkuPriceId | Conditional | Price book rate identifier not exposed in billing API | Missing: Conditional |
| SkuPriceDetails | Conditional | Not applicable (flat per-unit pricing; no tiering in the standard Nutanix model) | Missing: Conditional |
| RegionId | Conditional | N/A: Nutanix on-premises licenses are not region-specific in billing; NC2 infrastructure charges flow through the cloud provider | N/A |
| RegionName | Conditional | N/A | N/A |
| CommitmentDiscountId | Conditional | N/A: Nutanix subscriptions are term-based licenses, not FOCUS CommitmentDiscount constructs | N/A |
| CommitmentDiscountName | Conditional | N/A | N/A |
| CommitmentDiscountType | Conditional | N/A | N/A |
| CommitmentDiscountCategory | Conditional | N/A | N/A |
| CommitmentDiscountStatus | Conditional | N/A | N/A |
| CommitmentDiscountQuantity | Conditional | N/A | N/A |
| CommitmentDiscountUnit | Conditional | N/A | N/A |
| CapacityReservationId | Conditional | N/A | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | Nutanix invoice number from Customer Portal | Present |
| ServiceSubcategory | Recommended | No native field; requires mapping from product name to subcategory | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: on-premises software licenses have no availability zone | N/A |

**Tally:** 20 Present, 8 Deviation, 0 Missing Mandatory, 7 Missing Conditional, 1 Missing Recommended, 21 N/A

### 1.4 What Is Solved, and What Remains

**Solved**

The invoicing framework is complete. Nutanix invoices expose account identification, billing dates, subscription period, product names, license quantities, units, and invoice numbers. These give 20 directly Present columns. The 21 N/A columns reflect Nutanix's billing model correctly: a software subscription vendor genuinely does not have resource IDs, sub-accounts, or consumption metering at the billing level.

**Remaining**

The main work is cost enrichment. Neither the MSRP nor the contracted rate is in the billing API. Both require supplementary price book data or a Nutanix pricing API that does not currently exist. Multi-year contract EffectiveCost amortization requires logic to spread upfront payments across the subscription term. ChargeCategory and ServiceCategory require mapping tables built from Nutanix product type codes.

### 1.5 Deviations to Fix

**EffectiveCost**  
Annual subscriptions: EffectiveCost = BilledCost. Multi-year upfront payments: amortize the total contract value across the term. Per-period EffectiveCost = total contract value ÷ number of periods. Document the amortization method in the native-to-FOCUS mapping.

**ListCost and ContractedCost**  
Integrate Nutanix's MSRP price book for ListCost. ContractedCost requires the customer's negotiated rate. Both require supplementary data files until Nutanix publishes a programmatic pricing API.

**ChargeCategory**  
All Nutanix charges are subscription-based. Use "Purchase" for subscription activations and renewals. Use "Credit" for any promotional credits or adjustments. Avoid "Usage" (Nutanix subscriptions are not usage-based).

**ServiceCategory**  
Map Nutanix product lines to FOCUS ServiceCategory: NCI (hyperconverged compute) → "Compute"; Nutanix Unified Storage, Objects → "Storage"; Nutanix Flow → "Networking"; Nutanix Era, Data Services → "Databases"; Nutanix Prism (management) → "Management and Governance".

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (June 4, 2026); certify at FOCUS v1.2. ProviderName and PublisherName are deprecated in v1.3 and removed in v1.4.

### 2.2 What Certification Requires

Contact `member-cert@finops.org` for the RFI. The 21 N/A columns must be documented as legitimately not applicable for a software subscription billing model. This is a supported FOCUS state. Certification requires documenting the null justification for each N/A column.

### 2.3 Phased Roadmap

**Phase 0:** Confirm Customer Portal or invoice API access. Pull a sample invoice and license entitlement dataset. Identify available fields per line item.

**Phase 1: Core subscription transform.** Map BilledCost, ChargePeriod, BillingAccount, ServiceName, SkuId, PricingQuantity/Unit, ChargeDescription, InvoiceId, ChargeClass, InvoiceIssuerName. Derive ChargeCategory = "Purchase" and ServiceCategory from product name. EffectiveCost = BilledCost for annual subscriptions. Delivers conformant output for 20 Present columns.

**Phase 2: Cost enrichment.** Integrate Nutanix price book for ListCost and ListUnitPrice. Add contracted rate file for ContractedCost. Implement multi-year EffectiveCost amortization. Add PricingCategory = "Committed" for all subscription rows.

**Phase 3: Certify.** Add ServiceSubcategory mapping. Drop ProviderName, PublisherName (v1.4). Validate with FOCUS Validator. Submit for certification.

### 2.4 FOCUS Use Cases Nutanix Customers Unlock

**After Phase 1:** Cost by Nutanix product and subscription. Invoice reconciliation via InvoiceId. Subscription term tracking via ChargePeriodStart/End.

**After Phase 2:** List vs. contracted vs. billed cost comparison to verify enterprise discount application. Multi-year contract cost allocation using amortized EffectiveCost.

**Out of scope:** Resource-level cost allocation (N/A for software subscriptions). Regional cost analysis. CommitmentDiscount and CapacityReservation use cases.

---

## Part 3: Immediate Next Steps

1. Identify the programmatic access method for Nutanix invoice and license data: Customer Portal export, invoice API (if available), or automated PDF/CSV invoice processing.
2. Obtain the current Nutanix MSRP price book and map each SKU to a list unit price per license unit.
3. Build the ServiceCategory and ChargeCategory mapping tables from Nutanix product names and part numbers.
4. Implement the Phase 1 core subscription transform for annual contracts. Run through the FOCUS Validator.
5. Design the multi-year EffectiveCost amortization logic. Open the RFI with `member-cert@finops.org`.

---

## Confidence Summary

- **High:** Nutanix invoices expose product name, license quantity, unit, and billing period for all subscription line items. The 20 Present columns are grounded in standard invoice fields.
- **High:** The 21 N/A columns correctly reflect Nutanix's software subscription model. A software license billing system genuinely does not have resource IDs, sub-accounts, or regional breakouts.
- **Moderate:** ServiceCategory and ChargeCategory mapping. Nutanix's product portfolio has expanded significantly with Data Services, Era, and NC2. A comprehensive mapping requires reviewing all current Nutanix SKUs.
- **Low:** ListCost and ContractedCost from the Nutanix price book. The price book is typically a static document. Automated integration requires either Nutanix publishing a pricing API or a manual ETL process per customer.
- **Unknown:** Programmatic invoice API access. Nutanix does not advertise a public invoice API. If invoice data is only available as PDF downloads from the Customer Portal, automated ingestion requires PDF parsing or a manual export step.

---

## Sources

- Nutanix Customer Portal: [my.nutanix.com](https://my.nutanix.com)
- Nutanix License Manager: [Nutanix Licensing Documentation](https://portal.nutanix.com/page/documents/details?targetId=Nutanix-License-Manager-Guide:lic-license-manager-guide-intro-c.html)
- Nutanix NC2 Documentation: [Nutanix Cloud Clusters](https://www.nutanix.com/products/cloud-clusters)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
