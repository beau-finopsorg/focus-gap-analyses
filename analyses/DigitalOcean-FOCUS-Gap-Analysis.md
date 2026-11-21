# DigitalOcean and FOCUS: Compliance Gap and Adoption Roadmap

*Analysis run: June 30, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Provider and product in scope:** DigitalOcean (cloud infrastructure and GPU Droplets), billing and usage data.
**Prepared:** 2026-06-30.
**Source analyzed:** DigitalOcean Billing API (`/v2/customers/my/balance`, `/v2/customers/my/invoices`, `/v2/customers/my/billing_history`, billing insights), the downloadable invoice CSV, and the project spend CSV (beta).
**FOCUS baseline:** v1.2 (current certification baseline). **Build target:** v1.4 (latest ratified, 2026-06-04).

---

## Executive summary

DigitalOcean already produces the spine of a FOCUS dataset: a resource-level invoice CSV with per-resource cost, a usage duration and unit, ISO 8601 start and end times, product and service category, and a project name for allocation. The Billing Insights API adds day-over-day usage detail by SKU, region, and description. This is a meaningfully better starting point than a monthly-aggregate-only provider.

The dataset's defining limitation is its single cost figure. DigitalOcean publishes one `amount` per line, denominated in USD, and applies credits, promo codes, prepayment commitments, and taxes at the invoice level rather than against usage lines. FOCUS requires four distinct cost columns (`BilledCost`, `EffectiveCost`, `ListCost`, `ContractedCost`). Whether these are a trivial copy or a substantive reconciliation depends on whether discounts and credits exist, and for DigitalOcean they do exist but live at invoice time, so the split is substantive, not cosmetic.

A 4-stat read: 57 FOCUS columns at v1.2; 22 are present or present-with-a-deviation today (16 clean, 6 deviations). Of the 21 Mandatory columns, 9 are missing, and all 9 are trivial plumbing: identity, currency, charge-metadata, and pricing-quantity fields derivable from data or constants already in the source. The substantive work is not in the missing column count: it sits in 2 of the cost deviations (`BilledCost` and `EffectiveCost`), which need invoice-level credits and commitments reconciled back to usage lines.

**Readiness (data source reviewed, not a certification result):**

- Cost: Partial
- Granularity: Strong
- Allocation: Partial
- Coverage: Partial
- FOCUS shape: Gap
- Overall band: Not yet aligned (per public docs)

**Recommendation:** Treat this as a transform-and-enrich project, not a from-scratch build. Standardize the invoice CSV and Insights feed into FOCUS column IDs, derive the trivial Mandatory fields, and concentrate real engineering on reconciling invoice-level credits and commitments back to usage lines so `BilledCost` and `EffectiveCost` are correct at the row level.

---

## Part 1: The conformance gap

### 1.1 The data source

DigitalOcean exposes billing and usage through several surfaces:

- **Invoice CSV (downloadable):** the most detailed source. Each line carries the resource ID and UUID where applicable, product name, description, group description, amount charged in USD, usage duration, duration unit (such as hours), the invoice-period start and end times in ISO 8601, the project name the resource belongs to, and a category (such as `iaas`). This is resource-level and the strongest input for FOCUS.
- **Billing API:** `balance` returns account balance; `invoices` lists invoices (generated on the first of each month, with a daily-updated `preview`); `billing_history` returns billing events (amount, date, description, and `invoice_id` where applicable, covering payments, invoices issued, and credits granted); billing insights returns day-over-day usage by total amount, region, SKU, and description for a date range.
- **Project spend CSV (beta):** estimates team spend by project (project, product, description, USD), with bandwidth charges apportioned across projects.

Key characteristics:

- **Granularity:** daily. The Insights API and the daily-updated invoice preview provide sub-monthly, day-level usage; the invoice CSV is resource-level with usage duration and explicit start and end times.
- **Currency:** USD only. DigitalOcean bills exclusively in USD and does not invoice in local currency.
- **Allocation:** projects group resources, and the CSV records the project name per line. Organizations consolidate related teams for billing. Resource UUIDs identify individual resources. Droplet-level user tags exist in the platform but are not confirmed as a billing CSV field.
- **Discounts and commitments:** DigitalOcean uses flat published pricing with no formal reserved-instance tiers. Prepayment commitments (annual or 6-month) and negotiated GPU committed-use contracts exist, along with credits and promo codes. These are applied at the balance and invoice level, not as discount lines against usage.
- **Charge model:** Droplets and GPU Droplets bill per second with a minimum charge, surfaced as a usage duration on the invoice line.

