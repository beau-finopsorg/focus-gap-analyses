# Echo & FOCUS: Data Generator Gap Analysis

*Analysis run: November 17, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** Echo Software Ltd. (Echo, Inc. in the echo.ai site footer)  
**Prepared:** November 17, 2026  
**Origin:** KubeCon NA 2026 booth outreach  
**Source:** Echo pricing page and FAQ; echo.ai product pages (Container Images, Integrations, image catalog); echo.ai Terms of Use; press coverage of the Series A and the Minimus asset acquisition  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 17 Present, 6 Deviation, 2 Missing Mandatory, 10 Missing Conditional, 1 Missing Recommended, 21 N/A

> **Public billing docs are thin.** Echo publishes no prices, no billing or usage export, no invoice format, no billing or registry API, and no account hierarchy. Its product docs (docs.echohq.com) sit behind a customer login. The only public billing facts are two quote-based pricing models (per artifact, or all-access priced by engineering headcount) and a statement that Echo sells through the AWS, Azure, and GCP marketplaces. The column table below is therefore mapped against what a standard SaaS invoice and order form would carry, not against any documented Echo schema. Treat every "Present" status as provisional until Echo shares a sample invoice and whatever usage view the customer portal provides.

---

## Executive Summary

Echo sells hardened, CVE-free software artifacts: container base images (including FIPS 140-3 and STIG-hardened variants), language libraries, VM images, serverless runtimes, and OS packages, plus Helm charts and end-of-life support. Images are rebuilt continuously, ship with SBOM, provenance, and VEX, and are mirrored into the customer's own registry (ECR, ACR, Artifact Registry, JFrog, Docker Hub, GitHub Packages, Nexus, Harbor, Quay). Echo raised a $35M Series A in December 2025 and acquired Minimus's hardened-image assets in August 2026.

Pricing is custom-quoted under one of two models: **pay per artifact**, or **access to all artifacts priced by the size of the engineering organization**, where an engineer is "any individual who has made a commit to a private repository within the last 180 days." A startup plan exists. Customers can switch models as their contract permits. Echo also sells through cloud marketplaces.

This is a contract-subscription vendor with no published data surface. Mapped against assumed invoice content, 17 of 57 FOCUS v1.2 columns map directly and 19 of 21 Mandatory columns have a likely source. **EffectiveCost** is the substantive Mandatory gap: subscriptions are contracted for a term and invoiced up front, so a FOCUS dataset must amortize them into per-period rows, and no per-period data exists today. **ListCost** is trivial once Echo defines a list rate per artifact and per engineer; until then it equals ContractedCost.

The larger gaps sit outside the column table. Echo has no machine-readable billing delivery at all, no per-period granularity, and no allocation: neither the artifacts a customer consumes nor the engineer count that drives the all-access price is exposed alongside cost. For marketplace buyers, the hyperscaler's own FOCUS export is the only FOCUS-shaped record of Echo spend today, with the cloud provider as invoice issuer.

**Recommendation:** Publish a monthly FOCUS export per customer from the Echo portal: one Purchase row per subscription term, monthly rows carrying amortized EffectiveCost, one row per entitled artifact under the per-artifact model (ResourceId = artifact), and the measured engineer count as ConsumedQuantity under the all-access model, plus Tax and Credit rows so the dataset reconciles to the invoice. Deliver it through an API or a scheduled object-storage drop.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

Echo publishes no billing data interface. The material available for a FOCUS mapping:

- **Pricing page and FAQ:** Two models, pay per artifact or all-access priced by engineering-organization size. Exact prices by custom quote. Startup plan by contacting sales. Switching models allowed within contract terms. No published prices, free tier, or billing cadence.
- **Invoices and order forms (direct contracts):** Not publicly documented. The analysis assumes a standard SaaS invoice: invoice number, customer, service term, line description (product and pricing model), quantity (artifacts or engineers), unit price, amount, and currency.
- **Customer portal (app.echohq.com) and docs (docs.echohq.com):** Both require a login. Nothing public describes a billing page, usage view, export, or API.
- **Marketplaces:** The pricing FAQ says Echo supports "all of the popular marketplaces, including AWS, Azure, and GCP"; the Integrations page lists AWS and Azure Marketplace as "Available for consumption." Marketplace purchases reach the buyer as line items in the cloud provider's billing data, invoiced by the cloud provider.
- **Product telemetry:** Echo must measure engineer headcount (private-repository committers over 180 days) to price the all-access model, and must know which artifacts each customer is entitled to under the per-artifact model. Neither measure is exposed with cost.

Key characteristics:

- **Products:** Echo Containers, Echo Libraries, Echo VMs, Echo Serverless, Echo OS Packages, and Echo Frontier; Helm charts and EOL support in the ecosystem.
- **Pricing units:** Artifacts (per-artifact model) or engineers (all-access model).
- **Commercial terms:** Custom quotes and contracts; no public list price.
- **Delivery:** Images mirrored into the customer's registry; no Echo-hosted regions or zones in the pricing.
- **Entity:** The Terms of Use name Echo Software Ltd. under Israeli law; the site footer reads Echo, Inc.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven: every Mandatory column must be present and valid, and Conditional columns are required when the provider's model triggers their condition. Three modeling decisions drive this analysis:

- **The contract is a prepaid subscription, not a commitment discount.** FOCUS defines a commitment discount as reduced rates in exchange for a commitment. Echo publishes no uncommitted rate, so no discount is visible, and the seven CommitmentDiscount columns are N/A. EffectiveCost still has to amortize the prepayment across the service term. From v1.3 the Contract Commitment dataset is the natural home for the contract itself.
- **Artifacts are the resources behind per-artifact charges.** Each entitled image, library, or VM image is what the customer pays for, so ResourceId, ResourceName, and ResourceType are Missing, not N/A.
- **Engineer headcount is a measured quantity.** The all-access price depends on a rolling 180-day committer count that Echo measures, so ConsumedQuantity and ConsumedUnit are Missing, not N/A.

Echo has no documented sub-account hierarchy, billing tags, regions, zones, capacity reservations, alternate pricing currencies, or multiple billing-account types; those columns are N/A and should exist as null. Feature levels follow the FOCUS v1.2 Content Constraints, spot-checked against the live spec on November 17, 2026.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | Echo source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Invoice line amount (direct contracts) | Present |
| EffectiveCost | Mandatory | Not available: needs the up-front subscription amortized across the service term, plus credit allocation | Missing: Mandatory |
| ListCost | Mandatory | Not available: no list price exists; define list rates per artifact and per engineer, or set equal to ContractedCost | Missing: Mandatory |
| ContractedCost | Mandatory | Invoice unit price × quantity (custom-quoted rate) | Present |
| BillingAccountId | Mandatory | Echo customer or organization identifier on the invoice and in the portal | Present |
| BillingAccountName | Mandatory | Customer legal or organization name | Present |
| BillingCurrency | Mandatory | Invoice currency (USD assumed) | Present |
| BillingPeriodStart | Mandatory | Invoice billing period start | Present |
| BillingPeriodEnd | Mandatory | Invoice billing period end | Present |
| ChargePeriodStart | Mandatory | Service term start on the invoice line | Present |
| ChargePeriodEnd | Mandatory | Service term end on the invoice line | Present |
| ChargeDescription | Mandatory | Invoice line description | Present |
| ChargeCategory | Mandatory | Derive: "Purchase" for subscriptions; "Tax" and "Credit" rows from the invoice | Deviation |
| ChargeClass | Mandatory (nullable) | null; "Correction" for re-issued charges | Present |
| InvoiceIssuerName | Mandatory | "Echo Software Ltd." for direct contracts; the cloud provider for marketplace purchases | Present |
| ProviderName | Mandatory (dep. v1.3) | "Echo" | Present |
| PublisherName | Mandatory (dep. v1.3) | "Echo" | Present |
| ServiceName | Mandatory | Product name (e.g., "Echo Containers", "Echo Libraries", "Echo VMs", "Echo Serverless", "Echo OS Packages") | Present |
| ServiceCategory | Mandatory | Derive: "Security" for all products | Deviation |
| PricingQuantity | Mandatory | Invoice quantity (artifacts or engineers); must be non-null on every non-Tax row | Deviation |
| PricingUnit | Mandatory | Normalize: "Artifacts" or "Engineers" | Deviation |
| ConsumedQuantity | Conditional | Not exposed: measured engineer count (180-day committers) or artifacts in use | Missing: Conditional |
| ConsumedUnit | Conditional | Not exposed | Missing: Conditional |
| ListUnitPrice | Conditional | Not available: no public price list | Missing: Conditional |
| ContractedUnitPrice | Conditional | Invoice unit price | Present |
| PricingCategory | Conditional | Derive: "Standard" | Deviation |
| BillingAccountType | Conditional | N/A: single customer account type | N/A |
| SubAccountId | Conditional | N/A: no documented sub-account hierarchy | N/A |
| SubAccountName | Conditional | N/A | N/A |
| SubAccountType | Conditional | N/A | N/A |
| ResourceId | Conditional | Not exposed: candidate is the artifact identifier (e.g., image name such as "golang-fips") | Missing: Conditional |
| ResourceName | Conditional | Not exposed | Missing: Conditional |
| ResourceType | Conditional | Not exposed (e.g., "Container Image", "Library", "VM Image") | Missing: Conditional |
| SkuId | Conditional | Not exposed; internal product and pricing-model codes | Missing: Conditional |
| Tags | Conditional | N/A: no billing tags or labels | N/A |
| PricingCurrency | Conditional | N/A: single pricing currency assumed | N/A |
| PricingCurrencyListUnitPrice | Conditional | N/A | N/A |
| PricingCurrencyContractedUnitPrice | Conditional | N/A | N/A |
| PricingCurrencyEffectiveCost | Conditional | N/A | N/A |
| SkuMeter | Conditional | Not exposed (e.g., "Engineers" for all-access, "Artifacts" for per-artifact) | Missing: Conditional |
| SkuPriceId | Conditional | Not exposed | Missing: Conditional |
| SkuPriceDetails | Conditional | Not exposed; needed to distinguish pricing model, artifact type, and startup plan | Missing: Conditional |
| RegionId | Conditional | N/A: no region-based pricing; images mirror into the customer's registry | N/A |
| RegionName | Conditional | N/A | N/A |
| CommitmentDiscountId | Conditional | N/A: prepaid subscription with no visible commitment discount | N/A |
| CommitmentDiscountName | Conditional | N/A | N/A |
| CommitmentDiscountType | Conditional | N/A | N/A |
| CommitmentDiscountCategory | Conditional | N/A | N/A |
| CommitmentDiscountStatus | Conditional | N/A | N/A |
| CommitmentDiscountQuantity | Conditional | N/A | N/A |
| CommitmentDiscountUnit | Conditional | N/A | N/A |
| CapacityReservationId | Conditional | N/A: no capacity reservations | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | Invoice number | Present |
| ChargeFrequency | Recommended | Derive: "Recurring" for subscriptions | Deviation |
| ServiceSubcategory | Recommended | Not exposed; map each product to an allowed v1.2 Security subcategory | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: no zones | N/A |

