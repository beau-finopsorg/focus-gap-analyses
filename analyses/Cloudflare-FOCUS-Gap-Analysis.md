# Cloudflare and FOCUS: Compliance Gap and Adoption Roadmap

*Analysis run: August 3, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

Prepared 2026-08-03. Source analyzed: Cloudflare Billable Usage API (REST, `GET /accounts/{account_id}/billable-usage`), announced 2026-08-03, plus the Cloudflare billing documentation. FOCUS baseline v1.2, build target v1.4.

Cloudflare is not listed on the FOCUS provider "get started" page, so it holds no FinOps Certified FOCUS designation. This analysis assesses readiness only; it reflects the data source reviewed, not a formal certification result.

## Executive summary

Cloudflare's Billable Usage API is unusual among newly shipped billing feeds: it was built around FOCUS. The payload emits FOCUS column names directly (`ServiceName`, `ChargePeriodStart`, `ChargePeriodEnd`, `ConsumedQuantity`, `ConsumedUnit`, `PricingQuantity`, `ContractedCost`, `BillingCurrency`, `BillingPeriodStart`), and it carries an actual per-line cost in currency, not only a usage quantity. That puts the usage-based slice of a self-serve account close to FOCUS shape without a transformation layer.

The gaps are about scope, not shaping. The API covers only usage-based charges (not flat-rate plans, add-ons, or tax), only self-serve Pay-as-you-go accounts (not Enterprise contracts), one account at a time (no organization or sub-account rollup), and it carries no tags and only zone-level resource identity.

- FOCUS columns (v1.2): 57
- Already present: 13 (10 exact matches, 3 carrying the right data under a native name)
- Substantive Mandatory gaps: 0 of 12 (all 12 missing Mandatory columns are trivial for self-serve)
- Deviations to fix: 3

Readiness (RAG): Cost Partial, Granularity Strong, Allocation Gap, Coverage Partial, FOCUS shape Strong. Overall band: Partially aligned.

Recommendation: Emit the remaining Mandatory columns, which for self-serve are constants, derivations, or copies of `ContractedCost` (with no discounts or commitments, `ListCost` = `BilledCost` = `EffectiveCost` = `ContractedCost`). Map `ServiceFamilyName` to the FOCUS `ServiceCategory` vocabulary and surface `ZoneId` and `ZoneName` as `ResourceId` and `ResourceName`. Then extend scope to flat-rate charges, tax, tags, sub-accounts, and Enterprise contracts, where the cost columns become a real reconciliation rather than a copy.

## Part 1: The conformance gap

### 1.1 The data source

The Billable Usage API is a REST endpoint on the standard Cloudflare v4 API:

- `GET https://api.cloudflare.com/client/v4/accounts/{account_id}/billable-usage`, with optional `from` and `to` date parameters, authenticated by an API token holding the Billing Read permission.
- The response uses the standard Cloudflare envelope: `result` is an array of rows (`success`, `errors`, `messages` alongside), one row per product per charge period.

