# Harness & FOCUS: Data Generator Gap Analysis

*Analysis run: November 17, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** Harness Inc.  
**Prepared:** November 17, 2026  
**Origin:** KubeCon NA 2026 booth outreach  
**Source:** Public Harness documentation only: Harness pricing page; Developer 360 pricing announcement; Subscriptions and Licenses docs (Account Settings > Subscriptions, Cloud Credits); CI subscription and Harness Cloud credit docs; Cloud Marketplace offerings docs; Cloud & AI Cost Management (CACM) Custom Cost Provider and data ingestion reference  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 16 Present, 8 Deviation, 3 Missing Mandatory, 19 Missing Conditional, 1 Missing Recommended, 10 N/A

---

## Executive Summary

Harness sells a software delivery platform: Continuous Integration, Continuous Delivery & GitOps, Infrastructure as Code Management (IACM), Security Testing Orchestration (STO), Supply Chain Security (SCS), Feature Management & Experimentation (FME), Internal Developer Portal (IDP), Chaos Engineering, Service Reliability Management (SRM), Database DevOps, Software Engineering Insights, and Cloud & AI Cost Management (CACM, formerly CCM). It bills on four meters at once: per-developer licenses ("Developer 360"), consumption entitlements bundled with those licenses (services, executions, scans), CACM licensed on managed cloud spend, and Harness Cloud credits drawn down per build minute.

**Public billing documentation is thin.** Harness publishes no billing API, no invoice field definitions, and no usage export. The richest surface is the in-app **Cloud Credits** page, which breaks credit usage down by organization, project, and resource class, and even that sits behind a feature flag (`PL_ENABLE_LICENSE_USAGE_COMPUTE`). Plan names are inconsistent across Harness's own pages (Free/Enterprise in the docs, Free/Essentials/Enterprise on the pricing page, Free/Startup/Enterprise in the CI limits tables), and Essentials and Enterprise are "priced by quotation." Every Present status below rests on in-app pages and standard invoicing, not on a documented data contract.

Harness touches FOCUS in two directions:

1. **Harness as a data generator for its own charges.** Weak. Of the 21 Mandatory columns, 18 have a source and 3 are missing. One gap is substantive: **EffectiveCost**, because licenses are contracted up front and Harness Cloud credits are prepaid, roll over, and expire after a year. **ListCost** and **ContractedCost** are price-book joins.
2. **Harness as a FOCUS consumer.** CACM's Custom Cost Provider ingests third-party spend as a FOCUS CSV. It references FOCUS v1.1, lists 17 columns as "mandatory," and omits BilledCost, ListCost, and BillingCurrency. It lags the spec by three releases.

The irony is the headline. A Harness customer can load a SaaS vendor's FOCUS file into Harness CACM, but cannot load Harness's own bill, including the CACM license itself, because Harness does not produce one.

**Recommendation:** Turn the Cloud Credits breakdown into a monthly FOCUS export per account: one Usage row per resource class × project × day for credit consumption, Purchase rows for license terms and credit packs, a CommitmentDiscount draw-down against prepaid credits, and Tax and Credit rows so the dataset reconciles to the invoice. Publish it through the same API surface CACM already uses, and let CACM ingest it natively as the reference implementation.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

Harness's own billing data (the subject of the column table):

- **Account Settings > Subscriptions:** Plan type, subscribed limits, start and expiry dates, developer license counts, consumption entitlements, and "License Utilization" (users over licenses). Payment details and billing admins live under Account Settings > Billing. Self-service "is not available for all modules." No export is documented.
- **Cloud Credits page** (feature flag `PL_ENABLE_LICENSE_USAGE_COMPUTE`): "Available Credits," "Month-to-date Credit Usage," "Next Expiry Date," and "Credit Overage"; a **Credits Breakdown** by organization, project, or resource class with date filters; and a **Credits Allocation** table with Start Date, Expiry Date, Type (Free, Team, Enterprise), Quota, Used, Available, and Status. No pipeline-level breakdown is documented.
- **Invoices:** Credit overages are invoiced in arrears and due within 30 days. No public invoice sample or field list. No documented invoice download API.
- **Pricing page:** Prices in USD. Free is $0; Essentials (CD & GitOps, CI, IACM, STO; one organization, up to 500 users) and Enterprise are priced by quotation.
- **Harness Cloud credit rates** (effective September 1, 2026): credits = execution minutes × minute multiplier, at $0.005 per credit. Linux AMD64 runs from xsmall (×1, $0.005 per minute) to xxxlarge (×48, $0.24 per minute); Windows from small (×4) to xxxlarge (×96); macOS ARM64 M4 medium is ×36 ($0.18 per minute).

