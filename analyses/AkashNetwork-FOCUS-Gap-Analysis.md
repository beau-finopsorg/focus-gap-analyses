# Akash Network and FOCUS: Compliance Gap and Adoption Roadmap

*Analysis run: July 1, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

Prepared: July 1, 2026
Provider and product in scope: Akash Network (decentralized GPU and compute marketplace), analyzed across the on-chain lease and settlement records (deployment, order, bid, lease objects on the Akash blockchain) and the Akash Console Billing and Usage feature (Credit Purchase History plus Usage analytics, AEP-68).
FOCUS baseline version: v1.2 (current certification baseline).
FOCUS build target: v1.4 (latest ratified, June 4, 2026).
Feature levels verified against the FOCUS Specification via the FOCUS MCP column library on July 1, 2026. The bundled reference table was confirmed current (SPEC_VERSIONS_AS_OF 2026-06-23): 57 columns for v1.2, with ProviderName and PublisherName deprecated in v1.3 and removed in v1.4.

---

## Executive summary

Akash Network is a decentralized compute marketplace where cost data is not produced by a single billing system but is reconstructed from blockchain state. Every lease is an on-chain object carrying a per-block price (in uAKT or a whitelisted stablecoin such as USDC), a tenant wallet address, a provider wallet address, and a resource specification (CPU, memory, storage, GPU) drawn from the deployment's SDL. This gives Akash something most SaaS vendors lack from day one: immutable, timestamped, resource-level, sub-daily usage and settlement records that are public and auditable.

What Akash does not have is a FOCUS-shaped billing export. The on-chain data is a marketplace ledger, not a cost and usage dataset: it records prices in uAKT per block, identifies parties by cryptographic wallet addresses rather than named accounts, and carries no ServiceCategory, ChargeCategory, or currency-normalized cost columns. The Console Billing and Usage feature (launched August 2025) is a first step toward cost transparency for credit-card users, but it surfaces credit purchases and spend charts, not a line-item usage feed. A conformant dataset can be built from the chain, but it requires an ETL layer that decodes lease events, converts uAKT-per-block into currency-denominated cost per charge period, and maps marketplace concepts onto FOCUS columns.

The strongest finding: the underlying data is unusually rich on granularity and resource identity, the two dimensions many providers struggle with. The hardest finding: cost normalization is substantive. Turning per-block uAKT streams into BilledCost and EffectiveCost in a stable BillingCurrency requires a defensible token-to-fiat conversion policy, and the crypto-native settlement model complicates BillingCurrency, InvoiceIssuerName, and account identity.

Stat strip:
- 57 FOCUS columns (v1.2 target).
- 0 columns present in FOCUS shape today (the source is native on-chain and Console data, no FOCUS mapping exists).
- 21 Mandatory columns, of which the substantive gaps concentrate in the cost family and identity family.
- All present-equivalent data requires transformation, so deviations are pervasive rather than isolated.

Recommendation: treat this as a build-a-dataset-from-a-ledger exercise, not a reshape-an-export exercise. The chain already supplies granularity, resource identity, and quantities; the project's center of gravity is a currency conversion and cost-derivation layer plus a FOCUS emitter. Baseline to v1.2, design toward v1.4.

RAG readiness: Cost Gap, Granularity Strong, Allocation Partial, Coverage Gap, FOCUS shape Gap. Overall band: Not yet aligned (per public docs).

---

## Part 1: The conformance gap

### 1.1 The data source

Akash Network has no single billing pipeline. Cost and usage information exists in three places, and a FOCUS dataset would be assembled from them:

1. On-chain marketplace and settlement records. The Akash blockchain (a Cosmos SDK chain) records the full deployment lifecycle as typed objects:
   - Deployment (identified by owner wallet address plus a deployment sequence, dseq).
   - Order and bid (a reverse auction: providers submit bids priced per block; the lowest qualifying bid typically wins).
   - Lease (the accepted bid: a tuple of owner, dseq, group sequence gseq, order sequence oseq, and provider address, carrying a price in uAKT per block or a stablecoin denom per block).
   - Escrow account activity: the tenant funds an escrow, and the protocol streams payment to the provider per block (roughly every six seconds), with providers able to withdraw and either party able to close the lease.

   This is the authoritative record of what was consumed and what was paid. It is timestamped to the block, immutable, and public via block explorers and stats.akash.network.

2. Akash Console Billing and Usage (AEP-68, August 2025). A managed-experience layer for credit-card users. It exposes a Credit Purchase History table (date, amount, payment method, status, downloadable receipt, CSV export) and a Usage tab (total spend, total deployments, spend-over-time and cumulative-spend charts, with weekly/monthly/annual or custom ranges). This is spend reporting and receipts, not a per-lease line-item cost feed.

3. SDL (Stack Definition Language). The tenant-authored manifest that specifies requested resources (CPU units, memory, storage, GPU vendor/model) and a per-resource price ceiling. SDL is the source of resource type and quantity semantics.

Granularity: the on-chain record is sub-daily by construction. Payment accrues per block (about six-second cadence), and every lease event is individually timestamped. This is finer than the daily grain FOCUS treats as strong.

Currency: the native unit is uAKT (1 AKT = 1,000,000 uAKT), a volatile token. Under AKT 2.0 stable payments (AEP-23), leases can be priced and settled in whitelisted stablecoins such as USDC, and Console credit-card users transact in USD-denominated credits. So the currency picture is mixed: a given lease may settle in AKT, in USDC, or be funded by USD credit purchases.

Key limitations for FOCUS purposes:
- No native cost columns in a currency FOCUS expects. Prices are uAKT (or stablecoin) per block, not a settled fiat cost per charge period.
- Identity is cryptographic. Tenant and provider are wallet addresses (akash1...), not named billing accounts or a named invoice issuer.
- No service taxonomy, charge taxonomy, or SKU model. The marketplace sells raw compute resources, not named services or SKUs.
- No traditional invoice. Settlement is a continuous on-chain escrow stream, not a periodic invoice document (though v1.4 billing-period constructs map onto this reasonably).

### 1.2 How conformance is judged

