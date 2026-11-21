# Sedai & FOCUS: Data Generator Gap Analysis

*Analysis run: November 17, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** Sedai, Inc.  
**Prepared:** November 17, 2026  
**Origin:** KubeCon NA 2026 booth outreach  
**Source:** Sedai pricing page (Sedai Billing Unit model); Sedai docs (docs.sedai.io: Augmented FinOps onboarding, integrations, tag configuration, groups); Sedai MCP server page; AWS Marketplace listing  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 15 Present, 8 Deviation, 2 Missing Mandatory, 14 Missing Conditional, 1 Missing Recommended, 17 N/A

---

## Executive Summary

Sedai sells an autonomous cloud optimization platform covering Kubernetes (EKS, AKS, GKE, and on-premises clusters), AWS Lambda, ECS, EC2, and storage, Azure VMs, GCP Dataflow, Databricks, Kubernetes GPU workloads, and a FinOps module. It charges in Sedai Billing Units (SBUs): one SBU per vCPU the platform manages. Customers sign a fixed annual commitment sized to expected usage; usage above the commitment is charged at the same rate, with no penalty. Quotes are custom. Sedai is also sold as SaaS through AWS Marketplace on 12-month contracts with usage overages.

Sedai has the billing model FOCUS handles well, metered usage against a prepaid commitment, but it publishes nothing to put in a FOCUS dataset. Its docs describe no billing API, usage export, or invoice API for Sedai's own charges. The integrations cover IaC, notifications, and ticketing only, and the MCP server returns savings data, not Sedai's charges. Everything a customer can see about Sedai spend is on an invoice or, for Marketplace buyers, in AWS's billing data.

Mapped against invoice and order-form content, 15 of 57 FOCUS v1.2 columns map directly and 19 of 21 Mandatory columns have a source. **EffectiveCost** is the substantive Mandatory gap: the annual SBU commitment is paid ahead of use, so amortizing it requires per-period SBU consumption that Sedai does not expose. **ListCost** is trivial once Sedai sets a list SBU rate; pricing is custom-quoted today. The bigger gaps sit outside the column table: no machine-readable delivery at all, no per-period consumption, and no allocation to the clusters, workloads, and cloud accounts that consume the SBUs.

Sedai already **consumes** FOCUS. Its AWS FinOps onboarding accepts "Focus 1.0 (Standard Data Export)" alongside legacy CUR, though it prefers CUR. That puts Sedai on both sides of the specification and makes it a natural candidate to generate FOCUS for its own charges.

**Recommendation:** Publish a monthly FOCUS export per customer: one Purchase row per annual SBU commitment, one Usage row per managed resource (cluster, workload, or VM) per day or month, with ConsumedQuantity in vCPUs and EffectiveCost amortized from the commitment, plus overage, Tax, and Credit rows so the dataset reconciles to the invoice. Expose it through the existing platform (API or scheduled object-storage drop), and carry the connected cloud account as SubAccountId and the managed resource's tags as Tags.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

Sedai publishes no billing data interface. The material available for a FOCUS mapping:

- **Invoices and order forms (direct contracts):** Not publicly documented. The analysis assumes a standard SaaS invoice: invoice number, customer, service term, line description (annual SBU commitment, overage), quantity in SBUs, unit price, amount, and USD currency.
- **AWS Marketplace (channel sales):** "Sedai - Autonomous Cloud Optimization and Management Platform," a SaaS contract with usage overages and 12-month terms. Listed dimensions include a $1 30-day POC offer and placeholder tiers; real pricing runs through private offers. These charges reach the buyer as AWS Marketplace line items in AWS billing data, invoiced by AWS, not Sedai.
- **Sedai platform:** Sedai must meter managed vCPUs to bill overage, but no customer-facing SBU usage view or export is documented.
- **Sedai MCP server:** Lets users "pull savings data" and "surface opportunities" from coding assistants. It documents no tool names, fields, or charge data.
- **Tags and groups:** Sedai reads cloud tags and Kubernetes annotations to control its behavior (prefixes `settings.sedai.io.`, `settings.sedai.io/`, `configs:sedai.io:`) and builds "Groups" that can infer cloud provider tags. These are control settings, not billing fields, but they show Sedai already holds the tag context of every resource it manages.

