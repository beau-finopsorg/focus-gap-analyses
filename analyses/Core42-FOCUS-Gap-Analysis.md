# Core42 (G42) and FOCUS: Conformance Gap Analysis

*Analysis run: July 1, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Provider and product in scope:** Core42, the AI cloud arm of G42 (UAE sovereign AI). Two billing surfaces are in scope: Core42 Sovereign AI Cloud (GPUaaS: on-demand and large-scale clusters across NVIDIA H100/H200/B200/GB300, AMD MI300X/MI355X, Cerebras WSE-3, Qualcomm Cloud AI100, orchestrated via Kubernetes or Slurm) and Core42 Compass (sovereign model inference and GenAI services billed by tokens, minutes, pages, and API calls).

**Source analyzed:** the public Core42 Sovereign AI Cloud pages, the Core42 Compass documentation (Model Pricing, View Usage Reports, Set Budget for PYG Models, Usage Report API Reference, Create and Manage Departments), and the GITEX 2025 self-service launch materials. No FOCUS export, data dictionary, or sample billing row is published for either product.

**FOCUS baseline:** v1.2 (current certification baseline, ratified 2025-05-29). **Build target:** v1.4 (latest, ratified 2026-06-04).

**Prepared:** 2026-07-01.

---

## Executive summary

Core42 exposes usage and cost data through a native, provider-specific interface, not a FOCUS dataset. The Compass platform ships a Usage Reports console with an Overview across Cost, Tokens, Images, Videos, Audio, and API Requests, per-card CSV export, and a Usage Report API that aggregates per minute, per hour, or per day and filters by model, API key, project, and department. The Sovereign AI Cloud side bills GPU instances at hourly rates through a self-service console. This is a real, queryable cost feed, but it carries none of the FOCUS column IDs, key-value tags, or enum values that conformance requires. The analysis is therefore a from-native mapping, not a review of an already-FOCUS-shaped export.

The strongest positive finding is that the raw material for allocation exists. Cost is tracked in USD, quantities are captured as tokens, GPU-hours, minutes, pages, and API calls, granularity reaches per-minute, and attribution runs down to department, project, resource name, and API key. Those are the inputs FOCUS needs for `ChargePeriodStart`, `ConsumedQuantity`, `SubAccountId`, and resource-level identity.

The most consequential gap is the cost columns. The published feed surfaces a single cost figure against list token and hourly rates, but Core42 also applies a documented 50 percent Batch discount and prices large-scale GPU clusters and custom models "On Request" through enterprise contracts. Because discounted and contracted pricing exists but is not reconciled back to usage lines in the public feed, `BilledCost`, `EffectiveCost`, and `ContractedCost` are a substantive gap, not a trivial copy of `ListCost`. Coverage of the FOCUS-shaped columns is otherwise low: the feed is measured against 57 v1.2 columns of which few are emitted in a FOCUS-conformant shape today.

**Recommendation:** Treat Core42 as an emerging FOCUS data source. The usage and attribution data needed for a first conformant dataset largely exists inside Compass and the Sovereign AI Cloud billing system; the work is a native-to-FOCUS transform plus a cost-reconciliation layer that lands billed, effective, and contracted cost on the usage lines.

---

## Part 1: The conformance gap

### 1.1 The data source

Core42 bills across two products with distinct but related cost surfaces:

- **Sovereign AI Cloud (GPUaaS):** on-demand GPU instances at published hourly rates (NVIDIA H100 from $2.50/hr, H200 from $4.00/hr, B200 from $5.00/hr; AMD MI300X from $3.50/hr; GB300, MI355X, Cerebras WSE-3, and Qualcomm Cloud AI100 priced On Request), plus pre-tested large-scale clusters sold through enterprise engagement. Orchestration is Kubernetes or Slurm. Access is a self-service console with hourly, pay-as-you-go pricing.
- **Compass (inference and GenAI):** consumption billed per 1M tokens (input and output priced separately per model), per minute (text-to-speech), per hour (Whisper transcription), per 1000 pages (Document AI), per 1M tokens for embeddings and fine-tuning training, and per 1000 transactions (Web Search, File Search). A 50 percent Batch discount applies to supported models. All prices are quoted in USD, exclusive of VAT.

Cost and usage visibility is concentrated in Compass:

- **Usage Reports console:** an Overview tab consolidating Cost, Tokens, Images, Videos, Audio, and API Requests, with interactive charts, period comparison, and tabs for TPM Quota, Resources, API Keys, and Fine-Tuning (including per-job cost). Filters cover Model, Department, Projects, Resource Name, API key, time duration, and call status. Each card exports to CSV.
- **Usage Report API:** `POST https://api.core42.ai/logs/v1/admin/usage_reports`, admin-key only, returning usage aggregated at `per_minute`, `per_hour`, or `per_day`, filtered by `model_ids`, `api_key_name`, `project`, and `department`, over a `start_date`/`end_date` window (YYYY-MM-DD).
- **Budgets:** daily and monthly spend limits in USD per pay-as-you-go model, for online and batch processing.
- **Attribution structures:** workspaces, departments, projects, resources, and API keys, with role-based access control and audit logs.

Key characteristics relevant to FOCUS:

- **Granularity:** sub-daily. The Usage Report API supports per-minute and per-hour aggregation, which satisfies the sub-monthly granularity FOCUS expects.
- **Cost model:** usage-based, in USD, against list rates. Discounts (Batch 50 percent) and contracted pricing (clusters and custom models, On Request) exist but are not shown as reconciled effective or contracted cost on the public feed.
- **Attribution:** department, project, resource name, and API key are all filterable, giving the raw material for `SubAccountId`, resource identity, and cost-center allocation.
- **Currency:** USD throughout.

Key limitations for this analysis: Core42 publishes no FOCUS export, no billing data dictionary, and no sample usage row or CSV schema. The Usage Report API documents request parameters but not the response field set. Column-level classification below is therefore inferred from the console description, the API request contract, and the pricing model, and is marked provisional where the underlying field is not directly evidenced.

### 1.2 How conformance is judged

FOCUS assigns every column a feature level: Mandatory, Conditional, Recommended, or Optional. A conformant dataset must include and populate all Mandatory columns, must populate Conditional columns when the provider's business model triggers the condition, should populate Recommended columns, and may include Optional ones. Conformance is judged column by column against the spec's Requirements Model, not by an overall impression.

Feature levels in this report were taken from the verified reference table and cross-checked against the live FOCUS Specification v1.2 via the FOCUS column service on 2026-07-01. The v1.2 column set (57 columns) and the commonly-misremembered levels (`ServiceSubcategory` Recommended, `ChargeClass` Mandatory-nullable, `PricingQuantity`/`PricingUnit` Mandatory, `ChargeFrequency` and `InvoiceId` Recommended) were confirmed against the live spec; the bundled cache was current, and the v1.3 deprecation of `ProviderName`/`PublisherName` was reconfirmed.

### 1.3 Column-by-column status

Feature levels verified against the FOCUS Specification v1.2. Status reflects what the public documentation supports. Because Core42 emits no FOCUS-shaped dataset, columns whose underlying data exists in the native feed are marked "Present, deviation to fix" (data exists, native shape, needs a transform) rather than "Present," and columns whose data does not appear in the feed are marked as Mandatory, Conditional, or Recommended gaps.

Status legend: Present; Present, deviation to fix; Missing: Mandatory; Missing: Recommended; Missing: Conditional; N/A: null valid.

