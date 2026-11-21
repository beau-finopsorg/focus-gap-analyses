# Fluidstack and FOCUS: Compliance Gap and Adoption Roadmap

*Analysis run: June 30, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Provider and product in scope:** Fluidstack (GPU cloud for AI training and inference), organization and project billing model.
**Prepared:** 2026-06-30
**Source analyzed:** Fluidstack public documentation (Management API v1alpha1, Projects/Organizations model, dashboard and API-key docs), Fluidstack pricing and legal pages, and third-party pricing aggregators. No native cost or usage export or billing API was found in the public documentation.
**FOCUS baseline:** v1.2 (current certification baseline). **Build target:** v1.4 (latest ratified, 2026-06-04).

---

## Executive summary

Fluidstack today exposes no documented machine-readable cost or usage dataset. The public Management API covers infrastructure (regions, clusters, organizations, members, instances, SSH keys) but has no billing, usage, or cost-export endpoint. Billing is run on a monthly cycle through Stripe, with service credits handled manually and reserved-cluster commitments negotiated per order. Against FOCUS, this means the conformance question is not "how close is the export," it is "there is no export yet." The verdict is therefore a build, not a remediation.

That said, the underlying account and resource model is a reasonable foundation. Organizations are an explicit billing entity, projects give a natural sub-account boundary, instances carry stable UUIDs and key-value tags, and regions are named. A flat per-hour or per-second rate card with no egress fees keeps the cost columns unusually simple to populate once a usage feed exists.

- **Total FOCUS columns (v1.2):** 57
- **Already present in a FOCUS-shaped cost dataset:** 0 (no cost dataset exists)
- **Substantive Mandatory gaps:** 2 of 21 (the cost and reconciliation work; see Part 1.4)
- **Deviations to fix on existing fields:** 0 (nothing is emitted in FOCUS shape yet)

**Readiness:** Cost Gap, Granularity Gap, Allocation Partial, Coverage Gap, FOCUS shape Gap. Overall band: **Not yet aligned (per public docs)**.

**Recommendation:** Treat this as a green-field FOCUS build. Stand up a usage feed at instance-and-day granularity keyed on organization, project, and instance UUID, then layer the cost columns on top. Because the rate card is flat and there are no egress fees, the cost columns are mostly a clean derivation once usage records exist. Engage `member-cert@finops.org` only after a first dataset can pass the FOCUS Validator.

---

## Part 1: The conformance gap

Fluidstack has a clean infrastructure model and a simple commercial model. What it lacks is any cost or usage data product to map to FOCUS. This section establishes what exists, how conformance is judged, classifies all 57 columns, and separates the real build from the plumbing.

### 1.1 The data source

What Fluidstack exposes today, from public documentation:

- **Management API (v1alpha1):** RESTful endpoints for regions, clusters, organizations, members, invitations, instances, and SSH keys. The instance object carries `id` (UUID), `name`, `type`, `state`, `ip`, `image`, `preemptible`, `ephemeral`, `tags` (key-value map), `project_id`, `region`, `health`, and `updated_at`. There is no usage, metering, or cost field on any object.
- **Account model:** Organizations group users for authorization and billing. Projects sit under organizations and provide logical and network isolation, commonly one per team. This gives a clean billing-account (organization) and sub-account (project) hierarchy.
- **Pricing model:** Per-hour rates with per-second billing on-demand (for example, H100 around 2.10 USD/hr, A100 around 1.30 USD/hr, H200 around 2.30 USD/hr), reserved clusters at a discount for commitments of 30 days or more, and fully custom private-cloud deals (B200, GB200) negotiated per order. No egress or ingress fees. On-node NVMe storage and support are included in the rate.
- **Billing operations:** Monthly billing cycle, card payments processed by Stripe. Service credits are reconciled manually in the billing cycle following customer notification. Currency is presumed USD (to confirm).

Key limitations for FOCUS:

- **No cost or usage dataset:** There is no billing API, no usage export, and no documented cost CSV or data feed. Every FOCUS column must be produced from scratch.
- **No metering record:** Instances expose state and an `updated_at` timestamp, but no documented per-period consumption record (hours run, start/stop events) is published through the API.
- **Granularity unknown:** Without a usage feed, charge-period granularity is undefined. The per-second billing basis suggests sub-hourly metering exists internally, but it is not exposed.

