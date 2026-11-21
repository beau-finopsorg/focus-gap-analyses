# Yotta and FOCUS: Conformance Gap and Adoption Roadmap

*Analysis run: July 1, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

Prepared: 2026-07-01
Provider and product in scope: Yotta Data Services (India sovereign cloud and AI infrastructure), covering Shakti Cloud GPU services: AI Lab, AI Workspace VM (on-demand and dedicated), Bare Metal GPU (H100/B200/B300/L40S), SLURM and Kubernetes Clusters, and Shakti Studio (AI Endpoints, Serverless GPUs, Fine-Tuning), plus the AI Support Services catalog (CPU VMs, storage, network, database, security).
Source analyzed: Yotta and Shakti Cloud public materials (shakticloud.ai pricing and product pages, yotta.com Shakti Cloud and corporate pages). No customer-portal billing export, invoice schema, or billing API documentation was available for review.
FOCUS baseline: v1.2 (current certification baseline). Build target: v1.4 (latest ratified, 2026-06-04).
Feature levels verified against the FOCUS Specification via the FOCUS column library on 2026-07-01; the bundled v1.2 table (57 columns) was confirmed current and no refresh was required.

---

## Executive summary

Yotta has a detailed, unit-priced rate card and a stated single-portal billing model, but it does not publish a machine-readable, line-item cost and usage dataset. The public materials describe "a single portal for all billing and service management," "unified dashboards and APIs," and "full visibility of usage, performance, and billing," and Shakti Studio advertises usage, latency, and cost observability with logs, dashboards, and role-based access controls. What is not documented anywhere public is a per-charge-record export, a billing or usage API that returns costed line items, or a FOCUS-style dataset.

That absence is the headline. Yotta clearly meters consumption (per-hour, per-minute, per-token, per-GB) and prices it cleanly in Indian Rupees, and it operates a customer console. But the dataset that FOCUS normalizes, a per-resource, per-charge costed record, is not exposed for review today. A conformance effort here is mostly a data-production project (emit and expose a per-charge-record usage and cost feed) rather than a re-shaping project.

Stat strip:
- 57 FOCUS columns assessed (v1.2 baseline)
- 0 columns confirmed present in a conformant exportable dataset (metering and a console exist, but no line-item export was available for review)
- 21 of 21 Mandatory columns are gaps; the substantive core is the four cost columns plus billing-period and charge-period framing
- 0 deviations to fix (no FOCUS-shaped dataset exists to deviate)

Recommendation: treat this as a Phase 1 dataset-production and dataset-exposure effort. Yotta already holds the inputs (metered consumption, an INR price catalog, a customer account and console, and term-based commitments). The work is to assemble them into a daily, per-resource charge record carrying List, Billed, Effective, and Contracted cost, expose it as an export or API, then shape that record to FOCUS column IDs.

Readiness (reflects the data source reviewed, not a formal certification result):
- Cost: Gap
- Granularity: Partial
- Allocation: Partial
- Coverage: Gap
- FOCUS shape: Gap
- Overall band: Not yet aligned (per public docs)

---

## Part 1: The conformance gap

### 1.1 The data source

Yotta Data Services is India's sovereign cloud and AI infrastructure provider, operating hyperscale data centers in Navi Mumbai and Greater Noida, with the Yntraa hyperscale cloud (MeitY-empanelled) and Shakti Cloud (AI and GPU services, NVIDIA partnership). Shakti Cloud's billing-relevant surface, as documented publicly, has these characteristics.

Product and metering model: a broad catalog spanning several billing grains. AI Lab is priced per workstation, per month. AI Workspace VM splits into On Demand GPU Compute billed per hour, per compute (for example, ₹356/hour for 1x H100) and Dedicated GPU Compute billed per month, per compute with selectable 1-month, 3-month, 6-month, and 1-year terms. Bare Metal GPU (8x HGX H100, 8x HGX B200, 8x HGX B300, 4x L40S) is billed per GPU, per hour with commitment terms up to 5 years. SLURM and Kubernetes Clusters bill per GPU, per hour. Shakti Studio bills AI Endpoints per million input and output tokens, and Serverless GPUs on a Spot (per-minute) or Flex (per-month) basis. AI Support Services (CPU VMs per month, storage per GB per month, network per GB or per Mbps, databases, security) round out the catalog.

