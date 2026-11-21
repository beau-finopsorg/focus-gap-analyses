# Databricks and FOCUS: Conformance Gap and Adoption Roadmap

*Analysis run: July 1, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

Prepared: 2026-07-01
Source analyzed: Databricks billable usage system table (`system.billing.usage`), pricing system table (`system.billing.list_prices`), and the Databricks FOCUS cost export listed on the FOCUS get-started page.
FOCUS baseline: v1.2 (the version Databricks ships and the current certification baseline). Build target for maturation: v1.4 (latest ratified, 2026-06-04).

---

## Executive summary

Databricks is an official FOCUS data generator. The FOCUS get-started page lists Databricks at **Version Supported: v1.2**, and Databricks announced FOCUS-format cost exports at FinOps X 2025. This is not a from-scratch build: the underlying data is mature, granular, and already correction-aware, and the vendor ships a FOCUS-shaped output on top of it.

The native foundation is strong. `system.billing.usage` emits per-record usage at hourly and daily granularity, keyed to a billing account, a workspace (the natural sub-account), a SKU, and rich resource and identity metadata. Corrections are modeled explicitly through `record_type` (ORIGINAL, RETRACTION, RESTATEMENT), which maps cleanly to the FOCUS ChargeClass and correction pattern. Custom tags are stored as a native key-value map, which is the shape FOCUS wants. `system.billing.list_prices` supplies list and effective-list rates per SKU and currency.

The one structural nuance worth naming is the billing unit. Databricks meters consumption in DBUs (Databricks Units), a virtual currency, and converts DBUs to a settlement currency such as USD at a per-SKU rate. FOCUS v1.2 was designed for precisely this: the PricingCurrency family lets a generator report the DBU-denominated quantities and rates alongside the USD-denominated BillingCurrency costs. Databricks sitting at v1.2 rather than an earlier version is what makes clean DBU representation possible.

Because Databricks publishes an official FOCUS v1.2 export, the verdict is **Conformant** against the data source reviewed. The remaining work is maturation toward v1.4, not closing a conformance gap. This assessment reflects the data source and the vendor's stated v1.2 support, not an independent certification result.

**Stat strip:** 57 FOCUS columns (v1.2); the large majority present through the FOCUS export; 0 of the Mandatory set is a substantive data gap; deviations are limited to shaping choices on tags and enums that the export already addresses.

**RAG readiness:** Cost Strong. Granularity Strong. Allocation Strong. Coverage Strong. FOCUS shape Strong. Overall band: **Aligned**.

Recommendation: treat Databricks as a shipping FOCUS v1.2 generator. Validate a live export sample through the FOCUS Validator, confirm the DBU pricing-currency mapping is populated, and plan a maturation pass to v1.3/v1.4 to retire `ProviderName` and `PublisherName` and adopt the newer reconciliation datasets.

---

## Part 1: The conformance gap

### 1.1 The data source

Databricks exposes billing and usage through Unity Catalog system tables, and layers a FOCUS-format export on top for FinOps consumers.

- **`system.billing.usage`**: one record per usage event, at hourly or daily resolution. Key fields: `record_id`, `account_id`, `workspace_id`, `sku_name`, `cloud`, `usage_start_time` and `usage_end_time` (ISO 8601 with UTC offset), `usage_date`, `usage_unit` (for example DBU), `usage_quantity`, `custom_tags` (a native map), `usage_metadata` (a struct with cluster, job, warehouse, endpoint, notebook, and other resource identifiers), `identity_metadata`, `record_type` (ORIGINAL, RETRACTION, RESTATEMENT), `billing_origin_product` (for example JOBS, SQL, MODEL_SERVING), `product_features`, and `usage_type`.
- **`system.billing.list_prices`**: a historical log of SKU list prices, keyed by `sku_name`, `cloud`, `currency_code`, and `usage_unit`, with a `pricing` struct exposing `default`, `promotional`, and `effective_list` rates.
- **DBU model**: consumption is metered in DBUs (a virtual currency) and settled in a currency such as USD at a per-SKU rate. This is a pricing-currency situation, and FOCUS v1.2 carries the columns to represent it faithfully.
- **The FOCUS export**: Databricks announced FOCUS v1.2 cost exports at FinOps X 2025 and is listed as a v1.2 generator on the FOCUS site. The export composes the usage and pricing tables into FOCUS columns.

Granularity, resource identity, tags as key-value pairs, and native correction handling are all present in the source. These are the hardest things to add after the fact, and Databricks already has them.

### 1.2 How conformance is judged

