# PerfectScale & FOCUS: Data Generator Gap Analysis

*Analysis run: November 17, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** PerfectScale by DoiT  
**Prepared:** November 17, 2026  
**Origin:** KubeCon NA 2026 booth outreach  
**Source:** PerfectScale pricing page; DoiT help center (PerfectScale service description, vCPU measurement, DoiT pricing, cloud billing integration); AWS Marketplace listing  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 16 Present, 10 Deviation, 2 Missing Mandatory, 18 Missing Conditional, 1 Missing Recommended, 10 N/A

---

## Executive Summary

PerfectScale, now sold as "PerfectScale by DoiT," is a Kubernetes optimization and governance platform for EKS, AKS, GKE, and self-hosted clusters. It charges per monthly vCPU: Community is free up to 300 vCPUs per month, Advanced is $2.00 and Expert $4.00 per monthly vCPU on AWS Marketplace, and Enterprise bundles Expert with DoiT Cloud Intelligence (DCI) Enterprise. The billed unit is allocated node capacity (sum of node CPU capacity × hours), metered hourly in vCPU-hours. Direct customers buy capacity on an Order Form with a DoiT-run true-up above it; Marketplace buyers sign 1- or 12-month contracts with usage-based overage.

PerfectScale is closer to FOCUS than most SaaS vendors because its billing unit is already a metered, hourly, per-cluster quantity, and it shows customers a monthly vCPU consumption trend in-app. What it lacks is any machine-readable output of its own charges: no billing API, invoice API, or usage export is documented, and the Public API (Expert only) covers optimization data, not PerfectScale fees.

Mapped against invoice, order-form, and public price content, 16 of 57 FOCUS v1.2 columns map directly and 19 of 21 Mandatory columns have a source. **EffectiveCost** is the substantive Mandatory gap: prepaid contract capacity and true-ups must be amortized over hourly consumption. **ListCost** is trivial, since list rates are public. The rest of the work is delivery, per-cluster allocation, and a commitment-discount model for contracted capacity priced below overage.

PerfectScale also **consumes** cloud billing data (AWS CUR via a Legacy CUR export, Azure Cost Management, GCP Cloud Billing, and DoiT pricing for EKS and GKE) to price and allocate Kubernetes costs. None of its documentation mentions FOCUS.

**Recommendation:** Publish a FOCUS export per customer from the existing hourly metering: one Usage row per cluster per day with ConsumedQuantity in vCPU-hours, ResourceId set to the cluster, SubAccountId set to the hosting cloud account, and cluster labels as Tags; one Purchase row per contract; and true-up, Tax, and Credit rows so the dataset reconciles to the invoice. Expose it through the Public API and the "Subscription Details" page.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

PerfectScale publishes no billing data interface for its own charges. The material available for a FOCUS mapping:

- **Pricing page:** Plans and units ("Free up to 300 vCPU/month"; Advanced and Expert "per vCPU" with "Get a quote"). Payment by card, wire, direct debit, or bill.com. No dollar amounts.
- **AWS Marketplace:** "PerfectScale by DoiT - Kubernetes Optimization and Governance Platform," a SaaS contract with usage-based overage, sold by PerfectScale and paid "through your AWS bill." Advanced is "equivalent to $2.00 per monthly vCPU, with usage metered hourly and billed in 1 vCPU-hour increments"; Expert is equivalent to $4.00. Overage unit rates exceed contracted unit rates. Terms are 1 or 12 months, paid upfront or in installments, with no refunds.
- **Service description (direct contracts):** Capacity is set in the Order Form. "Above this capacity, a True-Up process will be initiated by a DoiT employee to collect the delta capacity," with notice in the platform UI and from the customer success manager.
- **In-app subscription view:** "Subscription Details" and a "View over-time vCPU consumption report" showing normalized monthly vCPU consumption. Display only; no export is documented.
- **Measurement:** Customers verify usage by summing `kube_node_status_capacity{resource="cpu"}` across nodes and multiplying by hours (e.g., `90*24*30 = 64800`). The unit is allocated capacity, not utilization or peak.

Key characteristics:

- **Unit:** vCPU-hours of node capacity, normalized to monthly vCPUs.
- **Plans:** Community (free), Advanced, Expert, Enterprise (Expert plus DCI Enterprise); self-hosted is Expert only.
- **Commitment:** Order-form capacity with true-up (direct); 1- or 12-month contracts with overage at a higher unit rate (Marketplace).
- **Hierarchy:** Customer organization billed once; clusters connected across AWS, Azure, GCP, and self-hosted environments.
- **No regions, zones, or capacity reservations** in PerfectScale's own pricing.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven: every Mandatory column must be present and valid, and Conditional columns are required when the provider's model triggers their condition. Two modeling decisions drive this analysis:

- **Contracted capacity is a commitment discount.** FOCUS defines a commitment discount as reduced rates in exchange for a usage or spend commitment. On Marketplace, contracted vCPU-hours are priced below overage, so the commitment buys a lower rate. The seven CommitmentDiscount columns are therefore Missing: Conditional, PricingCategory is "Committed" for drawn-down usage and "Standard" for overage, and EffectiveCost must amortize the upfront payment. From v1.3 the Contract Commitment dataset is the right home for the contract itself.
- **Clusters and their cloud accounts are applicable allocation keys.** Charges accrue per node vCPU-hour in a specific cluster, so the cluster is the resource behind each charge and the hosting AWS account, Azure subscription, or GCP project is the grouping that owns it. The Resource, SubAccount, and Tags columns are Missing, not N/A.