| § | FOCUS Column | Level | In the source? | Status |
|---|---|---|---|---|
| 3.1 | AvailabilityZone | R | Regions listed; zones not documented | N/A: null valid (regions, no documented zones) |
| 3.2 | BilledCost | M | Cost shown against list rates; discounts/contracts not reconciled on feed | Missing: Mandatory (substantive) |
| 3.3 | BillingAccountId | M | Workspace/account identity in console | Present, deviation to fix (map workspace to BillingAccountId) |
| 3.4 | BillingAccountName | M | Workspace/account name | Present, deviation to fix |
| 3.5 | BillingAccountType | C | Not documented | Missing: Conditional |
| 3.6 | BillingCurrency | M | USD throughout | Present, deviation to fix (emit as ISO 4217 column) |
| 3.7 | BillingPeriodEnd | M | Reporting window supported, not a billing-period field | Missing: Mandatory (trivial, derive from period) |
| 3.8 | BillingPeriodStart | M | Reporting window supported | Missing: Mandatory (trivial, derive from period) |
| 3.9 | CapacityReservationId | C | Clusters are contracted, reservation model not documented | N/A: null valid (no documented capacity-reservation mechanic) |
| 3.10 | CapacityReservationStatus | C | Not documented | N/A: null valid |
| 3.11 | ChargeCategory | M | Usage present; taxes (VAT) and credits not on feed | Present, deviation to fix (emit valid enum; add Tax/Adjustment where applicable) |
| 3.12 | ChargeClass | M | Corrections not documented | Missing: Mandatory (trivial, nullable; populate on corrections) |
| 3.13 | ChargeDescription | M | Model/instance descriptors available | Present, deviation to fix |
| 3.14 | ChargeFrequency | R | Usage-based and hourly billing implied | Missing: Recommended |
| 3.15 | ChargePeriodEnd | M | Per-minute/per-hour aggregation | Present, deviation to fix (emit as ISO 8601 timestamp) |
| 3.16 | ChargePeriodStart | M | Per-minute/per-hour aggregation | Present, deviation to fix |
| 3.17 | CommitmentDiscountCategory | C | Cluster/custom contracts exist; no discount reporting mechanic on feed | Missing: Conditional |
| 3.18 | CommitmentDiscountId | C | Not surfaced | Missing: Conditional |
| 3.19 | CommitmentDiscountName | C | Not surfaced | Missing: Conditional |
| 3.20 | CommitmentDiscountQuantity | C | Not surfaced | Missing: Conditional |
| 3.21 | CommitmentDiscountStatus | C | Not surfaced | Missing: Conditional |
| 3.22 | CommitmentDiscountType | C | Not surfaced | Missing: Conditional |
| 3.23 | CommitmentDiscountUnit | C | Not surfaced | Missing: Conditional |
| 3.24 | ConsumedQuantity | C | Yes (tokens, GPU-hours, minutes, pages, calls) | Present, deviation to fix (emit as FOCUS column) |
| 3.25 | ConsumedUnit | C | Yes (unit implied per meter) | Present, deviation to fix |
| 3.26 | ContractedCost | M | Contracted rates exist (clusters, custom) but off public feed | Missing: Mandatory (substantive) |
| 3.27 | ContractedUnitPrice | C | On-Request rates not published | Missing: Conditional |
| 3.28 | EffectiveCost | M | Batch 50% discount and contracts not reconciled on feed | Missing: Mandatory (substantive) |
| 3.29 | InvoiceId | R | Invoice not exposed in usage feed | Missing: Recommended |
| 3.30 | InvoiceIssuerName | M | Issuer (Core42/G42 entity) known but not a feed field | Missing: Mandatory (trivial, constant) |
| 3.31 | ListCost | M | Cost against published list rates | Present, deviation to fix (emit as ListCost column) |
| 3.32 | ListUnitPrice | C | Published per-token and per-hour rates | Present, deviation to fix |
| 3.33 | PricingCategory | C | On-demand vs contract distinction exists | Missing: Conditional |
| 3.34 | PricingCurrency | C | USD | Present, deviation to fix |
| 3.35 | PricingCurrencyContractedUnitPrice | C | Not surfaced | Missing: Conditional |
| 3.36 | PricingCurrencyEffectiveCost | C | Not surfaced | Missing: Conditional |
| 3.37 | PricingCurrencyListUnitPrice | C | List rates in USD | Present, deviation to fix |
| 3.38 | PricingQuantity | M | Derivable from consumed quantity for flat-rate meters | Missing: Mandatory (trivial for flat-rate; compute for tiered) |
| 3.39 | PricingUnit | M | Unit per meter (1M tokens, hour, page) | Missing: Mandatory (trivial, derive from meter) |
| 3.40 | ProviderName | M (deprecated v1.3, removed v1.4) | Constant (Core42) | Missing: Mandatory (trivial; omit at v1.4 target) |
| 3.41 | PublisherName | M (deprecated v1.3, removed v1.4) | Constant | Missing: Mandatory (trivial; omit at v1.4 target) |
| 3.42 | RegionId | C | Regions listed (Abu Dhabi, France, US sites) | Present, deviation to fix (emit RegionId) |
| 3.43 | RegionName | C | Region names available | Present, deviation to fix |
| 3.44 | ResourceId | C | Resource-level filtering (Resource Name) | Present, deviation to fix (confirm stable resource ID) |
| 3.45 | ResourceName | C | Yes (Resource Name filter) | Present, deviation to fix |
| 3.46 | ResourceType | C | Model/instance type implied | Present, deviation to fix |
| 3.47 | ServiceCategory | M | AI/ML and Compute implied by product | Missing: Mandatory (trivial, derive; use valid enum) |
| 3.48 | ServiceName | M | Model ID and instance type available | Present, deviation to fix |
| 3.49 | ServiceSubcategory | R | Derivable (inference, training, storage) | Missing: Recommended |
| 3.50 | SkuId | C | Model ID / instance type serve as SKU | Present, deviation to fix (map model/instance to SkuId) |
| 3.51 | SkuMeter | C | Meter implied (input tokens, output tokens, GPU-hour) | Present, deviation to fix |
| 3.52 | SkuPriceDetails | C | Rate detail available in pricing table | Missing: Conditional |
| 3.53 | SkuPriceId | C | Not surfaced | Missing: Conditional |
| 3.54 | SubAccountId | C | Department/project filtering | Present, deviation to fix (map department or project to SubAccountId) |
| 3.55 | SubAccountName | C | Department/project names | Present, deviation to fix |
| 3.56 | SubAccountType | C | Not documented | Missing: Conditional |
| 3.57 | Tags | C | No documented resource-tagging mechanic | Missing: Conditional (confirm whether resources carry key-value labels) |

