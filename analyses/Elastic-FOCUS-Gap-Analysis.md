# Elastic & FOCUS: Data Generator Gap Analysis

*Analysis run: November 17, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** Elastic N.V. (Elastic Cloud: Hosted deployments and Serverless projects)  
**Prepared:** November 17, 2026  
**Origin:** KubeCon NA 2026 booth outreach  
**Source:** Public Elastic documentation only: Elastic Cloud Billing API v2 (OpenAPI spec); deprecated v1 billing costs endpoints; Billing History API; Elastic Cloud billing docs (ECU, billing models, billing dimensions, FAQ, Usage page); Elastic Cloud pricing pages; `ess_billing` integration field reference; deployment tags and Serverless project settings docs  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 20 Present, 12 Deviation, 2 Missing Mandatory, 14 Missing Conditional, 2 Missing Recommended, 7 N/A

---

## Executive Summary

Elastic sells Elastic Cloud in two forms: Hosted deployments (dedicated Elasticsearch, Kibana, APM, and Integrations Server clusters on AWS, Google Cloud, or Azure) and Serverless projects (Elasticsearch, Observability, and Security). All usage is metered hourly and priced in Elastic Consumption Units (ECU), where 1 ECU equals $1.00 at list. Customers pay monthly by credit card, through a cloud marketplace, or by buying prepaid ECU credits up front at a negotiated discount and in a choice of currencies.

Elastic is closer to FOCUS than most SaaS vendors. The v2 Cloud Billing API returns per-instance, per-SKU line items with a unit, quantity, list rate, ECU total, and a tier breakdown, as JSON or CSV, over any date range. Of the 21 Mandatory columns, 19 have a source and 2 are missing. **ContractedCost** is trivial. **EffectiveCost** is substantive.

The problem is that every number in the API is list-price ECU. Elastic's own docs say the Usage page "is an estimate, and does not include prepaid credits, free allowances or any discounts." Prepaid customers, who are the large accounts FinOps teams care about, buy ECU at a discount and in non-USD currencies, and none of that reaches the cost API. For them, BilledCost and EffectiveCost cannot be produced from public data.

**Public billing documentation is thin where FOCUS needs it most.** The v2 schema is published but has no example responses, types `total_ecu` and `rate.value` as integers while Elastic's own integration emits decimals, and declares Billing Accounts, Prices, Line Items, and marketplace API groups with no paths. The console CSV export has no documented column list. Credits, discounts, taxes, and invoice linkage have no public API fields.

**Recommendation:** Add a FOCUS export to the v2 Billing API (`Accept: text/focus+csv` or a new `/focus` path) that emits one Usage row per instance × SKU × day, with BillingCurrency set to the contract currency and PricingCurrency set to `ECU`. Model prepaid consumption as a spend-based commitment discount: one Purchase row per order line and Usage rows drawing down against it, so EffectiveCost reflects the negotiated discount. Join deployment and project tags into Tags and parse region from the SKU into RegionId.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

**Elastic Cloud Billing API v2** (`https://cloud.elastic.co`, `Authorization: ApiKey`):

- **`GET /api/v2/billing/organizations/{org}/costs/instances`:** Costs per Hosted deployment or Serverless project. Returns `total_ecu` and `instances[]{id, name, type, total_ecu, product_line_items[]}`. `from` and `to` are required; `include_names` adds instance names. JSON or `text/csv`.
- **`.../costs/instances/{instance_id}/items`:** Itemized line items for one instance.
- **`.../costs/items`:** Organization-wide items by product, with `serverless_group_by=product|product_family`.
- **Line item shape (`ProductLineItem`):** `name`, `type`, `sku`, `unit`, `quantity{value, formatted_value}`, `display_quantity{value, formatted_value, type}`, `rate{value, formatted_value}`, `total_ecu`, optional `kind`, and `quantities[]{from, to, total_ecu, rate, quantity, tiers[]{min, max, total_ecu, quantity, rate}}`. The `quantities` array segments usage by price range and tier.
- **`.../charts`:** Daily or monthly cost buckets, organization-wide or per instance.
- **`GET /api/v1/billing/organization/{org}/history`:** Invoice and statement headers: invoice `number`, `issue_date`, period start and end, `status`, `type`, `invoiced_amount_in_cents`, PDF links, and `payment_metadata{amount, currency, external_invoice_id}`. Statements add `ecu_total`, `currency`, and a `reseller` flag. No line items.
- **Budgets API:** Create, list, update, and delete organization budgets.