PerfectScale has no regions, zones, capacity reservations, alternate pricing currencies, or multiple billing-account types; those columns are N/A and should exist as null. Feature levels follow the bundled FOCUS v1.2 Content Constraints table.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | PerfectScale source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Invoice line amount (direct) or AWS Marketplace charge | Present |
| EffectiveCost | Mandatory | Not available: needs upfront contract and true-up amortized over hourly vCPU consumption, plus credit allocation | Missing: Mandatory |
| ListCost | Mandatory | Not emitted; public list rate × PricingQuantity | Missing: Mandatory |
| ContractedCost | Mandatory | Contracted rate × capacity from the Order Form or Marketplace contract | Present |
| BillingAccountId | Mandatory | PerfectScale organization or tenant ID on the invoice | Present |
| BillingAccountName | Mandatory | Customer organization name | Present |
| BillingCurrency | Mandatory | "USD" | Present |
| BillingPeriodStart | Mandatory | Invoice service period start | Present |
| BillingPeriodEnd | Mandatory | Invoice service period end | Present |
| ChargePeriodStart | Mandatory | Contract term only; usage rows need hourly or daily periods from existing metering | Deviation |
| ChargePeriodEnd | Mandatory | Contract term only; same fix | Deviation |
| ChargeDescription | Mandatory | Invoice line description (plan, capacity, true-up) | Present |
| ChargeCategory | Mandatory | Derive: "Purchase" for contracts; "Usage" for consumption, overage, and true-up; "Tax" and "Credit" from the invoice | Deviation |
| ChargeClass | Mandatory (nullable) | null; "Correction" for re-issued charges | Present |
| InvoiceIssuerName | Mandatory | DoiT or PerfectScale entity for direct contracts; "Amazon Web Services" for Marketplace | Present |
| ProviderName | Mandatory (dep. v1.3) | "PerfectScale" | Present |
| PublisherName | Mandatory (dep. v1.3) | "PerfectScale" | Present |
| ServiceName | Mandatory | "PerfectScale" (plan in SkuId) | Present |
| ServiceCategory | Mandatory | Derive: "Management and Governance" | Deviation |
| PricingQuantity | Mandatory | Contract capacity only; usage rows need metered vCPU-hours | Deviation |
| PricingUnit | Mandatory | Normalize "monthly vCPU" and "vCPU-hour" to one FOCUS unit (e.g., "vCPU-Hours") | Deviation |
| ConsumedQuantity | Conditional | Shown in-app as normalized monthly vCPUs per organization; needs vCPU-hours per cluster per period | Deviation |
| ConsumedUnit | Conditional | Same: "vCPU-Hours" | Deviation |
| ListUnitPrice | Conditional | Public: $2.00 (Advanced) and $4.00 (Expert) per monthly vCPU | Present |
| ContractedUnitPrice | Conditional | Contracted rate on the Order Form or Marketplace contract | Present |
| PricingCategory | Conditional | Derive: "Committed" for drawn-down usage; "Standard" for overage | Deviation |
| BillingAccountType | Conditional | N/A: one billing-account type | N/A |
| SubAccountId | Conditional | Not exposed: AWS account, Azure subscription, or GCP project hosting each cluster | Missing: Conditional |
| SubAccountName | Conditional | Not exposed | Missing: Conditional |
| SubAccountType | Conditional | Not exposed (e.g., "AWS Account", "Azure Subscription", "GCP Project") | Missing: Conditional |
| ResourceId | Conditional | Not exposed: cluster ID | Missing: Conditional |
| ResourceName | Conditional | Not exposed: cluster name | Missing: Conditional |
| ResourceType | Conditional | Not exposed (e.g., "Kubernetes Cluster") | Missing: Conditional |
| SkuId | Conditional | Not exposed; plan code or Marketplace dimension (Community, Advanced, Expert) | Missing: Conditional |
| Tags | Conditional | Not exposed: PerfectScale holds cluster and cloud labels but emits none with charges | Missing: Conditional |
| PricingCurrency | Conditional | N/A: priced and billed in USD only | N/A |
| PricingCurrencyListUnitPrice | Conditional | N/A | N/A |
| PricingCurrencyContractedUnitPrice | Conditional | N/A | N/A |
| PricingCurrencyEffectiveCost | Conditional | N/A | N/A |
| SkuMeter | Conditional | Not exposed: "Node vCPU capacity" | Missing: Conditional |
| SkuPriceId | Conditional | Not exposed | Missing: Conditional |
| SkuPriceDetails | Conditional | Not exposed; needed to state the capacity-based measurement and monthly normalization | Missing: Conditional |
| RegionId | Conditional | N/A: no region-based pricing | N/A |
| RegionName | Conditional | N/A | N/A |
| CommitmentDiscountId | Conditional | Not exposed: contract or Order Form ID | Missing: Conditional |
| CommitmentDiscountName | Conditional | Not exposed | Missing: Conditional |
| CommitmentDiscountType | Conditional | Not exposed: provider-defined (e.g., "Capacity Contract") | Missing: Conditional |
| CommitmentDiscountCategory | Conditional | Not exposed: "Usage" | Missing: Conditional |
| CommitmentDiscountStatus | Conditional | Not exposed: "Used" or "Unused" per period | Missing: Conditional |
| CommitmentDiscountQuantity | Conditional | Not exposed: contracted vCPU-hours drawn per period | Missing: Conditional |
| CommitmentDiscountUnit | Conditional | Not exposed: "vCPU-Hours" | Missing: Conditional |
| CapacityReservationId | Conditional | N/A: no capacity reservations | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | Invoice number | Present |
| ChargeFrequency | Recommended | Derive: "One-Time" or "Recurring" for contracts by payment schedule; "Usage-Based" for consumption and overage | Deviation |
| ServiceSubcategory | Recommended | Not exposed; map to "Cost Management" | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: no zones | N/A |

**Tally:** 16 Present, 10 Deviation, 2 Missing Mandatory, 18 Missing Conditional, 1 Missing Recommended, 10 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Billing account, currency, service periods, invoiced and contracted amounts, public list and contracted rates, line descriptions, invoice numbers, and an hourly metered quantity that maps cleanly to ConsumedQuantity.

**Substantive (1 of 2 Mandatory gaps):**

- **EffectiveCost.** Marketplace contracts are paid upfront or in installments, and direct true-ups collect capacity after the fact. EffectiveCost means amortizing both across the vCPU-hours consumed in each period and allocating credits back to the charges they offset.

**Trivial (1 of 2 Mandatory gaps):**

- **ListCost.** List rates are public. Multiply ListUnitPrice by PricingQuantity on every row.

**Substantive, beyond the column table:**

