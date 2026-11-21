# Microsoft Copilot & FOCUS: Data Generator Gap Analysis

*Analysis run: November 18, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** Microsoft (Microsoft 365 Copilot, Copilot Business, Copilot Chat agents, Copilot Studio, Copilot Cowork)  
**Prepared:** November 18, 2026  
**Source:** Microsoft 365 admin center Copilot Cost management; Azure Cost Management (pay-as-you-go Copilot meters and FOCUS export); Microsoft 365 commerce invoices, MCA transaction detail, and CSP reconciliation files  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 29 Present, 13 Deviation, 0 Missing Mandatory, 9 Missing Conditional, 1 Missing Recommended, 5 N/A

---

## Executive Summary

Copilot spend reaches the customer through three billing paths, and no single dataset shows all of it:

1. **Per-user licenses** (Microsoft 365 Copilot, Copilot Business) bill on the Microsoft 365 commerce surface: monthly or annual subscription lines with no usage, resource, or tag detail.
2. **Prepaid Copilot Credit packs** (25,000 credits per pack per month) also bill on the commerce surface as a purchase. Drawdown against the pack is visible only in the admin center, not as cost lines.
3. **Pay-as-you-go Copilot Credits** ($0.01 per credit) bill through an Azure subscription linked by a billing policy. These meters appear in Azure Cost Management, which already produces a FOCUS export.

The metered path is close to conformant today because it rides Azure's FOCUS pipeline. The license and pack paths have the cost and account substance but no FOCUS shaping. All 21 Mandatory columns have a source; 7 need fixes, and 1 of those 7 (EffectiveCost) is substantive: usage covered by prepaid packs, and annual licenses paid up front, are never amortized to the period or consumer that used them.

The more consequential gap is allocation, not conformance. Azure cost data shows Copilot spend at the billing-policy level; the per-user, per-agent, and per-environment breakdown lives only in the Microsoft 365 and Power Platform admin centers. A dataset can pass the FOCUS Validator and still be unable to answer "which team's agents drove this bill."

**Recommendation:** Treat Copilot as one FOCUS dataset assembled from two feeds: the Azure FOCUS export (filtered to Copilot meters) plus a FOCUS-shaped transform of the commerce surface. Model prepaid credit packs as a usage-based commitment discount so pack-covered consumption carries EffectiveCost, and push the admin-center attribution (user, agent, environment) into Tags or ResourceId.

This analysis is scoped to Copilot. The broader Microsoft 365 seat estate is covered in the companion [Microsoft 365 gap analysis](Microsoft365-FOCUS-Gap-Analysis.md); Azure itself is covered in the [Microsoft Azure gap analysis](MicrosoftAzure-FOCUS-Gap-Analysis.md).

---

## Part 1: The Conformance Gap

### 1.1 The Data Sources

**Surface A, commerce billing (licenses and packs).** Microsoft 365 Copilot and Copilot Business per-user licenses, and prepaid Copilot Credit packs, appear on the Microsoft 365 admin center invoice, the Microsoft Customer Agreement (MCA) transaction list, or the CSP reconciliation file for partner-sold tenants. Granularity is the billing month and subscription term, at product and SKU level.

**Surface B, metered Copilot Credits (pay-as-you-go).** An admin creates a billing policy in the Microsoft 365 admin center that links a set of users to an Azure subscription and resource group. Consumption by Copilot Chat agents, Copilot Studio agents, SharePoint agents, Copilot Cowork, and the Work IQ API bills as Copilot Credits on Azure meters. Billed amounts update daily in Azure Cost Management, with up to 24 hours of latency.