**Deprecated v1 costs endpoints** (`/api/v1/billing/costs/{organization_id}/...`): overview, deployments, items, and charts. The v1 overview exposed the prepaid `balance` with ECU `line_items[]{ecu_quantity, ecu_balance, start, end}`. v2 does not.

**`ess_billing` integration:** Elastic's own Fleet integration pulls billing and credits data daily (one year of history on first run). Its fields are the best public picture of a real line item: `deployment_id`, `deployment_name`, `deployment_tags`, `deployment_type`, `cloud.machine.type`, `kind`, `name`, `sku`, `type` (`capacity` or `usage`), `unit` (`hour`, `GB`), `quantity`, `rate`, `total_ecu`, `ram_per_zone`, `zone_count`, and `from`/`to`. Its credits stream (`ecu_balance`, `ecu_quantity`, `start`, `end`, `active`, `type` such as `prepaid_consumption`) works only for annual direct contracts and reads from an endpoint that is not in the public v2 spec.

**Console Billing > Usage page:** Usage grouped by product or resource, daily or monthly, with CSV download. Elastic labels it an estimate that excludes prepaid credits, free allowances, and discounts. The CSV columns are not documented.

Key characteristics:

- **ECU pricing:** 1 ECU = $1.00. Monthly usage is charged in USD only. Prepaid ECU credits are bought "at a discount, and in different currencies," consumed first-expiring-first, and forfeited at contract end. Overage beyond prepaid credits is invoiced in arrears at list.
- **Billing models:** Monthly direct (credit card), monthly through AWS, Google Cloud, or Azure Marketplace (usage reported hourly and shown as one line on the hyperscaler bill), and prepaid consumption (annual, bank transfer allowed).
- **Invoicing entities:** Elasticsearch Inc. for US customers (with US sales tax); Elasticsearch B.V. (Netherlands) for non-US customers (with VAT where applicable).
- **Hosted dimensions:** Capacity per instance-hour (sized by GB RAM per zone and zone count), data out and inter-node transfer (100 GB per month free combined), snapshot storage (100 GB free), snapshot API requests per 1,000 (100,000 free), plus Synthetics, inference tokens, and workflow executions.
- **Serverless dimensions:** Elasticsearch projects bill ingest, search, and ML VCU-hours plus GB retained and egress. Observability and Security projects bill GB ingested and GB retained with monthly volume tiers. Paid support on Serverless is a percentage of ECU consumption (5%, 10%, or 15% for Gold, Platinum, Enterprise).
- **Hierarchy:** One organization owns all deployments and projects. No billing sub-accounts.
- **Tags:** Hosted deployments take up to 64 key-value tags; Serverless projects take up to 64 `metadata.tags`. Neither appears in the v2 cost schema.
- **Region:** Not a field anywhere in the cost API. It is embedded in SKU strings (e.g., `gcp.es.ml.n2.68x32x45_gcp-europe-west1_8192_1`).

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven: every Mandatory column must be present and valid, and Conditional columns are required when the provider's model triggers their condition. Elastic deploys into cloud regions, supports user-defined key-value tags, prices in a virtual unit (ECU) distinct from the billing currency, and sells prepaid ECU at a discount with forfeiture of unused balance. So RegionId, RegionName, Tags, the PricingCurrency family, and the CommitmentDiscount family all apply. Elastic has one billing account type (the organization), no billing sub-accounts, no capacity reservations, and no customer-visible per-zone billing; those columns are N/A and should exist as null. Feature levels follow the FOCUS v1.2 Content Constraints, spot-checked against the live spec on November 17, 2026.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | Elastic source | Status |
|---|---|---|---|
| BilledCost | Mandatory | `total_ecu` per line item; correct only for monthly direct accounts with no credits or discounts. Prepaid drawdown and overage are not distinguished, and Tax and Credit rows do not exist | Deviation |
| EffectiveCost | Mandatory | Not available: needs the prepaid discount amortized onto usage and credits allocated; the API is list-price only | Missing: Mandatory |
| ListCost | Mandatory | `total_ecu` (list rate × quantity, after free allowances and tiers) | Present |
| ContractedCost | Mandatory | Not exposed; equals ListCost, because consumption draws down ECU at list and the negotiated discount sits on the prepaid purchase | Missing: Mandatory |
| BillingAccountId | Mandatory | Organization ID (path parameter) | Present |
| BillingAccountName | Mandatory | Organization name (Organizations API) | Present |
| BillingCurrency | Mandatory | Implicit: "ECU" is not ISO 4217. Emit "USD" for monthly accounts and the contract currency for prepaid (`payment_metadata.currency` on invoices) | Deviation |
| BillingPeriodStart | Mandatory | Invoice `period_start_date` | Present |
| BillingPeriodEnd | Mandatory | Invoice `period_end_date` | Present |
| ChargePeriodStart | Mandatory | `quantities[].from`, or the requested day when pulled per day | Present |
| ChargePeriodEnd | Mandatory | `quantities[].to` | Present |
| ChargeDescription | Mandatory | Line item `name` | Present |
| ChargeCategory | Mandatory | Native `type` is `capacity` or `usage`, not FOCUS values. Derive "Usage" for consumption, "Purchase" for prepaid order lines, plus "Tax" and "Credit" rows | Deviation |
| ChargeClass | Mandatory (nullable) | null; "Correction" for restated periods | Present |
| InvoiceIssuerName | Mandatory | Not emitted. Derive "Elasticsearch Inc." (US), "Elasticsearch B.V." (non-US), or the marketplace for marketplace billing | Deviation |
| ProviderName | Mandatory (dep. v1.3) | "Elastic" | Present |
| PublisherName | Mandatory (dep. v1.3) | "Elastic" | Present |
| ServiceName | Mandatory | Instance and product `type` (e.g., "Elastic Cloud Hosted", "Elasticsearch Serverless", "Elastic Observability Serverless", "Elastic Security Serverless") | Present |
| ServiceCategory | Mandatory | Derive: "Analytics" for Elasticsearch, "Management and Governance" for Observability, "Security" for Security, "Networking" for data transfer | Deviation |
| PricingQuantity | Mandatory | `quantity.value`, with per-tier quantities in `quantities[].tiers[]` | Present |
| PricingUnit | Mandatory | `unit` (`hour`, `GB`); normalize to FOCUS unit format ("Hours", "GB", "GB-Months", "VCU-Hours", "1000 Requests") | Deviation |
| ConsumedQuantity | Conditional | `display_quantity.value` | Present |
| ConsumedUnit | Conditional | Implicit in `unit` and `display_quantity.type`; normalize | Deviation |
| ListUnitPrice | Conditional | `rate.value` in ECU; equals USD only when BillingCurrency is USD | Deviation |
| ContractedUnitPrice | Conditional | Not exposed; equals ListUnitPrice in ECU | Missing: Conditional |
| PricingCategory | Conditional | Not emitted; derive "Committed" for prepaid drawdown, "Standard" for monthly and overage | Missing: Conditional |
| BillingAccountType | Conditional | N/A: one account type (organization) | N/A |
| SubAccountId | Conditional | N/A: no billing sub-accounts; deployments and projects are resources | N/A |
| SubAccountName | Conditional | N/A | N/A |
| SubAccountType | Conditional | N/A | N/A |
| ResourceId | Conditional | Instance `id` (deployment ID or project ID) | Present |
| ResourceName | Conditional | Instance `name` (`include_names=true`) | Present |
| ResourceType | Conditional | Instance `type` (deployment or project) plus line item `kind` (elasticsearch, kibana, apm, integrations_server) | Present |
| SkuId | Conditional | `sku` encodes cloud, instance config, region, and size; strip region and size for a stable product SKU | Deviation |
| Tags | Conditional | Deployment tags and project `metadata.tags` (key-value, up to 64) exist but are not in the cost API | Missing: Conditional |
| PricingCurrency | Conditional | Not emitted; "ECU" | Missing: Conditional |
| PricingCurrencyListUnitPrice | Conditional | `rate.value` (ECU) | Present |
| PricingCurrencyContractedUnitPrice | Conditional | Not exposed; equals `rate.value` | Missing: Conditional |
| PricingCurrencyEffectiveCost | Conditional | Not exposed; needs prepaid discount and credits | Missing: Conditional |
| SkuMeter | Conditional | Line item `name` / dimension (capacity, data out, inter-node, snapshot storage, VCU type, GB ingested) | Present |
| SkuPriceId | Conditional | `sku` (region- and size-specific price point) | Present |
| SkuPriceDetails | Conditional | `quantities[].tiers[]{min, max, rate}`; reformat as FOCUS key-value JSON | Deviation |
| RegionId | Conditional | Embedded in the `sku` string only; parse | Deviation |
| RegionName | Conditional | Not exposed; map from the parsed region | Missing: Conditional |
| CommitmentDiscountId | Conditional | Prepaid order line ID; console only, not in the public API | Missing: Conditional |
| CommitmentDiscountName | Conditional | Not exposed | Missing: Conditional |
| CommitmentDiscountType | Conditional | Not exposed (e.g., "Prepaid Consumption") | Missing: Conditional |
| CommitmentDiscountCategory | Conditional | "Spend"; not exposed | Missing: Conditional |
| CommitmentDiscountStatus | Conditional | "Used"/"Unused" against the prepaid balance; not exposed | Missing: Conditional |
| CommitmentDiscountQuantity | Conditional | ECU drawn against the order line; not exposed | Missing: Conditional |
| CommitmentDiscountUnit | Conditional | "ECU"; not exposed | Missing: Conditional |
| CapacityReservationId | Conditional | N/A: no capacity reservations | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | Invoice `number` exists in the History API, but line items carry no invoice reference; join by billing period | Deviation |
| ChargeFrequency | Recommended | Not emitted; derive "Usage-Based" for consumption, "One-Time" for prepaid purchases | Missing: Recommended |
| ServiceSubcategory | Recommended | Not emitted; map each product to an allowed v1.2 value (e.g., "Search", "Observability") | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: customers choose a zone count (`zone_count`), not named zones, and cost is not split by zone | N/A |