Key characteristics:

- **Unit:** 1 SBU per vCPU managed, across clouds, Kubernetes, and on-premises.
- **Commitment:** Fixed annual SBU commitment; overage at the committed rate; commitments adjustable.
- **Pricing:** Custom quotes; no public per-SBU rate.
- **Hierarchy:** Customer organization billed once; within it, Sedai connects cloud accounts, Azure subscriptions, and Kubernetes clusters, and organizes resources into Groups.
- **No regions, zones, or capacity reservations** in Sedai's own pricing.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven: every Mandatory column must be present and valid, and Conditional columns are required when the provider's model triggers their condition. Two modeling decisions drive this analysis:

- **The annual SBU commitment is a prepaid purchase, not a commitment discount.** FOCUS defines a commitment discount as reduced rates in exchange for a commitment. Sedai charges overage at the committed rate and publishes no uncommitted rate, so no discount is visible; the seven CommitmentDiscount columns are N/A. EffectiveCost still has to amortize the prepayment, since FOCUS defines it to include the applicable portion of prepaid purchases. From v1.3 the Contract Commitment dataset is the right home for the commitment itself.
- **Managed resources and connected cloud accounts are applicable allocation keys.** SBUs are consumed per managed vCPU, so the cluster, workload, or VM is the resource behind each charge, and the connected cloud account or subscription is the grouping that owns it. The Resource, SubAccount, and Tags columns are therefore Missing, not N/A.

