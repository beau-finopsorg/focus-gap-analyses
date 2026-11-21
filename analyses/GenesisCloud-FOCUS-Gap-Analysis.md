# Genesis Cloud and FOCUS: Compliance Gap and Adoption Roadmap

*Analysis run: June 30, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

Prepared: 2026-06-30
Provider and product in scope: Genesis Cloud GmbH, GPU cloud (Compute API, console billing dashboard)
Source analyzed: Genesis Cloud Developer documentation (Compute API instance schema and resource endpoints), pricing page, and billing-dashboard references at developers.genesiscloud.com and genesiscloud.com
FOCUS baseline: v1.2 (current certification baseline)
FOCUS build target: v1.4 (latest ratified, 2026-06-04)

## Executive summary

Genesis Cloud is a European GPU-first cloud built for AI training, inference, and HPC. It exposes a clean resource-management Compute API (instances, volumes, snapshots, regions, instance types, floating IPs) and a credit-based billing model with committed-use discounts. What it does not expose, on the public evidence available, is any structured cost-and-usage record: there is a human-facing billing dashboard, but no documented billing export, cost API, or line-item usage feed. The strongest finding is therefore about shape rather than gaps: Genesis Cloud already holds rich resource identity, region data, instance-type SKUs, and a real discount mechanic, but none of it is published as a FOCUS-style record. The analysis here treats the Compute API and billing model as the available proxy for what a future cost dataset would carry.

Against FOCUS v1.2 (57 columns), no column is currently emitted in a conformant cost record because no cost record exists. The practical gap is the absence of a billing dataset, not dozens of independent column failures. Once Genesis Cloud produces a per-resource, per-period charge record, the majority of Mandatory columns are straightforward to populate from data the platform already holds (resource identity, instance type, region, timestamps, the credit-denominated rate). The genuinely substantive work concentrates in the cost columns and the discount-aware effective cost, because committed-use discounts and credit pre-funding must be reconciled back to usage lines.

Four-stat summary:

- FOCUS columns (v1.2): 57
- Already present in a conformant cost record: 0
- Substantive Mandatory gaps: 2 of 21 (the cost family: EffectiveCost reconciled against committed-use discounts and credits; the surrounding cost columns derive once a record exists)
- Deviations to fix: 0 today (no cost record to deviate); resource identity and region data will need FOCUS shaping when the record is built

Readiness (data source reviewed, not a certification result): Cost Gap, Granularity Gap, Allocation Partial, Coverage Gap, FOCUS shape Gap. Overall band: Not yet aligned (per public docs).

Recommendation: The first deliverable is not column-level conformance, it is a billing dataset at all. Stand up a per-resource, per-day charge export (CSV or API) that joins the existing resource and instance-type metadata to the credit-denominated rate, then map that export to FOCUS v1.2 and design toward v1.4.

## Part 1: The conformance gap

### 1.1 The data source

Genesis Cloud publishes a REST Compute API at `api.genesiscloud.com/compute/v1`. The documented objects carry strong resource identity and configuration, for example the instance schema:

- `id`, `name`, `hostname`, `dns_name`: resource identifiers.
- `type`: the instance type, encoded as a descriptive SKU-like string (for example `vcpu-8_memory-48g_nvidia-rtx-3090-2`).
- `region`: a region identifier (for example `NORD-NO-KRS-1`).
- `placement_option`: physical placement within a zone (for example `AUTO`).
- `status`, `is_protected`, `disk_size`, `private_ip`, `public_ip`.
- `created_at`, `updated_at`: ISO 8601 timestamps.

Parallel endpoints describe volumes, snapshots, filesystems, floating IPs, images, instance types, and regions, so the platform holds the resource, location, and configuration data that allocation and resource-level reporting depend on.

Billing is handled separately. The documentation directs users to a billing dashboard (`console.genesiscloud.com/dashboard/billing`) to see billed resources, and states that charges begin when an instance is created and stop when destruction is requested. The pricing model is pay-as-you-go on pre-funded credits, with monthly invoicing available for enterprise customers and committed-use discounts (documented at 20 percent for three months, 30 percent for six months, and up to 50 percent for longer commitments on eligible RTX instances). Genesis Cloud GmbH is a German entity; invoicing is Euro-denominated.