**Tally:** 20 Present, 12 Deviation, 2 Missing Mandatory, 14 Missing Conditional, 2 Missing Recommended, 7 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Organization identity, invoice periods, per-instance and per-SKU line items, resource IDs and names, list rates, quantities, tier breakdowns, and a CSV output option. Most of the FOCUS row structure already exists in the v2 Billing API; this is a mapping and enrichment job for monthly direct accounts, not a rebuild.

**Substantive (1 of 2 Mandatory gaps):**

- **EffectiveCost.** Prepaid customers buy ECU at a negotiated discount, sometimes in EUR or another currency, and consume it at list. Producing EffectiveCost means applying the order line's effective ECU price (amount paid ÷ ECU purchased) to each usage row and allocating promotional and trial credits. Elastic holds this in the order lines it shows in the console (list unit price, discount, paid amount, start and expiry), but no public API returns it.

**Trivial (1 of 2 Mandatory gaps):**

- **ContractedCost.** Consumption draws down at list ECU rates, so ContractedCost equals ListCost in ECU, converted to BillingCurrency.

**Substantive deviation on a present column:**

- **BilledCost.** For monthly direct accounts, `total_ecu` in USD is a fair BilledCost. For prepaid accounts it is wrong: usage covered by prepaid credit should carry BilledCost of 0 (the money moved on the Purchase row), and only overage should carry billed amounts. The API cannot distinguish drawdown from overage, and it emits no Tax or Credit rows. BilledCost summed per invoice will not reconcile to `invoiced_amount_in_cents` without those.

