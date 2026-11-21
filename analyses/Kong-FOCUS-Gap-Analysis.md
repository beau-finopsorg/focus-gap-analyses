# Kong & FOCUS: Data Generator Gap Analysis

*Analysis run: November 17, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** Kong Inc.  
**Prepared:** November 17, 2026  
**Origin:** KubeCon NA 2026 booth outreach  
**Source:** Public Kong documentation only: Konnect pricing page; Konnect account docs (Billing and Usage page); Konnect Advanced Analytics API; Konnect geos and labels docs; Kong Gateway Enterprise `GET /license/report`; Kong AI Cost Management exports, price catalog, and analytics docs; Kong AI Gateway audit log reference  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 16 Present, 8 Deviation, 3 Missing Mandatory, 18 Missing Conditional, 1 Missing Recommended, 11 N/A

---

## Executive Summary

Kong sells Kong Konnect, a SaaS API platform (API Gateway, AI Gateway, Dedicated Cloud Gateways, Developer Portals, Analytics, Metering & Billing, Kong Identity, Event Gateway), and self-managed Kong Gateway Enterprise licenses. Konnect Plus is self-serve: a $25 monthly base plus metered usage, billed monthly in arrears in USD, with resource meters (control planes, portals, models) prorated hourly on a 730-hour month. Enterprise is custom pricing billed annually, with contracted request volumes and volume discounts.

This analysis covers the two directions in which Kong touches FOCUS:

1. **Kong as a data generator for its own charges.** This is weak. The only documented billing surface is the Konnect **Billing and Usage** page, which shows service, Dev Portal, and API call usage. Kong publishes no billing API, no invoice field definitions, and no usage export. Of the 21 Mandatory columns, 18 have a source and 3 are missing. One gap is substantive: **EffectiveCost**, because Enterprise contracts are billed annually up front and trial and promotional credits exist, so no current surface shows amortized, credit-adjusted cost. **ListCost** and **ContractedCost** are price-book joins.
2. **Kong as a FOCUS producer for third-party AI spend.** This is already shipping. Kong AI Cost Management exports a `focus` dataset (FOCUS 1.3 or 1.4, CSV or Parquet, daily or hourly) covering estimated LLM spend routed through Kong AI Gateway, with a monthly true-up to provider invoices. This is unusual: Kong emits FOCUS for other vendors' bills before it emits FOCUS for its own.

The irony is the headline. Kong has the FOCUS tooling, the export scheduler, and a key-value label model on control planes. It has not pointed any of it at the Konnect invoice.

**Recommendation:** Reuse the AI Cost Management export pipeline to publish a monthly Konnect FOCUS export per organization: one Usage row per meter × control plane (or portal, model, or Dedicated Cloud Gateway network) × day, one Purchase row for the Plus base fee or Enterprise subscription, and separate Tax and Credit rows so the dataset reconciles to the invoice. Carry control plane labels into Tags and the Konnect geo into RegionId.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

Kong's own billing data (the subject of the column table):

- **Billing and Usage page** (`cloud.konghq.com/global/plan-and-usage/`): Shows "service, Dev Portal, and API call usage" and manages payment. Kong documents no CSV export, no per-control-plane or per-geo breakdown, and no invoice field list.
- **Monthly invoices:** "Calculated at the end of every calendar month" and billed in arrears for Plus. Enterprise pays by invoice or PO. No public sample or field definition.
- **Konnect pricing page:** Full published price list for Plus. API requests: 1M included, then $200 per additional million per month (10M cap on Plus). AI model proxy: $100 per model per month. Dedicated Cloud Gateways: $500 per control plane per month plus $0.15 per GB bandwidth. Serverless control planes $25 and hybrid control planes $200 per month. Extra Developer Portal $200 per month. Analytics $20 per 1M requests above 1M. Metering & Billing $20 per million events plus 0.4% of billing volume. Kong Identity $30 per 1M access tokens.
- **Konnect Advanced Analytics API:** Request metrics groupable by `control_plane`, `control_plane_group`, `gateway_service`, `route`, `consumer`, `application`, `api_product`, `data_plane_node`, and time, down to 10-second granularity. It carries no price or cost.
- **Kong Gateway Enterprise `GET /license/report`:** On-demand report of `services_count`, `routes_count`, `consumers_count`, `workspaces_count`, `rbac_users`, `plugins_count`, request `counters`, and the license payload (`customer`, `product_subscription`, `dataplanes`, `admin_seats`, expiration). Nothing is sent to Kong and there is no cost data.

