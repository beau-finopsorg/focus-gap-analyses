# Pulumi & FOCUS: Data Generator Gap Analysis

*Analysis run: November 17, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** Pulumi Corporation  
**Prepared:** November 17, 2026  
**Origin:** KubeCon NA 2026 booth outreach  
**Source:** Public Pulumi documentation only: Pulumi pricing page and FAQ; edition selection guide; billing managers docs; `pulumi org usage get` CLI reference; Pulumi Cloud REST API index and OpenAPI spec (`api.pulumi.com/api/openapi/pulumi-spec.json`)  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 15 Present, 9 Deviation, 3 Missing Mandatory, 19 Missing Conditional, 1 Missing Recommended, 10 N/A

---

## Executive Summary

Pulumi sells Pulumi Cloud, the managed backend for Pulumi infrastructure as code, plus Pulumi ESC (secrets and configuration), Insights (discovery and policy), Deployments (workflow minutes), and Neo (an AI infrastructure agent). Every meter draws from one pool of Pulumi Credits priced at $1 each: IaC resource-hours, ESC secret-hours, ESC API calls, discovered resource-hours, workflow minutes, and Neo tokens. Editions are Free, Essentials ($40 per month including 40 credits), Pro ($400 per month including 400 credits), and Enterprise (contract pricing).

**Public billing documentation is thin.** Pulumi publishes a clear rate card and, unusually, a usage API: six org-level summary endpoints in the Pulumi Cloud REST API, one per meter, at hourly to yearly granularity. But those endpoints return quantities only, with no dollar amounts, no currency, no SKU or price, and no breakdown by project or stack. No invoice API, invoice field list, or billing export is documented. The Billing & usage page offers a "download usage history" file whose columns are not documented. Every cost column below rests on the public rate card and standard invoicing, not on a documented data contract.

Of the 21 Mandatory FOCUS columns, 18 have a source and 3 are missing. One gap is substantive: **EffectiveCost**, because base fees buy credits that expire monthly, Pro and Enterprise sign annual commitments, and top-ups and volume tiers are discounted. **ListCost** and **ContractedCost** are rate-card joins.

Pulumi is better placed than most SaaS vendors at this size. The meters are already hourly, already metered per product, and already exposed by API. What is missing is the price join, the allocation dimension, and a row-level shape.

**Recommendation:** Extend the existing usage summary endpoints into a monthly FOCUS export per organization: one Usage row per meter × stack × day, priced at the organization's rate, with Purchase rows for base fees, commitments, and top-ups, a CommitmentDiscount draw-down against the credit pool, and Tax rows so the dataset reconciles to the invoice. Carry stack tags into the Tags column.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

- **Usage summary API** (Pulumi Cloud REST API, `GET`, org-scoped): `GetUsageSummaryResourceHours` (`/api/orgs/{orgName}/resources/summary`), `GetUsageSummaryEnvironmentSecrets`, `GetUsageSummaryDiscoveredResourceHours`, `GetUsageSummaryDeployCompute`, `GetUsageSummaryInsightsScans`, and `GetUsageSummaryNeoTokens`. Parameters: `granularity` (hourly, daily, weekly, monthly, yearly; hourly limited to a two-day lookback), `lookbackDays` or `lookbackStart` (within the last year). Response: an array of `ResourceCountSummary` with `year`, `month`, `day`, `weekNumber`, `hour`, `resources` (average count), and `resourceHours` (sum). Only the Neo endpoint offers a tag breakdown (TaskID, Feature).
- **CLI:** `pulumi org usage get` (experimental) wraps `GetUsageSummaryResourceHours` and returns resources under management and resource-hours, org level only.
- **Billing & usage page:** Tracks IaC resources, deployment minutes, and ESC secrets, with a usage history download. Restricted to org admins and billing managers, who can view payments and update the subscription and card. Monthly usage reports are emailed. No invoice download API or field list is documented.
- **Data Export** (Pro and Enterprise): CSV of resource search results (project, stack, type, URN). Inventory only, no usage or cost.
- **Pricing page:** USD. One credit = $1. Sales tax appears as a separate invoice line.

Key characteristics:

- **Meters and rates:** IaC resources at $0.00025 per hour on Essentials and from $0.0005 per hour on Pro; ESC secrets at $0.000685 and $0.001 per hour; ESC API calls (ReadOpen only) at $0.10 per 10,000; discovered resources at $0.000025 and from $0.00005 per hour; workflow minutes (Discovery, Deployments, and agent workers) at $0.01; Neo at $3 per million tokens. Free includes 25 secrets, 10,000 API calls, and 500 workflow minutes. Enterprise is contract-priced on every meter.
- **Rounding:** A partial resource-hour is billed as a full hour. Provider resources, component resources, and stacks all count as resources.
- **Credits and commitments:** Essentials and Pro pay a base fee up front each month; included credits expire at the end of the term. Overage is billed in arrears on the first of the month. Discounted credit top-ups are available on Essentials and Pro. Annual commitments are available on Pro and Enterprise; volume pricing usually applies past about 4,750 IaC resources.
- **Hierarchy:** Organization > Project > Stack. Stacks carry tags. Pro and Enterprise allow multiple organizations, teams, and tag-based access control.
- **Self-hosted:** Enterprise only. A separate endpoint (`GetDeployUsageReport`) lets self-hosted customers self-report deployment consumption "for billing reconciliation purposes."

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven: every Mandatory column must be present and valid, and Conditional columns are required when the provider's model triggers their condition. Usage is generated by stacks inside projects, and stacks carry tags, so the SubAccount, Resource, and Tags families apply. Prepaid base-fee credits and annual commitments are drawn down by usage with overage billed separately, so this analysis treats the CommitmentDiscount family as applicable. Pulumi has one billing account type (the organization), no billed regions or zones, no capacity reservations, and credits pegged 1:1 to USD; those columns are N/A and should exist as null. Feature levels follow the FOCUS v1.2 Content Constraints.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | Pulumi source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Invoice and card charges; no line-level cost per meter, project, or stack, and the usage API carries no dollar amounts | Deviation |
| EffectiveCost | Mandatory | Not available: needs amortization of base fees, annual commitments, and discounted top-ups across credits drawn, plus expiry of unused monthly credits | Missing: Mandatory |
| ListCost | Mandatory | Not exposed; public rate × quantity for Essentials and Pro | Missing: Mandatory |
| ContractedCost | Mandatory | Not exposed; contract and volume rate × PricingQuantity | Missing: Mandatory |
| BillingAccountId | Mandatory | Pulumi organization ID | Present |
| BillingAccountName | Mandatory | Pulumi organization name | Present |
| BillingCurrency | Mandatory | "USD" | Present |
| BillingPeriodStart | Mandatory | Monthly term start | Present |
| BillingPeriodEnd | Mandatory | Monthly term end (exclusive) | Present |
| ChargePeriodStart | Mandatory | Usage summary bucket (`year`/`month`/`day`/`hour`) | Present |
| ChargePeriodEnd | Mandatory | Bucket start plus granularity | Present |
| ChargeDescription | Mandatory | Invoice line description | Present |
| ChargeCategory | Mandatory | Derive: "Purchase" for base fees, commitments, and top-ups; "Usage" for metered consumption and overage; "Tax" for sales tax; "Credit" for refunds | Deviation |
| ChargeClass | Mandatory (nullable) | null; "Correction" for re-issued charges | Present |
| InvoiceIssuerName | Mandatory | "Pulumi Corporation" | Present |
| ProviderName | Mandatory (dep. v1.3) | "Pulumi" | Present |
| PublisherName | Mandatory (dep. v1.3) | "Pulumi" | Present |
| ServiceName | Mandatory | Product per meter: "Pulumi IaC", "Pulumi ESC", "Pulumi Insights", "Pulumi Deployments", "Pulumi Neo" | Present |
| ServiceCategory | Mandatory | Derive: "Developer Tools" for IaC and Deployments; "Security" for ESC; "Management and Governance" for Insights; "AI and Machine Learning" for Neo | Deviation |
| PricingQuantity | Mandatory | Usage API `resourceHours`, but the same field name carries resource-hours, secret-hours, minutes, and tokens; API calls and tokens are priced per 10,000 and per million | Deviation |
| PricingUnit | Mandatory | Not emitted; normalize to "Resource-Hours", "Secret-Hours", "Minutes", "10000 Requests", "1000000 Tokens" | Deviation |
| ConsumedQuantity | Conditional | Usage API `resourceHours` per meter | Present |
| ConsumedUnit | Conditional | Implicit in the endpoint; normalize as for PricingUnit | Deviation |
| ListUnitPrice | Conditional | Not in data; public on the pricing page for Essentials and Pro | Missing: Conditional |
| ContractedUnitPrice | Conditional | Not exposed; contract and volume rates | Missing: Conditional |
| PricingCategory | Conditional | Derive: "Committed" for usage drawn from included or contracted credits; "Standard" for overage | Deviation |
| BillingAccountType | Conditional | N/A: one account type (organization) | N/A |
| SubAccountId | Conditional | Not in usage data; Pulumi project (summaries are org-level only) | Missing: Conditional |
| SubAccountName | Conditional | Not in usage data; project name | Missing: Conditional |
| SubAccountType | Conditional | Not in usage data; "Project" | Missing: Conditional |
| ResourceId | Conditional | Not in usage data; stack (`org/project/stack`), ESC environment, or Neo task | Missing: Conditional |
| ResourceName | Conditional | Not in usage data; stack, environment, or task name | Missing: Conditional |
| ResourceType | Conditional | Not in usage data; "Stack", "Environment", "Neo Task" | Missing: Conditional |
| SkuId | Conditional | Not exposed; edition × meter codes | Missing: Conditional |
| Tags | Conditional | Stack tags exist but are not carried into usage data; Neo's TaskID/Feature breakdown is the only tagged usage | Missing: Conditional |
| PricingCurrency | Conditional | N/A: credits are pegged 1:1 to USD | N/A |
| PricingCurrencyListUnitPrice | Conditional | N/A | N/A |
| PricingCurrencyContractedUnitPrice | Conditional | N/A | N/A |
| PricingCurrencyEffectiveCost | Conditional | N/A | N/A |
| SkuMeter | Conditional | Implied by which usage endpoint returned the row; no meter name emitted | Deviation |
| SkuPriceId | Conditional | Not exposed | Missing: Conditional |
| SkuPriceDetails | Conditional | Not exposed; edition and volume tier belong here | Missing: Conditional |
| RegionId | Conditional | N/A: no region appears in any pricing or billing surface | N/A |
| RegionName | Conditional | N/A | N/A |
| CommitmentDiscountId | Conditional | Credit pool (monthly base fee, annual commitment, or top-up); not exported | Missing: Conditional |
| CommitmentDiscountName | Conditional | Not exposed | Missing: Conditional |
| CommitmentDiscountType | Conditional | Not exposed (e.g., "Pulumi Credits") | Missing: Conditional |
| CommitmentDiscountCategory | Conditional | "Spend"; not exposed | Missing: Conditional |
| CommitmentDiscountStatus | Conditional | "Used"/"Unused"; unused credits expire at term end but are not reported | Missing: Conditional |
| CommitmentDiscountQuantity | Conditional | Credits drawn from the pool | Missing: Conditional |
| CommitmentDiscountUnit | Conditional | "Credits" | Missing: Conditional |
| CapacityReservationId | Conditional | N/A: no capacity reservations | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | Invoice number | Present |
| ChargeFrequency | Recommended | Derive: "Recurring" for base fees and annual commitments; "One-Time" for top-ups; "Usage-Based" for metered usage | Deviation |
| ServiceSubcategory | Recommended | Not exposed; map each product to an allowed v1.2 value | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: Pulumi operates the SaaS; zones are not customer-billed | N/A |