### 1.2 How conformance is judged

FOCUS assigns every column a feature level: Mandatory, Conditional, Recommended, or Optional. Conformance is judged column by column. Mandatory columns must be present and populated (some allow null). Conditional columns are required only when the provider's business model triggers the condition; when the model does not, the column should exist and be null. Recommended columns are encouraged but do not block conformance.

Feature levels for this analysis were verified against the FOCUS v1.2 Content Constraints tables and cross-checked live against the FOCUS column library on 2026-06-30. The bundled reference matched the live spec (all 57 v1.2 columns confirmed, with `ProviderName` and `PublisherName` carrying their v1.3 deprecation and v1.4 removal).

### 1.3 Column-by-column status

Status legend: Present (emitted and aligned); Present, deviation to fix (emitted, wrong format or invalid value); Missing: Mandatory (required and absent, blocks conformance); Missing: Recommended (encouraged, absent); Missing: Conditional (required when the model triggers it, absent); N/A: null valid (Conditional or Recommended, does not apply to this model, should exist and be null).

| FOCUS Column | Level | In the source? | Status |
|---|---|---|---|
| AvailabilityZone | R | No (regions only, no zones) | N/A: null valid |
| BilledCost | M | Partial (single USD `amount`, invoice-level credits not reconciled to lines) | Present, deviation to fix |
| BillingAccountId | M | Yes (account / team URN) | Present |
| BillingAccountName | M | Yes (team name) | Present |
| BillingAccountType | C | Derivable (team / organization) | Missing: Conditional |
| BillingCurrency | M | Implied (USD, not emitted as a column) | Missing: Mandatory |
| BillingPeriodEnd | M | Yes (invoice period end) | Present |
| BillingPeriodStart | M | Yes (invoice period start) | Present |
| CapacityReservationId | C | No | N/A: null valid |
| CapacityReservationStatus | C | No | N/A: null valid |
| ChargeCategory | M | No (not classified Usage/Purchase/Tax/Credit/Adjustment) | Missing: Mandatory |
| ChargeClass | M | No (corrections not flagged) | Missing: Mandatory |
| ChargeDescription | M | Yes (`description` / `group_description`) | Present |
| ChargeFrequency | R | Derivable (usage-based vs recurring) | Missing: Recommended |
| ChargePeriodEnd | M | Yes (`end_time`) | Present |
| ChargePeriodStart | M | Yes (`start_time`) | Present |
| CommitmentDiscountCategory | C | Commitments exist (prepay, GPU contracts) but not on usage lines | Missing: Conditional |
| CommitmentDiscountId | C | Not on usage lines | Missing: Conditional |
| CommitmentDiscountName | C | Not on usage lines | Missing: Conditional |
| CommitmentDiscountQuantity | C | Not on usage lines | Missing: Conditional |
| CommitmentDiscountStatus | C | Not on usage lines | Missing: Conditional |
| CommitmentDiscountType | C | Not on usage lines | Missing: Conditional |
| CommitmentDiscountUnit | C | Not on usage lines | Missing: Conditional |
| ConsumedQuantity | C | Yes (`duration`) | Present |
| ConsumedUnit | C | Yes (`duration_unit`, such as hours) | Present |
| ContractedCost | M | Partial (no contracted rate on lines) | Present, deviation to fix |
| ContractedUnitPrice | C | No | Missing: Conditional |
| EffectiveCost | M | Partial (credits and prepay applied at invoice, not amortized to lines) | Present, deviation to fix |
| InvoiceId | R | Yes (`invoice_id` in billing history) | Present |
| InvoiceIssuerName | M | Derivable (constant: DigitalOcean) | Missing: Mandatory |
| ListCost | M | Partial (single `amount`; list rate not separated) | Present, deviation to fix |
| ListUnitPrice | C | Derivable (published per-hour rates) | Missing: Conditional |
| PricingCategory | C | Derivable (On-Demand for most) | Missing: Conditional |
| PricingCurrency | C | Implied (USD) | Missing: Conditional |
| PricingCurrencyContractedUnitPrice | C | No | N/A: null valid |
| PricingCurrencyEffectiveCost | C | No | N/A: null valid |
| PricingCurrencyListUnitPrice | C | No | N/A: null valid |
| PricingQuantity | M | Derivable (from `duration`, flat-rate SKUs) | Missing: Mandatory |
| PricingUnit | M | Derivable (from `duration_unit`) | Missing: Mandatory |
| ProviderName | M (removed v1.4) | Derivable (constant: DigitalOcean) | Missing: Mandatory |
| PublisherName | M (removed v1.4) | Derivable (constant: DigitalOcean) | Missing: Mandatory |
| RegionId | C | Yes (region in Insights; slug on resources) | Present |
| RegionName | C | Yes (region) | Present |
| ResourceId | C | Yes (`resource_uuid`) | Present |
| ResourceName | C | Partial (description, not a clean name field) | Present, deviation to fix |
| ResourceType | C | Derivable (`product` / `category`) | Missing: Conditional |
| ServiceCategory | M | Derivable (`category` such as `iaas` maps to Compute/Storage/Networking) | Missing: Mandatory |
| ServiceName | M | Yes (`product`) | Present |
| ServiceSubcategory | R | Derivable (product family) | Missing: Recommended |
| SkuId | C | Partial (Insights `SKU`) | Present, deviation to fix |
| SkuMeter | C | No | Missing: Conditional |
| SkuPriceDetails | C | No | Missing: Conditional |
| SkuPriceId | C | No | Missing: Conditional |
| SubAccountId | C | Yes (project ID) | Present |
| SubAccountName | C | Yes (project name) | Present |
| SubAccountType | C | Derivable (project) | Missing: Conditional |
| Tags | C | Partial (Droplet tags exist in platform, not confirmed in billing CSV) | Missing: Conditional |