- **No delivery path.** No billing API, invoice API, or usage export is documented, and the Public API is Expert only. A FOCUS dataset needs an API endpoint or scheduled object-storage drop on every paid plan.
- **Per-cluster consumption.** The metering is hourly, but customers see only an organization-level monthly trend. Emitting vCPU-hours per cluster per day is the step that turns an existing meter into allocatable data.
- **Commitment modeling.** Contracted capacity priced below overage needs the CommitmentDiscount columns, used and unused rows per period, and Contract Commitment records in v1.3 and later.
- **Two channels.** Marketplace buyers see PerfectScale charges in AWS billing data, invoiced by AWS; direct customers deal with DoiT. A PerfectScale FOCUS export should cover consumption for both, with InvoiceIssuerName set per channel so neither double-counts the contract.

**On the consumer side.** PerfectScale's AWS integration asks customers to create a Legacy CUR export, and it reads Azure Cost Management and GCP Cloud Billing through separate connectors. Accepting FOCUS exports from all three, which they each now produce, would replace three provider-specific parsers with one and align PerfectScale with the format its parent's customers increasingly use.

### 1.5 Deviations to Fix

**ChargePeriodStart and ChargePeriodEnd:** Emit Usage rows per hour or day from existing metering. Keep Purchase rows on the contract term.

**ChargeCategory:** "Purchase" for contracts; "Usage" for consumption, overage, and true-up; "Tax" and "Credit" from the invoice, so that BilledCost summed per InvoiceId equals the invoice total.

**ServiceCategory:** "Management and Governance."

**PricingQuantity and PricingUnit:** Pick one unit. The meter counts vCPU-hours, while the price list quotes monthly vCPUs; use "vCPU-Hours" and document the monthly normalization in SkuPriceDetails. Populate PricingQuantity on every Usage row.

**ConsumedQuantity and ConsumedUnit:** Move the in-app normalized monthly figure to vCPU-hours per cluster per period.

**ChargeFrequency and PricingCategory:** Contract rows by payment schedule; "Usage-Based" for consumption; "Committed" for drawn-down usage and "Standard" for overage.

**Already right:** USD-only billing, a single billing entity per customer, public list rates, hourly metering, and a capacity-based unit that customers can reproduce from Kubernetes metrics.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (ratified June 4, 2026); certify at FOCUS v1.2, the version the conformance program currently names. FOCUS v1.5 is in release candidate with ratification scheduled for December 3, 2026. The Contract Commitment dataset (v1.3) fits PerfectScale's capacity contracts, and the Invoice Detail dataset (v1.4) fits invoice reconciliation.

### 2.2 What Certification Requires

FinOps Certified FOCUS v1.2 Conformant runs through the FinOps Foundation (contact `member-cert@finops.org` for the RFI; membership is required for certification). Deliverables: a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report seeded by this analysis. Tooling: FOCUS Validator, FOCUS Converter, and the FOCUS Requirements Model. Document the N/A rationale and the commitment-discount model for contracted capacity.

### 2.3 Phased Roadmap

**Phase 0: Validate.** Pull one month of hourly vCPU metering for a direct customer and a Marketplace customer. Hand-build a FOCUS file from it plus the invoice and run it through the Validator. Settle the PricingUnit.

**Phase 1: Close Mandatory gaps.** Emit ListCost from public rates. Emit per-cluster Usage rows and amortize contracts and true-ups across them for EffectiveCost. Add Tax and Credit rows so BilledCost reconciles to the invoice.

**Phase 2: Fix deviations.** Derive ChargeCategory, ServiceCategory, ChargeFrequency, and PricingCategory; normalize PricingUnit and ConsumedUnit; populate per-period charge periods and quantities on every Usage row.

**Phase 3: Allocation, commitments, and delivery.** Add ResourceId, ResourceName, and ResourceType per cluster; SubAccountId, SubAccountName, and SubAccountType for the hosting cloud account; Tags from cluster labels; the seven CommitmentDiscount columns; SkuId, SkuMeter, SkuPriceId, and SkuPriceDetails; ServiceSubcategory. Ship the export through the Public API on all paid plans and as a download from "Subscription Details."

**Phase 4: Mature and certify.** Drop ProviderName and PublisherName for v1.4; add the Contract Commitment and Invoice Detail datasets; certify at v1.2 and re-certify as the program advances. In parallel, accept FOCUS exports from AWS, Azure, and GCP in place of Legacy CUR and native billing connectors.