Billing model: pay-as-you-go for hourly, per-minute, and per-token services, alongside term-based commitments (the monthly and multi-year toggles). A managed-services fee scales on a spend bracket (for example, 20 percent of monthly cloud spend, falling to 17 percent above ₹1 crore and 15 percent above ₹5 crore), which is a services-fee sliding scale rather than a compute discount. The longer commitment terms imply lower effective rates for committed customers, though the public pages show one price per row and do not publish explicit committed-use discount percentages.

Account and portal model: Yotta operates a One Yotta account (account.yotta.com) and a Shakti Cloud console (portal.shakticloud.ai / console.shakticloud.ai), with Shakti Studio at shaktistudio.ai. Public messaging describes a single portal for all billing and service management, unified usage and billing dashboards, and role-based access controls in Shakti Studio. No project, sub-account, or cost-center construct is documented as a billing dimension, and no cost-allocation tagging is described (the only "tag" reference is container-image tagging in the registry service).

Usage and cost visibility: Shakti Studio advertises complete observability for usage, latency, and cost, plus logs and dashboards. This is product-level, in-console visibility. No downloadable line-item cost or usage export, no cost-and-usage-report equivalent file, and no billing or usage API returning costed records is documented publicly.

Pricing transparency and currency: the Shakti Cloud rate card is public and priced in Indian Rupees (₹) throughout, though enterprise engagements are frequently quote-based through the sales team. INR is a valid ISO 4217 code (INR), so currency will not need reshaping, but it should be emitted as the code rather than the ₹ symbol.

Key limitation: cost is not retrievable as structured per-charge records for review. The catalog establishes clean unit prices and metering grains, and the console surfaces usage and cost visually, but nothing publicly ties a consumption event to a costed, exportable line item. Everything downstream of FOCUS conformance depends on first producing and exposing that feed.

### 1.2 How conformance is judged