Tally: of 57 v1.2 columns, 16 are Present, 6 are Present with a deviation to fix, 9 are Missing: Mandatory, 2 are Missing: Recommended, 18 are Missing: Conditional, and 6 are N/A: null valid (16 + 6 + 9 + 2 + 18 + 6 = 57). Of the 21 Mandatory columns, 12 are covered (present or present-with-deviation) and 9 are missing; all 9 missing Mandatory columns are trivial plumbing, derivable from data or constants already present. The substantive cost issue sits inside the deviation bucket, in `BilledCost` and `EffectiveCost`.

### 1.4 What's solved, and what remains

**Solved or nearly so.** The temporal and identity backbone is in place: `BillingPeriodStart`/`End`, `ChargePeriodStart`/`End`, `BillingAccountId`/`Name`, `ResourceId`, `ServiceName`, `ChargeDescription`, `ConsumedQuantity`, `ConsumedUnit`, `RegionId`/`Name`, `SubAccountId`/`Name` (projects), and `InvoiceId`. Day-level granularity is genuinely present through the Insights API and daily invoice preview, which is a real strength.

**Trivial Mandatory adds (plumbing).** All nine missing Mandatory columns are derivable from data already present or from constants:

- `BillingCurrency` and (Conditional) `PricingCurrency`: constant USD.
- `InvoiceIssuerName`, `ProviderName`, `PublisherName`: constant DigitalOcean.
- `PricingQuantity` and `PricingUnit`: derivable from `duration` and `duration_unit` for flat-rate per-second or per-hour SKUs. For any tiered or blended SKU (some bandwidth tiers), `PricingQuantity` must be computed against the rate basis, not copied from consumption.
- `ServiceCategory`: derivable by mapping `product`/`category` (such as `iaas`) to the FOCUS enum.
- `ChargeCategory` and `ChargeClass`: classification fields, populated by mapping line types to the FOCUS enums (Usage, Purchase, Tax, Credit, Adjustment) and flagging corrections.

