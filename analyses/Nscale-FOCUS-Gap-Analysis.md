# Nscale and FOCUS: Conformance Gap and Adoption Roadmap

*Analysis run: June 30, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

Prepared: 2026-06-30
Provider and product in scope: Nscale (AI/GPU neocloud), covering GPU Nodes (bare-metal H100/H200/GB200), Serverless Inference (per-token), Fine-Tuning, Storage, and Networking.
Source analyzed: Nscale public documentation (docs.nscale.com), the Compute, Storage, and Serverless Inference OpenAPI specifications, and the Usage and Billing console documentation.
FOCUS baseline: v1.2 (current certification baseline). Build target: v1.4 (latest ratified, 2026-06-04).
Feature levels verified against the FOCUS Specification via the FOCUS MCP column library on 2026-06-30; bundled v1.2 table confirmed current (no refresh required).

---

## Executive summary

Nscale has strong account and resource primitives but does not yet publish a machine-readable cost and usage dataset. The platform exposes a clean Organization to Project hierarchy, resource IDs and names, FOCUS-shaped key-value tags, regions, and a credit-based billing ledger, yet cost itself is surfaced only as a daily-updated spend visualization in the Usage and Billing console. There is no documented line-item cost export, no billing API, and no FOCUS-style dataset.

That single absence is the headline: the building blocks for allocation are present, but the dataset that FOCUS normalizes does not exist in exportable form today. A conformance effort here is mostly a data-production project (emit a per-charge-record usage and cost feed) rather than a re-shaping project.

Stat strip:
- 57 FOCUS columns assessed (v1.2 baseline)
- 0 columns present in a conformant exportable dataset (the primitives exist in platform APIs but are not assembled into a billing record)
- 21 of 21 Mandatory columns are gaps; the substantive core is the four cost columns plus billing-period and charge-period framing
- 0 deviations to fix (no FOCUS-shaped dataset exists yet to deviate)

Recommendation: treat this as a Phase 1 dataset-production effort. Nscale already holds the inputs (consumption events, prices in decimal USD, resource and project identity, tags, regions, credit ledger). The work is to assemble them into a daily, per-resource charge record carrying List, Billed, Effective, and Contracted cost, then shape that record to FOCUS column IDs.

Readiness (data source reviewed, not a formal certification result):
- Cost: Gap
- Granularity: Partial
- Allocation: Partial
- Coverage: Gap
- FOCUS shape: Partial
- Overall band: Not yet aligned (per public docs)

---

## Part 1: The conformance gap

### 1.1 The data source

Nscale is a vertically integrated AI/GPU neocloud. Its billing-relevant surface, as documented publicly, has these characteristics:

Account hierarchy: a two-level Organization to Project model. Resources are project-scoped and carry both `organizationId` and `projectId` in API metadata. This maps directly to FOCUS billing-account and sub-account semantics.

Billing model: credit-based and prepaid. Customers purchase credits through a Stripe flow ($5 minimum, $10,000 maximum per transaction); credits are deducted as resources are consumed and expire three years after purchase. Receipts are emailed per purchase, and transaction history sits in the Usage and Billing console under the Credit tab. Billing details (name, address, contact) are stored per account.

Usage visibility: the Usage and Billing console provides a visual breakdown of inference usage and credit spend over a selected period, updated daily, with daily and weekly toggles. This is a dashboard view, not a downloadable line-item dataset. No cost or usage export, CUR-equivalent file, or billing API is documented.

Pricing: two models. GPU Nodes are bare-metal hourly compute on NVIDIA H100, H200, and GB200. Serverless Inference is priced per million tokens, with `input_price_per_million` and `output_price_per_million` exposed as decimal USD strings and a `price_type` enum of `PER_TOKEN` or `PER_PIXEL`. Reserved and multi-year private-cloud deployments exist alongside on-demand, implying contracted rates below list for committed customers.

Resource identity and tags: resources expose a unique `id`, a `name`, `creationTime`, `createdBy`, and a `tags` array of name-value objects. Tags are already in key-value form, which is the FOCUS-required shape. Resources also carry a `regionId`, and a Regions API enumerates available regions. No availability zones are documented.