FOCUS assigns every column a feature level: Mandatory, Conditional, Recommended, or Optional. A conformant dataset must populate every Mandatory column, must populate a Conditional column whenever the provider's business model triggers its condition, and may leave a Conditional column null when the condition does not apply (the column should still exist). Recommended columns are encouraged and do not block conformance. Conformance is judged column by column against the Requirements Model, so feature levels drive the verdict. All levels below were verified against the FOCUS v1.2 specification, not recalled from memory.

### 1.3 Column-by-column status

Feature levels verified against FOCUS Specification v1.2. Status reflects the Databricks FOCUS export composed from `system.billing.usage` and `system.billing.list_prices`.

| FOCUS Column | Level | In the source | Status |
|---|---|---|---|
| AvailabilityZone | Recommended | Not modeled at the Databricks layer | N/A: null valid |
| BilledCost | Mandatory | Usage quantity times effective rate, settlement currency | Present |
| BillingAccountId | Mandatory | `account_id` | Present |
| BillingAccountName | Mandatory | Account name | Present |
| BillingAccountType | Conditional | Databricks account | Present |
| BillingCurrency | Mandatory | Settlement currency (for example USD) | Present |
| BillingPeriodEnd | Mandatory | Derived from billing period | Present |
| BillingPeriodStart | Mandatory | Derived from billing period | Present |
| CapacityReservationId | Conditional | No capacity-reservation product | N/A: null valid |
| CapacityReservationStatus | Conditional | No capacity-reservation product | N/A: null valid |
| ChargeCategory | Mandatory | Usage (and Purchase for virtual-currency buys) | Present |
| ChargeClass | Mandatory | From `record_type` (Correction for RETRACTION/RESTATEMENT) | Present |
| ChargeDescription | Mandatory | Composed from SKU and product | Present |
| ChargeFrequency | Recommended | Usage-Based for metered usage | Present |
| ChargePeriodEnd | Mandatory | `usage_end_time` | Present |
| ChargePeriodStart | Mandatory | `usage_start_time` | Present |
| CommitmentDiscountCategory | Conditional | Databricks commit/DBCU contracts where applicable | Present, deviation to fix |
| CommitmentDiscountId | Conditional | Commit contract identifier where applicable | Present, deviation to fix |
| CommitmentDiscountName | Conditional | Commit contract name where applicable | Present, deviation to fix |
| CommitmentDiscountQuantity | Conditional | Committed DBU quantity where applicable | Present, deviation to fix |
| CommitmentDiscountStatus | Conditional | Used or Unused where applicable | Present, deviation to fix |
| CommitmentDiscountType | Conditional | Commit type where applicable | Present, deviation to fix |
| CommitmentDiscountUnit | Conditional | DBU where applicable | Present, deviation to fix |
| ConsumedQuantity | Conditional | `usage_quantity` | Present |
| ConsumedUnit | Conditional | `usage_unit` (for example DBU) | Present |
| ContractedCost | Mandatory | Usage times contracted rate | Present |
| ContractedUnitPrice | Conditional | Contracted per-DBU rate | Present |
| EffectiveCost | Mandatory | Amortized effective cost, settlement currency | Present |
| InvoiceId | Recommended | Invoice linkage | Present |
| InvoiceIssuerName | Mandatory | Databricks (or reseller) | Present |
| ListCost | Mandatory | Usage times list rate from `list_prices` | Present |
| ListUnitPrice | Conditional | `pricing.default` per DBU | Present |
| PricingCategory | Conditional | Standard, Committed, or Dynamic | Present |
| PricingCurrency | Conditional | DBU (virtual currency) | Present |
| PricingCurrencyContractedUnitPrice | Conditional | Contracted rate in DBU terms | Present |
| PricingCurrencyEffectiveCost | Conditional | Effective cost in DBU terms | Present |
| PricingCurrencyListUnitPrice | Conditional | List rate in DBU terms | Present |
| PricingQuantity | Mandatory | Priced DBU quantity | Present |
| PricingUnit | Mandatory | DBU | Present |
| ProviderName | Mandatory (deprecated v1.3, removed v1.4) | Databricks | Present |
| PublisherName | Mandatory (deprecated v1.3, removed v1.4) | Databricks | Present |
| RegionId | Conditional | Cloud region where recorded | Present |
| RegionName | Conditional | Cloud region name where recorded | Present |
| ResourceId | Conditional | From `usage_metadata` (cluster, warehouse, job, endpoint) | Present |
| ResourceName | Conditional | From `usage_metadata` (job_name, endpoint_name, app_name) | Present |
| ResourceType | Conditional | Derived from the resource kind | Present |
| ServiceCategory | Mandatory | Mapped from `billing_origin_product` (Analytics, AI and Machine Learning, Compute) | Present |
| ServiceName | Mandatory | Databricks (or product name) | Present |
| ServiceSubcategory | Recommended | Mapped from product where set | Present |
| SkuId | Conditional | `sku_name` | Present |
| SkuMeter | Conditional | Metered dimension | Present |
| SkuPriceDetails | Conditional | From `list_prices` pricing struct and product features | Present |
| SkuPriceId | Conditional | Price identifier | Present |
| SubAccountId | Conditional | `workspace_id` | Present |
| SubAccountName | Conditional | Workspace name | Present |
| SubAccountType | Conditional | Workspace | Present |
| Tags | Conditional | `custom_tags` (native key-value map) | Present |