**Substantive gaps (in the deviation bucket).** The cost columns are the real work, and they appear as deviations rather than missing columns because the source does carry a cost figure: it just carries one figure where FOCUS needs four. DigitalOcean emits one `amount` per line and applies credits, promo codes, prepayment commitments, and taxes at the balance and invoice level. Because those discounts and credits exist but are not attached to usage lines, `BilledCost` and `EffectiveCost` cannot be produced by copying `amount`. They require reconciling invoice-level adjustments back to the lines they relate to. This is the list-cost trap: the single cost figure is closest to a list or gross usage amount, and the billed and effective figures must be derived by allocating credits and commitments down to the row. `ListCost` and `ContractedCost` are flagged as deviations because the single `amount` must be split out into the four-cost model.

### 1.5 Deviations to fix

- **Single cost figure:** `amount` must be decomposed into `ListCost`, `ContractedCost`, `BilledCost`, and `EffectiveCost`. With no discounts on a line, all four equal `amount`; where credits, promos, or prepay commitments apply, `BilledCost` and `EffectiveCost` diverge and must be reconciled from invoice-level adjustments.
- **Currency not emitted:** USD is implied throughout but is not a column. Add `BillingCurrency` (and `PricingCurrency`) as a literal ISO 4217 `USD`.
- **No FOCUS column IDs:** every field uses DigitalOcean-native names (`product`, `group_description`, `resource_uuid`, `duration`). A rename and reshape into PascalCase FOCUS column IDs is required.
- **ResourceName:** the source leans on `description` rather than a dedicated resource name. Populate a clean `ResourceName` distinct from `ChargeDescription`.
- **SkuId:** the Insights `SKU` value is present but not aligned to a stable FOCUS `SkuId`/`SkuPriceId` pairing; reconcile SKU identity across Insights and invoice lines.
- **Tags:** if billing-line tags are added, they must be key-value pairs, not an array of bare strings.

Done right already: ISO 8601 timestamps with explicit start and end, resource-level identity, project-based allocation, and day-level usage detail.

---

## Part 2: The path forward

### 2.1 Which FOCUS version to target

Baseline the build against **v1.2**, the current certification baseline ("FinOps Certified FOCUS v1.2 Conformant"), and design toward **v1.4** (ratified 2026-06-04). Targeting v1.4 means not investing in `ProviderName`/`PublisherName`, which v1.4 removes, beyond the v1.2 certification need. The v1.4 Invoice Detail and billing-period datasets align well with DigitalOcean's monthly invoice model and are worth designing for. Validator support for v1.4 is expected later in Q3 2026; v1.3 is supported today.

### 2.2 What certification requires

FOCUS conformance for data generators runs through the FinOps Foundation. The deliverables are a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report (this analysis is its seed). Membership is required for certification, though contributing to the spec is open and free. To start the RFI, contact `member-cert@finops.org`. Open-source tooling to use along the way: the FOCUS Validator (checks data against the Requirements Model), the FOCUS Converter (provider-native to FOCUS), and the FOCUS Requirements Model (machine-readable MUST/SHOULD/MAY rules).

### 2.3 Phased roadmap

**Phase 0: Validate what exists.** Pull a real invoice CSV plus an Insights extract, map the native fields, and run a representative sample through the FOCUS Validator to establish a concrete baseline. Confirm scope (cloud and GPU Droplets) and target version.

**Phase 1: Close the Mandatory gaps.** Reshape into FOCUS column IDs. Add the trivial constants and derivations (`BillingCurrency`, `InvoiceIssuerName`, `ProviderName`/`PublisherName`, `PricingQuantity`/`PricingUnit`, `ServiceCategory`, `ChargeCategory`, `ChargeClass`). Then do the substantive work: reconcile invoice-level credits, promos, prepayment commitments, and taxes back to usage lines so `BilledCost` and `EffectiveCost` are correct per row, and split `amount` into the four-cost model.

**Phase 2: Fix deviations.** Decompose the single cost figure cleanly across all SKU types (handle tiered bandwidth), separate `ResourceName` from `ChargeDescription`, stabilize `SkuId`/`SkuPriceId`, and emit `Tags` as key-value pairs if billing-line tags are added.