Sedai has no regions, zones, capacity reservations, alternate pricing currencies, or multiple billing-account types; those columns are N/A and should exist as null. Feature levels follow the FOCUS v1.2 Content Constraints, spot-checked against the live spec on November 17, 2026.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | Sedai source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Invoice line amount (direct contracts) | Present |
| EffectiveCost | Mandatory | Not available: needs the annual SBU prepayment amortized over per-period consumption, plus credit allocation | Missing: Mandatory |
| ListCost | Mandatory | Not available: no list SBU rate; join a rate card × PricingQuantity | Missing: Mandatory |
| ContractedCost | Mandatory | Contracted SBU rate × SBU quantity from the order form | Present |
| BillingAccountId | Mandatory | Sedai customer or tenant ID on the invoice | Present |
| BillingAccountName | Mandatory | Customer organization name | Present |
| BillingCurrency | Mandatory | "USD" | Present |
| BillingPeriodStart | Mandatory | Invoice service period start | Present |
| BillingPeriodEnd | Mandatory | Invoice service period end | Present |
| ChargePeriodStart | Mandatory | Contract term start only; usage rows need daily or monthly periods from Sedai metering | Deviation |
| ChargePeriodEnd | Mandatory | Contract term end only; same fix | Deviation |
| ChargeDescription | Mandatory | Invoice line description (e.g., "Annual SBU commitment", "SBU overage") | Present |
| ChargeCategory | Mandatory | Derive: "Purchase" for the annual commitment; "Usage" for consumption and overage; "Tax" and "Credit" rows from the invoice | Deviation |
| ChargeClass | Mandatory (nullable) | null; "Correction" for re-issued charges | Present |
| InvoiceIssuerName | Mandatory | "Sedai, Inc." for direct contracts (AWS for Marketplace) | Present |
| ProviderName | Mandatory (dep. v1.3) | "Sedai" | Present |
| PublisherName | Mandatory (dep. v1.3) | "Sedai" | Present |
| ServiceName | Mandatory | "Sedai Autonomous Cloud Optimization Platform" | Present |
| ServiceCategory | Mandatory | Derive: "Management and Governance" | Deviation |
| PricingQuantity | Mandatory | SBU quantity on the order form; usage and overage rows need metered SBUs | Deviation |
| PricingUnit | Mandatory | Normalize "SBU" to a documented rate basis (e.g., "vCPU-Months") and state whether it is average or peak managed vCPUs | Deviation |
| ConsumedQuantity | Conditional | Not exposed: managed vCPUs per resource per period | Missing: Conditional |
| ConsumedUnit | Conditional | Not exposed: "vCPUs" or "vCPU-Hours" | Missing: Conditional |
| ListUnitPrice | Conditional | Not available: no public or list SBU rate | Missing: Conditional |
| ContractedUnitPrice | Conditional | Contracted per-SBU rate on the order form | Present |
| PricingCategory | Conditional | Derive: "Standard" for all rows (no commitment discount) | Deviation |
| BillingAccountType | Conditional | N/A: one billing-account type | N/A |
| SubAccountId | Conditional | Not exposed: connected AWS account, Azure subscription, or GCP project that owns the managed resources | Missing: Conditional |
| SubAccountName | Conditional | Not exposed | Missing: Conditional |
| SubAccountType | Conditional | Not exposed (e.g., "AWS Account", "Azure Subscription") | Missing: Conditional |
| ResourceId | Conditional | Not exposed: managed cluster, workload, function, or VM ID | Missing: Conditional |
| ResourceName | Conditional | Not exposed | Missing: Conditional |
| ResourceType | Conditional | Not exposed (e.g., "Kubernetes Workload", "Lambda Function", "EC2 Instance") | Missing: Conditional |
| SkuId | Conditional | Not exposed; internal plan code or Marketplace dimension key | Missing: Conditional |
| Tags | Conditional | Not exposed: Sedai reads cloud tags and Kubernetes labels of managed resources but emits none with charges | Missing: Conditional |
| PricingCurrency | Conditional | N/A: priced and billed in USD only | N/A |
| PricingCurrencyListUnitPrice | Conditional | N/A | N/A |
| PricingCurrencyContractedUnitPrice | Conditional | N/A | N/A |
| PricingCurrencyEffectiveCost | Conditional | N/A | N/A |
| SkuMeter | Conditional | Not exposed: "Managed vCPUs" | Missing: Conditional |
| SkuPriceId | Conditional | Not exposed | Missing: Conditional |
| SkuPriceDetails | Conditional | Not exposed; needed to state the SBU-to-vCPU conversion and measurement basis | Missing: Conditional |
| RegionId | Conditional | N/A: no region-based pricing | N/A |
| RegionName | Conditional | N/A | N/A |
| CommitmentDiscountId | Conditional | N/A: annual SBU commitment carries no rate discount (overage billed at the same rate) | N/A |
| CommitmentDiscountName | Conditional | N/A | N/A |
| CommitmentDiscountType | Conditional | N/A | N/A |
| CommitmentDiscountCategory | Conditional | N/A | N/A |
| CommitmentDiscountStatus | Conditional | N/A | N/A |
| CommitmentDiscountQuantity | Conditional | N/A | N/A |
| CommitmentDiscountUnit | Conditional | N/A | N/A |
| CapacityReservationId | Conditional | N/A: no capacity reservations | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | Invoice number | Present |
| ChargeFrequency | Recommended | Derive: "Recurring" for the annual commitment; "Usage-Based" for consumption and overage | Deviation |
| ServiceSubcategory | Recommended | Not exposed; map to "Cost Management" | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: no zones | N/A |

**Tally:** 15 Present, 8 Deviation, 2 Missing Mandatory, 14 Missing Conditional, 1 Missing Recommended, 17 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Billing account, currency, service periods, invoiced and contracted amounts, contracted SBU rate, line descriptions, and invoice numbers exist on Sedai's invoices and order forms.

**Substantive (1 of 2 Mandatory gaps):**

- **EffectiveCost.** The annual SBU commitment is paid ahead of use. Producing EffectiveCost means amortizing that prepayment across the SBUs consumed in each period and allocating any credits back to the charges they offset. That requires per-period consumption data no Sedai output exposes today.

**Trivial (1 of 2 Mandatory gaps):**

- **ListCost.** Sedai owns its price book. Define a list SBU rate (or document that ListUnitPrice equals the contracted rate where no list rate exists) and multiply by PricingQuantity.

**Substantive, beyond the column table:**

- **No delivery path.** No billing API, usage export, or invoice API is documented. A FOCUS dataset needs an API or scheduled object-storage drop.
- **No consumption view.** Sedai meters managed vCPUs to bill overage but shows customers no SBU usage by period. Without it, customers cannot see how fast they burn the commitment or forecast overage.
- **Allocation.** One invoice line per contract cannot be charged back. Sedai already knows which cluster, workload, and cloud account each managed vCPU belongs to and which tags it carries; emitting those as ResourceId, SubAccountId, and Tags is the most useful single addition.
- **Two channels.** Marketplace buyers see Sedai charges in AWS billing data, invoiced by AWS; direct customers see a Sedai invoice. A Sedai FOCUS export should cover consumption for both, with InvoiceIssuerName set per channel so neither double-counts the purchase.