Key limitations for FOCUS purposes:

- No cost or usage export: there is no documented billing API, cost-and-usage report, or downloadable line-item dataset. The billing dashboard is a viewing surface, not a data feed.
- No tags on resources: the instance schema carries no key-value tag field, so tag-based allocation is not available from the API today.
- No account hierarchy in the API: the public API is scoped by token and exposes no project, organization, or sub-account object, so multi-tenant attribution is not visible in the documented schema.
- Regions without zones: `region` is published; an availability-zone concept is not, though `placement_option` hints at sub-region placement.

The rest of this analysis treats the Compute API plus the billing model as a proxy for the cost record Genesis Cloud would need to produce. Because no cost dataset is published, every conformance judgment about emitted columns is provisional.

### 1.2 How conformance is judged

FOCUS assigns each column a feature level: Mandatory, Conditional, Recommended, or Optional. A conformant dataset must include and populate every Mandatory column, must populate Conditional columns when the provider's model triggers the condition, and is encouraged to populate Recommended columns. Conformance is judged column by column against the spec's Requirements Model, which encodes the MUST, SHOULD, and MAY rules. Feature levels in this report were verified against the FOCUS v1.2 specification using the FOCUS column reference, not asserted from memory.

### 1.3 Column-by-column status

Feature levels verified against the FOCUS Specification v1.2. Status reflects a conformant cost record: because Genesis Cloud publishes no cost record, no column is Present today. Columns are marked by whether the underlying data already exists in the Compute API or billing model (so the column is readily populated once a record is built) versus genuinely absent.

Legend: Present (emitted and aligned); Present, deviation to fix; Missing: Mandatory; Missing: Recommended; Missing: Conditional; N/A: null valid.