### 1.2 How conformance is judged

FOCUS assigns every column a feature level: Mandatory, Conditional, Recommended, or Optional. Conformance is judged column by column against the Requirements Model. A conformant dataset must populate all Mandatory columns, must populate Conditional columns when the provider's model triggers the condition, and should populate Recommended columns. Feature levels for this report were verified against the FOCUS v1.2 specification column set (57 columns) via the FOCUS column library, not from memory.

### 1.3 Column-by-column status

Every column is classified for the v1.2 baseline. Because Fluidstack publishes no cost dataset, no column is currently Present. Classifications below describe the target state once a dataset is built: which columns become Mandatory work, which apply Conditionally given the GPU-cloud model, and which are legitimately null.

Status legend: Present (emitted and aligned); Present, deviation (wrong format or value); Missing: Mandatory (required, absent, blocks conformance); Missing: Recommended (encouraged, absent); Missing: Conditional (required when the model triggers it, absent); N/A: null valid (does not apply to this model, should exist and be null).

Feature levels verified against the FOCUS Specification v1.2.

| FOCUS Column | Level | In the source? | Status |
|---|---|---|---|
| AvailabilityZone | Recommended | No (regions only, no zones) | N/A: null valid |
| BilledCost | Mandatory | No (no cost dataset) | Missing: Mandatory |
| BillingAccountId | Mandatory | Organization id (not in a cost feed) | Missing: Mandatory |
| BillingAccountName | Mandatory | Organization name (not in a cost feed) | Missing: Mandatory |
| BillingAccountType | Conditional | No | Missing: Conditional |
| BillingCurrency | Mandatory | No (USD presumed) | Missing: Mandatory |
| BillingPeriodEnd | Mandatory | No | Missing: Mandatory |
| BillingPeriodStart | Mandatory | No | Missing: Mandatory |
| CapacityReservationId | Conditional | No | Missing: Conditional |
| CapacityReservationStatus | Conditional | No | Missing: Conditional |
| ChargeCategory | Mandatory | No | Missing: Mandatory |
| ChargeClass | Mandatory (nullable) | No | Missing: Mandatory |
| ChargeDescription | Mandatory | No | Missing: Mandatory |
| ChargeFrequency | Recommended | No | Missing: Recommended |
| ChargePeriodEnd | Mandatory | No | Missing: Mandatory |
| ChargePeriodStart | Mandatory | No | Missing: Mandatory |
| CommitmentDiscountCategory | Conditional | No (reserved clusters exist) | Missing: Conditional |
| CommitmentDiscountId | Conditional | No (reserved clusters exist) | Missing: Conditional |
| CommitmentDiscountName | Conditional | No (reserved clusters exist) | Missing: Conditional |
| CommitmentDiscountQuantity | Conditional | No (reserved clusters exist) | Missing: Conditional |
| CommitmentDiscountStatus | Conditional | No (reserved clusters exist) | Missing: Conditional |
| CommitmentDiscountType | Conditional | No (reserved clusters exist) | Missing: Conditional |
| CommitmentDiscountUnit | Conditional | No (reserved clusters exist) | Missing: Conditional |
| ConsumedQuantity | Conditional | No (per-second metering exists internally) | Missing: Conditional |
| ConsumedUnit | Conditional | No | Missing: Conditional |
| ContractedCost | Mandatory | No (no cost dataset) | Missing: Mandatory |
| ContractedUnitPrice | Conditional | No (rate card exists) | Missing: Conditional |
| EffectiveCost | Mandatory | No (no cost dataset) | Missing: Mandatory |
| InvoiceId | Recommended | No (invoices exist via Stripe) | Missing: Recommended |
| InvoiceIssuerName | Mandatory | No (constant: Fluidstack) | Missing: Mandatory |
| ListCost | Mandatory | No (rate card exists) | Missing: Mandatory |
| ListUnitPrice | Conditional | No (rate card exists) | Missing: Conditional |
| PricingCategory | Conditional | No (On-Demand / Committed apply) | Missing: Conditional |
| PricingCurrency | Conditional | No | Missing: Conditional |
| PricingCurrencyContractedUnitPrice | Conditional | No | Missing: Conditional |
| PricingCurrencyEffectiveCost | Conditional | No | Missing: Conditional |
| PricingCurrencyListUnitPrice | Conditional | No | Missing: Conditional |
| PricingQuantity | Mandatory (nullable) | No (derivable for flat-rate SKUs) | Missing: Mandatory |
| PricingUnit | Mandatory (nullable) | No (GPU-hour) | Missing: Mandatory |
| ProviderName | Mandatory | No (constant: Fluidstack) | Missing: Mandatory |
| PublisherName | Mandatory | No (constant: Fluidstack) | Missing: Mandatory |
| RegionId | Conditional | Region slug (not in a cost feed) | Missing: Conditional |
| RegionName | Conditional | Region name (not in a cost feed) | Missing: Conditional |
| ResourceId | Conditional | Instance UUID (not in a cost feed) | Missing: Conditional |
| ResourceName | Conditional | Instance name (not in a cost feed) | Missing: Conditional |
| ResourceType | Conditional | Instance type (not in a cost feed) | Missing: Conditional |
| ServiceCategory | Mandatory | No (Compute) | Missing: Mandatory |
| ServiceName | Mandatory | No (constant per offering) | Missing: Mandatory |
| ServiceSubcategory | Recommended | No (GPU Cloud / Compute) | Missing: Recommended |
| SkuId | Conditional | No (GPU type maps to a SKU) | Missing: Conditional |
| SkuMeter | Conditional | No | Missing: Conditional |
| SkuPriceDetails | Conditional | No | Missing: Conditional |
| SkuPriceId | Conditional | No | Missing: Conditional |
| SubAccountId | Conditional | Project id (not in a cost feed) | Missing: Conditional |
| SubAccountName | Conditional | Project name (not in a cost feed) | Missing: Conditional |
| SubAccountType | Conditional | No | Missing: Conditional |
| Tags | Conditional | Instance tags are key-value (not in a cost feed) | Missing: Conditional |