Harness's FOCUS intake for third-party spend (assessed separately in 1.4):

- **CACM Custom Cost Provider:** UI upload of a FOCUS CSV (20 MB per file) under External Cost Data Sources. Data feeds Perspectives, Budgets, Cost Categories, and the Unified BI dashboard source.

Key characteristics:

- **Meters:** Developer licenses (CODE, CI, IDP, AIDI, FME count developers directly). Consumption entitlements per developer: 1 service per 3 developers (CD & GitOps, SRM, Chaos), 120 IACM executions per developer per year, 100 STO scans and 100 SCS executions per developer per month; add-ons purchasable. Database DevOps is licensed per database instance. CACM is "licensed as a Monthly/Annual Cloud Spend that is managed and optimized via Harness."
- **Credits:** Free plans get 2,000 credits per month, expiring at month end. Paid credits roll over month to month and generally expire one year from purchase. Usage beyond the pool is allowed and invoiced in arrears.
- **Hierarchy:** Account > Organization > Project. Credit usage is already attributed to organization and project.
- **Marketplaces:** AWS Marketplace (contract purchase, then a CSM provisions the license) and Google Cloud Marketplace (Software Delivery Platform as private offer; Continuous Delivery as private or public offer). Azure Marketplace is not listed.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven: every Mandatory column must be present and valid, and Conditional columns are required when the provider's model triggers their condition. Harness groups usage into organizations and projects and already attributes credit consumption to them, so the SubAccount family applies. Prepaid Harness Cloud credits are a spend commitment drawn down by usage with overage billed at a separate rate, so this analysis treats the CommitmentDiscount family as applicable. Harness has one billing account type, no customer-selected pricing regions or zones in any billing surface, no capacity reservations, and USD-only pricing; those columns are N/A and should exist as null. Feature levels follow the FOCUS v1.2 Content Constraints.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | Harness source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Invoice amount; no line-level export per module, meter, or project | Deviation |
| EffectiveCost | Mandatory | Not available: needs amortization of up-front license terms and prepaid credit packs, and allocation of free monthly credits | Missing: Mandatory |
| ListCost | Mandatory | Not exposed; credit price ($0.005) × credits is public, license prices are quoted | Missing: Mandatory |
| ContractedCost | Mandatory | Not exposed; contract rate card × PricingQuantity | Missing: Mandatory |
| BillingAccountId | Mandatory | Harness account ID | Present |
| BillingAccountName | Mandatory | Harness account name | Present |
| BillingCurrency | Mandatory | "USD" | Present |
| BillingPeriodStart | Mandatory | Invoice period start | Present |
| BillingPeriodEnd | Mandatory | Invoice period end (exclusive) | Present |
| ChargePeriodStart | Mandatory | Credits Breakdown date filter; license term start | Present |
| ChargePeriodEnd | Mandatory | Credits Breakdown date filter; license term end | Present |
| ChargeDescription | Mandatory | Invoice line description | Present |
| ChargeCategory | Mandatory | Derive: "Purchase" for license terms and credit packs; "Usage" for credit consumption and overage; "Tax" and "Credit" from the invoice | Deviation |
| ChargeClass | Mandatory (nullable) | null; "Correction" for re-issued charges | Present |
| InvoiceIssuerName | Mandatory | "Harness Inc." for direct; "Amazon Web Services" or "Google" for marketplace purchases | Present |
| ProviderName | Mandatory (dep. v1.3) | "Harness" | Present |
| PublisherName | Mandatory (dep. v1.3) | "Harness" | Present |
| ServiceName | Mandatory | Harness module (e.g., "Continuous Integration", "Continuous Delivery & GitOps", "Security Testing Orchestration", "Cloud & AI Cost Management", "Harness Cloud") | Present |
| ServiceCategory | Mandatory | Derive: "Developer Tools" for CI, CD, IACM, IDP, FME, Chaos, Database DevOps, and Harness Cloud; "Security" for STO and SCS; "Management and Governance" for CACM and SRM | Deviation |
| PricingQuantity | Mandatory | Developers, services, executions, scans, credits; credits are minutes × multiplier rounded to the minute, so compute against the credit, not the minute | Deviation |
| PricingUnit | Mandatory | Normalize: "Developers", "Services", "Executions", "Scans", "Credits", "Database Instances" | Deviation |
| ConsumedQuantity | Conditional | Subscriptions and Cloud Credits counts (developers in last 30 days, services, credits used) | Present |
| ConsumedUnit | Conditional | Implicit in the UI; normalize to FOCUS unit format ("Developers", "Minutes") | Deviation |
| ListUnitPrice | Conditional | Not in billing data; $0.005 per credit is public, license prices are not | Missing: Conditional |
| ContractedUnitPrice | Conditional | Not exposed; contract rates | Missing: Conditional |
| PricingCategory | Conditional | Derive: "Committed" for credits drawn from a prepaid pool; "Standard" for overage and licenses | Deviation |
| BillingAccountType | Conditional | N/A: one account type (Harness account) | N/A |
| SubAccountId | Conditional | Not in billing; Harness organization or project identifier (Credits Breakdown already groups by both) | Missing: Conditional |
| SubAccountName | Conditional | Not in billing; organization or project name | Missing: Conditional |
| SubAccountType | Conditional | Not in billing; "Organization" or "Project" | Missing: Conditional |
| ResourceId | Conditional | Not in billing; pipeline (credits), service (CD entitlements), or database instance (Database DevOps) | Missing: Conditional |
| ResourceName | Conditional | Not in billing; pipeline, service, or database instance name | Missing: Conditional |
| ResourceType | Conditional | Not in billing; "Pipeline", "Service", "Database Instance" | Missing: Conditional |
| SkuId | Conditional | Not exposed; plan, module, and resource class codes | Missing: Conditional |
| Tags | Conditional | Harness entity tags on pipelines, services, and projects are not carried into billing | Missing: Conditional |
| PricingCurrency | Conditional | N/A: priced and billed in USD only | N/A |
| PricingCurrencyListUnitPrice | Conditional | N/A | N/A |
| PricingCurrencyContractedUnitPrice | Conditional | N/A | N/A |
| PricingCurrencyEffectiveCost | Conditional | N/A | N/A |
| SkuMeter | Conditional | Resource class in Credits Breakdown (e.g., Linux AMD64 medium); license type in Subscriptions | Present |
| SkuPriceId | Conditional | Not exposed | Missing: Conditional |
| SkuPriceDetails | Conditional | Not exposed; the minute multiplier (×1 to ×96) and core/memory size belong here | Missing: Conditional |
| RegionId | Conditional | N/A: no region appears in any pricing or billing surface | N/A |
| RegionName | Conditional | N/A | N/A |
| CommitmentDiscountId | Conditional | Credit allocation (Credits Allocation table row); not exported | Missing: Conditional |
| CommitmentDiscountName | Conditional | Not exposed | Missing: Conditional |
| CommitmentDiscountType | Conditional | Not exposed (e.g., "Harness Cloud Credits") | Missing: Conditional |
| CommitmentDiscountCategory | Conditional | "Spend"; not exposed | Missing: Conditional |
| CommitmentDiscountStatus | Conditional | "Used"/"Unused"; Credits Allocation shows Used and Available but not per row | Missing: Conditional |
| CommitmentDiscountQuantity | Conditional | Credits drawn from the allocation | Missing: Conditional |
| CommitmentDiscountUnit | Conditional | "Credits" | Missing: Conditional |
| CapacityReservationId | Conditional | N/A: no capacity reservations | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | Invoice number | Present |
| ChargeFrequency | Recommended | Derive: "Recurring" for licenses and CACM; "One-Time" for credit packs; "Usage-Based" for credit consumption and overage | Deviation |
| ServiceSubcategory | Recommended | Not exposed; map each module to an allowed v1.2 value | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: Harness operates the build infrastructure; zones are not customer-billed | N/A |

