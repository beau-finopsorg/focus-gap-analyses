# Sakura Internet and FOCUS: Compliance Gap and Adoption Roadmap

*Analysis run: July 1, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

Prepared: 2026-07-01
Provider and product in scope: Sakura Internet (SAKURA internet Inc.), Sakura Cloud IaaS and the Koukaryoku GPU cloud (PHY bare metal, DOK containers, VRT VMs).
Source analyzed: Sakura Cloud API v1.1 billing endpoints (`/bill/by-contract`, `/bill/id`, `/billdetail`, `/coupon`) and the public pricing and payment documentation.
FOCUS baseline: v1.2 (current certification baseline). Build target: v1.4 (latest, ratified 2026-06-04).
Currency: JPY. The billing API reports amounts in Japanese yen with no explicit currency field.

This assessment uses the FinOps Open Cost and Usage Specification (FOCUS). Feature levels were verified against the live FOCUS spec via the FOCUS MCP server on 2026-07-01; the bundled v1.2 table (57 columns) matched, and v1.4 was confirmed as the latest ratified version with Provider and Publisher removed.

## Executive summary

Sakura Cloud exposes a genuine, authenticated billing API, which puts it ahead of providers that offer only a PDF invoice or a portal screen. The data it returns, however, is a monthly financial statement, not a usage-level cost and usage dataset. A FOCUS dataset is built from charge records that each carry a time period, a service, a resource, a quantity, and a set of cost measures. The Sakura billing feed instead returns one summary row per invoice and a flat list of detail lines keyed to an internal service class code and a contract ID, with a usage figure in seconds and a single post-discount amount in yen.

The result is a wide substantive gap rather than a shaping problem. Of the 21 Mandatory v1.2 columns, most are either absent from the source or present only in a degraded form. The cost columns are the central issue: the API returns one amount per line that already nets coupons and discount-passport adjustments, so List, Billed, Effective, and Contracted cost cannot be separated from what is emitted today. This is a substantive reconciliation gap, not a trivial copy.

What Sakura already has going for it is real: a machine-readable API, per-line service and zone identifiers, a usage quantity, an explicit discount and coupon mechanism that a FOCUS mapping can model, and stable contract and member identifiers that map cleanly to account fields. The path to conformance runs through re-shaping billing output into per-resource, sub-monthly charge records with separated cost measures, not through inventing a data platform from scratch.

Recommendation: treat this as a data-model project, not a relabeling exercise. Target a usage-level charge record with resource identity and separated cost measures, baseline FOCUS v1.2 for certification, and build toward v1.4.

## Part 1: The conformance gap

### 1.1 The data source

Sakura Cloud offers a REST API (v1.1, JSON, ISO 8601 timestamps, HTTPS, Basic or Digest auth with an API key and secret). Billing lives on a dedicated set of endpoints under a `system/1.0` path that is zone-neutral: it aggregates across all zones and returns one unified response.

The billing surface has four relevant shapes:

- Bill list (`GET /bill/by-contract/:accountid`, optionally by year and month): returns `Bills`, each with `Amount` (integer yen), `BillID`, `Date`, `MemberID`, `Paid`, `PayLimit`, and `PaymentClassID`. This is an invoice-level summary, one row per monthly bill.
- Bill by number (`GET /bill/id/:billno`): the same invoice-summary shape for a single bill.
- Bill detail (`GET /billdetail/:membercd/:billno`, also available as CSV): returns `BillDetails`, each with `Amount` (yen), `ContractID`, `Index`, `ServiceClassID`, `Usage`, and `Zone`. A detail line can carry a nested `Details` array that itemizes discounts (for example a discount-passport reduction), including negative-amount lines.
- Coupons (`GET /coupon/:accountid`): returns applied coupons with `Discount` (remaining balance), `ServiceClassID`, `AppliedAt`, and `UntilAt`.

Key characteristics and limitations for FOCUS purposes:

- Granularity: monthly. The unit of record is a monthly invoice, decomposed into detail lines. There is no daily or hourly charge record, and no charge-period start and end on a line. `Usage` is a cumulative count (seconds in the examples) for the billing month.
- Cost shape: one `Amount` per line, already net of coupons and discount-passport adjustments. List price and effective (amortized) cost are not separate fields. Discounts appear as nested negative lines rather than as per-line rate measures.
- Resource identity: none in the billing feed. Lines are keyed to `ServiceClassID` (an internal service or SKU code) and `ContractID`. There is no resource ID, resource name, or resource type on a billing line. Resource identity exists elsewhere in the API (server, disk, and other resource endpoints) but is not joined to billing.
- Tags: not present in the billing feed.
- Currency: JPY, carried implicitly. No ISO 4217 currency field is emitted.
- Accounts: `MemberID` (member or contract holder) and `ContractID` and `accountid` (project) provide a two-level account structure. There is no separate billing-account-versus-sub-account typing.
- Regions and zones: `Zone` values (is1a, is1b, is1c for Ishikari; tk1a, tk1b for Tokyo; tk1v Sandbox) identify the zone per line, which maps to region and availability-zone concepts.

The Koukaryoku GPU services (PHY bare metal, DOK containers with per-second billing from about 0.06 yen per second, and VRT VMs) bill through the same backend, so they inherit the same billing-data shape. Per-second GPU billing is a usage strength at the metering layer, but it still surfaces through the monthly detail feed as a summed `Usage` and a single `Amount`.

### 1.2 How conformance is judged

FOCUS defines a fixed set of columns, each carrying a feature level: Mandatory, Conditional, Recommended, or Optional. Conformance is judged column by column against the Requirements Model, which encodes the normative MUST, SHOULD, and MAY rules. A dataset conforms when every Mandatory column is present and correctly populated, every Conditional column that the provider's business model triggers is present, and values obey the allowed formats and enumerations.

Feature levels differ across spec versions, so this analysis takes each level from the verified FOCUS reference rather than from memory. v1.2 has 57 columns: 21 Mandatory, 32 Conditional, and 4 Recommended (AvailabilityZone, ChargeFrequency, InvoiceId, ServiceSubcategory).

### 1.3 Column-by-column status

Status legend:
- Present: emitted and aligned.
- Present, deviation to fix: emitted, but wrong format or invalid value.
- Missing: Mandatory: required and absent, blocks conformance.
- Missing: Recommended: encouraged, absent, does not block conformance.
- Missing: Conditional: required when the model triggers the condition, absent and the condition applies.
- N/A: null valid: Conditional or Recommended column that does not apply to this model, should exist and be null.

Feature levels verified against the FOCUS Specification v1.2.