Key characteristics:
- **Two currencies of consumption, one unit.** Copilot Studio "messages" were renamed Copilot Credits; packs and pay-as-you-go draw from the same unit.
- **Pack first, then overage.** Pack credits are consumed before pay-as-you-go. Azure cost data shows only the overage, so the Azure export alone understates total Copilot consumption.
- **Default shift to metering.** From November 2, 2026, new Copilot Business licenses purchased through CSP include usage-based billing by default, so metered lines will appear for more tenants without a deliberate opt-in.
- **Shared meters.** SharePoint agents and Copilot Chat agents use the Copilot Studio pay-as-you-go meter, so the meter name alone does not identify which Copilot product drove the cost. SharePoint Premium (Syntex) pay-as-you-go is a separate meter and policy.
- **Attribution lives outside billing.** Per-user, per-agent, and per-environment consumption is reported in the Microsoft 365 admin center (Copilot Cost management) and the Power Platform admin center, not in the Azure cost record.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven. Each column carries a feature level (Mandatory, Conditional, or Recommended). The table below assesses the combined Copilot dataset a customer would assemble from Surfaces A and B. Where one surface is conformant and the other needs work, the column is marked Deviation.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | Copilot source (A = commerce, B = Azure PAYG) | Status |
|---|---|---|---|
| BilledCost | Mandatory | A: invoice line net amount; B: Azure export BilledCost | Present |
| EffectiveCost | Mandatory | B: = BilledCost. A: pack-covered consumption and up-front annual licenses not amortized | Deviation |
| ListCost | Mandatory | B: $0.01 per credit list rate. A: price sheet or CSP recon unit price × quantity | Deviation |
| ContractedCost | Mandatory | B: Azure export. A: negotiated EA/MCA/CSP rate × quantity from price sheet | Deviation |
| BillingAccountId | Mandatory | MCA billing account / CSP customer; Azure billing account for B | Present |
| BillingAccountName | Mandatory | Billing account name | Present |
| BillingCurrency | Mandatory | Invoice currency | Present |
| BillingPeriodStart | Mandatory | Invoice billing month | Present |
| BillingPeriodEnd | Mandatory | Invoice billing month | Present |
| ChargePeriodStart | Mandatory | B: daily. A: subscription term or billing month | Present |
| ChargePeriodEnd | Mandatory | B: daily. A: subscription term or billing month | Present |
| ChargeDescription | Mandatory | Product and SKU description; Azure meter name | Present |
| ChargeCategory | Mandatory | B: "Usage". A: derive "Purchase" for licenses and packs, "Tax" for tax lines | Deviation |
| ChargeClass | Mandatory (nullable) | null except corrections | Present |
| InvoiceIssuerName | Mandatory | "Microsoft", or the CSP partner for partner-sold tenants | Present |
| ProviderName | Mandatory (dep. v1.3) | "Microsoft" | Present |
| PublisherName | Mandatory (dep. v1.3) | "Microsoft" | Present |
| ServiceName | Mandatory | B: shared Copilot Studio meter does not distinguish Copilot Chat agents, SharePoint agents, Cowork. A: product name | Deviation |
| ServiceCategory | Mandatory | Map all Copilot products to "AI and Machine Learning" on both surfaces | Deviation |
| PricingQuantity | Mandatory | A: seats or packs. B: credits | Present |
| PricingUnit | Mandatory | Normalize "messages" / "credits" / "licenses" to one unit per charge type | Deviation |
| ConsumedQuantity | Conditional | B: credits consumed. A: seats | Present |
| ConsumedUnit | Conditional | "Copilot Credits"; "Licenses" | Present |
| ListUnitPrice | Conditional | B: $0.01. A: price sheet | Deviation |
| ContractedUnitPrice | Conditional | B: Azure export. A: price sheet | Deviation |
| PricingCategory | Conditional | "Standard" for PAYG; "Committed" for annual licenses and pack-covered usage | Present |
| BillingAccountType | Conditional | Derive from agreement type (MCA, CSP) | Present |
| SubAccountId | Conditional | B: Azure subscription. A: MCA invoice section or CSP customer | Present |
| SubAccountName | Conditional | Subscription or invoice section name | Present |
| SubAccountType | Conditional | Derive | Present |
| ResourceId | Conditional | B: billing policy (Azure resource). No user, agent, or environment ID | Present |
| ResourceName | Conditional | B: billing policy name | Present |
| ResourceType | Conditional | B: billing policy resource type | Present |
| SkuId | Conditional | A: product SKU / part number. B: Azure product ID | Present |
| Tags | Conditional | B: Azure resource and resource-group tags on the policy. A: none (MCA cost center only) | Deviation |
| PricingCurrency | Conditional | = BillingCurrency | Present |
| PricingCurrencyListUnitPrice | Conditional | Follows ListUnitPrice | Deviation |
| PricingCurrencyContractedUnitPrice | Conditional | Follows ContractedUnitPrice | Deviation |
| PricingCurrencyEffectiveCost | Conditional | Follows EffectiveCost | Deviation |
| SkuMeter | Conditional | B: Azure meter name | Present |
| SkuPriceId | Conditional | B: Azure export. A: not exposed on commerce surface | Missing: Conditional |
| SkuPriceDetails | Conditional | Not exposed on either surface | Missing: Conditional |
| RegionId | Conditional | Global service, no billed region | N/A |
| RegionName | Conditional | Global service, no billed region | N/A |
| CommitmentDiscountId | Conditional | Prepaid credit pack (monthly allotment, consumed before PAYG) | Missing: Conditional |
| CommitmentDiscountName | Conditional | Pack name | Missing: Conditional |
| CommitmentDiscountType | Conditional | Pack type | Missing: Conditional |
| CommitmentDiscountCategory | Conditional | "Usage" | Missing: Conditional |
| CommitmentDiscountStatus | Conditional | "Used" / "Unused" for unconsumed monthly credits | Missing: Conditional |
| CommitmentDiscountQuantity | Conditional | Credits drawn from pack | Missing: Conditional |
| CommitmentDiscountUnit | Conditional | "Copilot Credits" | Missing: Conditional |
| CapacityReservationId | Conditional | Packs prepay credits; they do not reserve capacity | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | Invoice number | Present |
| ChargeFrequency | Recommended | "Recurring" for licenses and packs; "Usage-Based" for PAYG | Present |
| ServiceSubcategory | Recommended | Map to the AI and Machine Learning generative AI subcategory | Missing: Recommended |
| AvailabilityZone | Recommended | Global service, no zone | N/A |