Kong's FOCUS output for third-party spend (assessed separately in 1.4):

- **AI Cost Management exports:** `usage_events` and `focus` datasets, created in the Konnect UI or through `POST /v1/ai-cost-management/exports` and `/export-schedules` (public API in beta, v0.3.0). FOCUS version `1.3` or `1.4`; CSV, CSV gzip, or Parquet Zstandard; `day` or `hour` charge period; up to 64 tag keys; one file per calendar month with a SHA-256 `manifest.json`. Files are pulled through five-minute URLs, not pushed to storage.
- **Cost basis:** Token counts × a USD price catalog (list price, provider-wide discounts, or per-model custom rates). AI Gateway logs `ai.proxy.usage.cost` per request; Explorer shows LLM cost, embeddings cost, and cost savings.

Key characteristics:

- **Hierarchy:** One organization spans all geos; "only authentication, billing, and usage" are shared across geos. Below it sit control plane groups, control planes, gateway services, routes, consumers, and Developer Portals.
- **Geos:** US, EU, AU, ME, IN, and SG, each backed by AWS regions. Plus Dedicated Cloud Gateways are limited to one region.
- **Labels:** Case-sensitive key:value pairs, up to 5 user-defined per resource, supported on control planes.
- **Marketplaces:** Konnect is sold through AWS Marketplace and Google Cloud Marketplace. Those purchases are invoiced by the hyperscaler.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven: every Mandatory column must be present and valid, and Conditional columns are required when the provider's model triggers their condition. Kong deploys resources in geos and regions and supports user-defined labels, so RegionId, RegionName, and Tags apply. Enterprise contracts sell committed request volumes at volume-discounted rates, so this analysis treats the CommitmentDiscount family as applicable. Kong has one billing account type (the Konnect organization), no billing sub-accounts, no capacity reservations, and USD-only pricing; those columns are N/A and should exist as null. Feature levels follow the FOCUS v1.2 Content Constraints, spot-checked against the live spec on November 17, 2026.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | Kong source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Monthly invoice amount; no line-level export per meter or resource | Deviation |
| EffectiveCost | Mandatory | Not available: needs amortization of annual Enterprise fees and allocation of trial and promotional credits | Missing: Mandatory |
| ListCost | Mandatory | Not exposed; join the public price list × PricingQuantity | Missing: Mandatory |
| ContractedCost | Mandatory | Not exposed; equals ListCost on Plus, Enterprise contract rate card × PricingQuantity | Missing: Mandatory |
| BillingAccountId | Mandatory | Konnect organization ID | Present |
| BillingAccountName | Mandatory | Konnect organization name | Present |
| BillingCurrency | Mandatory | "USD" | Present |
| BillingPeriodStart | Mandatory | First day of the calendar month | Present |
| BillingPeriodEnd | Mandatory | First day of the following month (exclusive) | Present |
| ChargePeriodStart | Mandatory | Calendar month start (Billing and Usage is month-level) | Present |
| ChargePeriodEnd | Mandatory | Calendar month end | Present |
| ChargeDescription | Mandatory | Invoice line description | Present |
| ChargeCategory | Mandatory | Derive: "Purchase" for the Plus base fee and Enterprise subscription; "Usage" for requests, bandwidth, and hourly-prorated resources; "Tax" and "Credit" rows from the invoice | Deviation |
| ChargeClass | Mandatory (nullable) | null; "Correction" for re-issued charges | Present |
| InvoiceIssuerName | Mandatory | "Kong Inc." for direct; "Amazon Web Services" or "Google" for marketplace purchases | Present |
| ProviderName | Mandatory (dep. v1.3) | "Kong" | Present |
| PublisherName | Mandatory (dep. v1.3) | "Kong" | Present |
| ServiceName | Mandatory | Konnect product (e.g., "API Gateway", "AI Gateway", "Dedicated Cloud Gateways", "Developer Portal", "Advanced Analytics", "Metering & Billing", "Kong Identity") | Present |
| ServiceCategory | Mandatory | Derive: "Integration" for API, AI, and event gateways, portals, and Metering & Billing; "Networking" for gateway bandwidth; "Analytics" for analytics; "Identity" for Kong Identity | Deviation |
| PricingQuantity | Mandatory | Requests, control plane hours, GB, models, events, tokens; tiered (1M requests included), so compute against the rate basis | Deviation |
| PricingUnit | Mandatory | Normalize: "1M Requests", "Hours", "GB", "Models", "1M Events", "1M Tokens" | Deviation |
| ConsumedQuantity | Conditional | Billing and Usage counts (API calls, services, portals) | Present |
| ConsumedUnit | Conditional | Implicit in the usage page; normalize to FOCUS unit format | Deviation |
| ListUnitPrice | Conditional | Not exposed; public price list | Missing: Conditional |
| ContractedUnitPrice | Conditional | Not exposed; Enterprise contract rates | Missing: Conditional |
| PricingCategory | Conditional | Derive: "Standard" for Plus usage; "Committed" for usage within Enterprise contracted volumes | Deviation |
| BillingAccountType | Conditional | N/A: one account type (Konnect organization) | N/A |
| SubAccountId | Conditional | N/A: billing is organization-wide; geos and control planes are not billing entities | N/A |
| SubAccountName | Conditional | N/A | N/A |
| SubAccountType | Conditional | N/A | N/A |
| ResourceId | Conditional | Not in billing; candidates are control plane, Dedicated Cloud Gateway network, portal, and model IDs (Analytics API already keys requests by `control_plane`) | Missing: Conditional |
| ResourceName | Conditional | Not in billing; control plane and portal names | Missing: Conditional |
| ResourceType | Conditional | Not in billing; "Serverless Control Plane", "Hybrid Control Plane", "Dedicated Cloud Gateway", "Developer Portal" | Missing: Conditional |
| SkuId | Conditional | Not exposed; internal plan and meter codes | Missing: Conditional |
| Tags | Conditional | Konnect labels (key:value, up to 5 per resource) exist on control planes but are not in billing | Missing: Conditional |
| PricingCurrency | Conditional | N/A: priced and billed in USD only | N/A |
| PricingCurrencyListUnitPrice | Conditional | N/A | N/A |
| PricingCurrencyContractedUnitPrice | Conditional | N/A | N/A |
| PricingCurrencyEffectiveCost | Conditional | N/A | N/A |
| SkuMeter | Conditional | Usage page meters (API calls, services, Dev Portal) | Present |
| SkuPriceId | Conditional | Not exposed | Missing: Conditional |
| SkuPriceDetails | Conditional | Not exposed; needed for the included-allowance tier and Plus vs. Enterprise price points | Missing: Conditional |
| RegionId | Conditional | Not in billing; Konnect geo ("us", "eu", "au", "me", "in", "sg") or Dedicated Cloud Gateway cloud region | Missing: Conditional |
| RegionName | Conditional | Not in billing | Missing: Conditional |
| CommitmentDiscountId | Conditional | Enterprise contract or contracted request volume ID; not exposed | Missing: Conditional |
| CommitmentDiscountName | Conditional | Not exposed | Missing: Conditional |
| CommitmentDiscountType | Conditional | Not exposed (e.g., "Contracted Requests") | Missing: Conditional |
| CommitmentDiscountCategory | Conditional | "Usage"; not exposed | Missing: Conditional |
| CommitmentDiscountStatus | Conditional | "Used"/"Unused" against the contracted volume | Missing: Conditional |
| CommitmentDiscountQuantity | Conditional | Requests drawn against the contract | Missing: Conditional |
| CommitmentDiscountUnit | Conditional | "Requests" | Missing: Conditional |
| CapacityReservationId | Conditional | N/A: no capacity reservations | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | Invoice number | Present |
| ChargeFrequency | Recommended | Derive: "Recurring" for base fee, control planes, portals, and models; "Usage-Based" for requests, bandwidth, events, and tokens | Deviation |
| ServiceSubcategory | Recommended | Not exposed; map each product to an allowed v1.2 value (e.g., "API Management") | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: Kong operates the gateway infrastructure; zones are not customer-billed | N/A |

