# Prime Intellect and FOCUS: Compliance Gap and Adoption Roadmap

*Analysis run: July 1, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

Prepared: 2026-07-01
Source analyzed: Prime Intellect public API reference at docs.primeintellect.ai and api.primeintellect.ai/openapi.json (Pods, Pods History, Billing wallet and run-usage endpoints, Availability), the FAQ, and the Inference and Hosted Training pricing pages.
FOCUS baseline: v1.2 (current certification baseline). Build target: v1.4 (latest, ratified 2026-06-04).

## Executive summary

Prime Intellect is a GPU compute aggregator and marketplace: a single API, console, and prepaid wallet spanning roughly twenty underlying GPU clouds (RunPod, Lambda, Hyperstack, Crusoe, Nebius, Vultr, DataCrunch, Scaleway, and others) alongside its own Prime Compute capacity. Users rent on-demand, spot, reserved, and multi-node GPU pods, plus network disks, sandboxes, hosted training and RFT runs, and a per-token inference API. Every charge type deducts from one USD credit balance.

The aggregator model is the defining feature for FOCUS mapping. The underlying `providerType` (for example `lambdalabs` or `crusoecloud`) is the true Provider and Publisher, while Prime Intellect is the Invoice Issuer, and the team versus personal wallet distinction is the closest analog to a sub-account.

Prime Intellect is further along than a typical operational API because it exposes a real billing surface. The `/billing/wallet` endpoint reads the same `Billing` table the dashboard's Billing History uses, returning per-resource rows with a net USD amount, a currency, a resource type, a resource ID, and billed timestamps. The pods-history object adds `totalBilledPrice` and an average `priceHr` per resource. That gives a genuine charge-level cost record, which most consumption APIs lack. What is missing is FOCUS shaping: FOCUS column IDs, a per-charge time-sliced record rather than a running total, the split between list and effective cost, key-value tags, and region naming.

Verdict: a strong billing substrate with a thin published FOCUS surface. The net cost figure exists, so the cost family is closer than for a list-price-only feed, but reconciling spot discounts and promotional credits into a clean List, Billed, Effective, and Contracted set remains real work.

Stat strip: 57 FOCUS columns (v1.2). Roughly 16 present or trivially derivable from published fields. Of 17 Mandatory columns absent from the current schema, 3 are substantive and all sit in the cost family (BilledCost, EffectiveCost, ContractedCost); the other 14 are derivable or nullable plumbing. Several deviations to fix (no tags, region shaping, rate units, provider slugs).

RAG readiness: Cost Partial, Granularity Partial, Allocation Partial, Coverage Partial, FOCUS shape Gap. Overall band: Not yet aligned (per public docs).

Recommendation: Treat the `Billing` table and the pods-history object as two halves of one FOCUS dataset. Build a charge-level feed keyed on resource and charge period, map `amount_usd` to BilledCost and EffectiveCost while deriving ListCost from `priceHr` and consumed hours, and set Provider and Publisher to the underlying `providerType` with Prime Intellect as Invoice Issuer.

## Part 1: The conformance gap

### 1.1 The data source

Prime Intellect exposes a REST API (base `https://api.primeintellect.ai`), a CLI, and a console. The objects relevant to cost and usage:

- Billing wallet (`GET /api/v1/billing/wallet`): returns `wallet_id`, optional `team_id`, `balance_usd`, `currency`, `total_billings`, and an array of `recent_billings`. Each `BillingEntry` carries `id`, `created_at`, `updated_at`, `last_billed_at`, `amount_usd`, `currency`, `resource_type` (one of compute, training, inference, disks, sandboxes, images), and `resource_id` (a foreign key back to the pod, run, or disk). The docs state this is the same source-of-truth `Billing` table the dashboard's Billing History reads.
- Pods history (`GET /api/v1/pods/history`): returns `HistoryObj` rows with `id`, `name`, `providerType`, `provisionedBy`, `type` (ResourceType: Instance, Cluster, Disk, Sandbox, Inference, Image, Training), `createdAt`, `terminatedAt`, `gpuName`, `gpuCount`, `socket`, `priceHr` (average hourly rate), `userId`, `teamId`, and `totalBilledPrice` (total amount billed for the resource).
- Pod object (`APIPodConfig`): `id` (UUID), `userId`, `teamId`, `walletId`, `name`, `providerType`, `status`, `gpuName`, `gpuCount`, `socket`, `priceHr`, `stoppedPriceHr`, `provisioningPriceHr`, `isSpot`, `clusterId`, `dataCenterId`, `country`, `security` (secure_cloud or community_cloud), `createdAt`, `updatedAt`, `terminatedAt`, and a `resources` block (memory, disk, vcpus).
- Run usage (`GET /api/v1/billing/runs/{run_id}/usage`): for training and RFT runs, returns token counts and cost split into training and inference breakdowns, plus snapshotted per-million-token pricing and a `total_cost_usd`.
- Availability and GPU summary endpoints publish live pricing by GPU type and instance count.