**Tally:** 29 Present, 13 Deviation, 0 Missing Mandatory, 9 Missing Conditional, 1 Missing Recommended, 5 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Pay-as-you-go Copilot Credits already flow through Azure's FOCUS export at daily grain with cost, account, subscription, SKU, and meter detail. On the commerce surface, all Mandatory columns have source data.

**Remaining (substantive):**
- **EffectiveCost for pack-covered and prepaid consumption.** Pack credits consumed before pay-as-you-go produce no cost line. Annual licenses paid up front land as one purchase. Neither is spread to the day or consumer that used it. This is the cost gap that will widen as metered agents and Cowork grow.
- **Commitment modeling of packs.** A monthly pack of 25,000 credits that is consumed first and expires unused fits the FOCUS usage-based commitment shape. Without it, unused pack credits are invisible waste.

**Remaining (structural, not a conformance blocker):** Azure cost data stops at the billing policy. Per-user, per-agent, and per-environment attribution exists only in admin-center reports, so chargeback by team or agent requires a join that FOCUS does not carry today.

### 1.5 Deviations to Fix

**EffectiveCost:** Emit daily amortized rows for pack-covered credits (pack price ÷ credits × credits consumed) and for up-front annual licenses (term cost ÷ days). Set BilledCost to 0 on these rows and carry the commitment ID.

**ServiceName:** The shared Copilot Studio meter collapses Copilot Chat agents, SharePoint agents, and Copilot Studio into one service. Split by originating product, or carry the product in a tag.

**ChargeCategory and ServiceCategory:** Licenses and packs are "Purchase"; metered credits are "Usage." All Copilot products are "AI and Machine Learning."

**PricingUnit:** Settle on "Copilot Credits" for all metered and pack lines, and a single license unit for seats. Retire "messages."

**ListCost and ContractedCost:** On the commerce surface, list and negotiated prices live on the price sheet or CSP reconciliation, not the invoice. Pick one authoritative source per agreement type.

**Tags:** Surface admin-center attribution (user principal, agent ID, Power Platform environment) as key-value Tags on Copilot meter rows.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (June 4, 2026), which removes ProviderName and PublisherName; certify at FOCUS v1.2. The metered path tracks whatever FOCUS version Azure Cost Management exports.

### 2.2 What Certification Requires

Contact `member-cert@finops.org` for the RFI. Microsoft already holds FOCUS data-generator standing on the Azure side, which covers Surface B. The commerce surface would need its own conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report (this document is its seed).

### 2.3 Phased Roadmap

**Phase 0: Validate.** Pull a month of the Azure FOCUS export filtered to Copilot meters and confirm ServiceName, ServiceCategory, ResourceId, and SkuMeter values. Run it through the FOCUS Validator.

**Phase 1: Shape the commerce surface.** Transform MCA transaction detail or CSP reconciliation into FOCUS rows per billing period, subscription, and SKU. Derive ChargeCategory, ChargeFrequency, PricingUnit, ServiceCategory.