**Tally:** 16 Present, 8 Deviation, 3 Missing Mandatory, 19 Missing Conditional, 1 Missing Recommended, 10 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Account identity, USD billing, invoice numbers, a public per-credit price and minute-multiplier table, license and entitlement counts, and credit usage already attributed to organization, project, and resource class. Harness has done the hard attribution work for Harness Cloud; it just keeps it in a UI.

**Substantive (1 of 3 Mandatory gaps):**

- **EffectiveCost.** Licenses are contracted for a term and credits are prepaid, roll over, and expire after a year. Producing EffectiveCost means amortizing license fees across the term, amortizing each credit pack across the credits actually drawn (with unused credits at expiry as a separate charge), and allocating the 2,000 free monthly credits on Free plans. No current surface does any of this.

**Trivial (2 of 3 Mandatory gaps):**

- **ListCost.** For Harness Cloud, credits × $0.005 from the public rate table. For licenses, Harness holds an internal price book behind every quote; expose it, or set ListCost to ContractedCost where no list price exists.
- **ContractedCost.** Harness's billing system already holds each Order Form's rate card; expose it per row.

**Substantive, beyond the column table:**

- **No billing data feed.** Subscriptions and Cloud Credits are UI-only, and Cloud Credits is feature-flagged. No API, export, or invoice field list is published. Nothing about Harness's own charges reaches a FinOps tool except invoice PDFs.
- **Developer licenses do not allocate cleanly.** A developer seat is not tied to a project in any documented surface, and license assignment is "an honor system." Chargeback of the largest line on most Harness invoices needs an allocation rule (e.g., developers active per project in the last 30 days) that Harness would have to define.
- **Marketplace split.** AWS and Google Cloud Marketplace buyers see Harness as one contract line in the hyperscaler's FOCUS data. A Harness export with InvoiceIssuerName set to the marketplace is the only way to break that line into modules and credits.

