# InfrOS & FOCUS: Data Generator Gap Analysis

*Analysis run: November 17, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** Infros, Inc. (website operator and contracting entity: Cloudculate Ltd., Israel)  
**Prepared:** November 17, 2026  
**Origin:** KubeCon NA 2026 booth outreach  
**Source:** InfrOS website (home, product, pricing, terms, privacy, about); InfrOS blog (MCP setup instructions, FinOps cost optimization agent on Amazon Bedrock AgentCore); AWS Marketplace listings "InfrOS" and "InfrOS on Nimbus"; Toolradar pricing summary  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 7 Present, 21 Deviation, 3 Missing Mandatory, 8 Missing Conditional, 1 Missing Recommended, 17 N/A

---

## Executive Summary

InfrOS is an AI platform that turns business and technical requirements into cloud architectures for AWS, Google Cloud, Azure, and Oracle Cloud. It generates candidate designs, scores them on cost, performance, security, reliability, and other criteria, simulates them, and exports production-ready Terraform with embedded FinOps and compliance guardrails, then watches for drift. It is SaaS, not infrastructure: InfrOS charges for design and code-generation work, and the cloud spend it designs lands on the customer's own cloud bills.

Pricing is a prepaid credit model. A design run costs 200 to 1,200 credits, an IaC export 100 to 400, and fixes and updates 50 to 400, scaled by complexity (number of clouds, business processes, compliance requirements, and availability zones). Credits belong to the organization, expire 12 months after purchase, and are non-refundable. The website lists only a 700-credit free trial and custom-priced Enterprise; self-serve plans and dollar prices appear only on two AWS Marketplace listings.

**Public billing documentation is thin.** InfrOS has no public documentation site (`docs.infros.io` does not resolve; `infros.io/docs` and `infros.io/faq` return 404). No billing API, usage export, CSV download, credit ledger, invoice format, or billing currency is documented for direct customers. The only billing surfaces described are a dashboard low-credit notification, an instant top-up, and a per-action credit quote from the InfrOS assistant before it spends credits. The website terms cover only the website and defer product terms to "other specific agreements," which are not public. This analysis therefore assesses what InfrOS's billing model could supply, not a dataset that exists today.

On that basis, of the 21 Mandatory columns, 7 map directly, 11 need derivation, and 3 are missing. **2 of the 3 missing Mandatory columns are substantive.** InfrOS prices in credits, not currency, and there is no single public price per credit: implied Marketplace rates run from $1.09 to $2.73 per credit, and Enterprise volumes carry custom discounts. ListCost needs InfrOS to define a list price per credit, and EffectiveCost needs every credit-consuming action traced back to the purchase that funded it. ContractedCost falls out of the same drawdown ledger.

The encouraging part: FOCUS v1.2 was built for this model. The PricingCurrency column family supports virtual currencies such as credits, so InfrOS can publish credit prices natively and convert to USD for the cost columns. And InfrOS already computes and quotes the credit cost of every action before running it, so the per-action ledger almost certainly exists internally.

**Recommendation:** Publish a FOCUS export per organization with Purchase rows for credit packs and subscriptions (BilledCost in USD) and Usage rows per credit-consuming action per system per day (BilledCost 0, PricingCurrency "InfrOS Credits", PricingCurrencyEffectiveCost in credits, EffectiveCost in USD from a first-in, first-out drawdown of the funding purchase), plus rows for expired credits. Deliver it as a dashboard CSV and through the existing MCP server's Read scope.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