Currency: USD throughout (Stripe billing, prices quoted in decimal USD).

Key limitation: cost data is not retrievable as structured per-charge records. The console shows aggregate spend; the APIs expose resource metadata and unit prices, but nothing ties a consumption event to a costed line item in an exportable feed. Everything downstream of FOCUS conformance depends on first producing that feed.

### 1.2 How conformance is judged

FOCUS defines a billing dataset as a set of columns, each carrying a feature level: Mandatory (must be present and populated where applicable), Conditional (required when the provider's model triggers the condition), Recommended (encouraged), or Optional. Conformance is judged column by column against the Requirements Model, which encodes the MUST/SHOULD/MAY rules and allowed values. A dataset is conformant when every Mandatory column is present and correctly populated, every applicable Conditional column is populated, formats and enums are valid, and provider-specific extensions are prefixed `x_`.

Feature levels for this analysis were taken from the verified v1.2 reference and confirmed against the live FOCUS column library on 2026-06-30. The v1.2 baseline carries 21 Mandatory, 32 Conditional, and 4 Recommended columns.

### 1.3 Column-by-column status

Legend: Present / Present, deviation to fix / Missing: Mandatory / Missing: Recommended / Missing: Conditional / N/A: null valid.

Because Nscale publishes no FOCUS-style dataset, no column is "Present" in a conformant export. The status below records, for each column, whether the underlying data exists in Nscale's platform (so the gap is assembly) or does not exist at all (so the gap is substantive). The level column is the verified v1.2 feature level.

| FOCUS Column | Level | In the source? | Status |
|---|---|---|---|
| AvailabilityZone | R | No (regions only, no zones) | N/A: null valid |
| BilledCost | M | No (console spend only, not per-record) | Missing: Mandatory |
| BillingAccountId | M | Yes (organizationId, not in a billing record) | Missing: Mandatory |
| BillingAccountName | M | Yes (organization name) | Missing: Mandatory |
| BillingAccountType | C | Partial (organization construct) | Missing: Conditional |
| BillingCurrency | M | Yes (USD) | Missing: Mandatory |
| BillingPeriodEnd | M | No (no billing-period dataset) | Missing: Mandatory |
| BillingPeriodStart | M | No (no billing-period dataset) | Missing: Mandatory |
| CapacityReservationId | C | No (reservations not exposed in data) | N/A: null valid |
| CapacityReservationStatus | C | No | N/A: null valid |
| ChargeCategory | M | No (not classified in any feed) | Missing: Mandatory |
| ChargeClass | M | No | Missing: Mandatory |
| ChargeDescription | M | No | Missing: Mandatory |
| ChargeFrequency | R | No | Missing: Recommended |
| ChargePeriodEnd | M | No (no line-item time framing) | Missing: Mandatory |
| ChargePeriodStart | M | No | Missing: Mandatory |
| CommitmentDiscountCategory | C | Partial (reserved/private cloud exist) | Missing: Conditional |
| CommitmentDiscountId | C | Partial | Missing: Conditional |
| CommitmentDiscountName | C | Partial | Missing: Conditional |
| CommitmentDiscountQuantity | C | Partial | Missing: Conditional |
| CommitmentDiscountStatus | C | Partial | Missing: Conditional |
| CommitmentDiscountType | C | Partial | Missing: Conditional |
| CommitmentDiscountUnit | C | Partial | Missing: Conditional |
| ConsumedQuantity | C | Yes (GPU-hours, tokens consumed) | Missing: Conditional |
| ConsumedUnit | C | Yes (hours, tokens, pixels) | Missing: Conditional |
| ContractedCost | M | No (contract rates not in data) | Missing: Mandatory |
| ContractedUnitPrice | C | Partial (reserved rates exist contract-side) | Missing: Conditional |
| EffectiveCost | M | No (only aggregate credit spend) | Missing: Mandatory |
| InvoiceId | R | Partial (Stripe receipts, no invoice ID in data) | Missing: Recommended |
| InvoiceIssuerName | M | Yes (Nscale) | Missing: Mandatory |
| ListCost | M | No (list prices exist, not costed per record) | Missing: Mandatory |
| ListUnitPrice | C | Yes (per-token decimal USD, hourly node rates) | Missing: Conditional |
| PricingCategory | C | Partial (on-demand vs reserved) | Missing: Conditional |
| PricingCurrency | C | Yes (USD) | Missing: Conditional |
| PricingCurrencyContractedUnitPrice | C | Partial | Missing: Conditional |
| PricingCurrencyEffectiveCost | C | No | Missing: Conditional |
| PricingCurrencyListUnitPrice | C | Yes (decimal USD prices) | Missing: Conditional |
| PricingQuantity | M | Yes (derivable from consumption for flat-rate SKUs) | Missing: Mandatory |
| PricingUnit | M | Yes (GPU-hour, 1M tokens) | Missing: Mandatory |
| ProviderName | M (removed v1.4) | Yes (Nscale) | Missing: Mandatory |
| PublisherName | M (removed v1.4) | Yes (Nscale) | Missing: Mandatory |
| RegionId | C | Yes (regionId on resources) | Missing: Conditional |
| RegionName | C | Yes (Regions API) | Missing: Conditional |
| ResourceId | C | Yes (resource id) | Missing: Conditional |
| ResourceName | C | Yes (resource name) | Missing: Conditional |
| ResourceType | C | Yes (instance flavor, model, storage class) | Missing: Conditional |
| ServiceCategory | M | Yes (derivable: AI and Machine Learning, Compute, Storage) | Missing: Mandatory |
| ServiceName | M | Yes (GPU Nodes, Serverless Inference, etc.) | Missing: Mandatory |
| ServiceSubcategory | R | Yes (derivable) | Missing: Recommended |
| SkuId | C | Partial (model id, flavor id) | Missing: Conditional |
| SkuMeter | C | Partial (token type, GPU-hour) | Missing: Conditional |
| SkuPriceDetails | C | Partial (price_type, per-million pricing) | Missing: Conditional |
| SkuPriceId | C | No (no distinct price-record id) | Missing: Conditional |
| SubAccountId | C | Yes (projectId) | Missing: Conditional |
| SubAccountName | C | Yes (project name) | Missing: Conditional |
| SubAccountType | C | Partial (project construct) | Missing: Conditional |
| Tags | C | Yes (key-value tags, FOCUS shape) | Missing: Conditional |

Tally: of 57 v1.2 columns, 0 are present in a conformant export and 21 of 21 Mandatory columns are gaps. Three columns are correctly N/A (AvailabilityZone, both capacity-reservation columns) because Nscale exposes regions but not zones and does not surface reservations as billing data. The remaining gaps split into data that exists in the platform and needs assembling versus data that does not exist anywhere yet.

### 1.4 What's solved, and what remains

The honest framing: nothing is "solved" in the sense of a conformant column today, because there is no dataset. But the gaps are not equally hard. Separating them is what makes the roadmap tractable.

Substantive gaps (data does not exist in usable per-record form):
- BilledCost, EffectiveCost, ListCost, ContractedCost. This is the list-cost trap in its purest form: there is no list-cost dataset to copy from. Credit spend is shown only as a console aggregate, and discounts (reserved rates, multi-year private cloud) are negotiated contract-side and applied to the credit ledger, not attached to consumption events. Producing the four cost columns requires building a per-charge-record costing pipeline that joins consumption events to unit prices and reconciles contracted rates and credit drawdown. Treat all four as substantive, not trivial.
- BillingPeriodStart / BillingPeriodEnd and ChargePeriodStart / ChargePeriodEnd. No line-item time framing exists; these require the same new per-record feed.
- ChargeCategory, ChargeClass, ChargeDescription. These are classification fields that only come into being once a charge record exists.

Trivial-once-the-feed-exists gaps (data is already in the platform):
- Identity and structure: BillingAccountId/Name (organization), SubAccountId/Name (project), ResourceId/Name/Type, RegionId/Name. All present in APIs; populating them is a join, not a data hunt.
- Quantities and units: ConsumedQuantity, ConsumedUnit, PricingUnit are available (GPU-hours, tokens, pixels). PricingQuantity is derivable from consumption for flat-rate SKUs such as hourly GPU nodes and per-token inference; flag any tiered or volume-blended pricing for proper computation against the rate basis rather than a straight copy.
- Prices: ListUnitPrice and the pricing-currency unit-price columns map from the decimal-USD prices already exposed (per-million-token rates, hourly node rates).
- Provider framing: ProviderName, PublisherName, InvoiceIssuerName are all Nscale (Publisher and Provider are removed in v1.4, so a v1.4 build drops them).
- Currency: BillingCurrency and PricingCurrency are USD.
- Tags: already key-value, ready to carry straight into the Tags column.

Net: the substantive core is the four cost columns plus the period/charge framing they live on. Everything else is plumbing that becomes straightforward the moment a per-charge-record feed exists.

### 1.5 Deviations to fix

There are no format or enum deviations to correct, because no FOCUS-shaped dataset exists yet. This is worth stating plainly: the work ahead is production, not remediation. Two things Nscale already does right and should preserve when the feed is built:
- Tags are stored as name-value pairs, the FOCUS-required key-value shape, not an array of bare strings.
- Prices and currency are clean decimal USD, so currency will be a valid ISO 4217 code and unit prices will not need reshaping.

When the feed is built, validate that ChargeCategory uses only Usage, Purchase, Tax, Credit, Adjustment (credit purchases and drawdown will exercise Purchase and Credit), that ServiceCategory uses valid members (AI and Machine Learning for inference and fine-tuning, Compute for GPU nodes, Storage for object/file storage, Networking for VPC), and that any custom columns are prefixed `x_`.

---

## Part 2: The path forward

### 2.1 Which FOCUS version to target

Build toward v1.4, the latest ratified version (2026-06-04). Because Nscale is producing a dataset from scratch, there is no legacy schema to migrate, so it should target the current shape directly and skip the deprecated `ProviderName` and `PublisherName` columns that v1.4 removes (use `ServiceProviderName` and the host/publisher split where relevant). For the certification milestone, the program baseline has historically been v1.2; design to v1.4 and certify against whatever version the program names, confirming the badge version against the program page before finalizing. The v1.4 Invoice Detail and billing-period datasets are a natural fit given Nscale's Stripe-backed invoicing and credit ledger.

### 2.2 What certification requires

FOCUS conformance for data generators runs through the FinOps Foundation. The deliverables are a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report (this analysis is its seed). Membership is required for certification, though contributing to the spec is open and free; contact member-cert@finops.org for the RFI. The current badge has historically been "FinOps Certified FOCUS v1.2 Conformant"; confirm the version before finalizing.

Open-source tooling to use along the way: the FOCUS Validator (checks data against the Requirements Model), the FOCUS Converter (provider-native to FOCUS), and the FOCUS Requirements Model (machine-readable MUST/SHOULD/MAY rules).

### 2.3 Phased roadmap

Phase 0: Scope and design the feed. Decide grain (daily per-resource per-SKU charge records), confirm the target version, and define how credit drawdown and contracted rates reconcile to EffectiveCost. Inventory the source events (consumption logs, price catalog, resource metadata, credit ledger). No FOCUS output yet, but this is where the substantive work is scoped.

Phase 1: Produce the per-charge-record cost feed. This is the value-unlock phase. Build the pipeline that joins consumption events to unit prices and emits ListCost, BilledCost, EffectiveCost, and ContractedCost per record, framed by ChargePeriodStart/End and BillingPeriodStart/End, classified by ChargeCategory and ChargeDescription, with ChargeClass for corrections. Populate the identity, quantity, price, and currency columns from existing platform data in the same pass.

Phase 2: Shape to FOCUS. Apply FOCUS column IDs, valid enums (ChargeCategory, ServiceCategory, ChargeFrequency), key-value Tags, ISO 8601 timestamps (inclusive start, exclusive end), and `x_` prefixes for any Nscale-specific extensions. Run the feed through the FOCUS Validator.

Phase 3: Round out Conditional and Recommended columns. Populate the commitment-discount family for reserved and private-cloud customers (CommitmentDiscount Category/Id/Name/Type/Status/Quantity/Unit, ContractedUnitPrice), the SKU family (SkuId/Meter/PriceDetails/PriceId), PricingCategory, ServiceSubcategory, ChargeFrequency, and InvoiceId once invoices carry stable identifiers.

Phase 4: Mature and certify. Adopt v1.4 Invoice Detail and billing-period datasets for reconciliation, drop deprecated columns, validate public sample data, and pursue certification through the Foundation.

### 2.4 FOCUS Use Cases unlocked

Unlocked once Phase 1 produces the feed (resource-, project-, and day-level cost):
- Cost allocation by project and by tag (the Organization to Project hierarchy and key-value tags make this immediate).
- Resource-level cost reporting and chargeback/showback across GPU nodes, inference, fine-tuning, and storage.
- Anomaly detection and spend-trend analysis at daily grain.
- GPU-hour and token unit-economics analysis (cost per GPU-hour, cost per million tokens).

Unlocked at Phase 3 (commitment and SKU detail):
- Commitment and reserved-capacity utilization for multi-year private-cloud and reserved customers.
- Effective-rate and discount-coverage reporting.

Unlocked at Phase 4 (invoice and billing-period datasets):
- Invoice reconciliation and actuals-based budgeting against the credit ledger.

Out of scope for now: capacity-reservation use cases (reservations are not surfaced as billing data) and availability-zone-level analysis (regions only, no zones).

---

## Part 3: Immediate next steps

1. Decide the dataset grain and target version (daily per-resource per-SKU charge records, build to v1.4).
2. Inventory the source signals: consumption/usage events, the decimal-USD price catalog, resource and project metadata, and the credit-ledger and Stripe invoice records.
3. Define the cost model: how list prices, contracted/reserved rates, and credit drawdown reconcile to ListCost, ContractedCost, BilledCost, and EffectiveCost per record.
4. Prototype a small FOCUS-shaped sample (one project, a few days, GPU nodes plus inference) and run it through the FOCUS Validator.
5. Contact member-cert@finops.org for the certification RFI and confirm the current badge version.

---

## Confidence summary

- Account hierarchy, tag shape, resource identity, regions, and the credit-based Stripe billing model: high confidence, taken directly from Nscale's documentation and published OpenAPI specifications.
- Unit prices in decimal USD and the per-token / per-pixel pricing model: high confidence, from the Serverless Inference OpenAPI schema.
- Absence of a line-item cost/usage export or billing API: medium-high confidence. No such export or API is documented publicly as of 2026-06-30; this is provisional in that an undocumented or partner-only export could exist. Confirm directly with Nscale.
- Existence and contract-side handling of reserved and multi-year discounts: medium confidence, inferred from public product positioning ("multi-year private cloud," "reserved deployments"); the exact discount mechanics are not documented.
- GPU node hourly list rates: not published on pages reviewed; specific rates were not load-bearing for this column-level analysis.
- FOCUS feature levels: high confidence. The bundled v1.2 table was confirmed current against the live FOCUS column library on 2026-06-30; no refresh was required. A live Validator run on real sample data remains the objective arbiter once a feed exists.
- Overall: this assessment reflects the data source as publicly documented, not a formal certification result.

---

## Sources

- Nscale documentation: Monitoring usage (https://docs.nscale.com/docs/manage/monitoring-usage)
- Nscale documentation: Credit and billing (https://docs.nscale.com/docs/manage/credit)
- Nscale documentation: Projects (https://docs.nscale.com/docs/manage/projects)
- Nscale documentation index (https://docs.nscale.com/llms.txt)
- Nscale Storage Service OpenAPI: List object storage endpoints, tag and project/organization/region parameters (https://docs.nscale.com/api-reference/object-storage/list-endpoints)
- Nscale Inference API OpenAPI: List model endpoints, decimal-USD pricing and price_type (https://docs.nscale.com/api-reference/models/list-endpoints)
- Nscale product: GPU Nodes (https://www.nscale.com/product/gpu-nodes) and Serverless Inference (https://www.nscale.com/product/serverless)
- FOCUS Specification and column library (https://focus.finops.org/focus-specification/)
- FOCUS column feature levels verified via the FOCUS MCP column library, 2026-06-30

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