**Phase 2: Close the EffectiveCost gap.** Model credit packs as usage-based commitments; emit amortized pack-drawdown and up-front license rows with the CommitmentDiscount family populated.

**Phase 3: Attribution.** Push user, agent, and environment identifiers from admin-center reports into Tags or ResourceId on metered rows. Split the shared meter by originating product.

**Phase 4: Certify.** Add ServiceSubcategory and SkuPriceDetails, drop ProviderName and PublisherName (v1.4), validate, and certify.

### 2.4 FOCUS Use Cases Unlocked

Available now from the Azure path: daily Copilot Credit consumption tracking, anomaly detection on metered spend, budget alerts on the linked subscription. After Phase 1: invoice reconciliation across licenses, packs, and overage. After Phase 2: commitment utilization (unused pack credits) and unit economics per credit. After Phase 3: chargeback and showback by team, agent, or environment. Out of scope: region and capacity-reservation analysis.

---

## Part 3: Immediate Next Steps

1. Export one month of Azure FOCUS data filtered to Copilot meters and document the values Microsoft emits for ServiceName, ResourceId, and SkuMeter.
2. Pull the matching month of commerce invoice or CSP reconciliation and the admin-center Copilot Cost management report.
3. Reconcile the three: license spend, pack spend and drawdown, and pay-as-you-go overage.
4. Decide whether packs are modeled as commitment discounts or plain prepaid purchases, and document the choice.
5. Open the RFI with `member-cert@finops.org` if Microsoft pursues conformance for the commerce surface.

---

## Confidence Summary

- **High:** Copilot spend splits across commerce billing (licenses, packs) and Azure-metered pay-as-you-go Copilot Credits; the metered path appears in Azure Cost Management, which produces a FOCUS export.
- **High:** Pricing: $0.01 per pay-as-you-go credit; packs of 25,000 credits per month; pack credits consumed before pay-as-you-go.
- **High:** Feature levels taken from the bundled FOCUS v1.2 reference (stamped 2026-06-23, v1.4 latest). A live spec spot-check was not possible in this run; re-confirm before external use.
- **Moderate:** The billing policy appears as the Azure ResourceId on Copilot meter rows, and resource-group tags flow through to Tags. Confirm against a real export.
- **Moderate:** Classifying prepaid packs as a usage-based commitment discount is a modeling judgment. If they are treated as plain prepaid purchases, the seven CommitmentDiscount columns become N/A and the EffectiveCost gap remains.
- **Moderate:** The shared Copilot Studio meter for SharePoint and Copilot Chat agents may be split into product-specific meters as Microsoft's billing evolves.
- **Low:** How Copilot Cowork and Work IQ API consumption is labeled in Azure meter names; public documentation does not show sample export rows.

---

## Sources

- Microsoft Learn, Microsoft 365 Copilot pay-as-you-go overview: [learn.microsoft.com](https://learn.microsoft.com/en-us/microsoft-365/copilot/pay-as-you-go/overview)
- Microsoft Learn, Set up pay-as-you-go billing (billing policies): [learn.microsoft.com](https://learn.microsoft.com/en-us/microsoft-365/copilot/pay-as-you-go/setup)
- Microsoft Learn, Usage-based billing and cost management for Copilot Credits: [learn.microsoft.com](https://learn.microsoft.com/en-us/microsoft-365/copilot/usage-based-billing-overview-copilot-credits)
- Microsoft Learn, Manage Copilot Studio capacity: [learn.microsoft.com](https://learn.microsoft.com/power-platform/admin/manage-copilot-studio-messages-capacity)
- Microsoft Learn, Copilot Studio billed sessions analytics: [learn.microsoft.com](https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-billed-sessions)
- Microsoft Licensing Guidance, Microsoft Copilot Studio: [microsoft.com](https://www.microsoft.com/licensing/guidance/Microsoft-Copilot-Studio)
- Topedia, How to get cost and usage reports for Microsoft 365 pay-as-you-go billing in Azure: [blog-en.topedia.com](https://blog-en.topedia.com/2025/01/how-to-get-cost-and-usage-reports-for-microsoft-365-pay-as-you-go-billing-in-azure)
- Stoneridge Software, What Microsoft Copilot and Cowork actually cost in 2026: [stoneridgesoftware.com](https://stoneridgesoftware.com/what-microsoft-copilot-and-cowork-actually-cost-in-2026-and-how-to-avoid-a-surprise-bill/)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