**Tally:** 16 Present, 8 Deviation, 3 Missing Mandatory, 18 Missing Conditional, 1 Missing Recommended, 11 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Organization identity, USD billing, calendar-month periods, invoice numbers, a complete public price list for Plus, and usage counts by meter. The Analytics API already attributes requests to control planes, services, and consumers, and labels already use FOCUS's key-value shape.

**Substantive (1 of 3 Mandatory gaps):**

- **EffectiveCost.** Enterprise is billed annually up front, and trials and promotions grant credits. Producing EffectiveCost means amortizing the annual fee across the term and allocating credits back to the charges they offset. On a pure Plus account with no credits, EffectiveCost equals BilledCost; on the accounts FinOps teams care about, it does not.

**Trivial (2 of 3 Mandatory gaps):**

- **ListCost.** Kong publishes the price list. Join list unit price by meter and multiply by PricingQuantity, applying the included allowance through SkuPriceDetails.
- **ContractedCost.** Equal to ListCost on Plus. For Enterprise, Kong's billing system already holds the contract rate card; expose it.

**Substantive, beyond the column table:**

- **No billing data feed.** The Billing and Usage page is UI-only with no documented export or API. Nothing about Kong's own charges reaches a FinOps tool without screen-scraping or invoice PDFs.
- **Allocation.** Billing is organization-wide. A platform team running dozens of control planes across geos cannot attribute Konnect spend to the business units behind them, even though the Analytics API, the labels model, and the geo model all hold the needed keys.
- **Marketplace split.** Customers who buy through AWS or Google Cloud Marketplace see Kong as one subscription line in the hyperscaler's FOCUS data, with no meter or resource detail. A Kong export with InvoiceIssuerName set to the marketplace is the only way to break that line down.