### 2.4 FOCUS Use Cases Unlocked

- **After Phase 1:** Invoice reconciliation, amortized spend reporting, and actuals-based budgeting for the PerfectScale line item.
- **After Phase 2:** Spend by service category across providers, and contract burn-down and overage forecasting.
- **After Phase 3:** Chargeback and showback of PerfectScale fees by cluster and cloud account, commitment utilization, unit economics (PerfectScale cost per vCPU-hour against savings delivered), and anomaly detection on node-capacity growth.
- **Out of scope:** Region-based analysis and capacity reservation management.

---

## Part 3: Immediate Next Steps

1. Follow up with the PerfectScale contact from KubeCon NA 2026 to identify the owner of billing and vCPU metering at DoiT.
2. Confirm the invoicing legal entity for direct contracts, the true-up rate, and how Marketplace contract and overage units relate.
3. Build a v1.2 sample from one month of metering plus the invoice and run it through the FOCUS Validator.
4. Agree on the commitment model and the Marketplace versus direct row design.
5. Open the RFI with `member-cert@finops.org`.

---

## Confidence Summary

- **High:** PerfectScale bills per monthly vCPU of allocated node capacity, metered hourly, with a free tier up to 300 vCPUs and Marketplace rates equivalent to $2.00 (Advanced) and $4.00 (Expert). Its public docs describe no billing API, invoice API, or usage export for its own charges.
- **High:** Customers can view a monthly vCPU consumption trend in "Subscription Details"; direct overage is collected by a DoiT-run true-up.
- **High:** Feature levels match the bundled, verified FOCUS v1.2 Content Constraints table. A live spec spot-check was not run for this report.
- **Moderate:** Treating contracted capacity as a commitment discount. It rests on Marketplace overage unit rates exceeding contracted unit rates; if the direct true-up uses the contracted rate and Marketplace units differ, a prepaid-purchase model with the CommitmentDiscount columns N/A also fits.
- **Moderate:** Present status for invoice-sourced columns. The invoice layout is not public, so these follow standard SaaS invoice content.
- **Moderate:** PerfectScale's AWS ingestion uses a Legacy CUR export, and no documentation mentions FOCUS ingestion.
- **Moderate:** "Cost Management" as the ServiceSubcategory value. Confirm it against the v1.2 allowed values before mapping.
- **Low:** The invoicing entity for direct contracts (DoiT or a PerfectScale subsidiary). No public page names it.
- **Low:** The Marketplace Community dimension states "300k vCPU hours per month," which does not match "300 vCPU/month" (about 219,000 vCPU-hours) on the pricing page.

---

## Sources

- PerfectScale Pricing: [perfectscale.io/pricing](https://www.perfectscale.io/pricing)
- PerfectScale Service Description: [help.doit.com/docs/perfectscale-service-description](https://help.doit.com/docs/perfectscale-service-description)
- How to Find Your Allocated vCPU: [help.doit.com/.../how-to-find-your-allocated-vcpu](https://help.doit.com/ja/docs/perfectscale-for-kubernetes/saas/perfectscale-trial/perfectscale-trial/how-to-find-your-allocated-vcpu)
- DoiT Pricing Integration: [help.doit.com/.../doit-pricing](https://help.doit.com/docs/perfectscale-for-kubernetes/saas/cloud-billing-integration/doit-pricing)
- About Cloud Billing Integration: [help.doit.com/.../about-cloud-billing-integration](https://help.doit.com/docs/perfectscale-for-kubernetes/saas/cloud-billing-integration/about-cloud-billing-integration)
- Connecting AWS CUR: [docs.perfectscale.io/cloud-billing-integration/connecting-aws-cur](https://docs.perfectscale.io/cloud-billing-integration/connecting-aws-cur)
- PerfectScale on AWS Marketplace: [aws.amazon.com/marketplace/pp/prodview-pdvno3f3xmkek](https://aws.amazon.com/marketplace/pp/prodview-pdvno3f3xmkek)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FOCUS 1.5 Release Scope: [focus.finops.org/focus-1-5-release-scope/](https://focus.finops.org/focus-1-5-release-scope/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