Fields on each row (from the announcement's example payload and FOCUS mapping table):

- `ServiceName` and `ServiceFamilyName`: the product ("Workers Standard" under family "Workers", "R2 Storage" under "R2").
- `ChargePeriodStart` and `ChargePeriodEnd`: the window the row covers.
- `ConsumedQuantity` (also referenced as `PricingQuantity`) and `ConsumedUnit`: how much was used, in the unit billed on (GB-months, GB-seconds, requests).
- `ContractedCost`: what the period cost, in `BillingCurrency`.
- `CumulatedContractedCost` and `CumulatedPricingQuantity`: running totals for the billing period.
- `BillingCurrency` and `BillingPeriodStart`.
- `ZoneId` and `ZoneName`: present when usage is attributed to a specific zone.

Example row: `{"BillingCurrency":"USD","BillingPeriodStart":"2025-02-01T00:00:00Z","ChargePeriodStart":"2025-02-01T00:00:00Z","ChargePeriodEnd":"2025-02-28T23:59:59Z","ServiceName":"Workers Standard","ServiceFamilyName":"Workers","ConsumedQuantity":150000,"ConsumedUnit":"GB-months","ContractedCost":0.75,"CumulatedContractedCost":2.25}`.

Key characteristics and limits:

- Daily granularity: usage and cost are updated daily; the API returns charge-period rows, which for most products is a daily grain, satisfying the sub-monthly charge-record expectation.
- Cost present, in currency: `ContractedCost` is a real per-line dollar amount, and `BillingCurrency` states the ISO currency. This is stronger than most emerging usage feeds, which expose quantity only.
- Self-serve only: the endpoint is live for self-serve (Pay-as-you-go) accounts. An equivalent experience for Enterprise contracts is described as in progress.
- Usage-based only: the feed covers every usage-based product (Workers, R2, D1, Workers AI, Vectorize, Images, Stream). Flat-rate plan charges, subscription and add-on base fees, and sales tax are billed separately and are not in this payload.
- Single account: the endpoint is scoped to one `account_id`. There is no organization, tenant, reseller, or sub-account rollup in the API.
- No tags: the payload carries no cost-allocation tags. Tag-style allocation is available only through the partner integration (Vantage Virtual Tags), outside the API.
- Resource identity is zone-level and partial: `ZoneId` and `ZoneName` appear when usage is zone-attributed; product-level usage is not zone-scoped.
- No commitments or negotiated discounts: self-serve costs reflect the published rate card. Free tiers are included allowances (usage below the tier is not billed), not discounts applied to billed lines.

### 1.2 How conformance is judged

FOCUS assigns every column a feature level: Mandatory (must be present and populated), Conditional (required when the model triggers the condition), Recommended (encouraged), or Optional. Conformance is judged column by column against the Requirements Model. A dataset conforms when every Mandatory column is present and correctly populated, every applicable Conditional column is handled, tags are key-value pairs, enumerated columns carry valid members, and types, currency, and date formats follow the spec. Feature levels for this report were verified against the FOCUS v1.2 content-constraint tables.

### 1.3 Column-by-column status

Legend: Present; Present, deviation to fix; Missing: Mandatory; Missing: Recommended; Missing: Conditional; N/A: null valid.

| FOCUS Column | Level | In the source? | Status |
|---|---|---|---|
| AvailabilityZone | R | No (edge network, no availability zones) | N/A: null valid |
| BilledCost | M | No (equals ContractedCost for self-serve) | Missing: Mandatory |
| BillingAccountId | M | Yes (account in scope) | Present |
| BillingAccountName | M | No (account lookup) | Missing: Mandatory |
| BillingAccountType | C | No | Missing: Conditional |
| BillingCurrency | M | Yes (BillingCurrency) | Present |
| BillingPeriodEnd | M | No (only BillingPeriodStart emitted) | Missing: Mandatory |
| BillingPeriodStart | M | Yes (BillingPeriodStart) | Present |
| CapacityReservationId | C | No | N/A: null valid |
| CapacityReservationStatus | C | No | N/A: null valid |
| ChargeCategory | M | No (constant "Usage" for this feed) | Missing: Mandatory |
| ChargeClass | M | No (null; corrections not in feed) | Missing: Mandatory |
| ChargeDescription | M | No (derivable from ServiceName) | Missing: Mandatory |
| ChargeFrequency | R | No (constant "Usage-Based") | Missing: Recommended |
| ChargePeriodEnd | M | Yes (ChargePeriodEnd) | Present |
| ChargePeriodStart | M | Yes (ChargePeriodStart) | Present |
| CommitmentDiscountCategory | C | No (self-serve, no commitments) | N/A: null valid |
| CommitmentDiscountId | C | No | N/A: null valid |
| CommitmentDiscountName | C | No | N/A: null valid |
| CommitmentDiscountQuantity | C | No | N/A: null valid |
| CommitmentDiscountStatus | C | No | N/A: null valid |
| CommitmentDiscountType | C | No | N/A: null valid |
| CommitmentDiscountUnit | C | No | N/A: null valid |
| ConsumedQuantity | C | Yes (ConsumedQuantity) | Present |
| ConsumedUnit | C | Yes (ConsumedUnit) | Present |
| ContractedCost | M | Yes (ContractedCost) | Present |
| ContractedUnitPrice | C | No (derivable: cost / quantity) | Missing: Conditional |
| EffectiveCost | M | No (equals ContractedCost for self-serve) | Missing: Mandatory |
| InvoiceId | R | No | Missing: Recommended |
| InvoiceIssuerName | M | No (constant "Cloudflare") | Missing: Mandatory |
| ListCost | M | No (equals ContractedCost for self-serve) | Missing: Mandatory |
| ListUnitPrice | C | No (rate card, not on line) | Missing: Conditional |
| PricingCategory | C | No (constant "On-Demand") | Missing: Conditional |
| PricingCurrency | C | No (equals BillingCurrency) | Missing: Conditional |
| PricingCurrencyContractedUnitPrice | C | No | Missing: Conditional |
| PricingCurrencyEffectiveCost | C | No | Missing: Conditional |
| PricingCurrencyListUnitPrice | C | No | Missing: Conditional |
| PricingQuantity | M | Yes (PricingQuantity) | Present |
| PricingUnit | M | No (equals ConsumedUnit) | Missing: Mandatory |
| ProviderName | M (removed v1.4) | No (constant "Cloudflare") | Missing: Mandatory |
| PublisherName | M (removed v1.4) | No (constant "Cloudflare") | Missing: Mandatory |
| RegionId | C | No (global edge, not region-scoped) | N/A: null valid |
| RegionName | C | No | N/A: null valid |
| ResourceId | C | Partial (ZoneId where zone-attributed) | Present, deviation to fix |
| ResourceName | C | Partial (ZoneName where zone-attributed) | Present, deviation to fix |
| ResourceType | C | No (derivable, e.g. "Zone") | Missing: Conditional |
| ServiceCategory | M | Partial (ServiceFamilyName, not FOCUS enum) | Present, deviation to fix |
| ServiceName | M | Yes (ServiceName) | Present |
| ServiceSubcategory | R | No | Missing: Recommended |
| SkuId | C | No (ServiceName / rate-card SKU) | Missing: Conditional |
| SkuMeter | C | No (the billable metric) | Missing: Conditional |
| SkuPriceDetails | C | No | Missing: Conditional |
| SkuPriceId | C | No | Missing: Conditional |
| SubAccountId | C | No (single account, no rollup) | N/A: null valid |
| SubAccountName | C | No | N/A: null valid |
| SubAccountType | C | No | N/A: null valid |
| Tags | C | No (no native tags in the API) | Missing: Conditional |

Reading the tally: Of 57 v1.2 columns: 10 Present, 3 Present-with-deviation, 12 Missing Mandatory (all trivial: constants, derivations, or self-serve cost copies), 3 Missing Recommended, 14 Missing Conditional, and 15 N/A (commitments, capacity reservations, regions, sub-accounts, availability zone). The "already present" headline of 13 counts the 10 exact-match columns plus the 3 that carry the right data under a native name. Of the 21 Mandatory columns, 8 are present, 1 is a deviation (`ServiceCategory`), and 12 are missing but trivial.

### 1.4 What's solved, and what remains

Solved or near-solved: The payload uses FOCUS column IDs directly, so `ServiceName`, `ChargePeriodStart`, `ChargePeriodEnd`, `ConsumedQuantity`, `ConsumedUnit`, `PricingQuantity`, `ContractedCost`, `BillingCurrency`, and `BillingPeriodStart` need no renaming. Dates are ISO 8601, currency is an ISO code, and a real per-line cost is present. Daily charge periods come straight from `ChargePeriodStart` and `ChargePeriodEnd`. Zone identity is available where usage is zone-attributed.

Substantive gaps: At the column level there are none within the self-serve, usage-based scope. The `ListCost`, `BilledCost`, and `EffectiveCost` columns are absent, but for self-serve accounts they equal `ContractedCost`, because costs reflect the published rate card with no commitments, negotiated discounts, or amortization. Supplying them is a copy, not a reconciliation. The substantive limitations sit at the dataset scope level, not in any single column:

- Coverage of charge types: the API omits flat-rate plan charges, subscription and add-on base fees, and tax. A full FOCUS dataset for a Cloudflare account needs those non-usage charges (`ChargeCategory` values Purchase and Tax), which this feed does not carry.
- Enterprise contracts: out of scope today. When they arrive, `ContractedCost` will diverge from `ListCost`, and `EffectiveCost` will require commitment amortization, turning the cost quartet into a genuine reconciliation.
- Multi-account and sub-account rollup: absent, so organization-level allocation is not possible from the API alone.

Trivial gaps (plumbing, derivable from data already present):

- Constants: `InvoiceIssuerName`, `ProviderName`, `PublisherName` are "Cloudflare"; `ChargeCategory` is "Usage" for this feed; `ChargeClass` is null (no corrections in the payload); `PricingCategory` is "On-Demand".
- Derivations: `ChargeDescription` from `ServiceName`; `BillingAccountName` from an account lookup; `BillingPeriodEnd` from the billing cycle (`BillingPeriodStart` is present); `PricingUnit` equals `ConsumedUnit`.
- Cost copies: `ListCost` = `BilledCost` = `EffectiveCost` = `ContractedCost` for self-serve, flat-rate SKUs. Tiered products already expose both `ConsumedQuantity` and `PricingQuantity`, so the pricing basis is available.

### 1.5 Deviations to fix

- ServiceCategory: `ServiceFamilyName` is a Cloudflare-native grouping ("Workers", "R2"), not a member of the FOCUS `ServiceCategory` controlled vocabulary. Map it to a valid enum value (for example, "Compute", "Storage", "AI and Machine Learning").
- ResourceId and ResourceName: `ZoneId` and `ZoneName` carry the right identity where usage is zone-attributed. Emit them under the FOCUS column IDs, and null them where usage is not zone-scoped.
- Cumulative convenience fields: `CumulatedContractedCost` and `CumulatedPricingQuantity` are running totals. FOCUS treats cumulation as a query concern, so keep these as provider-specific columns prefixed `x_` rather than mapping them to FOCUS columns.

Already done right: FOCUS column names on the emitted fields, ISO 8601 date-times, an explicit ISO currency code, a real per-line cost, and daily charge periods.

## Part 2: The path forward

### 2.1 Which FOCUS version to target

Baseline the current certification version, v1.2, for any conformance conversation, and build toward v1.4 (ratified 2026-06-04). Cloudflare is already aligned with one v1.4 change: it does not emit `ProviderName` or `PublisherName`, which v1.4 removes. Building to v1.4 also means adopting the Invoice Detail and billing-period datasets, which suit Cloudflare's monthly invoice and the eventual flat-rate and tax coverage. A practical path shapes the transformation against v1.2 semantics, then layers the v1.3 and v1.4 additions.

### 2.2 What certification requires

FinOps Certified FOCUS conformance for data generators runs through the FinOps Foundation. The historical badge is "FinOps Certified FOCUS v1.2 Conformant"; confirm the current badge version on the program page. Contact `member-cert@finops.org` for the RFI. Membership is required for certification, though contributing to the spec is open and free. Deliverables are a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report, which this analysis seeds. Open-source tooling includes the FOCUS Validator (checks data against the Requirements Model), the FOCUS Converter (provider-native to FOCUS), and the FOCUS Requirements Model (machine-readable MUST, SHOULD, and MAY rules).

### 2.3 Phased roadmap

- Phase 0 (validate and scope): Run a sample billable-usage payload through the FOCUS Validator against v1.2 to establish a baseline. Confirm the v1.2 baseline and v1.4 build target, and confirm the scope reviewed (self-serve, usage-based, per-account).
- Phase 1 (Mandatory gaps, value-unlock): Add the trivial Mandatory columns: constants (`InvoiceIssuerName`, `ProviderName`, `PublisherName`, `ChargeCategory` = "Usage", `ChargeClass` = null), derivations (`ChargeDescription`, `BillingAccountName`, `BillingPeriodEnd`, `PricingUnit` = `ConsumedUnit`), and the self-serve cost copies (`ListCost` = `BilledCost` = `EffectiveCost` = `ContractedCost`).
- Phase 2 (deviations): Map `ServiceFamilyName` to the FOCUS `ServiceCategory` enum, emit `ZoneId` and `ZoneName` as `ResourceId` and `ResourceName`, and prefix the cumulative convenience fields as `x_`.
- Phase 3 (Conditional and Recommended): Add unit prices (`ContractedUnitPrice`, `ListUnitPrice`), `PricingCategory`, the SKU family (`SkuId`, `SkuMeter`, `SkuPriceDetails`, `SkuPriceId`), `ResourceType`, the pricing-currency columns, and Recommended `ChargeFrequency`, `InvoiceId`, and `ServiceSubcategory`. `Tags` needs a native tagging mechanism to populate.
- Phase 4 (extend scope, mature, and certify): Cover flat-rate plan and add-on charges and tax (`ChargeCategory` Purchase and Tax), add organization and sub-account rollups, and support Enterprise contracts, where `ContractedCost` diverges from `ListCost` and `EffectiveCost` needs commitment amortization, the real reconciliation. Adopt v1.3 and v1.4, drop `ProviderName` and `PublisherName`, wire in the Invoice Detail dataset, and pursue certification.

### 2.4 FOCUS Use Cases unlocked

- Unlocked now (FOCUS-named daily rows with per-line cost): per-account usage-based cost reporting and showback, product-level spend analysis, day-level trend and anomaly detection, and budget tracking (already surfaced through budget alerts and the Vantage integration).
- Unlocked with the cost columns filled (Phase 1): effective-cost views, since for self-serve the cost quartet coincides, and usage-versus-cost reconciliation for the usage-based portion of the bill.
- Unlocked with resource identity and tags (Phases 2 to 3): zone-level cost allocation, and tag-based chargeback and showback once a native tagging mechanism exists.
- Out of scope for now: commitment and capacity-reservation use cases (self-serve has none); organization and multi-account rollups; flat-rate and tax reconciliation; and Enterprise contract amortization.

## Part 3: Immediate next steps

1. Run a sample billable-usage payload through the FOCUS Validator against v1.2 and record the baseline.
2. Add the trivial Mandatory constants and derivations, and emit the self-serve cost copies (`ListCost`, `BilledCost`, `EffectiveCost` = `ContractedCost`).
3. Map `ServiceFamilyName` to the FOCUS `ServiceCategory` vocabulary and emit `ZoneId` and `ZoneName` as `ResourceId` and `ResourceName`.
4. Plan the scope extensions (flat-rate charges, tax, sub-accounts, Enterprise) where the cost columns become a genuine reconciliation.
5. Engage the FinOps Foundation conformance program and request the RFI.

## Confidence summary

- Data source structure (endpoint, envelope, fields, daily grain): high confidence, from the 2026-08-03 Cloudflare announcement of the Billable Usage API, which includes an example payload and an explicit Cloudflare-to-FOCUS mapping table, plus the current Cloudflare billing documentation.
- Feature-level classifications: high confidence. Levels were checked against the FOCUS v1.2 content-constraint reference; the bundled table was cache-validated on 2026-08-03 against the live spec index, confirming v1.2 exists as the certification baseline and v1.4 (2026-06-04) is the latest ratified version, consistent with the sibling reports, with no refresh needed.
- Cost columns trivial rather than substantive: high confidence for self-serve. Cloudflare states self-serve costs reflect the published rate card with no commitments or negotiated discounts, so `ListCost` = `BilledCost` = `EffectiveCost` = `ContractedCost`. Moderate caveat: any account-level credits or promotions would make `EffectiveCost` diverge, and Enterprise contracts (out of scope of this API) make the quartet a genuine reconciliation.
- Scope limitations: high confidence. The API is self-serve only, usage-based only, per-account, carries no tags, and offers zone-level resource identity, per the announcement and docs.
- Field-presence provisional: moderate confidence. The exact full field list of the API reference was inferred from the announcement's example payload and mapping table. Whether `BillingPeriodEnd`, `PricingUnit`, and `BillingAccountId`/`BillingAccountName` appear as row fields versus query context should be confirmed against the full published API reference.
- Overall readiness band (Structured): moderate-to-high confidence. Cloudflare has a FOCUS-native shape, daily granularity, and a real per-line cost, but coverage is roughly one-third of applicable columns, allocation is weak (no tags, no sub-accounts, partial zone identity), and the feed is scoped to the usage-based, self-serve slice.
- Certification status: Cloudflare is not on the FOCUS provider "get started" page and holds no FinOps Certified FOCUS designation; this report assesses readiness only and is not a certification result.

## Sources

- Cloudflare, "Introducing the Billable Usage API," blog.cloudflare.com/billable-usage-api/ (2026-08-03).
- Cloudflare Docs, Monitor billable usage, developers.cloudflare.com/billing/manage/billable-usage/.
- Cloudflare Docs, How Cloudflare billing works, developers.cloudflare.com/billing/understand/how-billing-works/.
- Cloudflare Docs, Usage-based billing, developers.cloudflare.com/billing/understand/usage-based-billing/.
- FOCUS Specification, focus.finops.org/focus-specification/, and the FOCUS Validator, FOCUS Converter, and FOCUS Requirements Model tooling.

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