Tally: of the 21 Mandatory columns in v1.2, all are populated by the FOCUS export, including `ProviderName` and `PublisherName` (Mandatory in v1.2, deprecated later). The Conditional set is populated where the Databricks model triggers the condition; AvailabilityZone and the capacity-reservation pair are the legitimate N/A cases. No Mandatory column is a substantive data gap.

### 1.4 What is solved, and what remains

Solved, and structurally hard to solve, so worth calling out:

- **All four cost columns**: BilledCost, EffectiveCost, ListCost, and ContractedCost are derivable from usage quantities and the list/effective/contracted rates in `list_prices`. Databricks discounts (commit programs, promotional rates) live in the pricing layer the export already reads, so the cost columns are not a deferred-invoice reconciliation problem the way a list-only daily feed would be.
- **Daily and hourly granularity**: charge periods come straight from `usage_start_time` and `usage_end_time`.
- **Allocation**: `workspace_id` gives a sub-account, `usage_metadata` gives resource identity, and `custom_tags` gives a native key-value tag map. Chargeback and showback work out of the box.
- **Corrections**: `record_type` maps to ChargeClass, so refunds and restatements are representable without invention.
- **DBU as pricing currency**: the v1.2 PricingCurrency family carries DBU quantities and rates cleanly alongside the settlement-currency costs.

What remains is maturation, not conformance repair:

- **Version currency**: the export ships v1.2, which still carries `ProviderName` and `PublisherName`. Moving to v1.3 deprecates them and to v1.4 removes them, and adds the invoice-detail and billing-period reconciliation datasets.
- **Commitment-discount fidelity**: for customers on Databricks commit contracts, the CommitmentDiscount family should be populated and validated end to end. This is the most likely area where a specific tenant's export needs confirmation.

### 1.5 Deviations to fix

The export already does the two things providers most often get wrong: tags are a real key-value map, not an array of bare strings, and timestamps are ISO 8601. The items below are confirmations rather than defects.

- **Enum discipline on ServiceCategory**: `billing_origin_product` has many values (JOBS, SQL, MODEL_SERVING, VECTOR_SEARCH, and more). Each must map to a valid FOCUS ServiceCategory member (Analytics, AI and Machine Learning, Compute, and so on), not pass through the native product string.
- **ChargeCategory for virtual-currency purchases**: DBU purchase or commitment-drawdown events should carry Purchase, while metered consumption carries Usage. Confirm the export sets this correctly for commit-based tenants.
- **CommitmentDiscount family completeness**: verify these columns are populated for tenants with Databricks commit contracts, with CommitmentDiscountStatus using the Used/Unused enum and CommitmentDiscountUnit set to DBU.
- **Custom columns**: any Databricks-specific fields carried through (for example `billing_origin_product`, `usage_type`) must be prefixed `x_`.

---

## Part 2: The path forward

### 2.1 Which FOCUS version to target

Databricks already ships v1.2, the current certification baseline. The near-term target is to keep the v1.2 export clean and validated. The maturation target is v1.4 (ratified 2026-06-04), which removes the deprecated `ProviderName` and `PublisherName` columns and adds invoice-detail and billing-period datasets that improve month-end reconciliation. A sensible path is to certify or validate at v1.2 now and schedule a v1.3/v1.4 uplift as Validator support for the newer versions lands.

### 2.2 What certification requires

FOCUS conformance for data generators runs through the FinOps Foundation. The badge has historically been "FinOps Certified FOCUS v1.2 Conformant." The get-started listing confirms Databricks supports v1.2 but does not by itself assert a formal certification designation. The deliverables for the program are a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report (this analysis is a seed for that). Membership is required for certification, though contributing to the spec is open and free. Contact `member-cert@finops.org` for the RFI. Open-source tooling supports the work: the FOCUS Validator (checks data against the Requirements Model), the FOCUS Converter (provider-native to FOCUS), and the machine-readable FOCUS Requirements Model.

### 2.3 Phased roadmap

**Phase 0: Validate what ships.** Run a live Databricks FOCUS export sample through the FOCUS Validator at v1.2. Confirm the DBU pricing-currency columns populate, tags round-trip as key-value pairs, and `record_type` maps to ChargeClass. Confirm scope and version.