| FOCUS Column | Level | In the source? | Status |
|---|---|---|---|
| AvailabilityZone | R | Zone (is1a, is1b, ...) | Present, deviation to fix |
| BilledCost | M | Amount (net, per line) | Present, deviation to fix |
| BillingAccountId | M | MemberID / ContractID | Present, deviation to fix |
| BillingAccountName | M | No | Missing: Mandatory |
| BillingAccountType | C | No | Missing: Conditional |
| BillingCurrency | M | Implicit JPY, no field | Missing: Mandatory |
| BillingPeriodEnd | M | Derivable from Date | Missing: Mandatory |
| BillingPeriodStart | M | Derivable from Date | Missing: Mandatory |
| CapacityReservationId | C | No | N/A: null valid |
| CapacityReservationStatus | C | No | N/A: null valid |
| ChargeCategory | M | No | Missing: Mandatory |
| ChargeClass | M | Negative discount lines | Present, deviation to fix |
| ChargeDescription | M | No (ServiceClassID only) | Missing: Mandatory |
| ChargeFrequency | R | No | Missing: Recommended |
| ChargePeriodEnd | M | No (monthly only) | Missing: Mandatory |
| ChargePeriodStart | M | No (monthly only) | Missing: Mandatory |
| CommitmentDiscountCategory | C | No | N/A: null valid |
| CommitmentDiscountId | C | No | N/A: null valid |
| CommitmentDiscountName | C | No | N/A: null valid |
| CommitmentDiscountQuantity | C | No | N/A: null valid |
| CommitmentDiscountStatus | C | No | N/A: null valid |
| CommitmentDiscountType | C | No | N/A: null valid |
| CommitmentDiscountUnit | C | No | N/A: null valid |
| ConsumedQuantity | C | Usage (seconds) | Present, deviation to fix |
| ConsumedUnit | C | Implicit (seconds) | Missing: Conditional |
| ContractedCost | M | No (netted into Amount) | Missing: Mandatory |
| ContractedUnitPrice | C | No | Missing: Conditional |
| EffectiveCost | M | No (netted into Amount) | Missing: Mandatory |
| InvoiceId | R | BillID | Present |
| InvoiceIssuerName | M | No (constant "SAKURA internet") | Missing: Mandatory |
| ListCost | M | No (netted into Amount) | Missing: Mandatory |
| ListUnitPrice | C | No | Missing: Conditional |
| PricingCategory | C | No | Missing: Conditional |
| PricingCurrency | C | Implicit JPY | Missing: Conditional |
| PricingCurrencyContractedUnitPrice | C | No | Missing: Conditional |
| PricingCurrencyEffectiveCost | C | No | Missing: Conditional |
| PricingCurrencyListUnitPrice | C | No | Missing: Conditional |
| PricingQuantity | M | No (derivable, tiered) | Missing: Mandatory |
| PricingUnit | M | No | Missing: Mandatory |
| ProviderName | M | No (constant "Sakura Internet") | Missing: Mandatory |
| PublisherName | M | No (constant "Sakura Internet") | Missing: Mandatory |
| RegionId | C | Zone prefix (is1, tk1) | Present, deviation to fix |
| RegionName | C | No | Missing: Conditional |
| ResourceId | C | No | Missing: Conditional |
| ResourceName | C | No | Missing: Conditional |
| ResourceType | C | No (ServiceClassID proxy) | Missing: Conditional |
| ServiceCategory | M | No (mappable from ServiceClassID) | Missing: Mandatory |
| ServiceName | M | No (ServiceClassID code only) | Missing: Mandatory |
| ServiceSubcategory | R | No | Missing: Recommended |
| SkuId | C | ServiceClassID | Present, deviation to fix |
| SkuMeter | C | No | Missing: Conditional |
| SkuPriceDetails | C | No | Missing: Conditional |
| SkuPriceId | C | No | Missing: Conditional |
| SubAccountId | C | ContractID (project) | Present, deviation to fix |
| SubAccountName | C | No | Missing: Conditional |
| SubAccountType | C | No | Missing: Conditional |
| Tags | C | No | Missing: Conditional |