**Substantive, beyond the column table:**

- **Thin public documentation.** No example responses for the v2 cost endpoints; `total_ecu` and `rate.value` are typed `integer` in the OpenAPI spec while Elastic's integration emits decimals (e.g., `8.4672`); the console CSV schema is undocumented; and the spec declares Billing Accounts, Prices, Line Items, and marketplace groups with no published paths. Any FOCUS mapping built today rests partly on inference from the integration.
- **Allocation.** Tags exist on deployments and projects but are absent from cost line items, so every consumer (Elastic's own integration, Vantage, CloudZero, Datadog) joins them separately or falls back to virtual tags.
- **Marketplace split.** Marketplace buyers see Elastic as one line on the AWS, Google Cloud, or Azure bill. An Elastic export with InvoiceIssuerName set to the marketplace is the only way to break that line down by deployment.

### 1.5 Deviations to Fix

**BilledCost:** Separate prepaid drawdown (BilledCost 0, EffectiveCost at the discounted ECU rate) from overage (BilledCost at list), and emit Purchase, Tax, and Credit rows so BilledCost summed per InvoiceId equals the invoice.

**BillingCurrency, ListUnitPrice, and the PricingCurrency family:** ECU is a pricing unit, not a billing currency. Set PricingCurrency to "ECU", keep ECU rates in the PricingCurrency columns, and convert to the contract's ISO 4217 currency for BillingCurrency, ListUnitPrice, and the cost columns. This is the case FOCUS v1.2 added the pricing-currency columns for.

**ChargeCategory:** Map `capacity` and `usage` both to "Usage"; add "Purchase" for prepaid order lines; add "Tax" and "Credit" rows.

**ServiceCategory:** "Analytics" for Elasticsearch (Hosted and Serverless), "Management and Governance" for Observability, "Security" for Security, "Networking" for data transfer lines.

**PricingUnit and ConsumedUnit:** Normalize `hour` to "Hours", GB-retained to "GB-Months", VCUs to "VCU-Hours", snapshot requests to "1000 Requests". Serverless ingest and retention are volume-tiered, so PricingQuantity must follow the tier basis in `quantities[].tiers[]`, not total consumption.

**SkuId and RegionId:** Split the composite `sku` into a stable product SKU (SkuId), the full price point (SkuPriceId, already present), and the region (RegionId).

**SkuPriceDetails:** Serialize tier `min`, `max`, and `rate` as FOCUS key-value JSON.

**InvoiceId:** Stamp the invoice `number` onto each line item once the period is invoiced.

**Already right:** Instance-level resource IDs and names, SKU-level rates and quantities, tier breakdowns, arbitrary date ranges, and CSV output.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (ratified June 4, 2026); certify at FOCUS v1.2, the version the conformance program currently names. FOCUS v1.5 is a candidate release; its scope is on the FOCUS site. The v1.3 Contract Commitment dataset is a natural home for prepaid ECU order lines (quantity, paid amount, term, and expiry), and the v1.4 Invoice Detail dataset addresses the missing invoice linkage.

### 2.2 What Certification Requires

FinOps Certified FOCUS v1.2 Conformant runs through the FinOps Foundation (contact `member-cert@finops.org` for the RFI; membership is required for certification). Deliverables: a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report seeded by this analysis. Tooling: FOCUS Validator, FOCUS Converter, and the FOCUS Requirements Model. Document the N/A rationale (single account type, no sub-accounts, no capacity reservations, no per-zone billing) and the decision to model prepaid consumption as a spend-based commitment discount.

### 2.3 Phased Roadmap

**Phase 0: Validate.** Pull one month from `costs/instances` and `costs/instances/{id}/items` for a monthly direct organization and a prepaid one. Hand-build a v1.2 file and run it through the Validator. Correct the OpenAPI types for `total_ecu` and `rate.value` and publish example responses.

**Phase 1: Close Mandatory gaps.** Emit BillingCurrency as ISO 4217 and PricingCurrency as "ECU". Set ContractedCost to ListCost. Apply each prepaid order line's effective ECU price for EffectiveCost. Split drawdown from overage in BilledCost and add Purchase, Tax, and Credit rows so the dataset reconciles to the invoice.

**Phase 2: Fix deviations.** Map ChargeCategory, ServiceCategory, and PricingUnit; derive InvoiceIssuerName from entity and billing model; parse SkuId and RegionId out of the composite SKU; serialize SkuPriceDetails; stamp InvoiceId.

**Phase 3: Allocation and Conditional columns.** Join deployment and project tags into Tags; add RegionName, PricingCategory, ChargeFrequency, ServiceSubcategory, and the CommitmentDiscount family keyed to prepaid order lines. Expose the order lines and credit balance in the public API, and offer scheduled delivery to S3, GCS, or Azure Blob.

**Phase 4: Mature and certify.** Drop ProviderName and PublisherName for v1.4; add the Contract Commitment and Invoice Detail datasets; certify at v1.2 and re-certify as the program advances.

### 2.4 FOCUS Use Cases Unlocked

- **Available now (monthly direct accounts):** Spend by deployment or project, SKU-level unit cost, and daily trend and anomaly detection at list price.
- **After Phase 1:** Invoice reconciliation, actuals-based budgeting and forecasting, and amortized spend reporting for prepaid customers.
- **After Phase 2:** Spend by service category and region across providers.
- **After Phase 3:** Chargeback and showback by tag; prepaid commitment utilization and forfeiture risk; unit economics per GB ingested or VCU-hour.
- **Out of scope:** Capacity reservation management and per-zone cost analysis.

---

## Part 3: Immediate Next Steps

1. Follow up with the Elastic contact from KubeCon NA 2026 to identify the owner of the Cloud Billing API and the `ess_billing` integration.
2. Ask Elastic to publish example v2 responses, the console CSV column list, and the credits endpoint the integration uses.
3. Confirm how prepaid order lines, discounts, and non-USD contracts appear on invoices and statements.
4. Build a v1.2 sample from one billing month and run it through the FOCUS Validator.
5. Open the RFI with `member-cert@finops.org`.

---

## Confidence Summary

- **High:** The v2 Billing API endpoints, parameters, and line item schema, taken from Elastic's published OpenAPI spec. The v1 costs endpoints are marked deprecated.
- **High:** ECU = $1.00, USD-only monthly billing, discounted multi-currency prepaid credits with forfeiture, overage at list, and the Usage page's exclusion of credits, allowances, and discounts, all from Elastic's billing docs.
- **High:** Feature levels match the FOCUS v1.2 Content Constraints; ChargeFrequency, ServiceSubcategory, PricingQuantity, and InvoiceId were spot-checked against the live spec on November 17, 2026, and v1.4 remains the latest ratified version. The FOCUS MCP was unavailable for this run, so the check used the public spec pages.
- **Moderate:** Present status for ChargePeriodStart/End and SkuMeter rests on the `quantities[]` schema and integration fields, since no v2 example payload is published.
- **Moderate:** Modeling prepaid consumption as a spend-based commitment discount. If Elastic treats prepaid ECU as a currency purchase rather than a discount instrument, the CommitmentDiscount columns become N/A and the discount moves entirely into the PricingCurrency exchange rate.
- **Moderate:** "ECU" as a valid PricingCurrency value. Confirm the v1.2 Currency Format attribute's treatment of virtual currencies against the Requirements Model.
- **Moderate:** ServiceCategory and ServiceSubcategory mappings ("Analytics"/"Search", "Management and Governance"/"Observability"); confirm against the v1.2 allowed-value tables.
- **Moderate:** Absence of any Elastic FOCUS export or announcement. Searches of elastic.co and the web found none, but absence is hard to prove.
- **Low:** The console CSV schema. It probably mirrors the v2 `text/csv` response, but Elastic does not document it.
- **Unknown:** Whether `total_ecu` and `rate.value` are integers (as typed in the spec) or decimals (as emitted by the integration).

---

## Sources

- Elastic Cloud Billing API v2: [elastic.co/docs/api/doc/cloud-billing](https://www.elastic.co/docs/api/doc/cloud-billing)
- Elastic Cloud API, Billing Costs Analysis (v1, deprecated): [elastic.co/docs/api/doc/cloud/group/endpoint-billingcostsanalysis](https://www.elastic.co/docs/api/doc/cloud/group/endpoint-billingcostsanalysis)
- Elastic Cloud Billing overview: [elastic.co/docs/deploy-manage/cloud-organization/billing](https://www.elastic.co/docs/deploy-manage/cloud-organization/billing)
- Elastic Consumption Units: [elastic.co/docs/deploy-manage/cloud-organization/billing/ecu](https://www.elastic.co/docs/deploy-manage/cloud-organization/billing/ecu)
- Billing Models: [elastic.co/docs/deploy-manage/cloud-organization/billing/billing-models](https://www.elastic.co/docs/deploy-manage/cloud-organization/billing/billing-models)
- Billing FAQ: [elastic.co/docs/deploy-manage/cloud-organization/billing/billing-faq](https://www.elastic.co/docs/deploy-manage/cloud-organization/billing/billing-faq)
- Monitor and Analyze Usage: [elastic.co/docs/deploy-manage/cloud-organization/billing/monitor-analyze-usage](https://www.elastic.co/docs/deploy-manage/cloud-organization/billing/monitor-analyze-usage)
- Hosted Deployment Billing Dimensions: [elastic.co/docs/deploy-manage/cloud-organization/billing/cloud-hosted-deployment-billing-dimensions](https://www.elastic.co/docs/deploy-manage/cloud-organization/billing/cloud-hosted-deployment-billing-dimensions)
- Serverless Billing Dimensions: [Elasticsearch](https://www.elastic.co/docs/deploy-manage/cloud-organization/billing/elasticsearch-billing-dimensions), [Observability](https://www.elastic.co/docs/deploy-manage/cloud-organization/billing/elastic-observability-billing-dimensions), [Security](https://www.elastic.co/docs/deploy-manage/cloud-organization/billing/security-billing-dimensions)
- Elastic Pricing: [elastic.co/pricing/serverless-search](https://www.elastic.co/pricing/serverless-search), [elastic.co/pricing/faq](https://www.elastic.co/pricing/faq)
- Elasticsearch Service Billing integration: [elastic.co/docs/reference/integrations/ess_billing](https://www.elastic.co/docs/reference/integrations/ess_billing)
- Deployment Tags API: [elastic.co/docs/api/doc/cloud/operation/operation-set-deployment-tags](https://www.elastic.co/docs/api/doc/cloud/operation/operation-set-deployment-tags)
- Serverless Project Settings: [elastic.co/docs/deploy-manage/deploy/elastic-cloud/project-settings](https://www.elastic.co/docs/deploy-manage/deploy/elastic-cloud/project-settings)
- Elastic Blog, Elastic Cloud Spend Insights (October 2023): [elastic.co/blog/elastic-cloud-spend-data-driven-insights](https://www.elastic.co/blog/elastic-cloud-spend-data-driven-insights)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FOCUS 1.5 Release Scope: [focus.finops.org/focus-1-5-release-scope/](https://focus.finops.org/focus-1-5-release-scope/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