| FOCUS Column | Level | In the source? | Status |
|---|---|---|---|
| BilledCost | M | No cost record; credit-denominated rate exists | Missing: Mandatory |
| BillingAccountId | M | Account scoped by token, not exposed as a field | Missing: Mandatory |
| BillingAccountName | M | No | Missing: Mandatory |
| BillingCurrency | M | EUR implied by GmbH invoicing, not in a record | Missing: Mandatory |
| BillingPeriodEnd | M | No (monthly invoice cycle exists) | Missing: Mandatory |
| BillingPeriodStart | M | No (monthly invoice cycle exists) | Missing: Mandatory |
| ChargePeriodEnd | M | No (instance created_at/destroy time exist) | Missing: Mandatory |
| ChargePeriodStart | M | No (instance created_at exists) | Missing: Mandatory |
| ChargeCategory | M | No (Usage is the dominant case) | Missing: Mandatory |
| ChargeClass | M | No (nullable; for corrections only) | Missing: Mandatory |
| ChargeDescription | M | No (derivable from type and resource) | Missing: Mandatory |
| ContractedCost | M | No (committed-use rate exists in pricing) | Missing: Mandatory |
| EffectiveCost | M | No (discounts and credits applied off-line) | Missing: Mandatory |
| InvoiceIssuerName | M | "Genesis Cloud" (constant), not in a record | Missing: Mandatory |
| ListCost | M | No (on-demand rate exists in pricing) | Missing: Mandatory |
| PricingQuantity | M | No (compute hours derivable for flat-rate SKUs) | Missing: Mandatory |
| PricingUnit | M | No (hour/GiB derivable) | Missing: Mandatory |
| ProviderName | M | "Genesis Cloud" (constant), not in a record | Missing: Mandatory |
| PublisherName | M | "Genesis Cloud" (constant), not in a record | Missing: Mandatory |
| ServiceCategory | M | No (Compute for GPU/CPU instances) | Missing: Mandatory |
| ServiceName | M | No (derivable from resource type) | Missing: Mandatory |
| AvailabilityZone | R | placement_option hints at zone; not published as a record field | Missing: Recommended |
| ChargeFrequency | R | No (Usage-Based for on-demand) | Missing: Recommended |
| InvoiceId | R | No (invoices exist but no id in a record) | Missing: Recommended |
| ServiceSubcategory | R | No (GPU Cloud / Compute subcategory) | Missing: Recommended |
| BillingAccountType | C | No | Missing: Conditional |
| CapacityReservationId | C | Reserved cluster capacity exists; not exposed in API | Missing: Conditional |
| CapacityReservationStatus | C | As above | Missing: Conditional |
| CommitmentDiscountCategory | C | Committed-use discounts exist; not in a record | Missing: Conditional |
| CommitmentDiscountId | C | As above | Missing: Conditional |
| CommitmentDiscountName | C | As above | Missing: Conditional |
| CommitmentDiscountQuantity | C | As above | Missing: Conditional |
| CommitmentDiscountStatus | C | As above | Missing: Conditional |
| CommitmentDiscountType | C | As above | Missing: Conditional |
| CommitmentDiscountUnit | C | As above | Missing: Conditional |
| ConsumedQuantity | C | Compute time exists; not in a record | Missing: Conditional |
| ConsumedUnit | C | Hours/GiB derivable | Missing: Conditional |
| ContractedUnitPrice | C | Committed-use unit rate exists in pricing | Missing: Conditional |
| ListUnitPrice | C | On-demand unit rate exists in pricing | Missing: Conditional |
| PricingCategory | C | On-Demand / Committed distinction exists | Missing: Conditional |
| PricingCurrency | C | EUR; not in a record | Missing: Conditional |
| PricingCurrencyContractedUnitPrice | C | No | Missing: Conditional |
| PricingCurrencyEffectiveCost | C | No | Missing: Conditional |
| PricingCurrencyListUnitPrice | C | No | Missing: Conditional |
| RegionId | C | region identifier present (NORD-NO-KRS-1) | Missing: Conditional |
| RegionName | C | Derivable from region identifier | Missing: Conditional |
| ResourceId | C | instance id present | Missing: Conditional |
| ResourceName | C | instance name present | Missing: Conditional |
| ResourceType | C | instance type present | Missing: Conditional |
| SkuId | C | type string is a SKU-like identifier | Missing: Conditional |
| SkuMeter | C | No | Missing: Conditional |
| SkuPriceDetails | C | No | Missing: Conditional |
| SkuPriceId | C | No | Missing: Conditional |
| SubAccountId | C | No project/sub-account object in the API | N/A: null valid |
| SubAccountName | C | As above | N/A: null valid |
| SubAccountType | C | As above | N/A: null valid |
| Tags | C | No tag field on resources | Missing: Conditional |

### 1.4 What's solved, and what remains

Because there is no published cost dataset, nothing is "solved" in the sense of an emitted, conformant column. The right way to read the table is by how far the underlying data already exists.

Already held by the platform, so readily populated once a charge record exists (trivial plumbing, not data creation):

- Resource identity: `ResourceId`, `ResourceName`, `ResourceType` from the instance schema.
- Location: `RegionId` and `RegionName` from the `region` identifier.
- SKU identity: `SkuId` from the `type` string.
- Constants: `ProviderName`, `PublisherName`, `InvoiceIssuerName` ("Genesis Cloud"); `BillingCurrency` and `PricingCurrency` (EUR); `ServiceCategory` (Compute); `ChargeCategory` (Usage for the dominant case); `ChargeFrequency` (Usage-Based).
- Timestamps: `ChargePeriodStart` and `ChargePeriodEnd` from instance create and destroy times; `BillingPeriodStart` and `BillingPeriodEnd` from the monthly invoice cycle.
- Pricing: `PricingQuantity` and `PricingUnit` derivable as compute hours and hour/GiB for flat-rate instance SKUs (RTX instances are flat-rate on-demand, so the consumed quantity maps to pricing quantity; verify any tiered storage rates separately). `ListUnitPrice` and `ContractedUnitPrice` from the published on-demand and committed-use rates.

Substantive gaps (real data work, not plumbing):