**Phase 3: Round out Conditional and Recommended.** Populate `BillingAccountType`, `SubAccountType`, `ResourceType`, `PricingCategory`, `ListUnitPrice`, `ServiceSubcategory`, and `ChargeFrequency` from existing product and project metadata. Add the commitment-discount family for prepay and GPU committed-use contracts so committed spend is visible on the lines it offsets.

**Phase 4: Mature to v1.4.** Adopt the Invoice Detail and billing-period datasets, drop `ProviderName`/`PublisherName`, and pursue certification once the Validator supports v1.4.

### 2.4 FOCUS Use Cases unlocked

Unlocked as soon as the reshape and trivial adds land (Phase 1), because day-level, resource-level, project-level data already exists:

- Analyze costs by service name (by ServiceName / product).
- Analyze service costs by subaccount (by project).
- Analyze cost per compute service for a subaccount (GPU and CPU Droplets per project).
- Analyze service costs by region.
- Identify anomalous daily spending by subaccount, region, and service.
- Analyze tag coverage (once billing-line tags are emitted).
- Report application cost month over month.

Unlocked once the cost columns are reconciled (Phase 1 substantive work):

- Compare billed cost per subaccount to budget.
- Determine Effective Savings Rate (and by service), once prepay and committed-use savings reach the lines.
- Forecast amortized costs and cashflow month over month.

Out of scope for DigitalOcean's model:

- Capacity-reservation use cases (no capacity reservations).
- Availability-zone use cases (regions, no zones).
- Some commitment-discount reporting applies only in the narrow prepay and GPU-contract cases, not the broad reserved-instance sense.

---

## Part 3: Immediate next steps

1. Pull a real invoice CSV and an Insights extract, and assemble the native-to-FOCUS field mapping from the column table above.
2. Run a representative sample through the FOCUS Validator to convert this manual pass into objective findings.
3. Decide v1.2 certification timing versus building straight to v1.4, and confirm the target representation against the FOCUS Requirements Model.
4. Scope the cost-reconciliation work: how credits, promo codes, prepayment commitments, and taxes can be allocated from invoice level back to usage lines.
5. Confirm whether resource (Droplet) tags can be surfaced on billing lines, and in key-value form.

---

## Confidence summary

- **High confidence:** the invoice CSV field set (amount, description, group_description, product, resource_uuid, duration, duration_unit, start_time, end_time, project, category), the Billing API surfaces, USD-only billing, monthly invoicing with daily preview, and day-level Insights. These are documented in DigitalOcean's official docs.
- **High confidence:** the FOCUS v1.2 feature levels. The bundled reference was cross-checked live against the FOCUS column library on 2026-06-30 and matched (all 57 columns, deprecations intact). No refresh was needed.
- **Medium confidence:** that credits, promo codes, prepayment commitments, and taxes are applied at invoice or balance level and not attached to usage lines. Documentation describes credits and purchase orders at the invoice level and states invoices do not reflect prepayments, which supports treating the cost split as substantive; a real CSV plus invoice would confirm the exact reconciliation needed.
- **Medium confidence:** that resource (Droplet) tags are not present on billing lines. Tags exist in the platform; their presence in the billing CSV is unconfirmed and is flagged for verification.
- **Provisional:** the precise mapping of DigitalOcean `category` values (such as `iaas`) and `product` names to FOCUS `ServiceCategory` and `ServiceName`, pending a real CSV sample.
- This score reflects the data source reviewed, not a formal FOCUS certification result.

Overall data quality of this analysis: solid on the documented data surfaces, provisional on invoice-level reconciliation specifics.

---

## Sources

- DigitalOcean Billing documentation: https://docs.digitalocean.com/platform/billing/
- DigitalOcean Invoices (CSV and project spend CSV): https://docs.digitalocean.com/platform/billing/invoices/
- DigitalOcean Billing API and CLI reference: https://docs.digitalocean.com/platform/billing/reference/
- DigitalOcean API reference (Billing): https://docs.digitalocean.com/reference/api/reference/billing/
- DigitalOcean GPU Droplets pricing: https://www.digitalocean.com/pricing/gpu-droplets
- FOCUS Specification: https://focus.finops.org/focus-specification/
- FOCUS column library: https://focus.finops.org/
- FOCUS Validator, Converter, and Requirements Model: https://focus.finops.org/

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