- **Dashboard:** Shows a notification when credits run low and supports instant top-up. No usage history, credit ledger, invoice download, or export is documented.
- **InfrOS assistant and MCP server** (`https://api.app.infros.io/assistant/mcp`): Scopes Read, Write, Spend, and Admin. "Spend" lets the assistant start design runs and Terraform generation "which use your organization's credits"; only organization admins can grant it, and the assistant "always tells you the price first." No tool names are published and no balance, usage, or billing tool is described.
- **Direct purchases:** Free trial (700 credits, no card) and Enterprise ("custom pricing," "custom credit volumes & bulk discounts," user management). Credit packs can be bought anytime. Pack sizes, prices, currency, payment processor, and invoice structure are not published.
- **AWS Marketplace, "InfrOS":** SaaS contract, 1-month and 12-month terms. Dimensions `Spin-up` (1,100 credits, $3,000/month) and `Turbo Boost` (3,300 credits, $7,500/month). USD, billed on the AWS invoice.
- **AWS Marketplace, "InfrOS on Nimbus":** SaaS contract, 1-, 12-, 24-, and 36-month terms (12 to 36 months "save up to" 16% to 21%). Dimensions `Starter Plan` ($199/month), `Builder Plan` ($699/month), credit allocations not stated, and `Top-up 100 Credits` ($109, one-time). USD, billed on the AWS invoice.

Key characteristics:

- **Credit costs per action:** Architecture design 200 to 1,200 credits (about 400 for a nominal architecture); IaC export 100 to 400; fixes and updates 50 to 400. Complexity drivers: number of cloud providers, business processes, compliance requirements, and availability zones. Published monthly usage examples: about 950, 2,850, and 5,500+ credits.
- **Implied price per credit:** $1.09 (Nimbus top-up), $2.27 (`Turbo Boost`), $2.73 (`Spin-up`). Starter and Builder allocations are unpublished, so their rate cannot be computed. Whether Marketplace plans bundle anything beyond credits is not stated.
- **Expiry and refunds:** Credits expire 12 months after purchase. All sales are final.
- **Hierarchy:** Organization owns credits; work is organized as systems and versions. No sub-account, project, or team layer is documented. User management is Enterprise-only.
- **Region:** None customer-facing. InfrOS runs as SaaS; the regions in its designs belong to the customer's clouds.
- **Entities:** Site footer "© Infros, Inc."; terms and privacy policy name "Cloudculate Ltd." under Israeli law, Tel Aviv jurisdiction. The two Marketplace listings use different AWS seller IDs.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven: every Mandatory column must be present and valid, and Conditional columns are required when the provider's model triggers their condition. Because InfrOS has no customer billing dataset, this analysis marks a column Present when the value exists on a customer-visible InfrOS or AWS Marketplace surface and maps one-to-one, and Deviation when it exists but must be derived or re-cut. Missing means no documented surface carries it.