**Tally:** 15 Present, 9 Deviation, 3 Missing Mandatory, 19 Missing Conditional, 1 Missing Recommended, 10 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Organization identity, USD billing, a public per-meter rate card, hourly metering, and a documented, versioned usage API that already returns every meter by time bucket. Few SaaS vendors at Pulumi's stage expose this much.

**Substantive (1 of 3 Mandatory gaps):**

- **EffectiveCost.** Essentials and Pro pay a base fee up front for credits that expire at month end; Pro and Enterprise can sign annual commitments; top-ups are discounted; volume pricing applies at scale. EffectiveCost means amortizing each credit purchase across the credits actually drawn, recording unused credits at expiry, and pricing overage at the on-demand rate. No documented surface does this.

**Trivial (2 of 3 Mandatory gaps):**

- **ListCost.** Usage quantity × the public rate for the organization's edition. Rates are flat per meter, so the join is direct. Enterprise has no public rate; use ContractedCost where no list price exists.
- **ContractedCost.** Pulumi's billing system already holds each organization's contract and volume rates; expose them per row.

**Substantive, beyond the column table:**

- **No allocation dimension.** Usage summaries are org-wide. Pulumi already counts resources per stack (resource search returns project and stack per resource), but the usage API cannot group by either. Without a project or stack split, Pulumi spend cannot be charged back, which is the first thing a FinOps team asks of an IaC platform bill.
- **No cost or invoice data by API.** Dollars live only on invoices and the Billing & usage page. The usage API's single `resources`/`resourceHours` shape is reused for secrets, minutes, and tokens without unit labels.
- **Credit definition conflict.** The OpenAPI spec says "1 resource hour = 1 Pulumi credit"; the pricing page says one credit costs $1 and a resource-hour costs $0.00025 to $0.0005. A FOCUS export forces one definition, since it drives PricingUnit, PricingCurrency, and the CommitmentDiscount unit.