**Kong as a FOCUS producer for third-party AI spend:**

Kong AI Cost Management already emits FOCUS for LLM spend routed through AI Gateway. Two design choices stand out:

- **FOCUS 1.3 output double-counts.** BilledCost, EffectiveCost, ListCost, and ContractedCost all carry Kong's estimate. Kong's own docs warn that loading this beside the model provider's FOCUS data "counts the same spend twice."
- **FOCUS 1.4 output zeroes the cost columns** and moves the estimate to `x_ReportedCost`. This avoids double-counting because Kong does not invoice model usage. The cost is that FOCUS-native tools see $0 rows, and ListCost of 0 misstates the list price of tokens Kong has in its own price catalog.

The underlying problem is that Kong is an allocation layer, not the invoice issuer, and FOCUS v1.2 through v1.4 have no first-class way to express "attribution metadata for someone else's charge." The monthly true-up (invoice amount ÷ Kong estimate, matched by month, provider, model, and region) is the valuable part. Kong should bring this pattern to the FOCUS working group rather than settle it unilaterally with zero-cost rows.

### 1.5 Deviations to Fix

**BilledCost:** Emit one row per meter and resource rather than an invoice total, plus Tax and Credit rows, so that BilledCost summed per InvoiceId equals the invoice total.

**ChargeCategory:** "Purchase" for the Plus base fee and the Enterprise subscription; "Usage" for requests, bandwidth, events, tokens, and hourly-prorated resources; "Tax" and "Credit" as above.