FOCUS assigns every column a feature level: Mandatory (must be present and populated), Conditional (required when the provider's business model triggers the condition), Recommended (encouraged), or Optional. Conformance is judged column by column against the Requirements Model, not by an overall percentage. The levels in this report were verified against the FOCUS Specification column library on July 1, 2026, not stated from memory. The commonly misremembered levels were checked: ServiceSubcategory is Recommended (not Mandatory); PricingQuantity, PricingUnit, and ChargeClass are Mandatory; ChargeFrequency and InvoiceId are Recommended; ResourceId, ResourceName, and Tags are Conditional.

Because Akash emits no FOCUS-shaped data today, every classification below reflects whether the underlying data exists on-chain or in Console (and could be mapped), not whether an aligned field is emitted.

### 1.3 Column-by-column status (FOCUS v1.2, all 57 columns)

Status legend:
- Present: emitted and aligned.
- Present, deviation to fix: emitted but wrong format or invalid values.
- Missing: Mandatory: required and absent; blocks conformance.
- Missing: Recommended: encouraged, absent; does not block conformance.
- Missing: Conditional: required when the model triggers the condition; absent and the condition applies.
- N/A: null valid: Conditional or Recommended column that does not apply to Akash's model; should exist and be null.

Because no FOCUS emitter exists, "Missing" here means the data must be produced, and the parenthetical notes whether the underlying data exists in the source (a build-it question) or does not exist at all (a substantive-data question).

| # | FOCUS Column | Level | In the source? | Status |
|---|---|---|---|---|
| 3.1 | AvailabilityZone | Recommended | No (providers publish region/datacenter/city, not zones) | N/A: null valid |
| 3.2 | BilledCost | Mandatory | Underlying uAKT/stablecoin per-block price exists; settled fiat cost does not | Missing: Mandatory |
| 3.3 | BillingAccountId | Mandatory | Tenant wallet address (akash1...) or Console account | Missing: Mandatory |
| 3.4 | BillingAccountName | Mandatory | No named account; wallet address only | Missing: Mandatory |
| 3.5 | BillingAccountType | Conditional | No account type taxonomy | Missing: Conditional |
| 3.6 | BillingCurrency | Mandatory | Denom exists (uAKT/USDC/USD credit) but not an ISO currency of settlement | Missing: Mandatory |
| 3.7 | BillingPeriodEnd | Mandatory | Derivable from block timestamps (no native billing period) | Missing: Mandatory |
| 3.8 | BillingPeriodStart | Mandatory | Derivable from block timestamps | Missing: Mandatory |
| 3.9 | CapacityReservationId | Conditional | No capacity reservation construct | N/A: null valid |
| 3.10 | CapacityReservationStatus | Conditional | No capacity reservation construct | N/A: null valid |
| 3.11 | ChargeCategory | Mandatory | Derivable (leases are Usage; fees are Usage/Purchase) | Missing: Mandatory |
| 3.12 | ChargeClass | Mandatory (nullable) | No corrections concept; null | Missing: Mandatory |
| 3.13 | ChargeDescription | Mandatory (nullable) | Derivable from lease/resource metadata | Missing: Mandatory |
| 3.14 | ChargeFrequency | Recommended | Derivable (Usage-Based) | Missing: Recommended |
| 3.15 | ChargePeriodEnd | Mandatory | Block timestamps (native, fine-grained) | Missing: Mandatory |
| 3.16 | ChargePeriodStart | Mandatory | Block timestamps (native, fine-grained) | Missing: Mandatory |
| 3.17 | CommitmentDiscountCategory | Conditional | No commitment discounts | N/A: null valid |
| 3.18 | CommitmentDiscountId | Conditional | No commitment discounts | N/A: null valid |
| 3.19 | CommitmentDiscountName | Conditional | No commitment discounts | N/A: null valid |
| 3.20 | CommitmentDiscountQuantity | Conditional | No commitment discounts | N/A: null valid |
| 3.21 | CommitmentDiscountStatus | Conditional | No commitment discounts | N/A: null valid |
| 3.22 | CommitmentDiscountType | Conditional | No commitment discounts | N/A: null valid |
| 3.23 | CommitmentDiscountUnit | Conditional | No commitment discounts | N/A: null valid |
| 3.24 | ConsumedQuantity | Conditional | Resource units from SDL times duration; derivable | Missing: Conditional |
| 3.25 | ConsumedUnit | Conditional | Resource units (vCPU, GB, GPU-count); derivable | Missing: Conditional |
| 3.26 | ContractedCost | Mandatory | Bid price is effectively the contracted rate; needs currency normalization | Missing: Mandatory |
| 3.27 | ContractedUnitPrice | Conditional | Per-block bid price per resource; derivable | Missing: Conditional |
| 3.28 | EffectiveCost | Mandatory | Underlying settlement exists; settled fiat cost does not | Missing: Mandatory |
| 3.29 | InvoiceId | Recommended | No invoice; a synthetic billing-period ID could be assigned | Missing: Recommended |
| 3.30 | InvoiceIssuerName | Mandatory | No single issuer (decentralized); needs a defined convention | Missing: Mandatory |
| 3.31 | ListCost | Mandatory | Bid price is the market rate; needs currency normalization | Missing: Mandatory |
| 3.32 | ListUnitPrice | Conditional | Per-block bid price; derivable | Missing: Conditional |
| 3.33 | PricingCategory | Conditional | Derivable (On-Demand / market) | Missing: Conditional |
| 3.34 | PricingCurrency | Conditional | The lease denom (uAKT/USDC); the pricing-currency case is central here | Missing: Conditional |
| 3.35 | PricingCurrencyContractedUnitPrice | Conditional | Per-block bid price in native denom; derivable | Missing: Conditional |
| 3.36 | PricingCurrencyEffectiveCost | Conditional | Native-denom settled amount from escrow; derivable | Missing: Conditional |
| 3.37 | PricingCurrencyListUnitPrice | Conditional | Per-block bid price in native denom; derivable | Missing: Conditional |
| 3.38 | PricingQuantity | Mandatory (nullable) | Derivable from resource units and block duration | Missing: Mandatory |
| 3.39 | PricingUnit | Mandatory (nullable) | Derivable (per-block, or normalized per-hour) | Missing: Mandatory |
| 3.40 | ProviderName | Mandatory (deprecated v1.3, removed v1.4) | "Akash Network" (the marketplace) | Missing: Mandatory |
| 3.41 | PublisherName | Mandatory (deprecated v1.3, removed v1.4) | The individual compute provider (by address/hostname) | Missing: Mandatory |
| 3.42 | RegionId | Conditional | Provider attribute (e.g., location-region: us-west) | Missing: Conditional |
| 3.43 | RegionName | Conditional | Provider attribute (region/city/country) | Missing: Conditional |
| 3.44 | ResourceId | Conditional | Lease tuple (owner/dseq/gseq/oseq/provider) is a natural resource ID | Missing: Conditional |
| 3.45 | ResourceName | Conditional | Deployment/service name from SDL | Missing: Conditional |
| 3.46 | ResourceType | Conditional | Derivable (compute lease, GPU lease, IP lease, storage) | Missing: Conditional |
| 3.47 | ServiceCategory | Mandatory | Derivable (Compute; AI and Machine Learning for GPU) | Missing: Mandatory |
| 3.48 | ServiceName | Mandatory | Derivable (e.g., Akash Compute, Akash GPU) | Missing: Mandatory |
| 3.49 | ServiceSubcategory | Recommended | Derivable (GPU, CPU, Storage, Networking) | Missing: Recommended |
| 3.50 | SkuId | Conditional | No SKU model; a synthetic SKU (resource profile) could be built | Missing: Conditional |
| 3.51 | SkuMeter | Conditional | Derivable (the metered resource) | Missing: Conditional |
| 3.52 | SkuPriceDetails | Conditional | Bid price structure could populate this | Missing: Conditional |
| 3.53 | SkuPriceId | Conditional | No SKU price catalog (prices are auction-determined) | N/A: null valid |
| 3.54 | SubAccountId | Conditional | No sub-account layer under a wallet | N/A: null valid |
| 3.55 | SubAccountName | Conditional | No sub-account layer | N/A: null valid |
| 3.56 | SubAccountType | Conditional | No sub-account layer | N/A: null valid |
| 3.57 | Tags | Conditional | SDL labels exist and could carry key-value tags | Missing: Conditional |

Tally (v1.2, 57 columns): 0 Present, 0 Present-with-deviation, 21 Missing Mandatory, 3 Missing Recommended (AvailabilityZone is N/A), 18 Missing Conditional, and 15 N/A null-valid. The Mandatory and Recommended and Conditional missing counts plus the N/A count reconcile to 57 (21 + 3 + 18 + 15 = 57). No column is emitted in FOCUS shape today, so the analysis is about what to build from the ledger, not what to reshape.

Note: AvailabilityZone (Recommended) is counted as N/A because Akash exposes region/datacenter/city but not sub-region zones.

### 1.4 What's solved, and what remains

Solved, or nearly so (the data exists and is high quality):
- Granularity is a genuine strength. Block-level timestamps make ChargePeriodStart and ChargePeriodEnd trivial to populate at a grain finer than FOCUS requires. Aggregation to a daily or billing-period grain is a straightforward rollup.
- Resource identity exists natively. The lease tuple (owner, dseq, gseq, oseq, provider) is a stable, unique identifier for ResourceId. Deployment and service names from SDL supply ResourceName. This is real allocation data that many SaaS providers cannot produce.
- Quantities and units exist. Requested resources (vCPU, memory GB, storage GB, GPU count) times lease duration in blocks give ConsumedQuantity, ConsumedUnit, PricingQuantity, and PricingUnit. These are derivable, but note the caveat below.
- Native-denom pricing exists. The per-block bid price supplies the PricingCurrency family (ListUnitPrice, ContractedUnitPrice, and the effective amount) in uAKT or the stablecoin denom directly.

Substantive gaps (real data or real policy decisions that do not exist in the source today):
- The cost columns are the core substantive gap. BilledCost, EffectiveCost, ListCost, and ContractedCost must be expressed in a single BillingCurrency, but Akash settles in uAKT (volatile), in stablecoins, or via USD credits. Producing these requires a defined token-to-fiat conversion policy (which rate, at what timestamp, block-time or daily close) and a decision on the reporting BillingCurrency. This is not a copy from ListCost; it is a currency-normalization and cost-derivation layer. Because settlement happens continuously on-chain in a volatile denom, treat these as substantive, not trivial.
- BillingCurrency and the pricing-currency split are substantive by model. FOCUS separates the currency a charge is priced in (PricingCurrency) from the currency it is billed in (BillingCurrency). Akash's mixed uAKT/USDC/USD-credit reality is exactly the case the pricing-currency columns exist for, but populating them correctly requires a settlement-currency policy per lease.
- Account and issuer identity need a convention. BillingAccountId can map to the tenant wallet or Console account, but BillingAccountName, InvoiceIssuerName, and the Provider/Publisher pair have no clean native answer in a decentralized marketplace. A defensible convention is needed: for example, InvoiceIssuerName = "Akash Network" (or the settling entity for Console), ProviderName = "Akash Network", PublisherName = the individual compute provider address or moniker.

Trivial gaps (Mandatory but derivable or nullable once the pipeline exists):
- ChargeClass is nullable and populated only for corrections; Akash has no corrections concept, so null is valid and aligned.
- ChargeCategory is derivable: leases are Usage; take/make fees are Usage or Purchase depending on treatment.
- ServiceCategory and ServiceName are derivable from resource type (Compute, or AI and Machine Learning for GPU leases; ServiceName such as Akash Compute or Akash GPU).
- BillingPeriodStart/End are a rollup decision over block timestamps once a reporting period is defined.
- ChargePeriodStart/End are direct from block timestamps.

Caveat on pricing quantities: PricingQuantity equals the consumed quantity only for flat-rate resources. Akash bids are effectively flat per-block rates per resource, so for a single lease the derivation is clean. Where a deployment blends multiple resource types or the emitter aggregates to a coarser grain, PricingQuantity must be computed against the rate basis, not copied from raw consumption.

### 1.5 Deviations to fix

Because no FOCUS-shaped field is emitted, there are no in-place format deviations to correct; there is instead a set of shape decisions the emitter must get right from the start:
- Currency codes. BillingCurrency and PricingCurrency must use ISO 4217 codes (USD) or a documented convention for non-ISO crypto denoms. uAKT is not an ISO currency; the dataset needs a clear rule (for example, report BillingCurrency as USD after conversion, and record the native denom in a documented pricing-currency treatment or an x_ column).
- Tags as key-value pairs. SDL labels should be emitted as FOCUS key-value tags, not an array of bare strings.
- Enum discipline. ChargeCategory, ChargeFrequency, and ServiceCategory must use valid FOCUS members. GPU compute maps to ServiceCategory "AI and Machine Learning" or "Compute"; do not invent values.
- Timestamps. Block times are already timestamped; emit as ISO 8601 with inclusive-start, exclusive-end periods.
- Custom columns. Akash-specific fields with no FOCUS home (dseq, provider address, escrow balance, take/make fee, block height) must be prefixed x_ (for example, x_DeploymentSequence, x_ProviderAddress, x_BlockHeight).

What is already done right, conceptually: immutable timestamps, a stable resource identifier, explicit resource quantities and units, and public auditable records. These are the parts that are usually hardest to retrofit, and Akash has them by design.

---

## Part 2: The path forward

### 2.1 Which FOCUS version to target

Baseline to v1.2, the current certification baseline, so a conformant dataset can be measured against the program's badge. Design and build toward v1.4 (ratified June 4, 2026), the latest version, since a greenfield emitter should not encode soon-to-be-deprecated columns.

The version choice matters more than usual here because of the Provider/Publisher deprecation. In v1.2 and v1.3, ProviderName and PublisherName are Mandatory, and they are the natural home for the "Akash marketplace vs. individual compute provider" distinction. In v1.4 both are removed. A v1.4-targeted emitter should carry that distinction through the account and resource identity columns and any x_ provider fields instead, so the decentralized-provider information is not lost when Provider/Publisher disappear. The v1.4 Invoice Detail and billing-period datasets are also a natural fit for expressing Akash's continuous escrow settlement as periodic billing constructs.

### 2.2 What certification requires

FOCUS conformance for data generators runs through the FinOps Foundation. The current badge has historically been "FinOps Certified FOCUS v1.2 Conformant"; confirm the current badge version against the program page before finalizing. The RFI contact is member-cert@finops.org. Membership is required for certification, though contributing to the spec is open and free.

The certification deliverables are a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report (this analysis is its seed). The supporting open-source tooling: the FOCUS Validator (checks data against the Requirements Model), the FOCUS Converter (provider-native to FOCUS), and the FOCUS Requirements Model (machine-readable MUST/SHOULD/MAY rules).

For Akash specifically, the mapping deliverable is the crux: it must document how on-chain lease objects and uAKT-per-block prices become FOCUS rows, and it must state the currency-conversion policy transparently, since that policy directly determines the cost columns a reviewer will validate.

### 2.3 Phased roadmap

Phase 0: Validate scope and define policy. Confirm the target version (baseline v1.2, build v1.4). Decide the reporting BillingCurrency and the token-to-fiat conversion policy (rate source, timestamp basis). Define the account/issuer/provider conventions for a decentralized marketplace. Pick a representative set of leases (CPU, GPU, storage, IP) as sample data. This phase is policy, not code, and everything downstream depends on it.

Phase 1: Build the cost and identity core (closes the substantive Mandatory gaps). Stand up the ETL that decodes lease and escrow events, applies the conversion policy, and emits ListCost, ContractedCost, BilledCost, and EffectiveCost in the chosen BillingCurrency, plus BillingCurrency, BillingAccountId/Name, InvoiceIssuerName, ProviderName/PublisherName (for v1.2/v1.3), ServiceCategory, ServiceName, ChargeCategory, ChargeDescription, and the trivially-derivable ChargePeriod and BillingPeriod columns. Populate ChargeClass as null. This is the phase that unlocks usable conformance.

Phase 2: Round out quantities, pricing-currency, and resource identity (Conditional and Recommended). Emit ConsumedQuantity/Unit, PricingQuantity/Unit, the PricingCurrency family (the natural home for the native uAKT/stablecoin denom), ResourceId (the lease tuple), ResourceName, ResourceType, RegionId/RegionName (from provider attributes), and Tags (SDL labels as key-value pairs). Add ChargeFrequency and ServiceSubcategory.

Phase 3: Validate and fix shape. Run sample data through the FOCUS Validator. Fix enum values, currency codes, tag key-value structure, and timestamp conventions. Confirm N/A columns (commitment discount family, capacity reservation family, sub-account family, SkuPriceId) are present and null with documented justification.

Phase 4: Mature to v1.4 and certify. Migrate the emitter off Provider/Publisher to the v1.4 column set, adopt the Invoice Detail and billing-period datasets to model escrow settlement, complete the native-to-FOCUS mapping document and Conformance Gap Report, and engage member-cert@finops.org for the RFI.

### 2.4 FOCUS Use Cases unlocked

Unlocked once Phase 1 lands (cost plus identity plus day-level periods):
- Cost reporting and showback across deployments and providers.
- Spend trend and anomaly detection over time (the block grain makes this precise).
- Provider cost comparison (which compute provider is cheapest for a given resource profile).

Unlocked with Phase 2 (resource, tag, region detail):
- Allocation by deployment, service, and tag.
- Region and GPU-model cost breakdowns.
- Resource-level unit economics (cost per vCPU-hour, per GPU-hour).

Out of scope for Akash's model (note, do not force-fit):
- Commitment-based discount and utilization use cases: Akash has no reservations or committed-use discounts (pricing is a live reverse auction).
- Capacity reservation reporting: no reservation construct.
- Amortization of upfront commitments: no upfront commitment purchases.

---

## Part 3: Immediate next steps

1. Decide the reporting BillingCurrency and the token-to-fiat conversion policy (rate source and timestamp basis). This single decision governs every cost column.
2. Define the decentralized-marketplace identity conventions: what fills BillingAccountId/Name, InvoiceIssuerName, and ProviderName/PublisherName.
3. Assemble a representative sample of on-chain leases (CPU, GPU, storage, IP) plus matching Console records for the same period.
4. Build a proof-of-concept emitter for the Phase 1 core columns and run it through the FOCUS Validator.
5. Confirm the current certification badge version and open the RFI conversation with member-cert@finops.org.

---

## Confidence summary

- Feature levels and column set: high confidence. Verified against the FOCUS column library via the FOCUS MCP on July 1, 2026; the bundled v1.2 table (57 columns, Provider/Publisher deprecation path) was confirmed current as of the 2026-06-23 stamp. No cache refresh was required.
- Akash on-chain data model (deployment/order/bid/lease, per-block uAKT pricing, escrow settlement, wallet-based identity, SDL resources): high confidence, drawn from Akash official documentation.
- Stable payments and mixed currency (AKT 2.0 / AEP-23 stablecoin settlement, USDC, USD credits): solid confidence; the mechanism is documented, but per-lease settlement-currency distribution across the network was not quantified here.
- Console Billing and Usage feature scope (Credit Purchase History, CSV export, Usage charts, AEP-68): solid confidence, from the official Akash blog. It was confirmed to be spend reporting and receipts, not a line-item usage feed; no FOCUS-shaped export exists.
- No formal FOCUS export or mapping exists today: high confidence. The classification therefore reflects whether the underlying data can be built into each FOCUS column, not whether an aligned field is emitted.
- Overall: this analysis reflects the data source reviewed (public on-chain records plus the Console Billing and Usage feature and documentation), not a formal certification result. The readiness band Emerging reflects strong underlying granularity and resource identity offset by the absence of any FOCUS shaping and a substantive cost-normalization gap. Data quality of this analysis: solid.

---

## Sources

- Akash Network documentation, Providers and Leases (core concepts): https://akash.network/docs/learn/core-concepts/providers-leases/
- Akash Network documentation, Provider Lease Management: https://akash.network/docs/providers/provider-faq-and-guide/lease-management/
- Akash Network blog, Billing and Usage Analytics in Akash Console and API (AEP-68), August 2025: https://akash.network/blog/billing-and-usage-analytics-in-akash-console-and-api/
- Akash Network discussion, AKT 2.0 Stable Payments and Take Rates (AEP-23): https://github.com/orgs/akash-network/discussions/147
- Akash Console: https://console.akash.network/
- Akash Stats (on-chain transactions and provider metrics): https://stats.akash.network/
- FOCUS Specification and column library: https://focus.finops.org/focus-specification/
- FOCUS tooling (Validator, Converter, Requirements Model): https://focus.finops.org/

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