**Pulumi and FOCUS on the cloud side:** Pulumi stacks provision the AWS, Azure, and Google Cloud resources that appear in those providers' own FOCUS exports. Propagating stack and project tags to cloud resource tags (already possible in Pulumi programs) gives customers a join between hyperscaler FOCUS data and Pulumi stacks. That is a complementary story, not a substitute for Pulumi publishing FOCUS data for its own charges.

### 1.5 Deviations to Fix

**BilledCost:** Emit one row per meter, project, and stack rather than an invoice total, plus Purchase, Tax, and Credit rows, so that BilledCost summed per InvoiceId equals the invoice total.

**ChargeCategory:** "Purchase" for base fees, commitments, and top-ups; "Usage" for metered consumption and overage; "Tax" and "Credit" as above.

**ServiceCategory:** "Developer Tools" for IaC and Deployments; "Security" for ESC; "Management and Governance" for Insights; "AI and Machine Learning" for Neo.

**PricingQuantity and PricingUnit:** Price each meter in its billed unit: resource-hours and secret-hours (partial hours rounded up), minutes, requests in blocks of 10,000, and tokens in blocks of one million. ConsumedQuantity carries the raw count.

**SkuMeter, ConsumedUnit, PricingCategory, ChargeFrequency:** Derive from meter and purchase type as shown in the table.

**Already right:** USD billing, a flat published rate per meter, hourly metering, and an Organization > Project > Stack hierarchy that maps directly to BillingAccount, SubAccount, and Resource.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (ratified June 4, 2026); certify at FOCUS v1.2, the version the conformance program currently names. FOCUS v1.5 is a candidate release; its scope is on the FOCUS site. The v1.3 Contract Commitment dataset fits Pro and Enterprise annual commitments better than per-row CommitmentDiscount columns alone.

### 2.2 What Certification Requires

FinOps Certified FOCUS v1.2 Conformant runs through the FinOps Foundation (contact `member-cert@finops.org` for the RFI; membership is required for certification). Deliverables: a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report seeded by this analysis. Tooling: FOCUS Validator, FOCUS Converter, and the FOCUS Requirements Model. Document the N/A rationale (single account type, no billed regions, zones, reservations, or alternate currencies) and the decision on modeling the credit pool as a commitment discount.

### 2.3 Phased Roadmap

**Phase 0: Validate.** Pull one month of usage summaries and the invoice for an Essentials organization and a Pro organization with an annual commitment. Hand-build a v1.2 file and run it through the Validator. Settle the credit definition and the commitment model.

**Phase 1: Close Mandatory gaps.** Join the public rate card for ListCost and the organization's contract rates for ContractedCost. Amortize base fees, commitments, and top-ups for EffectiveCost. Emit line-level BilledCost with Purchase, Tax, and Credit rows so it reconciles to the invoice.

**Phase 2: Fix deviations.** Derive ChargeCategory, ServiceCategory, ChargeFrequency, PricingCategory, and SkuMeter; label units per meter.

**Phase 3: Allocation and Conditional columns.** Add a project and stack group-by to the usage API and populate SubAccountId, SubAccountName, and SubAccountType from project, and ResourceId, ResourceName, and ResourceType from stack, ESC environment, or Neo task; Tags from stack tags; SkuId, SkuPriceId, and SkuPriceDetails; ListUnitPrice and ContractedUnitPrice; the CommitmentDiscount family for credit draw-down; and ServiceSubcategory. Deliver by API and scheduled push to object storage.

