# Shadeform and FOCUS: Compliance Gap and Adoption Roadmap

*Analysis run: June 30, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

Prepared: 2026-06-30
Source analyzed: Shadeform public API reference (instances/clusters/volumes), Core Concepts, FAQ, and billing documentation at docs.shadeform.ai, plus the public marketplace pages.
FOCUS baseline: v1.2 (current certification baseline). Build target: v1.4 (latest, ratified 2026-06-04).

## Executive summary

Shadeform is a GPU cloud marketplace and aggregator: a single API, console, and invoice spanning 15 or more underlying GPU clouds (Lambda, Crusoe, Hyperstack, Nebius, and others). Its instance API exposes a clean, well-structured object with the consumption primitives FOCUS cares about: a resource identity, the underlying cloud, region, GPU SKU, an hourly price, an accrued cost figure, key tags, and minute-level timestamps. Billing is centralized through Stripe into one monthly invoice that itemizes provider cost versus Shadeform charges.

The data Shadeform publishes today is an operational instance and pricing API, not a FOCUS-shaped billing export. It carries the raw materials for most Mandatory columns but does not yet emit them as a per-charge dataset with FOCUS column IDs, key-value tags, or the full cost family (List, Billed, Effective, Contracted). The aggregator model is the defining feature for FOCUS mapping: the underlying `cloud` is the true Provider and Publisher, while Shadeform is the Invoice Issuer, and the closest analog to a sub-account is the linked-cloud-account versus Shade Cloud distinction.

Verdict: a strong consumption substrate with a thin published cost surface. Conformance is reachable but requires building a charge-level dataset and reconciling Stripe invoice totals back to instance-hours.

Stat strip: 57 FOCUS columns (v1.2). Roughly 14 present or trivially derivable from published fields. 3 of 6 substantive Mandatory gaps sit in the cost family. Multiple deviations to fix (tags, enums, currency shaping).

RAG readiness: Cost Gap, Granularity Strong, Allocation Partial, Coverage Partial, FOCUS shape Gap. Overall band: Not yet aligned (per public docs).

Recommendation: Treat Shadeform's instance API plus Stripe invoice as two halves of one dataset. Build a charge-level FOCUS feed keyed on instance and charge period, derive the cost family by reconciling the monthly Stripe total to instance-hours, and set Provider/Publisher to the underlying cloud with Shadeform as Invoice Issuer.

## Part 1: The conformance gap

### 1.1 The data source

Shadeform exposes a REST API (base `https://api.shadeform.ai/v1`) and a console. The objects relevant to cost and usage:

- Instance object (`/instances`, `/instances/{id}/info`): `id` (UUID resource identity), `cloud` (underlying provider, e.g. hyperstack, lambda, crusoe), `region`, `shade_instance_type` (Shadeform-standardized type), `cloud_instance_type` (provider-native SKU string), `cloud_assigned_id`, `shade_cloud` (boolean: deployed in Shadeform's pooled accounts or a customer-linked cloud account), `name`, a `configuration` block (gpu_type, num_gpus, vram_per_gpu_in_gb, vcpus, memory_in_gb, storage_in_gb, interconnect), `cost_estimate` (string, cost incurred via Shadeform), `hourly_price` (integer, cents), `tags` (array of bare strings), and `created_at` / `active_at` / `deleted_at` (ISO 8601 UTC timestamps).
- Clusters and volumes APIs follow the same shape for multi-node and storage resources.

Billing and invoicing (from FAQ and public sources):

- Pay-as-you-go by default, charged through Stripe. Larger customers can request monthly invoicing via Stripe Invoicing.
- A single monthly invoice aggregates all usage with a breakdown by GPU type, provider, duration, and cost. Every invoice itemizes provider cost versus Shadeform charges.
- Billing granularity is 1-minute increments (rent 37 minutes, pay for 37 minutes).
- Currency is USD.
- Reservation discounts and cloud credits exist but are arranged through support, not exposed as structured fields in the public API.

Key limitations for FOCUS: there is no published per-charge billing export. `cost_estimate` is a single running total per instance, not a time-sliced charge record. There is no documented field carrying list price versus effective price after any reservation discount or credit, and discounts and credits are handled at invoice time outside the API. Tags are bare strings, not key-value pairs.

### 1.2 How conformance is judged

FOCUS assigns each column a feature level: Mandatory (must be present and populated where applicable), Conditional (required when the provider's model triggers the condition), Recommended, or Optional. Conformance is evaluated column by column against the FOCUS Requirements Model. Feature levels in this report were verified against the FOCUS v1.2 specification Content Constraints tables (cache stamp 2026-06-23, spot-checked live on 2026-06-30: ChargeClass Mandatory, ChargeFrequency Recommended, both confirmed).

### 1.3 Column-by-column status (FOCUS v1.2, all 57 columns)

Legend: Present / Present, deviation to fix / Missing: Mandatory / Missing: Recommended / Missing: Conditional / N/A: null valid.

| FOCUS Column | Level | In the source? | Status |
|---|---|---|---|
| AvailabilityZone | R | No (region only) | Missing: Recommended |
| BilledCost | M | Partial (cost_estimate, not per-charge) | Missing: Mandatory |
| BillingAccountId | M | Implicit (Shadeform account) | Missing: Mandatory (derivable) |
| BillingAccountName | M | Implicit (account) | Missing: Mandatory (derivable) |
| BillingAccountType | C | No | Missing: Conditional |
| BillingCurrency | M | Implicit (USD) | Missing: Mandatory (derivable) |
| BillingPeriodEnd | M | No (monthly invoice cycle) | Missing: Mandatory (derivable) |
| BillingPeriodStart | M | No (monthly invoice cycle) | Missing: Mandatory (derivable) |
| CapacityReservationId | C | No | N/A: null valid |
| CapacityReservationStatus | C | No | N/A: null valid |
| ChargeCategory | M | No (implied Usage) | Missing: Mandatory (derivable) |
| ChargeClass | M | No | Missing: Mandatory (nullable, plumbing) |
| ChargeDescription | M | Partial (instance type / GPU) | Missing: Mandatory (derivable) |
| ChargeFrequency | R | No (implied Usage-Based) | Missing: Recommended |
| ChargePeriodEnd | M | Partial (deleted_at / active_at) | Missing: Mandatory (derivable) |
| ChargePeriodStart | M | Partial (active_at / created_at) | Missing: Mandatory (derivable) |
| CommitmentDiscountCategory | C | No | N/A: null valid |
| CommitmentDiscountId | C | No | N/A: null valid |
| CommitmentDiscountName | C | No | N/A: null valid |
| CommitmentDiscountQuantity | C | No | N/A: null valid |
| CommitmentDiscountStatus | C | No | N/A: null valid |
| CommitmentDiscountType | C | No | N/A: null valid |
| CommitmentDiscountUnit | C | No | N/A: null valid |
| ConsumedQuantity | C | Partial (derivable from duration) | Missing: Conditional (derivable) |
| ConsumedUnit | C | No (implied hours) | Missing: Conditional (derivable) |
| ContractedCost | M | No | Missing: Mandatory |
| ContractedUnitPrice | C | Partial (hourly_price) | Missing: Conditional (derivable) |
| EffectiveCost | M | Partial (cost_estimate) | Missing: Mandatory |
| InvoiceId | R | No (Stripe invoice exists) | Missing: Recommended (derivable) |
| InvoiceIssuerName | M | Implicit (Shadeform) | Missing: Mandatory (derivable) |
| ListCost | M | Partial (hourly_price x hours) | Missing: Mandatory (derivable) |
| ListUnitPrice | C | Yes (hourly_price, cents) | Present, deviation to fix |
| PricingCategory | C | No (on-demand implied) | Missing: Conditional (derivable) |
| PricingCurrency | C | Implicit (USD) | Missing: Conditional (derivable) |
| PricingCurrencyContractedUnitPrice | C | No | N/A: null valid |
| PricingCurrencyEffectiveCost | C | No | N/A: null valid |
| PricingCurrencyListUnitPrice | C | No | N/A: null valid |
| PricingQuantity | M | Partial (derivable, flat-rate) | Missing: Mandatory (derivable) |
| PricingUnit | M | No (implied hours) | Missing: Mandatory (derivable) |
| ProviderName | M | Yes (cloud) | Present, deviation to fix |
| PublisherName | M | Yes (cloud) | Present, deviation to fix |
| RegionId | C | Yes (region) | Present, deviation to fix |
| RegionName | C | Partial (region) | Present, deviation to fix |
| ResourceId | C | Yes (id / cloud_assigned_id) | Present |
| ResourceName | C | Yes (name) | Present |
| ResourceType | C | Partial (shade_instance_type) | Present, deviation to fix |
| ServiceCategory | M | No (implied Compute) | Missing: Mandatory (derivable) |
| ServiceName | M | No (GPU instance implied) | Missing: Mandatory (derivable) |
| ServiceSubcategory | R | No | Missing: Recommended |
| SkuId | C | Yes (cloud_instance_type) | Present, deviation to fix |
| SkuMeter | C | No | Missing: Conditional |
| SkuPriceDetails | C | Partial (config block) | Missing: Conditional |
| SkuPriceId | C | No | Missing: Conditional |
| SubAccountId | C | Partial (shade_cloud / cloud account) | Missing: Conditional (derivable) |
| SubAccountName | C | Partial (cloud account) | Missing: Conditional (derivable) |
| SubAccountType | C | No | Missing: Conditional |
| Tags | C | Yes (array of strings) | Present, deviation to fix |

### 1.4 What's solved, and what remains

Reading the tally: of 57 columns, roughly 6 are present (some with deviations) and another 8 are trivially derivable from fields already published, leaving the cost family as the real work. Excluding the legitimately N/A commitment and capacity columns, coverage of applicable columns sits in the low-to-mid range.

**Substantive gaps (real data not in the source):**

1. **BilledCost and EffectiveCost.** Shadeform publishes `cost_estimate`, a single running total per instance, plus a monthly Stripe invoice that itemizes provider cost versus Shadeform charges and applies any reservation discounts or credits at invoice time. Producing per-charge BilledCost and EffectiveCost requires reconciling those invoice-level adjustments back to instance-hours. The FAQ states discounts and credits are arranged outside the API, which is the tell: this is reconciliation work, not a copy of `cost_estimate`. Treat both as substantive.
2. **ContractedCost.** Reservation discounts exist (arranged via support) but are not exposed per charge. If a customer has a negotiated reservation rate, ContractedCost differs from ListCost and must be sourced from the agreement, not the API.

**Trivial gaps (derivable from data already present, flat-rate compute):**

- ListCost = `hourly_price` x billed hours. `hourly_price` is a flat per-hour rate, so PricingQuantity equals consumed hours and ListUnitPrice is `hourly_price` converted from cents to a currency decimal.
- PricingQuantity, PricingUnit (hours), ConsumedQuantity, ConsumedUnit: derivable from `active_at`/`deleted_at` duration at 1-minute resolution.
- ChargePeriodStart/End: from `active_at` and `deleted_at`.
- BillingPeriodStart/End: the monthly Stripe cycle.
- ChargeCategory (Usage), ServiceCategory (Compute), ServiceName, ChargeDescription: constant or derivable from the instance type.
- BillingAccountId/Name, BillingCurrency (USD), InvoiceIssuerName (Shadeform), InvoiceId (the Stripe invoice number): account- and invoice-level constants.
- ChargeClass: null except for corrections.

### 1.5 Deviations to fix (present columns)

- **Tags**: emitted as an array of bare strings (`["tag1"]`); FOCUS requires key-value pairs.
- **ListUnitPrice**: `hourly_price` is an integer in cents; FOCUS expects a decimal in the billing currency.
- **ProviderName and PublisherName**: the `cloud` field carries the underlying provider, which is correct for the aggregator model, but it uses Shadeform's internal slugs (e.g. `hyperstack`); map to canonical provider names. Note these columns are deprecated in v1.3 and removed in v1.4.
- **RegionId/RegionName**: a single `region` slug (e.g. `canada-1`) serves both; split into ID and human name.
- **ResourceType / SkuId**: `shade_instance_type` and `cloud_instance_type` are native strings; confirm against the intended FOCUS representation.

What is already right: a stable ResourceId, a populated ResourceName, minute-level timestamps in ISO 8601 UTC, a clean underlying-provider dimension, and a per-instance price. These are the hard parts to retrofit, and Shadeform has them.

## Part 2: The path forward

### 2.1 Which FOCUS version to target

Baseline conformance against v1.2 (the current certification baseline) and build toward v1.4 (latest, ratified 2026-06-04). Because v1.3 deprecates and v1.4 removes ProviderName and PublisherName, design the aggregator's provider attribution so it does not depend on those columns long term; carry the underlying cloud as a first-class dimension that survives their removal. The Validator supports v1.3 today, with v1.4 support expected later in Q3 2026.

### 2.2 What certification requires

FOCUS conformance for data generators runs through the FinOps Foundation. The current badge is "FinOps Certified FOCUS v1.2 Conformant" (contact member-cert@finops.org for the RFI). Membership is required for certification, though contributing to the spec is open and free. Deliverables are a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report (this analysis is its seed). Open tooling: the FOCUS Validator (checks data against the Requirements Model), the FOCUS Converter (provider-native to FOCUS), and the FOCUS Requirements Model (machine-readable MUST/SHOULD/MAY rules).

### 2.3 Phased roadmap

**Phase 0: Validate and scope.** Define the FOCUS dataset as a charge-level feed (one row per instance per charge period), not the live instance object. Confirm the v1.2 baseline and v1.4 build target. Run any existing export through the FOCUS Validator to set a baseline.

**Phase 1 (unlock): Close the substantive Mandatory cost gaps and the trivial adds.** Build the reconciliation that ties the monthly Stripe invoice (provider cost, Shadeform charges, discounts, credits) back to instance-hours to produce BilledCost, EffectiveCost, and ContractedCost. In the same pass, emit the derivable Mandatory columns: ListCost, PricingQuantity, PricingUnit, ChargePeriodStart/End, BillingPeriodStart/End, ChargeCategory, ServiceCategory, ServiceName, ChargeDescription, BillingAccount fields, BillingCurrency, InvoiceIssuerName, and ChargeClass.

**Phase 2: Fix format and value deviations.** Convert Tags to key-value pairs, ListUnitPrice from cents to currency decimal, split region into RegionId and RegionName, and map provider slugs to canonical names.

**Phase 3: Round out applicable Conditional and Recommended columns.** Populate SubAccountId/Name from the Shade-Cloud-versus-linked-account distinction, ConsumedQuantity/Unit, ContractedUnitPrice, PricingCategory, PricingCurrency, InvoiceId, ChargeFrequency, ServiceSubcategory, and the SKU detail columns. Null the commitment and capacity-reservation families with a note that they do not apply.

**Phase 4: Mature to v1.4 and certify.** Migrate provider attribution off ProviderName/PublisherName ahead of their removal, adopt the v1.4 Invoice Detail and billing-period datasets for cleaner reconciliation, re-validate, and pursue certification.

### 2.4 FOCUS Use Cases unlocked

- Unlocked once the charge-level feed with resource, tags, sub-account, and day-level data exists (Phase 1 to 3): cost allocation by team and project, multi-cloud spend reporting across underlying providers, GPU-hour utilization analysis, anomaly detection, and tag-based showback.
- Unlocked once the cost family reconciles (Phase 1): invoice reconciliation, effective-cost reporting, and actuals-based budgeting.
- Out of scope for the model: commitment-discount and capacity-reservation use cases, since Shadeform's public model is on-demand pass-through (reservations are handled offline via support and would need structured exposure first).

## Part 3: Immediate next steps

1. Define the target FOCUS dataset as a charge-level feed keyed on instance and charge period, distinct from the live instance API.
2. Map the aggregator roles: underlying `cloud` to Provider and Publisher, Shadeform to Invoice Issuer, and the Shade-Cloud-versus-linked-account distinction to SubAccount.
3. Design the Stripe-to-instance-hours reconciliation that yields BilledCost, EffectiveCost, and ContractedCost.
4. Emit the derivable Mandatory columns and convert Tags to key-value pairs.
5. Run a sample through the FOCUS Validator and confirm the target representation against the Requirements Model.

## Confidence summary

- Instance and pricing API field structure: high confidence, taken directly from the published OpenAPI reference.
- Billing mechanics (single monthly Stripe invoice, 1-minute granularity, provider-cost-plus-charges itemization, USD, discounts arranged via support): medium-high confidence, drawn from the FAQ and public sources rather than a billing-export schema.
- The absence of a per-charge billing export: medium-high confidence; no such export is documented publicly. If Shadeform offers a private usage or billing export, the cost-family verdict would improve and several Missing items would move to Present.
- Feature levels: high confidence, verified against the v1.2 spec with a live spot-check on 2026-06-30.
- The substantive cost-family gap classification rests on the FAQ statement that discounts and invoice payments are arranged outside the API; confirm whether any per-line discount or credit data is available before finalizing the cost mapping.
- Data quality for this analysis: solid on data shape (API is well documented), provisional on the billing-line schema.

## Sources

- Shadeform API reference and OpenAPI: https://docs.shadeform.ai/api-reference/instances/instances-info, https://docs.shadeform.ai/openapi.yaml
- Shadeform Core Concepts, FAQ, Introduction: https://docs.shadeform.ai/getting-started/concepts, https://docs.shadeform.ai/getting-started/faq, https://docs.shadeform.ai/getting-started/introduction
- Shadeform marketplace and billing: https://shadeform.com/, https://stripe.com/customers/shadeform
- FOCUS Specification v1.2: https://focus.finops.org/focus-specification/v1-2/
- FOCUS project, tooling, and certification: https://focus.finops.org/

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