**Tally:** 17 Present, 6 Deviation, 2 Missing Mandatory, 10 Missing Conditional, 1 Missing Recommended, 21 N/A

### 1.4 What Is Solved, and What Remains

**Solved (provisionally):** Billing account, currency, billing and service periods, invoice line descriptions, contracted unit prices, invoice numbers, and product names should all exist on Echo's invoices. None is publicly documented.

**Substantive (1 of 2 Mandatory gaps):**

- **EffectiveCost.** Subscriptions are contracted for a term and invoiced ahead of use. Producing EffectiveCost means splitting each purchase into per-period rows across its service term and allocating any credits back to the charges they offset. Echo exposes no per-period data today.

**Trivial (1 of 2 Mandatory gaps):**

- **ListCost.** Echo owns its pricing. Once it sets a list rate per artifact and per engineer, ListCost is that rate × PricingQuantity. Without a list rate, ListCost equals ContractedCost.

**Substantive, beyond the column table:**

- **No delivery path.** No billing API, usage export, or documented portal view exists. Nothing about Echo's own charges reaches a FinOps tool except invoice PDFs and, for marketplace buyers, the hyperscaler's billing data.
- **No granularity.** A term subscription invoiced once gives one row per term. FinOps tools need at least monthly rows.
- **No allocation.** Under the per-artifact model, the artifact is the natural allocation key; under all-access, the engineer count is. Neither is exposed with cost, so customers cannot charge Echo spend back to the teams that consume the images.
- **Marketplace split.** Marketplace purchases carry the cloud provider as invoice issuer and appear only in that provider's export. A customer buying partly direct and partly through a marketplace has no single view.

### 1.5 Deviations to Fix

**ChargeCategory:** "Purchase" for subscription lines; "Tax" and "Credit" rows broken out so that BilledCost summed per InvoiceId equals the invoice total.

**ServiceCategory and ServiceSubcategory:** "Security" for every product. Map each product to an allowed v1.2 Security subcategory and confirm the choice against the spec's value list.

**PricingQuantity and PricingUnit:** Every non-Tax row needs a quantity: entitled artifacts under the per-artifact model, engineers under all-access. Use "Artifacts" and "Engineers" consistently. If the engineer count is re-measured during the term, PricingQuantity must reflect the contracted count, with ConsumedQuantity carrying the measured one.

**ChargeFrequency and PricingCategory:** "Recurring" and "Standard" for subscriptions.

**Already right:** Echo's two pricing units (artifacts and engineers) are concrete, countable, and map cleanly to FOCUS quantity and unit columns once exposed.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (ratified June 4, 2026); certify at FOCUS v1.2, the version the conformance program currently names. FOCUS v1.5 is in release candidate with ratification scheduled for December 3, 2026. The v1.3 Contract Commitment dataset fits Echo's term contracts, and the v1.4 Invoice Detail dataset fits an invoice-centric vendor with no usage feed.

### 2.2 What Certification Requires