Reading the tally: of 57 v1.2 columns, 9 are present in some form (7 of them with deviations, 2 clean or near-clean), 13 are Missing: Mandatory, 2 are Missing: Recommended, 24 are Missing: Conditional (condition applies), and 7 are N/A: null valid (commitment-discount and capacity-reservation families, which Sakura's pay-as-you-go model does not use). The 21 Mandatory columns break down as 4 present-with-deviation and 13 missing plus the two soon-to-be-removed Provider and Publisher, which are trivial constants.

### 1.4 What is solved, and what remains

Substantive gaps (real data that does not exist in the billing feed today):

- Separated cost measures (ListCost, EffectiveCost, ContractedCost): the API returns one `Amount` per line that is already net of coupon and discount-passport adjustments. List price is not carried, and amortization does not apply because there are no commitments, but reconstructing List versus Billed versus Effective requires joining the pre-discount rate (from the product or pricing API) to the netted line and modeling the discount lines explicitly. This is the reconciliation gap, and it is the single largest piece of work.
- Sub-monthly charge records (ChargePeriodStart, ChargePeriodEnd): the feed is monthly. Producing charge-level records means emitting per-resource, per-day (or finer) rows from the metering layer that already exists for per-second GPU billing, rather than the monthly rollup.
- Resource identity (ResourceId, ResourceName, ResourceType): billing lines carry no resource reference. Joining billing to the resource endpoints (server, disk, GPU task) is a data-pipeline build.
- Service semantics (ServiceName, ServiceCategory): lines carry only `ServiceClassID`, an internal code. A lookup table from service class to a FOCUS service name and one of the allowed ServiceCategory values must be built and maintained.
- ChargeDescription: no human-readable description is emitted per line.

Trivial gaps (derivable or constant, plumbing rather than data):

- ProviderName and PublisherName: constants ("Sakura Internet"). Both are removed in v1.4, so they matter only for a v1.2 certification snapshot.
- InvoiceIssuerName: constant ("SAKURA internet Inc.").
- BillingCurrency and PricingCurrency: constant "JPY" (ISO 4217), currently implicit.
- BillingPeriodStart and BillingPeriodEnd: derivable from the invoice `Date` and the monthly cycle.
- BillingAccountName: derivable from the member or contract record.
- ChargeCategory: derivable by rule (Usage for consumption lines, Credit or Adjustment for discount and coupon lines).
- ChargeClass: null for normal lines, set only for corrections.
- BilledCost: the netted `Amount` already is billed cost; the trivial part is naming and typing it, while separating the other cost measures from it is the substantive part above.
- PricingQuantity and PricingUnit: derivable from `Usage` for flat-rate, per-second SKUs (copy the consumed quantity and set the unit). For any tiered or bundled SKU, PricingQuantity must be computed against the rate basis rather than copied, so treat those SKUs as computation, not a copy.

### 1.5 Deviations to fix

These columns carry the right idea in the wrong shape:

- BilledCost: `Amount` is an integer yen value that already nets discounts. Retype as a decimal cost measure and pair it with the separated List, Effective, and Contracted measures.
- BillingAccountId: `MemberID` (or `ContractID`) works as the identifier, but a FOCUS dataset needs a consistent choice of billing-account identifier plus the sub-account split described below.
- ChargeClass: negative discount lines in the nested `Details` array express corrections and reductions, but not in the FOCUS shape. Model discounts as their own charge rows with the correct ChargeCategory and ChargeClass rather than as nested negatives.
- ConsumedQuantity: `Usage` is present (seconds) but needs an explicit ConsumedUnit and correct typing.
- AvailabilityZone and RegionId: `Zone` maps to availability zone; the region is derivable from the zone prefix (is1, tk1) but is not emitted as its own field.
- SkuId: `ServiceClassID` is a usable SKU identifier, but it needs a companion ServiceName and ServiceCategory lookup to be meaningful.
- SubAccountId: `ContractID` or the project ID works as a sub-account identifier once the billing-account-versus-sub-account model is defined.

What is already done right: an authenticated, documented REST API; ISO 8601 timestamps; per-line zone and service-class identifiers; a usage quantity; an explicit, itemized discount and coupon mechanism; and stable member, contract, and project identifiers. These are good raw materials.

## Part 2: The path forward

### 2.1 Which FOCUS version to target

Baseline v1.2 for certification, since the FinOps Certified FOCUS program has been anchored to v1.2. Build toward v1.4, the latest ratified version (2026-06-04), which removes Provider and Publisher (so the two trivial constants above disappear) and adds Invoice Detail and billing-period datasets that suit a provider whose native data is invoice-centric. Because the substantive work (per-resource charge records with separated cost measures) is version-independent, design for v1.4 shapes while validating against v1.2 for the badge.

### 2.2 What certification requires

FOCUS conformance for data generators runs through the FinOps Foundation. The current badge has been "FinOps Certified FOCUS v1.2 Conformant"; confirm the active badge version against the program page before finalizing. The deliverables are a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report (this analysis is its seed). Membership is required for certification, though contributing to the spec is open and free. Contact member-cert@finops.org for the RFI.

Open-source tooling to use along the way: the FOCUS Validator (checks data against the Requirements Model), the FOCUS Converter (provider-native to FOCUS), and the FOCUS Requirements Model (machine-readable MUST, SHOULD, MAY rules).

### 2.3 Phased roadmap

Phase 0: validate and scope. Confirm the target version and badge, and run a small hand-built sample of Sakura billing lines through the FOCUS Validator to see which rules fire. Decide the billing-account-versus-sub-account model (member as billing account, contract or project as sub-account is the natural mapping).

Phase 1: build the charge record and close the substantive Mandatory gaps. Emit per-resource, sub-monthly charge records from the metering layer that already supports per-second billing, joined to resource identity from the server, disk, and GPU-task endpoints. Separate the cost measures: carry ListCost from the pre-discount rate, keep BilledCost as the netted amount, derive EffectiveCost, and set ContractedCost. Add the trivial constants and derived fields (ProviderName, PublisherName, InvoiceIssuerName, BillingCurrency, BillingPeriodStart and End, ChargeCategory, ChargeClass, PricingQuantity and PricingUnit for flat-rate SKUs).

Phase 2: fix deviations. Model discounts and coupons as first-class charge rows with correct ChargeCategory (Credit or Adjustment) and ChargeClass rather than nested negatives. Add the ServiceClassID-to-ServiceName-and-ServiceCategory lookup and per-line ChargeDescription. Emit RegionId and RegionName from the zone.

Phase 3: round out applicable Conditional and Recommended columns. Add Tags (once resource tagging is exposed in billing), SubAccountName and Type, PricingCategory, unit-price and pricing-currency columns, SKU meter and price details, ConsumedUnit, ServiceSubcategory, and ChargeFrequency.

Phase 4: mature to v1.4. Drop Provider and Publisher, adopt the Invoice Detail and billing-period datasets, and pursue certification or re-certification.

### 2.4 FOCUS Use Cases unlocked

Unlocked once Phase 1 delivers per-resource, sub-monthly charge records with service and resource identity:

- Cost allocation by service, zone, and project or contract.
- Usage and spend trend reporting at daily granularity.
- Anomaly detection on charge records.

Unlocked once Phase 1 and 2 separate the cost measures and model discounts:

- Effective-cost and discount reporting (how much coupons and discount passports actually saved).
- Invoice reconciliation (charge records reconciling to the monthly bill).
- Actuals-based budgeting and showback.

Out of scope for Sakura's current model: commitment-discount use cases (rate and usage commitments, coverage, utilization) and capacity-reservation use cases, because the pay-as-you-go and coupon or discount-passport model does not use those mechanics. The corresponding FOCUS columns stay present and null.

## Part 3: Immediate next steps

1. Confirm the certification badge version and target build version with the FinOps Foundation, and decide the billing-account-versus-sub-account mapping (member, contract, project).
2. Hand-build a small FOCUS v1.2 sample from a real `billdetail` response plus the matching resource and pricing lookups, and run it through the FOCUS Validator to ground the gap list in actual rule failures.
3. Scope the Phase 1 pipeline: joining metering-layer usage to resource identity and to pre-discount rates, which is the work that unlocks most of the conformance value.
4. Build and version the ServiceClassID-to-ServiceName-and-ServiceCategory lookup table.
5. Model discounts and coupons as first-class FOCUS charge rows.

## Confidence summary

- The Sakura Cloud billing API shape (endpoints, fields, monthly granularity, nested discount details, coupon endpoint, JPY, zones): high confidence. Taken directly from the official v1.1 API documentation, including sample response bodies.
- The absence of resource identity, tags, separated cost measures, and charge-period fields in the billing feed: high confidence, based on the documented response schemas.
- FOCUS feature levels and the 57-column v1.2 set, plus v1.4 status and the Provider and Publisher removal: high confidence. Verified against the live FOCUS spec via the FOCUS MCP server on 2026-07-01; the bundled table matched.
- The mapping of ServiceClassID to a stable ServiceName and ServiceCategory, and the exact separation of List versus Billed versus Effective for discounted lines: moderate confidence. These depend on internal pricing tables not visible in the public API and should be confirmed against Sakura's product and pricing data before implementation.
- Koukaryoku GPU billing flowing through the same monthly detail backend: moderate confidence. Consistent with the shared billing endpoints and per-second metering, but confirm against a real GPU invoice.
- Whether the FOCUS Validator supports v1.4 today: pending. Validator support for v1.4 was expected later in Q3 2026; confirm before planning a v1.4 validation run, and use v1.3 or v1.2 validation in the interim.

## Sources

- Sakura Cloud API v1.1, billing-related API: https://manual.sakura.ad.jp/cloud-api/1.1/bill/index.html
- Sakura Cloud API v1.1, introduction and conventions (REST, JSON, ISO 8601, auth): https://manual.sakura.ad.jp/cloud-api/1.1/index.html
- Sakura Cloud API portal and product page: https://manual.sakura.ad.jp/api/cloud/portal/ and https://cloud.sakura.ad.jp/products/api/
- Sakura Cloud pricing and payment: https://cloud.sakura.ad.jp/payment/ and https://manual.sakura.ad.jp/cloud/manual-payment.html
- Koukaryoku GPU cloud (PHY, DOK, VRT): SAKURA internet corporate releases and Supermicro case study.
- FOCUS Specification v1.2 and v1.4, verified via the FOCUS MCP server on 2026-07-01: https://focus.finops.org/focus-specification/

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