**ServiceCategory:** "Integration" for API, AI, and event gateways, Developer Portals, and Metering & Billing; "Networking" for Dedicated Cloud Gateway bandwidth; "Analytics" for Advanced Analytics overages; "Identity" for Kong Identity.

**PricingQuantity and PricingUnit:** Requests and analytics are priced per million above a 1M included allowance, so they are tiered, not flat-rate. Compute PricingQuantity against the rate basis ("1M Requests") and express the free allowance in SkuPriceDetails. Control planes, portals, and models are monthly prices prorated hourly; use "Hours" with a list unit price of the monthly price ÷ 730.

**ConsumedUnit, PricingCategory, ChargeFrequency:** Derive from meter type as shown in the table.

**Already right:** USD-only billing, calendar-month periods, a public price list, and key-value labels map cleanly.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (ratified June 4, 2026); certify at FOCUS v1.2, the version the conformance program currently names. Kong's AI Cost Management export already supports v1.4, so the Konnect export should share that code path. FOCUS v1.5 is a candidate release; its scope is on the FOCUS site. The v1.3 Contract Commitment dataset fits Enterprise contracted request volumes better than per-row CommitmentDiscount columns alone.

### 2.2 What Certification Requires

FinOps Certified FOCUS v1.2 Conformant runs through the FinOps Foundation (contact `member-cert@finops.org` for the RFI; membership is required for certification, and Kong is not currently a member). Deliverables: a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report seeded by this analysis. Tooling: FOCUS Validator, FOCUS Converter, and the FOCUS Requirements Model. Document the N/A rationale (single account type, no sub-accounts, reservations, or alternate currencies) and the decision on modeling Enterprise contracted volumes as commitment discounts. Certification would cover the Konnect billing export, not the AI Cost Management overlay.

### 2.3 Phased Roadmap

**Phase 0: Validate.** Pull one month of Billing and Usage data and the matching invoice for a Plus organization and an Enterprise one. Hand-build a v1.2 file and run it through the Validator. Decide the Enterprise commitment model.

**Phase 1: Close Mandatory gaps.** Join the price list for ListCost and ListUnitPrice and the contract rate card for ContractedCost. Amortize annual Enterprise fees and allocate credits for EffectiveCost. Emit line-level BilledCost with Tax and Credit rows so it reconciles to the invoice.

**Phase 2: Fix deviations.** Derive ChargeCategory, ServiceCategory, ChargeFrequency, and PricingCategory; normalize PricingUnit and ConsumedUnit; compute PricingQuantity against the tiered rate basis.

**Phase 3: Allocation and Conditional columns.** Add ResourceId, ResourceName, and ResourceType per control plane, Dedicated Cloud Gateway, portal, and model; RegionId and RegionName from the Konnect geo; Tags from control plane labels; SkuId, SkuPriceId, and SkuPriceDetails; the CommitmentDiscount family; and ServiceSubcategory. Deliver through the existing export-schedule API, and add push delivery to object storage.

**Phase 4: Mature and certify.** Drop ProviderName and PublisherName for v1.4; add the Invoice Detail dataset; certify at v1.2 and re-certify as the program advances. In parallel, raise the AI Cost Management zero-cost-row pattern with the FOCUS working group.

### 2.4 FOCUS Use Cases Unlocked

- **After Phase 1:** Invoice reconciliation, actuals-based budgeting and forecasting, and amortized spend reporting for Konnect.
- **After Phase 2:** Spend by service category across providers, and subscription-versus-usage mix analysis.
- **After Phase 3:** Chargeback and showback by control plane, geo, or label; unit economics per million API requests; Enterprise contracted volume utilization; and anomaly detection on request and bandwidth meters.
- **Already available (AI Cost Management):** Allocation of LLM spend by team, application, consumer, and tag, with invoice true-up.
- **Out of scope:** Capacity reservation management and multi-currency analysis.