FinOps Certified FOCUS v1.2 Conformant runs through the FinOps Foundation (contact `member-cert@finops.org` for the RFI; membership is required for certification). Deliverables: a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report seeded by this analysis. Tooling: FOCUS Validator, FOCUS Converter, and the FOCUS Requirements Model. Document the N/A rationale (no sub-accounts, tags, regions, reservations, commitment discounts, or alternate currencies) and the decision to model contracts as prepaid subscriptions.

### 2.3 Phased Roadmap

**Phase 0: Validate.** Obtain one sample invoice and order form for each pricing model. Confirm the invoicing entity, currency, and what the customer portal shows. Hand-build a v1.2 file from them and run it through the Validator.

**Phase 1: Close Mandatory gaps and ship a feed.** Generate monthly rows per subscription with amortized EffectiveCost. Set ListCost from a defined list rate or equal to ContractedCost. Add Tax and Credit rows. Deliver the file through the portal, an API, or a scheduled object-storage drop.

**Phase 2: Fix deviations.** Derive ChargeCategory, ServiceCategory, ChargeFrequency, and PricingCategory; normalize PricingUnit; populate PricingQuantity on every non-Tax row.

**Phase 3: Allocation and Conditional columns.** Add ResourceId, ResourceName, and ResourceType per artifact; ConsumedQuantity and ConsumedUnit for measured engineer counts; SkuId, SkuMeter, SkuPriceId, and SkuPriceDetails; ListUnitPrice; and ServiceSubcategory.

**Phase 4: Mature and certify.** Drop ProviderName and PublisherName for v1.4; add the Contract Commitment and Invoice Detail datasets; certify at v1.2 and re-certify as the program advances.

### 2.4 FOCUS Use Cases Unlocked

- **After Phase 1:** Invoice reconciliation, amortized spend reporting, and actuals-based budgeting for Echo alongside cloud spend.
- **After Phase 2:** Spend by service category across providers (Echo as Security spend).
- **After Phase 3:** Chargeback and showback by artifact, unit cost per image or per engineer, and tracking engineer-count growth against the all-access price.
- **Out of scope:** Region analysis, capacity reservation management, commitment discount utilization, and tag-based allocation.

---

## Part 3: Immediate Next Steps

1. Follow up on the KubeCon booth conversation and request a sample invoice and order form for each pricing model.
2. Confirm the invoicing entity (Echo Software Ltd. or Echo, Inc.), billing currencies, and how engineer counts are measured and trued up.
3. Ask what billing or usage data the customer portal shows today and whether any export exists.
4. Build a v1.2 sample from one contract and run it through the FOCUS Validator.
5. Open the RFI with `member-cert@finops.org`.

---

## Confidence Summary

- **High:** Echo publishes no prices, billing or usage export, invoice format, or billing API; its docs require a login. The two pricing models and the engineer definition come from Echo's pricing page.
- **High:** Feature levels match the FOCUS v1.2 Content Constraints; the bundled table was spot-checked against the live spec on November 17, 2026, and v1.4 remains the latest ratified version.
- **Moderate:** Present status for invoice-sourced columns. No Echo invoice is public, so presence assumes standard SaaS invoice content.
- **Moderate:** Treating contracts as prepaid subscriptions rather than commitment discounts. If Echo discounts committed terms against a published rate, the CommitmentDiscount family becomes applicable.
- **Low:** InvoiceIssuerName. The Terms of Use name Echo Software Ltd.; the site footer names Echo, Inc. Either may invoice, depending on customer location.
- **Low:** USD as the sole billing currency. Nothing public states it.
- **Low:** Marketplace mechanics. Echo claims AWS, Azure, and GCP marketplace support but lists only AWS and Azure on its Integrations page; no listing's pricing dimensions were verified.

---

## Sources

- Echo Pricing: [echo.ai/pricing](https://www.echo.ai/pricing)
- Echo Container Images: [echo.ai/product/container-images](https://www.echo.ai/product/container-images)
- Echo Integrations: [echo.ai/product/integrations](https://www.echo.ai/product/integrations)
- Echo Image Catalog: [echo.ai/image-pulling](https://www.echo.ai/image-pulling)
- Echo Terms of Use: [echo.ai/legal/terms-of-use](https://www.echo.ai/legal/terms-of-use)
- SiliconANGLE, Series A (December 16, 2025): [siliconangle.com](https://siliconangle.com/2025/12/16/vulnerability-free-container-image-startup-echo-software-raises-35m/)
- Cloud Native Now, Minimus asset acquisition: [cloudnativenow.com](https://cloudnativenow.com/features/echo-acquires-hardened-container-assets-from-minimus/)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FOCUS 1.5 Release Scope: [focus.finops.org/focus-1-5-release-scope/](https://focus.finops.org/focus-1-5-release-scope/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
