# Microsoft 365 (including Copilot) and FOCUS: Data Generator Gap Analysis

*Analysis run: June 30, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

Prepared: June 30, 2026
Subject: Microsoft 365 commerce billing (subscriptions and licenses, including the Copilot per-user license) and metered Copilot consumption (Copilot Credits, pay-as-you-go)
Baseline: FOCUS v1.2. Build target: v1.4 (latest ratified).
Feature levels verified against the FOCUS v1.2 specification; spec confirmed current (v1.4 latest) on 2026-06-30.

## Executive summary

Microsoft 365 including Copilot is not one billing surface, it is two, and they sit at very different points of FOCUS readiness. Any single verdict that ignores the split is misleading.

The metered Copilot consumption (Copilot Credits, billed pay-as-you-go through an Azure subscription) rides Azure's billing pipeline, and Azure Cost Management already produces a FOCUS export. That slice is close to conformant today, because Microsoft is an established FOCUS data generator on the Azure side.

The core of M365 spend, the per-seat subscriptions and the Copilot per-user license, bills through the Microsoft 365 commerce surface (the admin center invoices, the Microsoft Customer Agreement, and CSP reconciliation files). That surface is invoice and subscription-term level: it has the cost and account substance but no FOCUS shaping, no daily granularity, and no resource or tag attribution. On its own it sits in the same Emerging band as other enterprise SaaS and license vendors.

So the recommendation is bifurcated. For metered Copilot, surface it through the existing Azure FOCUS export and confirm the Copilot meters carry through cleanly. For the seat-license surface, the work is the familiar one for SaaS billers: a transform to FOCUS shape, a service-category mapping, and a decision on how to represent subscription terms as charge periods. Treat the two as separate datasets that a customer joins, rather than pretending one conformant feed exists.

## Part 1: The conformance gap

### 1.1 The two data sources

Surface A, M365 commerce billing (the analyzed subject). Per-seat subscriptions (Microsoft 365 E3/E5 and similar) and the Microsoft 365 Copilot per-user license bill here. The data is reachable as: admin center invoices (PDF), the Microsoft Customer Agreement invoice with its billing summary of charges, credits, taxes, and totals plus a transaction list, and, for partner-sold tenants, the CSP reconciliation file (structured line items with product, SKU, quantity, unit price, term dates, and charge type). Granularity is monthly, at the subscription and SKU level. There are no per-resource lines, no usage tags, and no daily breakdown.

Surface B, metered Copilot consumption. Copilot Credits (priced at $0.01 per credit), Copilot Cowork (general availability June 16, 2026), and Copilot Studio agent actions bill either pay-as-you-go through a linked Azure subscription using Azure meters, or against prepaid capacity packs. Because the pay-as-you-go path uses Azure meters, the consumption appears in Azure Cost Management, which produces a FOCUS export. This surface is daily, meter-level, and already FOCUS-shaped through Azure.

Two scope items to confirm with Microsoft: whether the Copilot meters in the Azure FOCUS export carry a service taxonomy and resource detail specific enough to identify Copilot usage (versus generic Azure consumption), and whether prepaid Copilot capacity packs appear as a purchase line that reconciles against drawdown.

### 1.2 How conformance is judged