---

## Part 3: Immediate Next Steps

1. Follow up with the Kong contact from KubeCon NA 2026 to reach the owner of Konnect billing and the AI Cost Management export team.
2. Confirm what the Billing and Usage page and invoices contain today (line items, per-control-plane detail, any export).
3. Confirm whether the `kbilling` usage API referenced in some search summaries exists and is customer-facing.
4. Build a v1.2 sample from one billing month and run it through the FOCUS Validator.
5. Open the RFI with `member-cert@finops.org` and discuss FinOps Foundation membership.

---

## Confidence Summary

- **High:** Konnect Plus pricing, meters, hourly proration on 730 hours, calendar-month arrears billing, and USD-only payment are taken from Kong's pricing page.
- **High:** AI Cost Management exports a `focus` dataset in versions 1.3 and 1.4, with estimates in all four cost columns for 1.3 and zero cost columns plus `x_ReportedCost` for 1.4; Kong documents the double-counting risk.
- **High:** Feature levels match the FOCUS v1.2 Content Constraints; spot-checked against the live spec on November 17, 2026, and v1.4 remains the latest ratified version.
- **Moderate:** Present status for invoice-sourced columns (ChargeDescription, InvoiceId, BillingAccountName). Kong publishes no invoice sample or field list, so presence is inferred from standard invoicing.
- **Moderate:** Treating Enterprise contracted request volumes as commitment discounts. If Kong models them as flat Purchase entitlements with no per-unit rate benefit, the seven CommitmentDiscount columns become N/A.
- **Moderate:** ServiceCategory and ServiceSubcategory mappings for an API platform; "Integration" and "API Management" are the closest v1.2 values but should be confirmed against the spec's allowed-value tables.
- **Low:** A Konnect billing usage API. One search summary cited a `/kbilling/v1/usage` endpoint, but no published API reference confirms it.
- **Low:** InvoiceIssuerName as "Kong Inc." No public invoice names the issuing entity; non-US entities may invoice some contracts.
- **Low:** Event Gateway and Mesh pricing. These were not verified on the public pricing page.

---

## Sources

- Kong Pricing: [konghq.com/pricing](https://konghq.com/pricing)
- Konnect Account and Billing and Usage: [developer.konghq.com/konnect-platform/account/](https://developer.konghq.com/konnect-platform/account/)
- Konnect Geos: [developer.konghq.com/konnect-platform/geos/](https://developer.konghq.com/konnect-platform/geos/)
- Konnect Labels: [developer.konghq.com/konnect-platform/konnect-labels/](https://developer.konghq.com/konnect-platform/konnect-labels/)
- Konnect Advanced Analytics API: [docs.konghq.com/konnect/api/metrics/latest](https://docs.konghq.com/konnect/api/metrics/latest)
- Konnect Explorer: [developer.konghq.com/observability/explorer/](https://developer.konghq.com/observability/explorer/)
- Kong Gateway License Entity and Report: [developer.konghq.com/gateway/entities/license/](https://developer.konghq.com/gateway/entities/license/)
- AI Cost Management Exports: [developer.konghq.com/ai-cost-management/exports/](https://developer.konghq.com/ai-cost-management/exports/)
- AI Cost Management Price Catalog: [developer.konghq.com/ai-cost-management/price-catalog/](https://developer.konghq.com/ai-cost-management/price-catalog/)
- AI Gateway Audit Log Reference: [developer.konghq.com/ai-gateway/ai-audit-log-reference/](https://developer.konghq.com/ai-gateway/ai-audit-log-reference/)
- Kong Blog, AI Gateway FinOps Integration (November 5, 2026): [konghq.com/blog/product-releases/kong-ai-gateway-finops-integration](https://konghq.com/blog/product-releases/kong-ai-gateway-finops-integration)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FOCUS 1.5 Release Scope: [focus.finops.org/focus-1-5-release-scope/](https://focus.finops.org/focus-1-5-release-scope/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