Billing and invoicing (from the FAQ and pricing pages):

- Prepaid credit model. Each pod has an hourly cost depending on provider and GPU type, and credits are deducted every minute while active. If credits run out, pods are deleted. Auto-top-up is available.
- Spot instances offer discounts of up to ninety percent versus on-demand, reflected in the hourly rate. Reserved and long-term capacity is arranged through prepay (`prepaidForHr`) or a Custom GPU Quote.
- Inference is billed per input and output token at per-million-token rates; training and RFT runs are billed per token with snapshotted pricing.
- Currency is USD. Other currencies and alternative payment methods are handled through support, not the API.
- Promotional credits exist (promo codes at signup or top-up). Refunds and credits for provider-side failures are issued through support.
- Teams support a dedicated billing email for consolidated invoicing; team credits are addressed with the `X-Prime-Team-ID` header.

Key limitations for FOCUS: the billing rows carry a net `amount_usd` but not a separate list price, so the gap between list and effective (spot savings, promo credits) is not itemized per row. `totalBilledPrice` is a running total per resource, not a time-sliced per-charge record. There are no tags on pods or billing rows. Region is expressed as `dataCenterId` and `country`, not a named region pair. Rates such as the multi-node example are documented in dollars, while some pod price fields are plain numbers whose unit and precision should be pinned down. There is no per-line invoice identifier in the API.

### 1.2 How conformance is judged