**On the consumer side.** Sedai's AWS onboarding accepts FOCUS 1.0 but prefers legacy CUR "because it contains more data for calculating discounts," and reads monthly data only by default. Its Azure onboarding does not name the export type, and no GCP billing onboarding is documented. Moving AWS ingestion to the current FOCUS version, which carries the commitment-discount columns Sedai needs, and accepting FOCUS exports from Azure and GCP would remove three provider-specific parsers.

### 1.5 Deviations to Fix

**ChargePeriodStart and ChargePeriodEnd:** Emit Usage rows per day or month, not per contract term. Keep the Purchase row on the term.

**ChargeCategory:** "Purchase" for the annual SBU commitment; "Usage" for consumption drawn against it and for overage; "Tax" and "Credit" from the invoice, so that BilledCost summed per InvoiceId equals the invoice total.

**ServiceCategory:** "Management and Governance" for the platform.

**PricingQuantity and PricingUnit:** "SBU" is a Sedai-defined unit. State the rate basis (average or peak managed vCPUs per month, or vCPU-hours) and express PricingUnit in FOCUS unit format. Populate PricingQuantity on every Usage and overage row, not only the Purchase row.

**ChargeFrequency and PricingCategory:** "Recurring" for the annual commitment and "Usage-Based" for consumption; "Standard" pricing throughout.

**Already right:** USD-only billing, a single billing entity per customer, an explicit per-SBU contracted rate, and a unit (vCPUs) that converts cleanly to ConsumedQuantity.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (ratified June 4, 2026); certify at FOCUS v1.2, the version the conformance program currently names. FOCUS v1.5 is in release candidate with ratification scheduled for December 3, 2026. The Contract Commitment dataset (v1.3) fits Sedai's annual SBU commitment, and the Invoice Detail dataset (v1.4) fits its invoice reconciliation.

### 2.2 What Certification Requires

FinOps Certified FOCUS v1.2 Conformant runs through the FinOps Foundation (contact `member-cert@finops.org` for the RFI; membership is required for certification). Deliverables: a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report seeded by this analysis. Tooling: FOCUS Validator, FOCUS Converter, and the FOCUS Requirements Model. Document the N/A rationale (no regions, reservations, alternate currencies, or rate-discounted commitments) and the decision to treat the SBU commitment as a prepaid purchase.

### 2.3 Phased Roadmap

**Phase 0: Validate.** Pull one month of internal SBU metering for a direct customer and a Marketplace customer. Hand-build a FOCUS file from it plus the invoice and run it through the Validator. Fix the PricingUnit rate basis.

**Phase 1: Close Mandatory gaps.** Define the list SBU rate for ListCost and ListUnitPrice. Emit per-period Usage rows and amortize the annual commitment across them for EffectiveCost. Add Tax and Credit rows so BilledCost reconciles to the invoice.

**Phase 2: Fix deviations.** Derive ChargeCategory, ServiceCategory, ChargeFrequency, and PricingCategory; normalize PricingUnit; populate PricingQuantity and per-period charge periods on every Usage row.

**Phase 3: Allocation and delivery.** Add ResourceId, ResourceName, and ResourceType for each managed resource; SubAccountId, SubAccountName, and SubAccountType for the connected cloud account; Tags from the managed resource's cloud tags and Kubernetes labels; ConsumedQuantity and ConsumedUnit; SkuId, SkuMeter, SkuPriceId, and SkuPriceDetails; ServiceSubcategory. Ship an API or scheduled export, and expose it through the MCP server.

**Phase 4: Mature and certify.** Drop ProviderName and PublisherName for v1.4; add the Contract Commitment and Invoice Detail datasets; certify at v1.2 and re-certify as the program advances. In parallel, move AWS ingestion to current FOCUS and accept FOCUS from Azure and GCP.

### 2.4 FOCUS Use Cases Unlocked