**Harness as a FOCUS consumer:**

CACM's Custom Cost Provider is welcome, but its intake contract deviates from the spec in ways that matter:

- **Version lag.** The doc says "FOCUSv1" and links the v1.1 PDF. v1.2, v1.3, and v1.4 have all been ratified since. No v1.2 SaaS columns (InvoiceId, pricing-currency columns, BillingAccountType) are mentioned.
- **Wrong columns required.** The 17 "mandatory" fields include EffectiveCost but omit BilledCost, ListCost, ContractedCost, BillingCurrency, ChargeDescription, ServiceCategory, PricingQuantity, and InvoiceIssuerName, all Mandatory in FOCUS. CACM therefore cannot reconcile ingested data to an invoice or tell amortized from billed spend.
- **Conditional treated as Mandatory.** RegionName, ResourceId, SkuId, SubAccountId, SubAccountName, and Tags are required on upload. A SaaS vendor with no regions or sub-accounts (most of them) must fabricate values or fail ingestion, which defeats the point of accepting a conformant file.
- **Manual, one-shot intake.** 20 MB UI uploads with no API or scheduled refresh. Anomaly detection on ingested data requires a support ticket.

Native AWS, GCP, and Azure ingestion reads CUR, BigQuery, and Cost Management exports; the docs do not say whether CACM reads the hyperscalers' own FOCUS exports.

### 1.5 Deviations to Fix

**BilledCost:** Emit one row per module, meter, and project rather than an invoice total, plus Tax and Credit rows, so that BilledCost summed per InvoiceId equals the invoice total.

**ChargeCategory:** "Purchase" for license terms, CACM, and credit packs; "Usage" for credit consumption and overage; "Tax" and "Credit" as above.