InfrOS prices in credits and bills in USD (on Marketplace), which triggers the v1.2 PricingCurrency family; FOCUS v1.2's Currency Format attribute explicitly allows virtual currencies such as credits. InfrOS publishes no commitment discount or reservation program; prepaid credits are not a commitment discount in the FOCUS sense, so the CommitmentDiscount and CapacityReservation families are N/A. There is no sub-account layer, no customer-selectable region or zone, no documented tagging of InfrOS systems, and a single pricing category, so the SubAccount family, RegionId, RegionName, AvailabilityZone, Tags, and PricingCategory are N/A. Feature levels below follow the FOCUS v1.2 Content Constraints, spot-checked against the live spec on November 17, 2026.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | InfrOS source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Purchase amounts on the AWS invoice (Marketplace) or the direct invoice (format unpublished); no export. Usage rows carry 0 because credits are prepaid | Deviation |
| EffectiveCost | Mandatory | Not available: credits consumed per action must be converted to USD at the paid price per credit of the funding purchase (first-in, first-out), plus expired-credit rows | Missing: Mandatory |
| ListCost | Mandatory | Not available: no public list price per credit; implied rates range from $1.09 to $2.73 | Missing: Mandatory |
| ContractedCost | Mandatory | Not available: credits × paid price per credit of the funding pack (Marketplace term discount or Enterprise bulk discount) | Missing: Mandatory |
| BillingAccountId | Mandatory | InfrOS organization ID; AWS account ID for Marketplace buyers | Present |
| BillingAccountName | Mandatory | Organization name | Present |
| BillingCurrency | Mandatory | "USD" on AWS Marketplace; direct-sale currency not published | Present |
| BillingPeriodStart | Mandatory | Calendar month on AWS; direct credit packs are bought on demand with no billing period. Define as calendar month | Deviation |
| BillingPeriodEnd | Mandatory | As above | Deviation |
| ChargePeriodStart | Mandatory | Not emitted; actions are discrete events on a system version. Aggregate to day | Deviation |
| ChargePeriodEnd | Mandatory | As above | Deviation |
| ChargeDescription | Mandatory | Not emitted; derive (e.g., "Architecture design run · <system name>", "Top-up 100 Credits") | Deviation |
| ChargeCategory | Mandatory | Not emitted; "Purchase" for packs and plans, "Usage" for credit-consuming actions, "Adjustment" for expired credits, "Tax" where applied | Deviation |
| ChargeClass | Mandatory (nullable) | null; "Correction" for reissued charges | Present |
| InvoiceIssuerName | Mandatory | Ambiguous for direct sales ("Infros, Inc." vs. "Cloudculate Ltd."); AWS for Marketplace purchases | Deviation |
| ProviderName | Mandatory (dep. v1.3) | "InfrOS" | Present |
| PublisherName | Mandatory (dep. v1.3) | "InfrOS" | Present |
| ServiceName | Mandatory | "InfrOS" | Present |
| ServiceCategory | Mandatory | Not emitted; "Developer Tools" (architecture design and IaC generation) | Deviation |
| PricingQuantity | Mandatory | Not emitted; 1 per action, or pack count for purchases | Deviation |
| PricingUnit | Mandatory | Not emitted; "Design Runs", "IaC Exports", "Fixes"; "Credit Packs" for purchases | Deviation |
| ConsumedQuantity | Conditional | Not emitted; 1 per action | Deviation |
| ConsumedUnit | Conditional | Not emitted; as PricingUnit | Deviation |
| ListUnitPrice | Conditional | Not available: credits per action are public, USD per credit is not | Missing: Conditional |
| ContractedUnitPrice | Conditional | Not available: depends on the funding pack's paid price per credit | Missing: Conditional |
| PricingCategory | Conditional | N/A: one pricing category ("Standard") across all SKUs | N/A |
| BillingAccountType | Conditional | Not emitted; "Organization" (direct) or "AWS Marketplace Subscription" | Deviation |
| SubAccountId | Conditional | N/A: no sub-account, project, or team layer under an organization | N/A |
| SubAccountName | Conditional | N/A | N/A |
| SubAccountType | Conditional | N/A | N/A |
| ResourceId | Conditional | Not on any billing surface; the system ID is the natural resource | Missing: Conditional |
| ResourceName | Conditional | Not on any billing surface; system name | Missing: Conditional |
| ResourceType | Conditional | Not emitted; "System" | Missing: Conditional |
| SkuId | Conditional | Marketplace dimensions (`Spin-up`, `Turbo Boost`, `Starter Plan`, `Builder Plan`, `Top-up 100 Credits`) for purchases; no SKU for actions | Deviation |
| Tags | Conditional | N/A: no tagging of InfrOS systems documented (tags InfrOS writes into generated Terraform belong to the customer's cloud bills) | N/A |
| PricingCurrency | Conditional | Not emitted; "InfrOS Credits" (virtual currency) | Deviation |
| PricingCurrencyListUnitPrice | Conditional | Published credit ranges per action; the exact figure is quoted per action but not retained in any documented history | Deviation |
| PricingCurrencyContractedUnitPrice | Conditional | = PricingCurrencyListUnitPrice (Enterprise discounts apply to credit purchase price, not credits per action); not emitted | Deviation |
| PricingCurrencyEffectiveCost | Conditional | Credits deducted per action, quoted by the assistant; not emitted. 0 on Purchase rows | Deviation |
| SkuMeter | Conditional | Not exposed; "Architecture Design", "IaC Export", "Fixes and Updates" | Missing: Conditional |
| SkuPriceId | Conditional | Not exposed; complexity tier | Missing: Conditional |
| SkuPriceDetails | Conditional | Not exposed; needed for complexity drivers (clouds, business processes, compliance, zones) | Missing: Conditional |
| RegionId | Conditional | N/A: no customer-facing InfrOS region | N/A |
| RegionName | Conditional | N/A | N/A |
| CommitmentDiscountId | Conditional | N/A: no commitment discount program; prepaid credits are not a commitment discount | N/A |
| CommitmentDiscountName | Conditional | N/A | N/A |
| CommitmentDiscountType | Conditional | N/A | N/A |
| CommitmentDiscountCategory | Conditional | N/A | N/A |
| CommitmentDiscountStatus | Conditional | N/A | N/A |
| CommitmentDiscountQuantity | Conditional | N/A | N/A |
| CommitmentDiscountUnit | Conditional | N/A | N/A |
| CapacityReservationId | Conditional | N/A: no capacity reservations | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | AWS invoice ID for Marketplace purchases; direct invoice numbering not documented | Deviation |
| ChargeFrequency | Recommended | Not emitted; "One-Time" for top-ups, "Recurring" for monthly plans, "Usage-Based" for actions | Deviation |
| ServiceSubcategory | Recommended | Not emitted; a Developer Tools subcategory | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: no customer-facing zones | N/A |

**Tally:** 7 Present, 21 Deviation, 3 Missing Mandatory, 8 Missing Conditional, 1 Missing Recommended, 17 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Organization as billing account, a single service, published credit costs per action, USD billing on Marketplace, and no commitment, reservation, region, or sub-account mechanics to model. The credit model maps directly onto FOCUS v1.2's virtual-currency columns.

**Substantive (2 of 3 Mandatory gaps):**

- **ListCost.** Credits per action are public; USD per credit is not, and the channels disagree by a factor of 2.5 ($1.09 to $2.73). FOCUS needs a list price per credit to compute ListCost on usage rows. This is a pricing decision InfrOS must make and publish, not plumbing.
- **EffectiveCost.** Each action's credits must be converted to USD at the price actually paid for the credits it consumed. With packs bought at different prices across channels, Marketplace terms with 16% to 21% discounts, and Enterprise bulk discounts, that requires a first-in, first-out drawdown ledger linking every action to its funding purchase. Credits forfeited at 12-month expiry need their own rows so the sum reconciles to what was paid.

**Trivial (1 of 3 Mandatory gaps):**

- **ContractedCost.** Once the drawdown ledger exists, ContractedCost is credits × the funding pack's paid price per credit, and equals EffectiveCost on usage rows.

**Substantive, beyond the column table:**

- **No customer dataset.** Every column above is a design target, not a delivered field. The first deliverable is a credit ledger export of any shape.
- **Two channels, two invoice issuers.** Marketplace buyers are invoiced by AWS in USD and see contract-dimension charges on their AWS bill; direct buyers are invoiced by an InfrOS entity whose name, currency, and format are unpublished. Neither channel shows credit consumption. A FOCUS export must cover credit usage regardless of where the credits were bought.
- **Entity naming.** "Infros, Inc." and "Cloudculate Ltd." both appear as the company. InvoiceIssuerName must match the entity on the invoice.
- **Allocation grain.** Without a sub-account or team layer, the system is the only allocation key. Enterprise user management suggests user attribution exists; an `x_` user column would support showback by team.

### 1.5 Deviations to Fix

**PricingCurrency family:** Emit PricingCurrency "InfrOS Credits", PricingCurrencyListUnitPrice and PricingCurrencyContractedUnitPrice as the credits quoted per action, and PricingCurrencyEffectiveCost as the credits deducted (0 on Purchase rows). This is where InfrOS's native pricing belongs in FOCUS.

**PricingQuantity, PricingUnit, ConsumedQuantity, ConsumedUnit:** Count actions, not credits: 1 "Design Run", "IaC Export", or "Fix" per usage row (aggregated per system per day); pack count for purchases.

**ChargeCategory and ChargeFrequency:** "Purchase" and "One-Time" or "Recurring" for packs and plans; "Usage" and "Usage-Based" for actions; "Adjustment" for expired credits.

**Billing and charge periods:** Adopt calendar-month billing periods for direct purchases and daily charge periods for actions.

**InvoiceIssuerName, ServiceCategory, ChargeDescription, BillingAccountType, SkuId, InvoiceId:** Derive as shown in the table.

**Already right:** Organization identity, USD on Marketplace, and the service name map cleanly.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (ratified June 4, 2026); certify at FOCUS v1.2, the version the conformance program currently names. FOCUS v1.5 is a release candidate with ratification scheduled for December 3, 2026; it tightens currency formatting so virtual currencies must not use ISO 4217 codes, which an "InfrOS Credits" value already satisfies. Multi-year Marketplace terms fit the v1.3 Contract Commitment dataset if InfrOS chooses to model them.

### 2.2 What Certification Requires

FinOps Certified FOCUS v1.2 Conformant runs through the FinOps Foundation (contact `member-cert@finops.org` for the RFI; membership is required for certification). Deliverables: a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report seeded by this analysis. Tooling: FOCUS Validator, FOCUS Converter, and the FOCUS Requirements Model. Document the N/A rationale (no sub-accounts, commitments, reservations, regions, zones, tags, or second pricing category), the list price per credit, and the drawdown and expiry rules.

### 2.3 Phased Roadmap

**Phase 0: Validate.** Pull one month of the internal credit ledger for a test organization with its matching purchases. Hand-build a FOCUS file, run it through the Validator, and settle the list price per credit, the drawdown rule, and the expiry treatment.

**Phase 1: Ledger export.** Ship a per-organization CSV and an MCP Read tool at system × action × day grain with BillingAccount, ChargePeriod, Service, Resource, Sku, Pricing, Consumed, and PricingCurrency columns, plus Purchase rows. This is the prerequisite for everything else.

**Phase 2: Close Mandatory gaps.** Publish the list price per credit for ListCost and ListUnitPrice; apply the drawdown ledger for EffectiveCost, ContractedCost, and ContractedUnitPrice; emit expired-credit and Tax rows that reconcile to purchases.

**Phase 3: Fill Conditional and Recommended.** Add SkuMeter, SkuPriceId, SkuPriceDetails (complexity tier and drivers), ServiceSubcategory, and InvoiceId for direct invoices. Add an `x_` user column for Enterprise organizations.

**Phase 4: Mature and certify.** Drop ProviderName and PublisherName for v1.4; add recency and completeness metadata (v1.3) and the Invoice Detail dataset (v1.4); certify at v1.2 and re-certify as the program advances.

### 2.4 FOCUS Use Cases Unlocked

- **Today:** Organization-level credit balance; Marketplace buyers see contract charges on their AWS bill.
- **After Phase 1:** Credit burn by system and action type, credit-burn anomaly detection, and design-versus-export mix analysis.
- **After Phase 2:** USD showback per system, effective cost per architecture delivered, reconciliation of consumption to purchases, and forecasting of credits at risk of expiry.
- **After Phase 3:** User- or team-level showback for Enterprise organizations and unit cost comparison across complexity tiers.
- **Out of scope:** Commitment discount utilization, capacity reservation management, region and zone analysis, and sub-account rollups.

---

## Part 3: Immediate Next Steps

1. Follow up with the InfrOS contact from KubeCon NA 2026 to identify the owner of billing and the credit ledger.
2. Ask InfrOS to confirm whether any credit history or invoice export exists beyond what the website describes, and which entity issues direct invoices, in what currency.
3. Ask InfrOS to reconcile the two AWS Marketplace listings (credit allocations for Starter and Builder, and why implied price per credit ranges from $1.09 to $2.73) and to define a list price per credit.
4. Build a v1.2 sample from one month of the credit ledger and run it through the FOCUS Validator.
5. Open the RFI with `member-cert@finops.org`.

---

## Confidence Summary

- **High:** Credit costs per action, complexity drivers, 700-credit trial, Enterprise terms, and 12-month expiry, from the InfrOS pricing page.
- **High:** Marketplace dimensions, prices, terms, and "all sales are final," from the two AWS Marketplace listings.
- **High:** No public documentation site, billing API, usage export, credit ledger, or invoice format; `docs.infros.io` did not resolve and `infros.io/docs` and `infros.io/faq` returned 404 on November 17, 2026.
- **High:** Feature levels match the FOCUS v1.2 Content Constraints; ChargeFrequency, ServiceSubcategory, PricingQuantity, Tags, PricingCurrency, PricingCurrencyEffectiveCost, PricingCategory, and the Currency Format attribute were spot-checked against the live spec on November 17, 2026, and v1.4 remains the latest ratified version.
- **Moderate:** InfrOS retains a per-action credit ledger internally; inferred from per-action quotes and organization-level balances, not documented.
- **Moderate:** No commitment discount program. None is published, but multi-year Marketplace terms and Enterprise bulk discounts could be modeled as commitments if InfrOS structures them that way.
- **Moderate:** Marketplace purchases appear in buyers' AWS billing data, and therefore AWS's FOCUS export, at contract-dimension grain only.
- **Low:** Invoicing entity and currency for direct sales ("Infros, Inc." vs. "Cloudculate Ltd."), credit allocations for Starter and Builder, and whether Marketplace plans bundle anything beyond credits.
- **Low:** Self-serve Starter ($199) and Builder ($699) plans appear on the Nimbus Marketplace listing and Toolradar but no longer on the InfrOS pricing page.

---

## Sources

- InfrOS: [infros.io](https://infros.io) · [Product](https://infros.io/product) · [Pricing](https://infros.io/pricing) · [About](https://infros.io/about)
- InfrOS Terms: [infros.io/terms](https://infros.io/terms) · [Privacy Policy](https://infros.io/privacy-policy)
- InfrOS blog, MCP setup instructions: [infros.io/blog-posts/mcp-setup-instructions](https://infros.io/blog-posts/mcp-setup-instructions)
- InfrOS blog, FinOps cost optimization agent on Amazon Bedrock AgentCore: [infros.io/blog-posts/finops-cost-optimization-agent-on-amazon-bedrock-agentcore](https://www.infros.io/blog-posts/finops-cost-optimization-agent-on-amazon-bedrock-agentcore)
- AWS Marketplace, InfrOS: [prodview-6s4xb75sb5yru](https://aws.amazon.com/marketplace/pp/prodview-6s4xb75sb5yru)
- AWS Marketplace, InfrOS on Nimbus: [prodview-dur6kzbngjq5i](https://aws.amazon.com/marketplace/pp/prodview-dur6kzbngjq5i)
- Toolradar, InfrOS pricing: [toolradar.com/tools/infros/pricing](https://toolradar.com/tools/infros/pricing)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/) · [Currency Format](https://focus.finops.org/docs/specification/v1-2/attributes/currency-format/) · [Pricing Currency](https://focus.finops.org/docs/specification/v1-2/columns/cost-and-usage/pricing-currency/)
- FOCUS 1.5 Release Scope: [focus.finops.org/focus-1-5-release-scope/](https://focus.finops.org/focus-1-5-release-scope/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