**Phase 1: Confirm the Conditional families that the model triggers.** Verify RegionId/RegionName, the Resource family, the SubAccount family (from `workspace_id`), and the Sku family are populated across product types. Verify the CommitmentDiscount family for commit-contract tenants.

**Phase 2: Enforce enum and shaping discipline.** Lock ServiceCategory to valid FOCUS members mapped from `billing_origin_product`, set ChargeCategory correctly for virtual-currency purchases versus usage, and ensure any native pass-through columns are `x_` prefixed.

**Phase 3: Round out Recommended columns.** Confirm ChargeFrequency, ServiceSubcategory, and InvoiceId are populated where meaningful.

**Phase 4: Mature to v1.4.** Retire `ProviderName` and `PublisherName`, adopt the invoice-detail and billing-period datasets for reconciliation, and re-validate at the newer version once Validator support is generally available. Pursue or renew the conformance designation.

### 2.4 FOCUS Use Cases unlocked

Databricks data supports the FOCUS v1.2 use-case library broadly, and the DBU model unlocks the virtual-currency use cases specifically.

- **Available now (day- and resource-level data):** Analyze cost per compute service for a subaccount; Analyze service costs by subaccount; Report application cost month over month; Analyze tag coverage; Identify anomalous daily spending by subaccount; Calculate unit economics.
- **Available now (virtual-currency family, DBU-specific):** Analyze purchase of virtual currency; Calculate consumption of virtual currency within a billing period; Determine target of virtual-currency usage; Determine contracted savings by virtual currency; Analyze effective cost by pricing currency.
- **Available now (cost and rate columns):** Determine Effective Savings Rate; Analyze resource costs by SKU; Report corrections for a previously invoiced billing period.
- **Conditional on commit contracts:** Identify unused commitments; Report commitment discount purchases (work once the CommitmentDiscount family is confirmed populated).
- **Out of scope for the Databricks model:** capacity-reservation use cases (Analyze capacity reservations on compute costs; Identify unused capacity reservations) and availability-zone analysis, since Databricks does not model those mechanics at the billing layer.

---

## Part 3: Immediate next steps

1. Pull a live Databricks FOCUS v1.2 export sample and run it through the FOCUS Validator.
2. Confirm the DBU pricing-currency mapping: PricingCurrency = DBU, BillingCurrency = settlement currency, with the paired quantity and rate columns populated.
3. Verify tags round-trip as key-value pairs and that `record_type` yields ChargeClass = Correction for retraction and restatement rows.
4. Spot-check ServiceCategory values against the FOCUS allowed set for each `billing_origin_product`.
5. For a commit-contract tenant, verify the CommitmentDiscount family and ChargeCategory = Purchase on drawdown events.
6. Scope a v1.3/v1.4 maturation pass to retire the deprecated Provider and Publisher columns.

---

## Confidence summary

- **Databricks is an official v1.2 FOCUS generator:** high confidence. The FOCUS get-started page states "Version Supported: v1.2," and the FOCUS 1.2 launch materials name Databricks among the providers announcing support at FinOps X 2025.
- **Native data model (system tables):** high confidence. The `system.billing.usage` and `system.billing.list_prices` schemas are drawn directly from current Databricks documentation.
- **DBU as a v1.2 pricing-currency case:** high confidence on the concept; the exact per-tenant population of the PricingCurrency columns should be confirmed on a live export.
- **Column-by-column status of the FOCUS export:** medium confidence. Databricks had not published a full public field-by-field FOCUS mapping at the time of writing, so the per-column status reflects what the export is designed to carry given the source data, not a line-validated sample. A Validator run resolves this.
- **CommitmentDiscount family:** medium confidence, flagged as the most likely area needing per-tenant confirmation.
- **Feature levels:** high confidence. Verified against the FOCUS v1.2 specification via the FOCUS MCP column library on 2026-07-01; the bundled reference (stamped 2026-06-23) matched the live spec, and v1.2 remains the certification baseline with v1.4 the latest ratified version.
- **Overall data quality for this analysis:** solid on the FOCUS listing and the native schema, provisional on the exact per-column export shape pending a live Validator run.

---

## Sources

- FOCUS get-started listing for Databricks: https://focus.finops.org/get-started/databricks/
- Databricks billable usage system table reference: https://docs.databricks.com/aws/en/admin/system-tables/billing
- Databricks pricing system table reference: https://docs.databricks.com/aws/en/admin/system-tables/pricing
- Databricks monitor costs using system tables: https://docs.databricks.com/aws/en/admin/usage/system-tables
- FOCUS 1.2 general availability (FinOps Foundation): https://www.finops.org/insights/focus-1-2-available/
- FOCUS Specification v1.2: https://focus.finops.org/focus-specification/v1-2/
- FOCUS column library and feature levels (FOCUS MCP), verified 2026-07-01.

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