**ServiceCategory:** "Developer Tools" for CI, CD & GitOps, IACM, IDP, FME, Chaos, Database DevOps, and Harness Cloud; "Security" for STO and SCS; "Management and Governance" for CACM and SRM.

**PricingQuantity and PricingUnit:** Price Harness Cloud in "Credits," not minutes: PricingQuantity = rounded minutes × multiplier, ListUnitPrice = $0.005, and the multiplier goes in SkuPriceDetails. ConsumedQuantity carries the raw minutes. Licenses use "Developers" (or "Database Instances"); entitlement overages use "Services," "Executions," or "Scans."

**ConsumedUnit, PricingCategory, ChargeFrequency:** Derive from meter type as shown in the table.

**Already right:** USD-only billing, a published credit price and multiplier table, and an Account > Organization > Project hierarchy that maps directly to BillingAccount and SubAccount.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (ratified June 4, 2026); certify at FOCUS v1.2, the version the conformance program currently names. FOCUS v1.5 is a candidate release; its scope is on the FOCUS site. The v1.3 Contract Commitment dataset fits prepaid credit packs and multi-year license Order Forms better than per-row CommitmentDiscount columns alone. Upgrade the CACM intake to v1.2 or later in the same program so Harness can ingest its own export.

### 2.2 What Certification Requires

FinOps Certified FOCUS v1.2 Conformant runs through the FinOps Foundation (contact `member-cert@finops.org` for the RFI; membership is required for certification). Deliverables: a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report seeded by this analysis. Tooling: FOCUS Validator, FOCUS Converter, and the FOCUS Requirements Model. Document the N/A rationale (single account type, no billed regions, zones, reservations, or alternate currencies) and the decision on modeling prepaid credits as a commitment discount. Certification covers Harness's billing export as a data generator; CACM's intake is a consumer concern and is not certified.

### 2.3 Phased Roadmap

**Phase 0: Validate.** Pull one month of Subscriptions, Cloud Credits, and invoice data for a Free account and an Enterprise account with prepaid credits. Hand-build a v1.2 file and run it through the Validator. Decide the credit commitment model and the developer-license allocation rule.

**Phase 1: Close Mandatory gaps.** Join the credit rate table and internal price book for ListCost and ListUnitPrice, and the Order Form rate card for ContractedCost. Amortize license terms and credit packs for EffectiveCost. Emit line-level BilledCost with Tax and Credit rows so it reconciles to the invoice.

**Phase 2: Fix deviations.** Derive ChargeCategory, ServiceCategory, ChargeFrequency, and PricingCategory; price Harness Cloud in credits; normalize PricingUnit and ConsumedUnit.

**Phase 3: Allocation and Conditional columns.** Add SubAccountId, SubAccountName, and SubAccountType from organization and project; ResourceId, ResourceName, and ResourceType per pipeline, service, and database instance; Tags from Harness entity tags; SkuId, SkuPriceId, and SkuPriceDetails (minute multiplier); the CommitmentDiscount family for credit draw-down; and ServiceSubcategory. Deliver by API and scheduled push to object storage, and take the Cloud Credits page out from behind its feature flag.

**Phase 4: Mature and certify.** Drop ProviderName and PublisherName for v1.4; add the Invoice Detail dataset; certify at v1.2 and re-certify as the program advances. In parallel, bring CACM's Custom Cost Provider to v1.2+: require the spec's Mandatory columns, accept null Conditional columns, and add an ingestion API.

### 2.4 FOCUS Use Cases Unlocked

- **After Phase 1:** Invoice reconciliation, actuals-based budgeting and forecasting, and amortized spend reporting for Harness.
- **After Phase 2:** Spend by service category across providers, and license-versus-consumption mix analysis.
- **After Phase 3:** Chargeback and showback of Harness Cloud by organization, project, pipeline, or tag; unit economics per build minute and per pipeline run; prepaid credit utilization and expiry-risk tracking; and anomaly detection on credit burn by resource class.
- **Out of scope:** Capacity reservation management, regional cost analysis, and multi-currency analysis.

---