**Reading the tally:** 57 columns total. 21 Mandatory, all currently missing because no cost dataset exists. Of those 21, the substantive work concentrates in 2 areas (cost reconciliation and a metered usage record); the rest are constants or clean derivations. 32 Conditional and 4 Recommended columns; one Recommended column (AvailabilityZone) is N/A because Fluidstack exposes regions without zones. No column is currently Present, and no deviations exist because nothing is emitted in FOCUS shape yet.

### 1.4 What's solved, and what remains

Because there is no cost dataset, nothing is solved in FOCUS terms today. But the build is far smaller than 21 missing Mandatory columns implies, because most of those columns are constants or clean derivations once a usage feed exists.

**Substantive gaps (real data that must be created):**

- **A metered usage record.** FOCUS needs a per-charge-period row tied to a resource. Fluidstack meters per second internally (it bills per second), but no usage feed is exposed. Producing `ConsumedQuantity`, `ConsumedUnit`, `ChargePeriodStart`, and `ChargePeriodEnd` requires publishing that metering as records, ideally at instance-and-day granularity. This is the foundational gap; every other column hangs off it.
- **Cost reconciliation across the cost columns.** `ListCost`, `ContractedCost`, `BilledCost`, and `EffectiveCost` must reconcile. On-demand usage at a flat rate makes `ListCost` = `BilledCost` = `EffectiveCost` a clean computation (quantity times rate). The substantive part is the discounting: reserved clusters carry committed rates, and service credits are reconciled manually at the monthly cycle. Where those discounts and credits apply, `EffectiveCost` and `BilledCost` diverge from `ListCost`, and producing them means reconciling order-level commitments and manually-applied credits back to the usage lines. The tell that this is substantive, not trivial, is the manual-credit and per-order-commitment process.

**Trivial Mandatory adds (plumbing once the usage record exists):**