- **After Phase 1:** Invoice reconciliation, amortized spend reporting, and actuals-based budgeting for the Sedai line item.
- **After Phase 2:** Spend by service category across providers, and commitment burn-down and overage forecasting.
- **After Phase 3:** Chargeback and showback of Sedai fees to the teams and cloud accounts whose resources it manages, unit economics (Sedai cost per managed vCPU against savings delivered), and anomaly detection on managed-vCPU growth.
- **Out of scope:** Region-based analysis, capacity reservation management, and commitment-discount utilization (no rate-discounted commitment).

---

## Part 3: Immediate Next Steps

1. Follow up with the Sedai contact from KubeCon NA 2026 to identify the owner of billing and SBU metering.
2. Confirm the SBU measurement basis (average vs. peak managed vCPUs), whether an uncommitted rate exists, and the invoicing legal entity.
3. Build a v1.2 sample from one month of metering plus the invoice and run it through the FOCUS Validator.
4. Agree on the commitment model (prepaid purchase vs. commitment discount) and the Marketplace versus direct row design.
5. Open the RFI with `member-cert@finops.org`.

---

## Confidence Summary

- **High:** Sedai bills 1 SBU per managed vCPU under a fixed annual commitment, with overage at the same rate and custom quotes. Its public docs describe no billing API, usage export, or invoice API for its own charges.
- **High:** Sedai's AWS FinOps onboarding accepts "Focus 1.0 (Standard Data Export)" and prefers legacy CUR; it reads monthly data by default.
- **High:** Feature levels match the FOCUS v1.2 Content Constraints; spot-checked against the live spec on November 17, 2026, and v1.4 remains the latest ratified version.
- **Moderate:** Present status for invoice-sourced columns. Sedai's invoice layout is not public, so these follow standard SaaS invoice content.
- **Moderate:** Treating the annual SBU commitment as a prepaid purchase. If Sedai's committed rate is below an uncommitted rate, the seven CommitmentDiscount columns become applicable and PricingCategory becomes "Committed" for drawn-down usage.
- **Moderate:** "Cost Management" as the ServiceSubcategory value. Confirm it against the v1.2 allowed values before mapping.
- **Low:** InvoiceIssuerName as "Sedai, Inc." No public page names the invoicing entity.
- **Low:** USD-only billing. Sedai publishes no currency terms; non-USD contracts would make the PricingCurrency columns applicable.

---

## Sources

- Sedai Pricing: [sedai.io/pricing](https://www.sedai.io/pricing)
- Sedai Docs: [docs.sedai.io/get-started](https://docs.sedai.io/get-started)
- Sedai Augmented FinOps: [docs.sedai.io/get-started/onboarding/augmented-finops](https://docs.sedai.io/get-started/onboarding/augmented-finops.md)
- Sedai AWS FinOps Onboarding: [docs.sedai.io/.../aws-finops-onboarding](https://docs.sedai.io/get-started/onboarding/augmented-finops/aws-finops-onboarding.md)
- Sedai Connect AWS Billing Account: [docs.sedai.io/.../connect-aws-billing-account](https://docs.sedai.io/get-started/onboarding/augmented-finops/connect-aws-billing-account.md)
- Sedai Connect Azure Billing Account: [docs.sedai.io/.../connect-azure-billing-account](https://docs.sedai.io/get-started/onboarding/augmented-finops/connect-azure-billing-account.md)
- Sedai Integrations: [docs.sedai.io/get-started/platform/integrations](https://docs.sedai.io/get-started/platform/integrations.md)
- Sedai Tag Configuration: [docs.sedai.io/.../tag-configuration](https://docs.sedai.io/get-started/platform/settings/features/tag-configuration.md)
- Sedai Groups: [docs.sedai.io/get-started/platform/settings/groups](https://docs.sedai.io/get-started/platform/settings/groups.md)
- Sedai MCP Server: [sedai.io/platform/mcp](https://sedai.io/platform/mcp.md)
- Sedai on AWS Marketplace: [aws.amazon.com/marketplace/pp/prodview-6jog5c3bqub2e](https://aws.amazon.com/marketplace/pp/prodview-6jog5c3bqub2e)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FOCUS 1.5 Release Scope: [focus.finops.org/focus-1-5-release-scope/](https://focus.finops.org/focus-1-5-release-scope/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