## Part 3: Immediate Next Steps

1. Follow up with the Harness contact from KubeCon NA 2026 to reach the owners of Harness billing and of CACM's Custom Cost Provider.
2. Confirm what invoices and the Cloud Credits page contain today (line items, per-project detail, export, general availability of the feature flag).
3. Confirm the current plan lineup and whether any license list prices are public.
4. Build a v1.2 sample from one billing month and run it through the FOCUS Validator.
5. Open the RFI with `member-cert@finops.org` and confirm FinOps Foundation membership status.

---

## Confidence Summary

- **High:** Harness Cloud credit mechanics (minute multipliers, $0.005 per credit, 2,000 free monthly credits, one-year expiry, overage in arrears) come from Harness's CI subscription docs.
- **High:** Developer 360 licensing and consumption entitlements per developer come from Harness's subscriptions docs and pricing announcement.
- **High:** CACM Custom Cost Provider references FOCUS v1.1, requires the 17 listed columns, and accepts 20 MB UI uploads only, per Harness's docs.
- **High:** Feature levels match the bundled FOCUS v1.2 Content Constraints table (verified June 23, 2026); v1.4 remains the latest ratified version and v1.5 is a candidate release. A live spot-check through the FOCUS MCP was not run for this analysis.
- **Moderate:** Present status for invoice-sourced columns (ChargeDescription, InvoiceId, billing periods). Harness publishes no invoice sample or field list, so presence is inferred from standard invoicing.
- **Moderate:** Treating prepaid Harness Cloud credits as a spend commitment discount. If Harness models them as simple prepayment with no rate benefit, the seven CommitmentDiscount columns become N/A and the amortization moves entirely into EffectiveCost.
- **Moderate:** ServiceCategory mappings; "Developer Tools," "Security," and "Management and Governance" are the closest v1.2 values.
- **Moderate:** USD-only pricing. The pricing page lists USD; non-USD Order Forms are not documented either way.
- **Low:** RegionId as N/A. Harness may run SaaS clusters or Harness Cloud capacity in customer-selectable regions; no billing surface shows one.
- **Low:** Current plan lineup and list prices. Harness's own pages disagree (Free/Enterprise, Free/Essentials/Enterprise, Free/Startup/Enterprise), and a $57 per developer per month Startup price appears only in third-party summaries.
- **Low:** InvoiceIssuerName as "Harness Inc." No public invoice names the issuing entity.

---

## Sources

- Harness Pricing: [harness.io/pricing](https://www.harness.io/pricing)
- Introducing Developer 360 Pricing by Harness: [harness.io/blog/introducing-developer-360-pricing-by-harness](https://www.harness.io/blog/introducing-developer-360-pricing-by-harness)
- Harness Subscriptions and Licenses: [developer.harness.io/docs/platform/subscriptions-licenses/subscriptions](https://developer.harness.io/docs/platform/subscriptions-licenses/subscriptions)
- CI Subscriptions and Harness Cloud Credits: [developer.harness.io/docs/continuous-integration/get-started/ci-subscription-mgmt/](https://developer.harness.io/docs/continuous-integration/get-started/ci-subscription-mgmt/)
- Cloud Marketplace Offerings: [developer.harness.io/harness-platform/subscriptions-and-licenses/cloud-marketplaces](https://developer.harness.io/harness-platform/subscriptions-and-licenses/cloud-marketplaces)
- CACM Custom Cost Provider: [developer.harness.io/cloud-cost-management/integrations/custom-cost-provider](https://developer.harness.io/cloud-cost-management/integrations/custom-cost-provider)
- CACM Data Ingestion Reference: [developer.harness.io/cloud-cost-management/resources/data-ingestion-reference](https://developer.harness.io/cloud-cost-management/resources/data-ingestion-reference)
- CloudZero, Harness Pricing (third-party summary): [cloudzero.com/blog/harness-pricing/](https://www.cloudzero.com/blog/harness-pricing/)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FOCUS 1.5 Release Scope: [focus.finops.org/focus-1-5-release-scope/](https://focus.finops.org/focus-1-5-release-scope/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