FOCUS assigns each column a feature level: Mandatory (must be present and populated where applicable), Conditional (required when the provider's model triggers the condition), Recommended, or Optional. Conformance is evaluated column by column against the FOCUS Requirements Model. Feature levels in this report were verified against the FOCUS v1.2 specification Content Constraints tables (bundled cache stamp 2026-06-23, spot-checked live against the FOCUS column library on 2026-07-01: ChargeClass present in v1.2 at section 3.12, no ratified version newer than v1.4).

### 1.3 Column-by-column status (FOCUS v1.2, all 57 columns)

Legend: Present / Present, deviation to fix / Missing: Mandatory / Missing: Recommended / Missing: Conditional / N/A: null valid.

| FOCUS Column | Level | In the source? | Status |
|---|---|---|---|
| AvailabilityZone | R | No (data center and country only) | Missing: Recommended |
| BilledCost | M | Partial (amount_usd, running total) | Missing: Mandatory |
| BillingAccountId | M | Yes (wallet_id) | Present, deviation to fix |
| BillingAccountName | M | Implicit (account or team) | Missing: Mandatory (derivable) |
| BillingAccountType | C | No | Missing: Conditional (derivable) |
| BillingCurrency | M | Yes (currency, USD) | Present |
| BillingPeriodEnd | M | No (rolling prepaid wallet) | Missing: Mandatory (derivable) |
| BillingPeriodStart | M | No (rolling prepaid wallet) | Missing: Mandatory (derivable) |
| CapacityReservationId | C | No | N/A: null valid |
| CapacityReservationStatus | C | No | N/A: null valid |
| ChargeCategory | M | No (implied Usage or Purchase) | Missing: Mandatory (derivable) |
| ChargeClass | M | No | Missing: Mandatory (nullable, plumbing) |
| ChargeDescription | M | Partial (resource_type, gpuName) | Missing: Mandatory (derivable) |
| ChargeFrequency | R | No (implied Usage-Based) | Missing: Recommended (derivable) |
| ChargePeriodEnd | M | Partial (terminatedAt / updatedAt) | Missing: Mandatory (derivable) |
| ChargePeriodStart | M | Partial (createdAt) | Missing: Mandatory (derivable) |
| CommitmentDiscountCategory | C | No | N/A: null valid |
| CommitmentDiscountId | C | No | N/A: null valid |
| CommitmentDiscountName | C | No | N/A: null valid |
| CommitmentDiscountQuantity | C | No | N/A: null valid |
| CommitmentDiscountStatus | C | No | N/A: null valid |
| CommitmentDiscountType | C | No | N/A: null valid |
| CommitmentDiscountUnit | C | No | N/A: null valid |
| ConsumedQuantity | C | Partial (derivable from duration or tokens) | Missing: Conditional (derivable) |
| ConsumedUnit | C | No (implied hours or tokens) | Missing: Conditional (derivable) |
| ContractedCost | M | No | Missing: Mandatory |
| ContractedUnitPrice | C | Partial (priceHr for prepay) | Missing: Conditional |
| EffectiveCost | M | Partial (amount_usd) | Missing: Mandatory |
| InvoiceId | R | No | Missing: Recommended |
| InvoiceIssuerName | M | Implicit (Prime Intellect) | Missing: Mandatory (derivable) |
| ListCost | M | Partial (priceHr x hours) | Missing: Mandatory (derivable) |
| ListUnitPrice | C | Yes (priceHr) | Present, deviation to fix |
| PricingCategory | C | Partial (isSpot, prepaidForHr) | Missing: Conditional (derivable) |
| PricingCurrency | C | Implicit (USD) | Missing: Conditional (derivable) |
| PricingCurrencyContractedUnitPrice | C | No | N/A: null valid |
| PricingCurrencyEffectiveCost | C | No | N/A: null valid |
| PricingCurrencyListUnitPrice | C | No | N/A: null valid |
| PricingQuantity | M | Partial (derivable, flat-rate hours or tokens) | Missing: Mandatory (derivable) |
| PricingUnit | M | No (implied hours or tokens) | Missing: Mandatory (derivable) |
| ProviderName | M | Yes (providerType) | Present, deviation to fix |
| PublisherName | M | Yes (providerType) | Present, deviation to fix |
| RegionId | C | Partial (dataCenterId / country) | Present, deviation to fix |
| RegionName | C | Partial (country) | Present, deviation to fix |
| ResourceId | C | Yes (id / resource_id) | Present |
| ResourceName | C | Yes (name) | Present |
| ResourceType | C | Yes (type / gpuName) | Present, deviation to fix |
| ServiceCategory | M | No (implied Compute or AI and Machine Learning) | Missing: Mandatory (derivable) |
| ServiceName | M | Partial (resource_type) | Missing: Mandatory (derivable) |
| ServiceSubcategory | R | No | Missing: Recommended |
| SkuId | C | Partial (gpuName + socket + count) | Missing: Conditional (derivable) |
| SkuMeter | C | No | Missing: Conditional |
| SkuPriceDetails | C | Partial (resources block, pricing snapshot) | Missing: Conditional |
| SkuPriceId | C | No | Missing: Conditional |
| SubAccountId | C | Yes (teamId) | Present, deviation to fix |
| SubAccountName | C | Partial (team name) | Missing: Conditional (derivable) |
| SubAccountType | C | No (personal vs team) | Missing: Conditional (derivable) |
| Tags | C | No | Missing: Conditional |

### 1.4 What's solved, and what remains

Reading the tally: of 57 columns, roughly 8 are present (several with deviations) and another 8 are trivially derivable from fields already published, leaving parts of the cost family and the period shaping as the real work. Of the 17 Mandatory columns absent from the schema, 3 are substantive (the cost family) and the other 14 are derivable or nullable. Excluding the legitimately N/A commitment and capacity-reservation columns, coverage of applicable columns sits in the mid range, ahead of a pure operational API because a net cost figure is published.

**Substantive gaps (real data not cleanly in the source):**

1. BilledCost and EffectiveCost. Prime Intellect publishes `amount_usd` per billing row and `totalBilledPrice` per resource, which are net figures after any spot discount and after credit deduction. That is a genuine effective-cost signal, unlike a list-only feed, so this gap is narrower than usual. The remaining work is twofold: emit the value as a per-charge, time-sliced record rather than a running total, and decide how promotional credits and provider-failure refunds map (BilledCost is the amount invoiced before credits, EffectiveCost is after amortized credits). Reconciling promo credits and refunds back to individual charges is the substantive part.
2. ContractedCost. Reserved and long-term capacity is arranged through prepay or a Custom GPU Quote at a negotiated rate that can differ from list. Where a customer holds such a rate, ContractedCost must be sourced from the agreement, since the API does not expose a per-charge contracted price.

**Trivial gaps (derivable from data already present, flat-rate compute):**

- ListCost = `priceHr` x billed hours for pods, or per-million-token rate x tokens for inference and training. For flat-rate on-demand and spot pods, `priceHr` is a single per-hour rate, so PricingQuantity equals consumed hours and ListUnitPrice is `priceHr`.
- PricingQuantity, PricingUnit (hours or tokens), ConsumedQuantity, ConsumedUnit: derivable from `createdAt` and `terminatedAt` duration for pods, or from the run-usage token counts for training and inference.
- ChargePeriodStart and ChargePeriodEnd: from `createdAt` and `terminatedAt` (or `last_billed_at` for the per-minute increment).
- BillingPeriodStart and BillingPeriodEnd: define a billing period over the prepaid wallet (for example a monthly window aligned to statements).
- ChargeCategory (Usage for consumption, Purchase for prepay top-ups, Credit for promo and refunds), ServiceCategory (Compute for GPU pods, AI and Machine Learning for inference and training), ServiceName, ChargeDescription: constant or derivable from `resource_type` and `gpuName`.
- BillingAccountName, BillingCurrency (USD, already present), InvoiceIssuerName (Prime Intellect): account- and issuer-level constants.
- ChargeClass: null except for corrections.

### 1.5 Deviations to fix (present columns)

- BillingAccountId: `wallet_id` is a stable account key and maps cleanly, though the FOCUS Billing Account should be pinned to the payer entity (personal or team wallet), so confirm the intended grain.
- ListUnitPrice: `priceHr` is published as a plain number; confirm it is a currency decimal per hour (not cents) and set PricingUnit accordingly.
- ProviderName and PublisherName: `providerType` carries the underlying provider, which is correct for the aggregator model, but it uses internal slugs (for example `lambdalabs`, `crusoecloud`, `dc_impala`); map to canonical provider names. For Prime Compute capacity the provider is Prime Intellect itself. These two columns are deprecated in v1.3 and removed in v1.4.
- RegionId and RegionName: `dataCenterId` and `country` approximate a region but are not a FOCUS region ID and human name pair; construct both from the available location fields.
- ResourceType: the `type` field uses Prime Intellect resource classes (Instance, Cluster, Disk, Sandbox, Inference, Image, Training) and `gpuName` uses model enums; map to the intended FOCUS representation.
- SubAccountId: `teamId` maps to the sub-account, but personal-wallet resources have no team, so define how personal versus team ownership is expressed and populate SubAccountType accordingly.

What is already right: a stable ResourceId, a populated ResourceName, ISO 8601 timestamps, an explicit BillingCurrency, a clean underlying-provider dimension, a per-resource net cost figure, and a genuine billing table exposed through the API. These are the hard parts to retrofit, and Prime Intellect has them.

## Part 2: The path forward

### 2.1 Which FOCUS version to target

Baseline conformance against v1.2 (the current certification baseline) and build toward v1.4 (latest, ratified 2026-06-04). Because v1.3 deprecates and v1.4 removes ProviderName and PublisherName, design the aggregator's provider attribution so it does not depend on those columns long term; carry the underlying `providerType` as a first-class dimension that survives their removal. The Validator supports v1.3 today, with v1.4 support expected later in Q3 2026.

### 2.2 What certification requires

FOCUS conformance for data generators runs through the FinOps Foundation. The current badge is "FinOps Certified FOCUS v1.2 Conformant" (contact member-cert@finops.org for the RFI). Membership is required for certification, though contributing to the spec is open and free. Deliverables are a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report (this analysis is its seed). Open tooling: the FOCUS Validator (checks data against the Requirements Model), the FOCUS Converter (provider-native to FOCUS), and the FOCUS Requirements Model (machine-readable MUST, SHOULD, and MAY rules).

### 2.3 Phased roadmap

**Phase 0: Validate and scope.** Define the FOCUS dataset as a charge-level feed (one row per resource per charge period), sourced from the `Billing` table joined to the pods-history and run-usage objects, not the live pod object. Confirm the v1.2 baseline and v1.4 build target. Run any existing export through the FOCUS Validator to set a baseline.

**Phase 1 (unlock): Close the cost family and the trivial Mandatory adds.** Emit `amount_usd` as per-charge BilledCost and EffectiveCost, define the credit and refund treatment that separates the two, and derive ListCost from `priceHr` and billed hours (or per-token rate and token count). In the same pass, emit the derivable Mandatory columns: PricingQuantity, PricingUnit, ChargePeriodStart and End, BillingPeriodStart and End, ChargeCategory, ServiceCategory, ServiceName, ChargeDescription, BillingAccountName, InvoiceIssuerName, and ChargeClass. Source ContractedCost from the prepay or Custom Quote agreement where one applies.

**Phase 2: Fix format and value deviations.** Map `providerType` slugs to canonical provider names, construct RegionId and RegionName from `dataCenterId` and `country`, confirm `priceHr` units, and normalize ResourceType and SubAccount handling for personal versus team wallets.

**Phase 3: Round out applicable Conditional and Recommended columns.** Populate SubAccountName and SubAccountType, ConsumedQuantity and Unit, ContractedUnitPrice, PricingCategory (on-demand, spot, reserved), PricingCurrency, the SKU detail columns from `gpuName`, `socket`, and the pricing snapshot, ChargeFrequency, ServiceSubcategory, and InvoiceId once invoice identifiers are exposed. Add Tags if and when the platform introduces resource tagging. Null the commitment and capacity-reservation families with a note that they do not apply.

**Phase 4: Mature to v1.4 and certify.** Migrate provider attribution off ProviderName and PublisherName ahead of their removal, adopt the v1.4 Invoice Detail and billing-period datasets for cleaner statement reconciliation, re-validate, and pursue certification.

### 2.4 FOCUS Use Cases unlocked

- Unlocked once the charge-level feed with resource, sub-account, and day-level data exists (Phase 1 to 3): cost allocation by team and user, multi-cloud spend reporting across underlying providers, GPU-hour and token utilization analysis, anomaly detection, and showback by team. Tag-based allocation waits on resource tagging.
- Unlocked once the cost family is shaped (Phase 1): effective-cost reporting, spot-savings analysis (list versus effective), invoice reconciliation, and actuals-based budgeting against the prepaid wallet.
- Out of scope for the model: commitment-discount and capacity-reservation use cases, since Prime Intellect's model is on-demand, spot, and prepay pass-through rather than structured commitment discounts (reserved rates are arranged offline via Custom Quote and would need structured per-charge exposure first).

## Part 3: Immediate next steps

1. Define the target FOCUS dataset as a charge-level feed joining the `Billing` table, pods-history, and run-usage objects, distinct from the live pod API.
2. Map the aggregator roles: underlying `providerType` to Provider and Publisher, Prime Intellect to Invoice Issuer, and the team versus personal wallet to SubAccount.
3. Decide the BilledCost versus EffectiveCost treatment for spot discounts, promotional credits, and provider-failure refunds, and derive ListCost from `priceHr` and consumed hours.
4. Emit the derivable Mandatory columns and normalize provider slugs, region, and resource-type values.
5. Run a sample through the FOCUS Validator and confirm the target representation against the Requirements Model.

## Confidence summary

- Pod, pods-history, and billing endpoint field structure: high confidence, taken directly from the published OpenAPI reference at api.primeintellect.ai/openapi.json.
- Billing mechanics (prepaid credits deducted per minute, USD, spot discounts up to ninety percent, promo credits and refunds via support, team billing email): medium-high confidence, drawn from the FAQ and pricing pages.
- The interpretation that `amount_usd` and `totalBilledPrice` are net effective figures (post spot discount, post credit deduction) rather than list amounts: medium confidence; confirm against a sample billing export whether any list-versus-net split or credit line exists per row before finalizing the BilledCost and EffectiveCost mapping.
- The absence of tags, per-line invoice IDs, and named regions: medium-high confidence; no such fields appear in the public schema. If a private billing export carries them, several Missing items would move to Present.
- Feature levels: high confidence, verified against the v1.2 spec with a live spot-check on 2026-07-01.
- Data quality for this analysis: solid on data shape (API and billing endpoints are well documented), provisional on the exact list-versus-effective and credit treatment within a billing row.

## Sources

- Prime Intellect API reference and OpenAPI: https://docs.primeintellect.ai/api-reference/introduction, https://api.primeintellect.ai/openapi.json
- Prime Intellect Pods, Pods History, and Billing endpoints: https://docs.primeintellect.ai/api-reference/pods/create-pod, https://docs.primeintellect.ai/api-reference/pods/get-pods-history, https://docs.primeintellect.ai/api-reference/billing/wallet-balance-+-most-recent-billing-rows, https://docs.primeintellect.ai/api-reference/billing/token-usage-and-cost-for-a-single-rft-run
- Prime Intellect FAQ, Inference, and Hosted Training pricing: https://docs.primeintellect.ai/faq, https://docs.primeintellect.ai/inference/overview, https://docs.primeintellect.ai/hosted-training/models-and-pricing
- FOCUS Specification v1.2: https://focus.finops.org/focus-specification/v1-2/
- FOCUS project, tooling, and certification: https://focus.finops.org/

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