- **Constants:** `InvoiceIssuerName`, `ProviderName`, and `PublisherName` are all "Fluidstack." `ServiceCategory` is "Compute," `ServiceName` is the offering name. `BillingCurrency` is the account currency (presumed USD).
- **Derivations:** `PricingQuantity` and `PricingUnit` (GPU-hour) derive directly from the metered quantity for flat-rate on-demand SKUs. For reserved or custom-rate SKUs the pricing quantity is computed against the rate basis, not copied, so scope the easy derivation to flat-rate on-demand.
- **Account and period fields:** `BillingAccountId` / `BillingAccountName` come from the organization, `BillingPeriodStart` / `BillingPeriodEnd` from the monthly cycle.
- **Nullable Mandatory:** `ChargeClass` is null except on corrections. `ChargeDescription` is a generated human-readable string.

**Conditional columns that apply and should be populated:** resource identity (`ResourceId`, `ResourceName`, `ResourceType`) maps cleanly from the instance object; `SubAccountId` / `SubAccountName` from projects; `RegionId` / `RegionName` from the region; `Tags` from the instance tag map; the commitment-discount family from reserved clusters; `PricingCategory` (On-Demand vs Committed); SKU columns from the GPU type and rate card.

**Conditional/Recommended columns that are legitimately N/A:** `AvailabilityZone` (regions without zones).

### 1.5 Deviations to fix

None today. No data is emitted in FOCUS shape, so there are no format or enum deviations to correct. Two points worth carrying into the build so they do not become deviations later:

- **Tags are already key-value.** The instance `tags` field is a key-value map, which is the FOCUS shape. Carry that shape through to the cost dataset rather than flattening to an array of strings.
- **Enums must use FOCUS members.** When the cost dataset is built, `ServiceCategory` must be "Compute" (a valid member), `ChargeCategory` must be one of Usage / Purchase / Tax / Credit / Adjustment, and `ChargeFrequency` one of One-Time / Recurring / Usage-Based. Manually-applied service credits belong under `ChargeCategory` = Credit.

---

## Part 2: The path forward

### 2.1 Which FOCUS version to target

Baseline the build against **v1.2**, the current certification baseline, then build toward **v1.4** (ratified 2026-06-04). Two practical notes:

- `ProviderName` and `PublisherName` are Mandatory in v1.2, deprecated in v1.3, and removed in v1.4. Since Fluidstack is starting fresh, populate them for a v1.2-conformant dataset but plan to drop them when targeting v1.4.
- The v1.4 Invoice Detail and billing-period datasets align well with Fluidstack's monthly Stripe billing and would support invoice reconciliation. The FOCUS Validator's v1.4 support is expected later in Q3 2026; the Validator supports v1.3 today.

### 2.2 What certification requires

FOCUS conformance for data generators runs through the FinOps Foundation. The "FinOps Certified FOCUS v1.2 Conformant" program requires a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report (this analysis is its seed). Membership is required for certification, though contributing to the spec is open and free. Contact `member-cert@finops.org` for the RFI. Open-source tooling: the FOCUS Validator (checks data against the Requirements Model), the FOCUS Converter (provider-native to FOCUS), and the FOCUS Requirements Model (machine-readable MUST/SHOULD/MAY rules).

### 2.3 Phased roadmap

**Phase 0: Decide the dataset and scope.** Confirm the cost dataset will be a per-instance, per-day usage feed keyed on organization, project, and instance UUID. Confirm billing currency and the monthly billing-period boundaries. Decide delivery (CSV/Parquet export, or a billing API).

**Phase 1: Stand up the metered usage record plus the trivial Mandatory adds.** Publish per-charge-period consumption (`ConsumedQuantity`, `ConsumedUnit`, `ChargePeriodStart`, `ChargePeriodEnd`) from the internal per-second metering. Add the constants (`InvoiceIssuerName`, `ProviderName`, `PublisherName`, `ServiceCategory`, `ServiceName`, `BillingCurrency`), the account/period fields, and the derived pricing columns. This phase unlocks most allocation and reporting use cases.