- The cost record itself: there is no per-resource, per-period charge line anywhere in the public surface. This is the single blocking gap. Everything above is moot until a record is generated.
- `EffectiveCost` (and the discount-aware view): Genesis Cloud applies committed-use discounts and runs on pre-funded credits, with monthly invoicing for enterprise. Because discounts and credit drawdown are resolved at invoice time rather than on each usage line, computing `EffectiveCost` requires reconciling those adjustments back to the usage lines. This is the classic list-cost trap: `ListCost`, `BilledCost`, `ContractedCost`, and `EffectiveCost` are not a single trivial copy of one rate. They diverge whenever a committed-use discount or credit applies, so the cost family is substantive, not trivial.

So of 21 Mandatory columns, 2 are substantive (the reconciled cost view: `EffectiveCost`, and `BilledCost`/`ContractedCost` where discounts and credits diverge from list), and the remaining 19 are derivable plumbing once a record exists. The overriding gap is that the record does not exist at all.

### 1.5 Deviations to fix

No format or enum deviations can be flagged today, because there is no emitted cost record to inspect. The items below are the shaping work that will be needed when the record is built, not deviations in existing output:

- `RegionId` shape: the `NORD-NO-KRS-1` identifier is provider-native and will need a stable mapping to `RegionId` plus a human `RegionName`.
- `SkuId` from `type`: the `type` string is descriptive rather than a stable price-bearing SKU id; a durable `SkuId` and `SkuPriceId` should be minted so prices can be joined.
- Tags: when a tagging feature is added, it must be emitted as FOCUS key-value pairs, not an array of bare strings.
- Currency: emit ISO 4217 (`EUR`) in `BillingCurrency` and `PricingCurrency`.
- Timestamps: keep ISO 8601, inclusive-start and exclusive-end, which the Compute API already uses for `created_at`/`updated_at`.

## Part 2: The path forward

### 2.1 Which FOCUS version to target

Baseline the build against v1.2, the current certification baseline, so the work maps cleanly to the conformance program. Design the schema toward v1.4 (latest, ratified 2026-06-04): `ProviderName` and `PublisherName` are removed in v1.4, so treat them as transitional and rely on `InvoiceIssuerName` for issuer identity. v1.4 also adds Invoice Detail and billing-period datasets that suit a credit-and-invoice model like Genesis Cloud's. Validator support today reaches v1.3; v1.4 Validator support is expected later in 2026.

### 2.2 What certification requires

FOCUS conformance for data generators runs through the FinOps Foundation. The current badge is "FinOps Certified FOCUS v1.2 Conformant" (confirm the current badge version on the program page before finalizing). The deliverables are a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report (this analysis is its seed). Membership is required for certification, though contributing to the spec is open and free; contact `member-cert@finops.org` for the RFI. Open-source tooling: the FOCUS Validator (checks data against the Requirements Model), the FOCUS Converter (provider-native to FOCUS), and the FOCUS Requirements Model (machine-readable MUST/SHOULD/MAY rules).

### 2.3 Phased roadmap

Phase 0: Establish a cost record and validate scope. The precondition for everything else. Decide the grain (per-resource, per-day is the FOCUS-friendly target), confirm the Euro billing currency, and confirm there is no sub-account hierarchy to model. There is no dataset to run through the Validator yet, so Phase 0 is design, not validation.

Phase 1: Emit the charge record and close Mandatory columns. Generate a per-resource, per-day usage line joining instance, instance-type, and region metadata to the credit-denominated rate. Populate the 19 derivable Mandatory columns directly. Do the substantive cost work here: compute `ListCost` from on-demand rates, `ContractedCost` and `EffectiveCost` by reconciling committed-use discounts and credit drawdown back to the usage lines, and `BilledCost` to match invoiced amounts. This phase unlocks most usable conformance.

Phase 2: Shape and validate. Mint stable `SkuId`/`SkuPriceId`, map `RegionId`/`RegionName`, set valid enums (`ChargeCategory`, `ChargeFrequency`, `ServiceCategory`), and run the output through the FOCUS Validator.