FOCUS defines a billing dataset as a set of columns, each carrying a feature level: Mandatory (must be present and populated where applicable), Conditional (required when the provider's model triggers the condition), Recommended (encouraged), or Optional. Conformance is judged column by column against the Requirements Model, which encodes the MUST/SHOULD/MAY rules and allowed values. A dataset is conformant when every Mandatory column is present and correctly populated, every applicable Conditional column is populated, formats and enums are valid, and provider-specific extensions are prefixed `x_`.

Feature levels for this analysis were taken from the verified v1.2 reference and confirmed against the live FOCUS column library on 2026-07-01. The v1.2 baseline carries 21 Mandatory, 32 Conditional, and 4 Recommended columns.

### 1.3 Column-by-column status

Legend: Present / Present, deviation to fix / Missing: Mandatory / Missing: Recommended / Missing: Conditional / N/A: null valid.

Because Yotta publishes no FOCUS-style dataset and no line-item export was available for review, no column is confirmed "Present" in a conformant export. The status below records, for each column, whether the underlying data plausibly exists in Yotta's platform (so the gap is assembly and exposure) or does not exist at all (so the gap is substantive). The level column is the verified v1.2 feature level.

| FOCUS Column | Level | In the source? | Status |
|---|---|---|---|
| AvailabilityZone | R | No (regions/DCs, no zones documented) | N/A: null valid |
| BilledCost | M | No (console visibility only, not per-record export) | Missing: Mandatory |
| BillingAccountId | M | Likely (One Yotta account, not in a billing record) | Missing: Mandatory |
| BillingAccountName | M | Likely (account name) | Missing: Mandatory |
| BillingAccountType | C | Partial (account construct) | Missing: Conditional |
| BillingCurrency | M | Yes (INR) | Missing: Mandatory |
| BillingPeriodEnd | M | No (no billing-period dataset documented) | Missing: Mandatory |
| BillingPeriodStart | M | No (no billing-period dataset documented) | Missing: Mandatory |
| CapacityReservationId | C | No (reservations not exposed as billing data) | N/A: null valid |
| CapacityReservationStatus | C | No | N/A: null valid |
| ChargeCategory | M | No (not classified in any feed) | Missing: Mandatory |
| ChargeClass | M | No | Missing: Mandatory |
| ChargeDescription | M | No | Missing: Mandatory |
| ChargeFrequency | R | No (mixed grains exist, not labeled per record) | Missing: Recommended |
| ChargePeriodEnd | M | No (no line-item time framing) | Missing: Mandatory |
| ChargePeriodStart | M | No | Missing: Mandatory |
| CommitmentDiscountCategory | C | Partial (term-based commitments exist) | Missing: Conditional |
| CommitmentDiscountId | C | Partial | Missing: Conditional |
| CommitmentDiscountName | C | Partial | Missing: Conditional |
| CommitmentDiscountQuantity | C | Partial | Missing: Conditional |
| CommitmentDiscountStatus | C | Partial | Missing: Conditional |
| CommitmentDiscountType | C | Partial | Missing: Conditional |
| CommitmentDiscountUnit | C | Partial | Missing: Conditional |
| ConsumedQuantity | C | Likely (GPU-hours, GPU-minutes, tokens, GB) | Missing: Conditional |
| ConsumedUnit | C | Likely (hours, minutes, tokens, GB) | Missing: Conditional |
| ContractedCost | M | No (contract/committed rates not in data) | Missing: Mandatory |
| ContractedUnitPrice | C | Partial (committed-term rates exist contract-side) | Missing: Conditional |
| EffectiveCost | M | No (only in-console cost visibility) | Missing: Mandatory |
| InvoiceId | R | Partial (single billing portal, no invoice ID in data) | Missing: Recommended |
| InvoiceIssuerName | M | Yes (Yotta Data Services) | Missing: Mandatory |
| ListCost | M | No (list prices exist, not costed per record) | Missing: Mandatory |
| ListUnitPrice | C | Yes (INR rate card, per hour/minute/token/GB) | Missing: Conditional |
| PricingCategory | C | Partial (on-demand vs committed/dedicated) | Missing: Conditional |
| PricingCurrency | C | Yes (INR) | Missing: Conditional |
| PricingCurrencyContractedUnitPrice | C | Partial | Missing: Conditional |
| PricingCurrencyEffectiveCost | C | No | Missing: Conditional |
| PricingCurrencyListUnitPrice | C | Yes (INR rate card) | Missing: Conditional |
| PricingQuantity | M | Likely (derivable from consumption for flat-rate SKUs) | Missing: Mandatory |
| PricingUnit | M | Likely (GPU-hour, GPU-minute, 1M tokens, GB) | Missing: Mandatory |
| ProviderName | M (removed v1.4) | Yes (Yotta) | Missing: Mandatory |
| PublisherName | M (removed v1.4) | Yes (Yotta) | Missing: Mandatory |
| RegionId | C | Partial (India DCs: Navi Mumbai, Greater Noida) | Missing: Conditional |
| RegionName | C | Partial (data center locations) | Missing: Conditional |
| ResourceId | C | Partial (instances/endpoints provisioned via console/API) | Missing: Conditional |
| ResourceName | C | Partial | Missing: Conditional |
| ResourceType | C | Partial (GPU type, VM flavor, storage class, model) | Missing: Conditional |
| ServiceCategory | M | Likely (derivable: AI and Machine Learning, Compute, Storage) | Missing: Mandatory |
| ServiceName | M | Likely (AI Lab, Bare Metal, Cluster, Shakti Studio, etc.) | Missing: Mandatory |
| ServiceSubcategory | R | Likely (derivable) | Missing: Recommended |
| SkuId | C | Partial (product/plan codes on the rate card) | Missing: Conditional |
| SkuMeter | C | Partial (token type, GPU-hour, GB) | Missing: Conditional |
| SkuPriceDetails | C | Partial (per-term, per-tier rate structure) | Missing: Conditional |
| SkuPriceId | C | No (no distinct price-record id documented) | Missing: Conditional |
| SubAccountId | C | No (no sub-account/project billing construct documented) | N/A: null valid |
| SubAccountName | C | No | N/A: null valid |
| SubAccountType | C | No | N/A: null valid |
| Tags | C | No (no cost-allocation tagging documented) | N/A: null valid |

Tally: of 57 v1.2 columns, 0 are confirmed present in a conformant export and 21 of 21 Mandatory columns are gaps. Seven columns are classified N/A because the model does not surface them as billing data: AvailabilityZone (regions and data centers, no zones), both capacity-reservation columns (reservations not exposed as billing data), the three sub-account columns (no documented sub-account, project, or cost-center billing construct), and Tags (no cost-allocation tagging documented). The remaining gaps split into data that plausibly exists in the platform and needs assembling and exposing versus data that does not exist anywhere yet.

### 1.4 What's solved, and what remains

The honest framing: nothing is "solved" in the sense of a conformant column today, because there is no reviewable dataset. But the gaps are not equally hard. Separating them is what makes the roadmap tractable.

Substantive gaps (data does not exist in usable per-record form, or was not available for review):
- BilledCost, EffectiveCost, ListCost, ContractedCost. This is the list-cost trap in its purest form: there is no list-cost dataset to copy from. Cost is shown only in-console, and committed/dedicated-term rates are negotiated contract-side rather than attached to consumption events. Producing the four cost columns requires building a per-charge-record costing pipeline that joins consumption events to the INR unit prices and reconciles contracted/committed rates. Treat all four as substantive, not trivial.
- BillingPeriodStart / BillingPeriodEnd and ChargePeriodStart / ChargePeriodEnd. No line-item time framing exists publicly; these require the same new per-record feed.
- ChargeCategory, ChargeClass, ChargeDescription. These classification fields only come into being once a charge record exists.

Trivial-once-the-feed-exists gaps (data plausibly already in the platform):
- Identity and structure: BillingAccountId/Name (the One Yotta account), ResourceId/Name/Type (provisioned instances, endpoints, storage), RegionId/Name (India data centers). Populating them is a join, not a data hunt, though confirmation against the console/API is needed.
- Quantities and units: ConsumedQuantity, ConsumedUnit, PricingUnit follow from the metering grains (GPU-hours, GPU-minutes, tokens, GB). PricingQuantity is derivable from consumption for flat-rate SKUs such as hourly Bare Metal and per-minute serverless; flag tiered, term-blended, or token-tiered pricing for proper computation against the rate basis rather than a straight copy.
- Prices: ListUnitPrice and the pricing-currency unit-price columns map from the published INR rate card.
- Provider framing: ProviderName, PublisherName, InvoiceIssuerName are all Yotta (Provider and Publisher are removed in v1.4, so a v1.4 build drops them).
- Currency: BillingCurrency and PricingCurrency are INR, emitted as the ISO 4217 code.

Net: the substantive core is the four cost columns plus the period and charge framing they live on. Everything else is plumbing that becomes straightforward once a per-charge-record feed exists and is exposed for export.

### 1.5 Deviations to fix

There are no format or enum deviations to correct, because no FOCUS-shaped dataset exists yet. The work ahead is production and exposure, not remediation. Two things Yotta should carry cleanly into the feed when it is built:
- Currency is INR, a valid ISO 4217 code, so it needs no reshaping (emit the code, not the ₹ symbol, and set the decimal handling consistently).
- Unit prices are already clean decimal INR values on the rate card, so ListUnitPrice and the pricing-currency prices will not need reshaping.

When the feed is built, validate that ChargeCategory uses only Usage, Purchase, Tax, Credit, Adjustment; that ServiceCategory uses valid members (AI and Machine Learning for endpoints, fine-tuning, and serverless GPUs; Compute for VMs, Bare Metal, and clusters; Storage for object, block, and file storage; Networking for VPC, IP, and bandwidth; Databases for managed database services); and that any Yotta-specific columns are prefixed `x_`. If cost-allocation tags are added, store them as key-value pairs rather than an array of bare strings.

---

## Part 2: The path forward

### 2.1 Which FOCUS version to target

Build toward v1.4, the latest ratified version (2026-06-04). Because Yotta would be producing a dataset from scratch, there is no legacy schema to migrate, so it should target the current shape directly and skip the deprecated `ProviderName` and `PublisherName` columns that v1.4 removes. For the certification milestone, the program baseline has historically been v1.2; design to v1.4 and certify against whatever version the program names, confirming the badge version against the program page before finalizing. The v1.4 Invoice Detail and billing-period datasets are a natural fit given Yotta's single-portal billing and invoicing model.

### 2.2 What certification requires

FOCUS conformance for data generators runs through the FinOps Foundation. The deliverables are a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report (this analysis is its seed). Membership is required for certification, though contributing to the spec is open and free; contact member-cert@finops.org for the RFI. The current badge has historically been "FinOps Certified FOCUS v1.2 Conformant"; confirm the version before finalizing.

Open-source tooling to use along the way: the FOCUS Validator (checks data against the Requirements Model), the FOCUS Converter (provider-native to FOCUS), and the FOCUS Requirements Model (machine-readable MUST/SHOULD/MAY rules).

### 2.3 Phased roadmap

Phase 0: Scope and design the feed. Decide grain (daily per-resource per-SKU charge records), confirm the target version, and define how committed/dedicated-term rates reconcile to ContractedCost and EffectiveCost. Inventory the source signals (consumption/metering logs, the INR price catalog, account and resource metadata from the console/API, and any invoice records). No FOCUS output yet, but this is where the substantive work is scoped.

Phase 1: Produce and expose the per-charge-record cost feed. This is the value-unlock phase. Build the pipeline that joins consumption events to the INR unit prices and emits ListCost, BilledCost, EffectiveCost, and ContractedCost per record, framed by ChargePeriodStart/End and BillingPeriodStart/End, classified by ChargeCategory and ChargeDescription, with ChargeClass for corrections. Populate the identity, quantity, price, and currency columns from existing platform data in the same pass, and expose the result as an export or billing API rather than an in-console view only.

Phase 2: Shape to FOCUS. Apply FOCUS column IDs, valid enums (ChargeCategory, ServiceCategory, ChargeFrequency), ISO 8601 timestamps (inclusive start, exclusive end), ISO 4217 currency codes, and `x_` prefixes for any Yotta-specific extensions. Run the feed through the FOCUS Validator.

Phase 3: Round out Conditional and Recommended columns. Populate the commitment-discount family for term-committed customers (CommitmentDiscount Category/Id/Name/Type/Status/Quantity/Unit, ContractedUnitPrice), the SKU family (SkuId/Meter/PriceDetails/PriceId), PricingCategory, RegionId/Name, ResourceId/Name/Type, ServiceSubcategory, ChargeFrequency, and InvoiceId once invoices carry stable identifiers. If a project or cost-center construct is added to the platform, populate the sub-account family and key-value Tags to unlock allocation.

Phase 4: Mature and certify. Adopt v1.4 Invoice Detail and billing-period datasets for reconciliation, drop deprecated columns, validate public sample data, and pursue certification through the Foundation.

### 2.4 FOCUS Use Cases unlocked

Unlocked once Phase 1 produces and exposes the feed (resource- and day-level cost):
- Resource-level cost reporting and chargeback/showback across Bare Metal, clusters, VMs, endpoints, and storage.
- Anomaly detection and spend-trend analysis at daily grain.
- GPU-hour, GPU-minute, and token unit-economics analysis (cost per GPU-hour, cost per million tokens).

Unlocked at Phase 3 (commitment, SKU, and allocation detail):
- Cost allocation by project and by tag, once a sub-account/project construct and key-value tags exist. Today this is out of reach because no such billing dimension is documented.
- Commitment and reserved-capacity utilization for term-committed customers.
- Effective-rate and discount-coverage reporting.

Unlocked at Phase 4 (invoice and billing-period datasets):
- Invoice reconciliation and actuals-based budgeting against the single-portal billing records.

Out of scope for now: capacity-reservation use cases (reservations are not surfaced as billing data) and availability-zone-level analysis (India data centers and regions, no zones documented).

---

## Part 3: Immediate next steps

1. Decide the dataset grain and target version (daily per-resource per-SKU charge records, build to v1.4).
2. Inventory the source signals: consumption/metering events, the INR price catalog, account and resource metadata from the console/API, and any invoice records from the single billing portal.
3. Define the cost model: how list prices, committed/dedicated-term rates, and the spend-bracket managed-services fee reconcile to ListCost, ContractedCost, BilledCost, and EffectiveCost per record.
4. Prototype a small FOCUS-shaped sample (one account, a few days, Bare Metal plus a serverless or endpoint service) and run it through the FOCUS Validator.
5. Contact member-cert@finops.org for the certification RFI and confirm the current badge version.

---

## Confidence summary

- Product catalog, metering grains, and INR pricing: high confidence, taken directly from the public Shakti Cloud rate card and product pages.
- Pay-as-you-go plus term-based commitment structure (monthly through multi-year toggles) and the spend-bracket managed-services fee: high confidence, from the public pricing page.
- Existence of a customer account and console with usage and billing visibility: high confidence, from Yotta and Shakti Studio public messaging (One Yotta account, Shakti Cloud console, Shakti Studio observability).
- Absence of a line-item cost/usage export, a billing/usage API returning costed records, cost-allocation tags, and a sub-account/project billing construct: medium confidence and provisional. None of these are documented publicly as of 2026-07-01, but Yotta's customer portal, One Yotta account, and any enterprise contracts were not available for review; an undocumented or portal-only export, tagging, or account hierarchy could exist. Confirm directly with Yotta before treating the N/A classifications (sub-account family, Tags) and the cost/export gaps as final.
- Committed-term discount mechanics: medium confidence, inferred from the term toggles; exact discount percentages are not published.
- FOCUS feature levels: high confidence. The bundled v1.2 table (57 columns) was confirmed current against the live FOCUS column library on 2026-07-01; no refresh was required. A live Validator run on real sample data remains the objective arbiter once a feed exists.
- Overall: this assessment reflects the data source as publicly documented, not a formal certification result. Given the reliance on public marketing and rate-card material rather than portal or API documentation, the analysis should be treated as provisional pending confirmation with Yotta.

---

## Sources

- Yotta Shakti Cloud pricing (https://shakticloud.ai/pricing/)
- Yotta Shakti Studio: AI inference platform, serverless GPUs, observability (https://shakticloud.ai/shakti-studio/)
- Shakti Cloud Infrastructure as a Service: Bare Metal GPU, API and management tools, monitoring (https://yotta.com/shakticloud/Infrastructure-as-a-Service.html)
- Yotta corporate: India sovereign cloud, Navi Mumbai and Greater Noida, Yntraa MeitY empanelment (https://yotta.com/)
- One Yotta account portal (https://account.yotta.com/) and Shakti Cloud console (https://portal.shakticloud.ai/)
- FOCUS Specification and column library (https://focus.finops.org/focus-specification/)
- FOCUS column feature levels verified via the FOCUS column library, 2026-07-01

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