### 1.4 What's solved, and what remains

**Solved (the raw material exists):**

- **Quantities and granularity.** Tokens, GPU-hours, minutes, pages, and API calls are all metered, and the Usage Report API aggregates to per-minute and per-hour. This gives FOCUS the `ConsumedQuantity`, `ConsumedUnit`, `ChargePeriodStart`, and `ChargePeriodEnd` inputs without new instrumentation.
- **Attribution.** Department, project, resource name, and API key are first-class filters. Mapping department or project to `SubAccountId`/`SubAccountName`, and resource name to `ResourceId`/`ResourceName`, is a naming exercise on data that already exists.
- **List cost and list rates.** Published per-token and per-hour rates plus the console Cost figure give `ListCost` and `ListUnitPrice` directly.

**Remaining (substantive):**

- **The reconciled cost columns.** `BilledCost`, `EffectiveCost`, and `ContractedCost` are the core gap. The public feed reflects list-rate cost; the documented Batch 50 percent discount, enterprise cluster pricing, and On-Request custom-model rates are not reconciled onto usage lines. Producing these requires joining contract and discount terms to the metered usage. This is the classic list-cost trap and the single most likely place to understate the verdict, so it is treated as substantive.
- **FOCUS shaping across the board.** No column is emitted with FOCUS IDs, enums, or key-value tags today. Most "data exists" columns are therefore "Present, deviation to fix": the transform is the work.

**Remaining (trivial):**

- Constants and derivations: `InvoiceIssuerName`, `ProviderName`/`PublisherName` (constants; the latter two dropped at v1.4), `BillingPeriodStart`/`BillingPeriodEnd` (derive from the period), `ServiceCategory` (AI and Machine Learning, Compute), `PricingUnit` (from the meter), `ChargeClass` (nullable, populated only on corrections). `PricingQuantity` is trivial for flat-rate meters (hourly GPU, per-token) and must be computed for any tiered rate.

Of the 21 Mandatory columns, 3 are substantive gaps (`BilledCost`, `EffectiveCost`, `ContractedCost`). The rest are either data that exists in native shape (a transform) or trivial derivations and constants.

### 1.5 Deviations to fix

- **No FOCUS shaping:** the dataset uses native field names, not FOCUS column IDs. This is the primary deviation and touches every present column.
- **Currency format:** confirm `BillingCurrency` and `PricingCurrency` emit the ISO 4217 code (USD), not a symbol.
- **Timestamps:** the Usage Report API takes dates as YYYY-MM-DD and aggregates by interval; FOCUS requires ISO 8601 timestamps on `ChargePeriodStart`/`ChargePeriodEnd` with inclusive-start, exclusive-end semantics.
- **Enums:** `ChargeCategory` must use the FOCUS allowed set (Usage, Purchase, Tax, Credit, Adjustment), and VAT should surface as a Tax charge; `ServiceCategory` must use a valid member (AI and Machine Learning for Compass inference, Compute for GPUaaS).
- **Tags:** if Core42 resources carry labels, they must be emitted as FOCUS key-value pairs; if resources carry no labels, `Tags` is legitimately null.

What is already done right: usage-based metering with real quantities and units, sub-daily granularity, USD costing, and department/project/resource/API-key attribution. These are the hard-to-retrofit properties, and Core42 has them.

---

## Part 2: The path forward

### 2.1 Which FOCUS version to target

Baseline v1.2 (the version the FinOps Certified FOCUS conformance badge has historically been anchored to) and design toward v1.4 (latest). Because Core42 is building a FOCUS representation from scratch rather than uplifting an existing export, it can target the v1.4 column set directly and skip the deprecated `ProviderName`/`PublisherName` columns, while confirming the target representation against the Requirements Model. Re-verify the v1.3/v1.4 additions (split cost allocation, Invoice Detail, billing-period datasets) against the live spec at build time.

### 2.2 What certification requires

FOCUS conformance for data generators runs through the FinOps Foundation. The program has been the "FinOps Certified FOCUS v1.2 Conformant" designation; confirm the current badge version against the program page before finalizing. Membership is required for certification, though contributing to the spec is open and free; contact `member-cert@finops.org` for the RFI. Deliverables are a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report (this analysis is its seed).

Open-source tooling: the **FOCUS Converter** (provider-native to FOCUS) is the most relevant starting point given Core42 emits a native feed; the **FOCUS Validator** (checks data against the Requirements Model) confirms the output; and the **FOCUS Requirements Model** provides the machine-readable MUST/SHOULD/MAY rules.

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