FOCUS conformance is column-driven. Each column carries a feature level: Mandatory (must exist and be populated where applicable), Conditional (must exist; populated when the provider's model triggers the condition, otherwise null), or Recommended. A conformant dataset presents the full column set under FOCUS column IDs, populates every Mandatory column, satisfies Conditional columns where applicable, and uses the correct types and allowed values. These rules live in the FOCUS Requirements Model, which the FOCUS Validator checks against.

### 1.3 Column-by-column status (M365 commerce surface, all 57 FOCUS v1.2 columns)

This table assesses Surface A, the commerce billing. Surface B (metered Copilot via Azure) is covered by Azure's existing FOCUS export and is summarized in 1.4 rather than re-derived here. "Present" means the data exists and maps (a transform or rename), not that a conformant column ships today.

Status: Present (maps directly or by trivial derivation); Deviation (present but needs shaping, an enum mapping, or a pricing-source clarification); Missing: Conditional; Missing: Recommended; N/A: null valid.

| FOCUS Column | Level (1.2) | M365 commerce source | Status |
| --- | --- | --- | --- |
| BilledCost | Mandatory | invoice line net amount | Present |
| EffectiveCost | Mandatory | = billed (no amortization) | Present |
| ListCost | Mandatory | price sheet or recon unit price x qty | Deviation |
| ContractedCost | Mandatory | negotiated/EA rate x qty | Deviation |
| BillingAccountId | Mandatory | billing account / billing profile | Present |
| BillingAccountName | Mandatory | billing account name | Present |
| BillingCurrency | Mandatory | invoice currency | Present |
| BillingPeriodStart | Mandatory | invoice billing period | Present |
| BillingPeriodEnd | Mandatory | invoice billing period | Present |
| ChargePeriodStart | Mandatory | subscription term start | Present |
| ChargePeriodEnd | Mandatory | subscription term end | Present |
| ChargeDescription | Mandatory | product + SKU description | Present |
| ChargeCategory | Mandatory | derive (Purchase / Usage / Tax) | Deviation |
| ChargeClass | Mandatory (nullable) | null except corrections | Present |
| InvoiceIssuerName | Mandatory | constant "Microsoft" | Present |
| ProviderName | Mandatory (dep. 1.3) | constant "Microsoft" | Present |
| PublisherName | Mandatory (dep. 1.3) | "Microsoft" (or Marketplace ISV) | Present |
| ServiceName | Mandatory | product (e.g., Microsoft 365 E5, Copilot) | Present |
| ServiceCategory | Mandatory | map product to FOCUS enum | Deviation |
| PricingQuantity | Mandatory | seats (or credits) | Present |
| PricingUnit | Mandatory | license-month (or credit) | Present |
| ConsumedQuantity | Conditional | seats / credits | Present |
| ConsumedUnit | Conditional | license-month / credit | Present |
| ListUnitPrice | Conditional | price sheet | Deviation |
| ContractedUnitPrice | Conditional | price sheet | Deviation |
| PricingCategory | Conditional | Standard or Committed (annual term) | Present |
| BillingAccountType | Conditional (1.2) | derive | Present |
| SubAccountId | Conditional | MCA invoice section / CSP customer | Present |
| SubAccountName | Conditional | invoice section / customer name | Present |
| SubAccountType | Conditional (1.2) | derive | Present |
| SkuId | Conditional | product SKU / part number | Present |
| InvoiceId | Recommended | invoice number | Present |
| ChargeFrequency | Recommended | derive (Recurring / Usage-Based / One-Time) | Present |
| PricingCurrency | Conditional (1.2) | = BillingCurrency | Present |
| PricingCurrencyListUnitPrice | Conditional (1.2) | = ListUnitPrice | Present |
| PricingCurrencyContractedUnitPrice | Conditional (1.2) | = ContractedUnitPrice | Present |
| PricingCurrencyEffectiveCost | Conditional (1.2) | = EffectiveCost | Present |
| ResourceId | Conditional | no resource lines (seat licenses) | Missing: Conditional |
| ResourceName | Conditional | not present | Missing: Conditional |
| ResourceType | Conditional | not present | Missing: Conditional |
| Tags | Conditional | no usage tags (MCA cost center only) | Missing: Conditional |
| SkuPriceId | Conditional | not exposed on commerce surface | Missing: Conditional |
| SkuMeter | Conditional (1.1+) | not exposed | Missing: Conditional |
| SkuPriceDetails | Conditional (1.1+) | not exposed | Missing: Conditional |
| ServiceSubcategory | Recommended | map product / SKU | Missing: Recommended |
| AvailabilityZone | Recommended | global SaaS, no zone | N/A |
| RegionId | Conditional | global SaaS, no billed region | N/A |
| RegionName | Conditional | global SaaS, no billed region | N/A |
| CommitmentDiscountId | Conditional | annual term is not a FOCUS commitment discount | N/A |
| CommitmentDiscountName | Conditional | N/A | N/A |
| CommitmentDiscountType | Conditional | N/A | N/A |
| CommitmentDiscountCategory | Conditional | N/A | N/A |
| CommitmentDiscountStatus | Conditional | N/A | N/A |
| CommitmentDiscountQuantity | Conditional (1.1+) | N/A | N/A |
| CommitmentDiscountUnit | Conditional (1.1+) | N/A | N/A |
| CapacityReservationId | Conditional (1.1+) | N/A | N/A |
| CapacityReservationStatus | Conditional (1.1+) | N/A | N/A |

Tally (commerce surface): 31 Present, 6 Deviation, 7 Missing Conditional, 1 Missing Recommended, 12 N/A. All 21 Mandatory columns have a source; six need shaping or a pricing-source clarification. There are no missing-Mandatory data gaps, but the data is monthly and subscription-grained, with no resource or tag attribution.

### 1.4 What's solved, and what remains

Surface B is largely solved already. Metered Copilot consumption bills through Azure meters, and Azure Cost Management produces a FOCUS export, so daily, cost-complete, FOCUS-shaped data exists for that slice today. The open question is fidelity, whether the Copilot meters are identifiable and carry enough service and resource detail in the Azure export, not whether the pipeline exists.

Surface A has the substance but not the shape. Like other SaaS billers, the commerce invoice and CSP reconciliation carry billed cost, account, period, product, SKU, and quantity, so all 21 Mandatory columns are sourceable. What is missing is structural: monthly and subscription-term granularity rather than daily, no resource-level lines, and no usage tags. The remaining work is a FOCUS-shaping transform, a product-to-ServiceCategory mapping, and a pricing-source decision (below).

### 1.5 Deviations and clarifications to fix

ListCost and ContractedCost (and their unit prices). The net charge is on the invoice, but list and negotiated unit prices live on the price sheet or in the CSP reconciliation, not always on the customer-facing invoice. Decide the authoritative price source and populate ListCost versus ContractedCost accordingly rather than mapping both to the invoiced amount.

ChargeCategory and ServiceCategory. Both must carry valid FOCUS enum values. ChargeCategory: per-seat licenses map to Purchase, metered credits to Usage, taxes to Tax. ServiceCategory: build a product map (Microsoft 365 productivity to a productivity or "Other" category, Copilot to AI and Machine Learning).

Tags and cost centers. The commerce billing has no usage tags, but the Microsoft Customer Agreement carries a cost center on invoice sections. Decide whether to surface that as FOCUS Tags (key-value) or as SubAccount, and apply it consistently.

Charge period for subscriptions. A monthly subscription charge spans a term, not a day. Represent the charge period as the subscription term and the billing period as the invoice month, and be explicit that this is subscription-grained, not daily.

## Part 2: The path forward

### 2.1 Which FOCUS version to target

Live versions: 1.1 (Nov 7, 2024), 1.2 (May 29, 2025, the certification baseline), 1.3 (Dec 5, 2025), and 1.4 (June 4, 2026, the latest). Build the transform to the 1.4 column set, which removes ProviderName and PublisherName, and certify at v1.2, the offered badge. The metered Copilot slice should track whatever FOCUS version Azure Cost Management currently exports.

### 2.2 What certification requires

Certification for data generators runs through the FinOps Foundation (contact member-cert@finops.org for the RFI): a structurally conformant dataset under FOCUS column IDs, public sample data that passes the FOCUS Validator, a documented native-to-FOCUS mapping, and a Conformance Gap Report (this document is its seed). Microsoft already holds FOCUS data-generator standing on the Azure side, which is useful precedent for the M365 commerce surface.

### 2.3 Phased roadmap

Phase 0, validate and scope. Confirm the metered Copilot meters carry through the existing Azure FOCUS export with enough detail to identify Copilot. Decide the price source for the commerce surface and the cost-center representation. Build a sample commerce-surface transform and run it through the FOCUS Validator.

Phase 1, shape the commerce surface. Emit FOCUS column IDs from the CSP reconciliation or MCA transaction detail, one charge record per billing period, subscription, SKU, and invoice section. Map the cost columns, derive ChargeCategory and ChargeFrequency, populate PricingQuantity and PricingUnit, and stand up the product-to-ServiceCategory map.

Phase 2, fix deviations. Resolve list versus contracted pricing from the price sheet, validate the enums, and serialize the MCA cost center as Tags or SubAccount.

Phase 3, round out conditionals and unify. Add ServiceSubcategory and the SKU price family where available, and define how a customer joins the commerce dataset with the Azure-sourced metered Copilot dataset so M365 spend reads as one FOCUS dataset.

Phase 4, mature to 1.4 and certify.

### 2.4 FOCUS Use Cases M365 customers unlock

From the commerce surface once shaped: invoice reconciliation, cost by product and subscription, license spend by invoice section or cost center, and budgeting on billed cost. From the metered Copilot surface via Azure: daily Copilot consumption tracking, anomaly detection, and unit economics on Copilot Credits. Out of scope for the SaaS model: region analysis, capacity reservations, and commitment-discount use cases (the annual subscription term is not a FOCUS commitment discount).

## Part 3: Immediate next steps

1. Confirm whether metered Copilot consumption is already identifiable in the Azure FOCUS export, and at what fidelity.
2. Choose the authoritative price source for the commerce surface (price sheet versus invoice) to populate ListCost and ContractedCost.
3. Decide the cost-center representation (FOCUS Tags versus SubAccount).
4. Build a sample commerce-surface transform from the CSP reconciliation or MCA transaction detail and run it through the FOCUS Validator.
5. Define the join between the commerce dataset and the Azure-sourced metered Copilot dataset, so M365 including Copilot reads as one FOCUS dataset.

## Confidence summary

- High: M365 spans two billing surfaces with very different readiness; metered Copilot bills through Azure and Azure produces a FOCUS export, while seat licensing bills on the commerce surface.
- High: feature levels verified against the FOCUS v1.2 spec; spec confirmed current (v1.4 latest) on 2026-06-30.
- High: on the commerce surface all 21 Mandatory columns are sourceable, but the data is monthly and subscription-grained with no resource or tag detail.
- Moderate: the fidelity of Copilot meters within the Azure FOCUS export (identifiable as Copilot, with service and resource detail) needs confirmation.
- Moderate: list versus contracted pricing depends on the price source (price sheet, CSP reconciliation, or invoice), which varies by agreement type (MCA, MOSA, CSP).
- Moderate: whether the MCA cost center is best represented as FOCUS Tags or SubAccount.

## Sources

- Microsoft Learn, View or download your invoice in the Microsoft 365 admin center: https://learn.microsoft.com/en-us/microsoft-365/commerce/billing-and-payments/view-your-bill-or-invoice
- Microsoft Learn, Understand your invoice for your Microsoft MCA billing account: https://learn.microsoft.com/en-us/microsoft-365/commerce/billing-and-payments/understand-your-invoice
- Microsoft Learn, Microsoft 365 Copilot pay-as-you-go overview: https://learn.microsoft.com/en-us/microsoft-365/copilot/pay-as-you-go/overview
- Microsoft Learn, Usage-based billing and cost management for Copilot Credits: https://learn.microsoft.com/en-us/microsoft-365/copilot/usage-based-billing-overview-copilot-credits
- Microsoft Learn, Copilot Studio billing rates and management: https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-messages-management
- FOCUS Specification v1.2: https://focus.finops.org/focus-specification/v1-2/
- FinOps Certified FOCUS v1.2 Conformant: https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