**Phase 4: Mature and certify.** Drop ProviderName and PublisherName for v1.4; add the Invoice Detail dataset; certify at v1.2 and re-certify as the program advances.

### 2.4 FOCUS Use Cases Unlocked

- **After Phase 1:** Invoice reconciliation, actuals-based budgeting and forecasting, and amortized spend reporting for Pulumi.
- **After Phase 2:** Spend by service category across providers, and mix analysis across IaC, ESC, Insights, Deployments, and Neo.
- **After Phase 3:** Chargeback and showback by project, stack, or tag; unit economics per managed resource and per deployment; credit pool utilization and expiry-risk tracking; anomaly detection on resource-hour and Neo token growth; and a join from Pulumi stacks to hyperscaler FOCUS data.
- **Out of scope:** Capacity reservation management, regional cost analysis, and multi-currency analysis.

---

## Part 3: Immediate Next Steps

1. Follow up with the Pulumi contact from KubeCon NA 2026 to reach the owners of Pulumi Cloud billing and the usage API.
2. Confirm what the usage history download and invoices contain today (columns, line items, per-meter detail).
3. Confirm the credit definition (resource-hour vs. $1) and how annual commitments, top-ups, and volume tiers are invoiced.
4. Ask whether a project and stack group-by on the usage summary endpoints is feasible.
5. Build a v1.2 sample from one billing month and run it through the FOCUS Validator.
6. Open the RFI with `member-cert@finops.org` and confirm FinOps Foundation membership status.

---

## Confidence Summary

- **High:** Editions, base fees, included credits, per-meter rates, partial-hour rounding, monthly credit expiry, and overage in arrears come from Pulumi's pricing page.
- **High:** Six org-scoped usage summary endpoints exist with quantity-only responses and no project or stack grouping, per the Pulumi Cloud OpenAPI spec. The spec is large and was read in part, so an undocumented billing endpoint elsewhere in it cannot be ruled out.
- **High:** Feature levels match the bundled FOCUS v1.2 Content Constraints table (verified June 23, 2026); v1.4 remains the latest ratified version and v1.5 is a candidate release. A live spot-check through the FOCUS MCP was not run for this analysis.
- **Moderate:** Present status for invoice-sourced columns (ChargeDescription, InvoiceId, billing periods). Pulumi publishes no invoice sample or field list, so presence is inferred from standard invoicing.
- **Moderate:** Treating the credit pool as a spend commitment discount. If Pulumi models base-fee credits as simple prepayment, the seven CommitmentDiscount columns become N/A and the amortization moves entirely into EffectiveCost.
- **Moderate:** ServiceCategory mappings; the v1.2 values chosen are the closest fit.
- **Moderate:** PricingCurrency as N/A. If Pulumi defines credits as a unit distinct from USD (as the OpenAPI spec's "1 resource hour = 1 Pulumi credit" implies), the four PricingCurrency columns become applicable.
- **Low:** Marketplace availability. The pricing page does not mention AWS, Azure, or Google Cloud Marketplace; if Pulumi sells through one, InvoiceIssuerName must name the marketplace for those rows.
- **Low:** RegionId as N/A. No billing surface shows a customer-selected Pulumi Cloud region.
- **Low:** InvoiceIssuerName as "Pulumi Corporation." No public invoice names the issuing entity.

---

## Sources

- Pulumi Pricing: [pulumi.com/pricing](https://www.pulumi.com/pricing/)
- Choose an Edition: [pulumi.com/docs/administration/get-started/choose-edition/](https://www.pulumi.com/docs/administration/get-started/choose-edition/)
- Billing Managers: [pulumi.com/docs/administration/concepts/billing-managers/](https://www.pulumi.com/docs/administration/concepts/billing-managers/)
- `pulumi org usage get`: [pulumi.com/docs/iac/cli/commands/pulumi_org_usage_get/](https://www.pulumi.com/docs/iac/cli/commands/pulumi_org_usage_get/)
- Pulumi Cloud REST API: [pulumi.com/docs/reference/cloud-rest-api/](https://www.pulumi.com/docs/reference/cloud-rest-api/)
- Pulumi Cloud OpenAPI spec: [api.pulumi.com/api/openapi/pulumi-spec.json](https://api.pulumi.com/api/openapi/pulumi-spec.json)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FOCUS 1.5 Release Scope: [focus.finops.org/focus-1-5-release-scope/](https://focus.finops.org/focus-1-5-release-scope/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