**Phase 2: Build the cost columns and reconcile discounts.** Populate `ListCost`, `ContractedCost`, `BilledCost`, and `EffectiveCost`. For flat-rate on-demand this is quantity times rate. For reserved clusters and manual credits, reconcile order-level committed rates and applied credits back to the usage lines so the four cost columns are internally consistent.

**Phase 3: Round out applicable Conditional and Recommended columns.** Resource identity, sub-account (project), region, tags, the commitment-discount family for reserved clusters, the SKU columns, `PricingCategory`, `InvoiceId`, `ChargeFrequency`, and `ServiceSubcategory`. Set `AvailabilityZone` null.

**Phase 4: Validate, then mature to v1.4.** Run sample data through the FOCUS Validator, pursue certification at the v1.2 baseline, then drop `ProviderName` / `PublisherName` and adopt the v1.4 Invoice Detail and billing-period datasets.

### 2.4 FOCUS Use Cases unlocked

Grouped by the phase that unlocks each:

- **After Phase 1 (usage record plus identity):** cost allocation by project and by resource, tag-based showback and chargeback, usage and anomaly reporting, GPU utilization reporting by instance and region. Many allocation and reporting use cases work as soon as resource-, tag-, and day-level data exist.
- **After Phase 2 (cost columns):** effective-cost reporting, actuals-based budgeting and forecasting, invoice reconciliation, discount and commitment analysis for reserved clusters.
- **Out of scope for now:** any use case depending on availability zones (Fluidstack has none) and split-cost or shared-cost allocation mechanics that the model does not currently expose.

---

## Part 3: Immediate next steps

1. Confirm the billing currency and the monthly billing-period boundaries used on Stripe invoices.
2. Decide the cost-dataset grain (per-instance, per-day is recommended) and the delivery mechanism (export file or billing API endpoint).
3. Map the internal per-second metering to FOCUS charge-period records; this is the foundational build.
4. Draft the native-to-FOCUS field mapping from the instance/organization/project objects, then generate a small v1.2 sample dataset.
5. Run the sample through the FOCUS Validator and iterate before contacting `member-cert@finops.org`.

---

## Confidence summary

- **No public cost or usage dataset exists:** High confidence. The Management API (v1alpha1) and published docs cover infrastructure only; no billing, usage, or cost endpoint appears in the public documentation.
- **Account and resource model (organizations, projects, instance UUID, key-value tags, named regions, no zones):** High confidence, taken directly from the Management API schema and Projects documentation.
- **Pricing and commercial model (flat per-hour/per-second on-demand, reserved 30-day-plus clusters, custom private cloud, no egress fees, manual service credits, Stripe, monthly cycle):** Medium to high confidence, from Fluidstack pricing/legal pages and third-party aggregators; specific rates fluctuate.
- **Billing currency (USD):** Medium confidence; presumed from USD-denominated published rates, not confirmed against an invoice.
- **Internal per-second metering exists but is not exposed:** Medium confidence, inferred from the stated per-second billing basis.
- **Feature levels:** High confidence. Verified against the FOCUS v1.2 column set (57 columns) via the FOCUS column library on 2026-06-30; the bundled reference table (`SPEC_VERSIONS_AS_OF: 2026-06-23`) matched the live column set, including the v1.3 deprecation and v1.4 removal of Provider/Publisher. No cache refresh was needed.
- **Overall:** This analysis is provisional with respect to Fluidstack's internal billing data, because no cost dataset is published. It is firm on the FOCUS side. A live FOCUS Validator run is recommended once a first sample dataset exists.

---

## Sources

- Fluidstack Management API (v1alpha1): https://docs.fluidstack.io/api/management/
- Fluidstack API overview: https://docs.fluidstack.io/get-started/api-overview
- Fluidstack Projects and Organizations: https://docs.fluidstack.io/projects/overview
- Fluidstack pricing and legal pages: https://www.fluidstack.io/resources/pricing and https://fluidstack.io/legal/terms-conditions
- Third-party pricing/specs: https://getdeploying.com/fluidstack and https://computeprices.com/providers/fluidstack
- FOCUS Specification and column library: https://focus.finops.org/focus-specification/
- FOCUS tooling: FOCUS Validator, FOCUS Converter, FOCUS Requirements Model

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