Phase 3: Round out applicable Conditional and Recommended columns. Add `ConsumedQuantity`/`ConsumedUnit`, `ListUnitPrice`/`ContractedUnitPrice`, the commitment-discount family (so committed-use savings are visible per line), and capacity-reservation columns for reserved clusters. Add a tagging feature and emit `Tags` as key-value pairs. Populate the Recommended columns (`AvailabilityZone` from placement, `ServiceSubcategory`, `InvoiceId`).

Phase 4: Mature to v1.4 and certify. Drop `ProviderName`/`PublisherName`, adopt the Invoice Detail and billing-period datasets, re-validate against the v1.4 Requirements Model when Validator support lands, and pursue certification.

### 2.4 FOCUS Use Cases unlocked

Grouped by the phase that first enables them.

Unlocked by Phase 1 (a per-resource, per-day cost record with identity and region):

- Analyze cost per compute service for a subaccount (read here as "by resource," since there is no sub-account).
- Analyze costs of components of a resource.
- Analyze service costs by region.
- Report costs by service category.
- Identify anomalous daily spending (by resource and region; sub-account dimension is not applicable).
- Compare resource usage month over month.

Unlocked by Phase 3 (commitment-discount and consumption columns):

- Determine Effective Savings Rate, and by service: needs the reconciled `EffectiveCost` and `ListCost` from Phase 1 plus commitment context.
- Report commitment discount purchases.
- Identify unused commitments.
- Calculate unit economics.

Out of scope for the current model:

- Sub-account allocation, chargeback, and showback: no project or sub-account object exists in the API, so `SubAccount*` columns are null and these use cases do not apply until tenancy is modeled.
- Capacity-reservation analytics: applicable only once reserved-cluster capacity is exposed as data.
- Multi-currency allocation: a single Euro billing currency makes this moot unless billing currency varies.

## Part 3: Immediate next steps

1. Confirm scope: Euro billing currency, no sub-account hierarchy, the committed-use discount and credit mechanics, and that no cost export exists today.
2. Decide the cost-record grain and source it: a per-resource, per-day charge line joining Compute API resource and instance-type metadata to the credit-denominated rate.
3. Map the 19 derivable Mandatory columns from data the platform already holds.
4. Solve the cost family: define how committed-use discounts and credit drawdown reconcile to usage lines to produce `ContractedCost`, `EffectiveCost`, and `BilledCost` distinct from `ListCost`.
5. Run a sample through the FOCUS Validator and seed the Conformance Gap Report from this analysis.

## Confidence summary

- FOCUS v1.2 feature levels and the 57-column set: high confidence. Verified against the FOCUS column reference and spot-checked live via the FOCUS MCP on 2026-06-30; the bundled table was current (stamp 2026-06-23) and required no refresh. v1.4 removal of `ProviderName`/`PublisherName` confirmed against the live column list.
- Genesis Cloud has no published cost or usage export: medium-high confidence. Based on the public Developer docs and pricing pages, which document a Compute API and a billing dashboard but no billing/cost API. A private enterprise billing export could exist behind contract; this should be confirmed with Genesis Cloud.
- Resource, region, instance-type, and timestamp data exist in the Compute API: high confidence, taken directly from the documented instance schema.
- Credit-based billing, committed-use discounts (20 to 50 percent), and Euro invoicing: medium-high confidence from the pricing page and billing documentation; exact discount eligibility and credit-to-invoice reconciliation mechanics should be confirmed.
- No tags and no sub-account hierarchy in the public API: medium confidence, based on absence from the documented schema; confirm against the full console and any private API surfaces.
- Overall data quality for this analysis: provisional. The judgments rest on resource-management API docs and pricing pages used as a proxy, not on an actual cost-and-usage dataset.

## Sources

- Genesis Cloud Developer documentation, Compute API and instance schema: https://developers.genesiscloud.com/compute-api/instances
- Genesis Cloud Developer documentation, introduction: https://developers.genesiscloud.com/
- Genesis Cloud pricing: https://www.genesiscloud.com/pricing
- Genesis Cloud billing dashboard reference: https://console.genesiscloud.com/dashboard/billing
- FOCUS Specification v1.2: https://focus.finops.org/focus-specification/v1-2/
- FOCUS column library: https://focus.finops.org/ (verified via FOCUS MCP, 2026-06-30)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
