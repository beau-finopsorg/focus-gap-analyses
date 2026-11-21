# Neo4j Aura and FOCUS: Conformance Gap Analysis

*Analysis run: September 18, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Provider:** Neo4j (Aura, Neo4j's managed graph database and analytics platform)
**Product in scope:** Aura's paid tiers (AuraDB Professional, AuraDB Business Critical, AuraDS, Aura Graph Analytics, GraphQL API), billing exposed through the Aura API v2beta1 Billing resource (`/organizations/{org_id}/billing/usage` and `/organizations/{org_id}/billing/ledger`)
**Prepared:** 2026-09-18
**Source analyzed:** Aura API v2beta1 OpenAPI specification (`https://api.neo4j.io/v2beta1/spec.json`), the `UsageData` and `LedgerData` schemas it defines, the Aura Instances/Projects/Organizations resources (v1 and v2beta1), and the Aura billing documentation (billing dimensions, payment options, cost explorer)
**FOCUS baseline:** v1.2 (current certification baseline)
**Build target:** v1.4 (latest ratified)
**Status:** Neo4j is not listed as a Supported FOCUS data generator on focus.finops.org/get-started. This analysis assesses readiness only; it is not a conformance result and does not reflect any FinOps Certified FOCUS designation.

---

## Executive summary

Neo4j Aura is the most FOCUS-shaped native billing schema seen in this series to date, and that is by design: according to Neo4j, the Billing API was deliberately built with FOCUS alignment in mind rather than backed into it after the fact. The `UsageData` object returned by the new Billing API (Aura API v2beta1, in beta as of this writing) already carries `charge_period_start`, `charge_period_end`, `consumed_quantity`, `consumed_unit`, `list_cost`, `list_unit_price`, `resource_id`, `resource_name`, `resource_type`, `region_id`, `billing_account_id`, and `invoice_issuer_name`, snake_case siblings of the FOCUS column IDs of the same meaning. Aura's account hierarchy is also clean: organization is the billing account, project is a genuine sub-account (`project_id` / `project_name`), and every row is scoped to a single instance or session (`resource_id`). Usage rows are period-scoped by `charge_period_start` / `charge_period_end`, and the documented examples are day-scoped even though Aura's pay-as-you-go invoicing runs monthly, so sub-monthly charge records are available.

Three things hold this back from being straightforward. First, the API returns list cost only: `list_cost` and `list_unit_price` are the only cost fields on the row, and the credit ledger (`/billing/ledger`) reports an aggregate remaining balance per organization, not a per-row discount or reconciliation. `BilledCost`, `EffectiveCost`, and (for negotiated prepaid contracts) `ContractedCost` all require work Neo4j's API does not yet do. Second, Aura sells a genuine commitment-discount construct, prepaid Aura Consumption Units (ACUs) purchased under a minimum one-year contract, but nothing in the usage row says whether a given charge drew against that commitment or spilled over to pay-as-you-go rates, so the entire CommitmentDiscount column family is a real, triggered gap rather than an N/A. Third, Aura has no user-defined tags or labels anywhere in its API surface (Instances, Projects, Organizations, or Usage), so `Tags` is a genuine product gap, not just a reporting one.

**Stat strip:** 57 FOCUS columns (v1.2). 20 present (14 clean, 6 carrying a deviation to fix). 3 of 13 missing Mandatory columns are substantive (`BilledCost`, `ContractedCost`, `EffectiveCost`); the other 10 are plumbing. 6 deviations to fix, mostly a non-currency `pricing_currency` value ("credits") and raw internal codes that need display-value mapping.

**Recommendation:** Treat the Billing API's `UsageData` rows as the FOCUS charge record; the identity and granularity columns need little more than a field rename. The real work is building the cost family (reconciling ACU-denominated list cost into billed and effective dollar figures, with commitment-discount attribution) and deciding how to represent tags, which do not exist in the product today.

### Readiness (RAG)

| Dimension | Rating |
|---|---|
| Cost | Partial |
| Granularity | Strong |
| Allocation | Partial |
| Coverage | Partial |
| FOCUS shape | Partial |
| **Overall band** | **Structured** |

---

## Part 1: The conformance gap

### 1.1 The data source

Neo4j shipped a dedicated Billing API in the Aura API v2beta1 (currently beta), announced in the Aura changelog as "New Billing API in Aura API v2beta1." It exposes two endpoints, both scoped to an Aura organization and rate-limited to 10 requests per organization per 24 hours, with data refreshed once daily and lagging up to 48 hours behind real-time changes:

- **`GET /organizations/{org_id}/billing/usage`**: returns an array of `UsageData` rows for a `start`/`end` RFC3339 time range and a `project_id`. Each row carries `organization_id`, `billing_account_id`, `billing_account_type` (example: `payg`), `payment_method` (example: `creditcard`), `project_id`, `project_name`, `resource_id`, `resource_name`, `resource_type` (example: `Instance`), `region_id`, `cloud_service_provider` (`aws` / `gcp` / `azure`), `service_name` (example: `Primary DB`), `base_sku` (example: `professional.aws.primary_db.1gb`), `tier` (example: `business_critical`), `charge_period_start`, `charge_period_end`, `consumed_quantity`, `consumed_unit` (example: `GB-hours`), `billable_size` and `billable_size_unit`, `list_unit_price`, `list_cost`, `pricing_currency` (example: `credits`), and `invoice_issuer_name` (example: `direct`).
- **`GET /organizations/{org_id}/billing/ledger`**: returns `LedgerData` rows: `organization_id`, `billing_account_id`, `balance_date`, `initial_credit_quantity`, and `remaining_credit_quantity`. This is a periodic balance snapshot, not an itemized purchase or discount ledger.

Characteristics relevant to FOCUS:

- **Native field names:** snake_case, but semantically close to FOCUS. `charge_period_start`/`charge_period_end`, `consumed_quantity`/`consumed_unit`, `list_cost`/`list_unit_price`, and `resource_id`/`resource_name`/`resource_type` need a rename, not a redesign.
- **Granularity:** the documented row examples are day-scoped (`charge_period_start`/`end` one day apart) even though Aura's pay-as-you-go plan invoices monthly for the prior month's usage, so the usage feed already carries finer granularity than the invoice.
- **Currency:** Aura prices everything in Aura Consumption Units (ACUs), a proprietary unit that aggregates usage across billing dimensions (GB-hours, GB-minutes, MB-hours, GB). The `pricing_currency` field's example value is literally `"credits"`, not an ISO 4217 code. Aura's public list prices are USD-denominated ($65/GB/month for Professional, $146/GB/month for Business Critical), so a USD figure is derivable, but the API does not hand it over as a currency-coded amount today.
- **Account hierarchy:** organization (`organization_id`) is the natural billing account, though the row also carries a separate `billing_account_id`, meaning organization and billing account are not guaranteed to be the same entity; project (`project_id` / `project_name`) is a clean sub-account; `resource_id` identifies the instance or session.
- **Tags:** absent. Neither the Billing API nor the general-purpose Instances, Projects, or Organizations resources (v1 or v2beta1) expose a user-defined tag or label field anywhere. This is a product-level gap, not a reporting omission.
- **SKU:** `base_sku` is a composite dotted string encoding tier, cloud provider, component, and size (e.g., `professional.aws.primary_db.1gb`), a strong basis for `SkuId` and for deriving `ServiceSubcategory`, `ResourceType` detail, and `SkuMeter`.
- **Billing model:** Aura offers two payment tracks: pay-as-you-go (credit card or marketplace, billed monthly, no expiration) and prepaid (minimum one-year commitment, ACUs purchased up front, sales-assisted). Prepaid ACUs and any promotional or proof-of-concept credit both function as commitment-style discounts, but the Billing API does not mark which usage rows draw against them.
- **Marketplace resale:** Aura sells through the AWS, GCP, and Azure marketplaces in addition to direct billing. `invoice_issuer_name` (example: `direct`) is the intended signal for this, and FOCUS requires `BilledCost` to be 0 for marketplace-billed charges since the hyperscaler, not Neo4j, collects payment.

### 1.2 How conformance is judged

FOCUS assigns every column a feature level: Mandatory (must be present and populated), Conditional (required when the provider's business model triggers the condition), Recommended, or Optional. Conformance is judged column by column against the FOCUS Requirements Model. A dataset is conformant when every Mandatory column is present and correctly typed, every applicable Conditional column is populated, and values honor FOCUS allowed-value sets and formats.

Feature levels in this report were taken from the verified v1.2 reference and spot-checked live against the FOCUS specification (`ServiceSubcategory` Recommended, `ChargeClass` Mandatory-nullable, `ContractedCost`/`EffectiveCost`/`BilledCost` cost-family semantics) on 2026-09-18 via the FOCUS specification MCP. The bundled reference was current: v1.2 (57 columns) remains the certification baseline and v1.4 (123 columns, ratified 2026-06-04) is the latest ratified version.

### 1.3 Column-by-column status

Legend: Present; Present, deviation to fix; Missing: Mandatory; Missing: Recommended; Missing: Conditional; N/A: null valid.

| FOCUS Column | Level | In the source? | Status |
|---|---|---|---|
| AvailabilityZone | R | No (Business Critical spans zones automatically; zone is not user-visible or API-exposed) | Missing: Recommended |
| BilledCost | M | No (only `list_cost`; no discount/credit reconciliation) | Missing: Mandatory (substantive) |
| BillingAccountId | M | `billing_account_id` | Present |
| BillingAccountName | M | Organization name (via Organizations resource; not on the usage row) | Present, deviation to fix |
| BillingAccountType | C | `billing_account_type` (example `payg`) | Present, deviation to fix |
| BillingCurrency | M | `pricing_currency` (example `credits`, not ISO 4217) | Present, deviation to fix |
| BillingPeriodEnd | M | No (only `charge_period_end`; billing cycle not returned per row) | Missing: Mandatory (trivial) |
| BillingPeriodStart | M | No | Missing: Mandatory (trivial) |
| CapacityReservationId | C | No | N/A: null valid |
| CapacityReservationStatus | C | No | N/A: null valid |
| ChargeCategory | M | No (endpoint returns usage rows only) | Missing: Mandatory (trivial) |
| ChargeClass | M | No | Missing: Mandatory (trivial) |
| ChargeDescription | M | Derivable from `service_name` / `base_sku` | Missing: Mandatory (trivial) |
| ChargeFrequency | R | Derivable (Aura is consumption-billed, not subscription) | Missing: Recommended (trivial) |
| ChargePeriodEnd | M | `charge_period_end` | Present |
| ChargePeriodStart | M | `charge_period_start` | Present |
| CommitmentDiscountCategory | C | No (prepaid ACU contracts exist; not attributed per row) | Missing: Conditional |
| CommitmentDiscountId | C | No | Missing: Conditional |
| CommitmentDiscountName | C | No | Missing: Conditional |
| CommitmentDiscountQuantity | C | No | Missing: Conditional |
| CommitmentDiscountStatus | C | No | Missing: Conditional |
| CommitmentDiscountType | C | No | Missing: Conditional |
| CommitmentDiscountUnit | C | No | Missing: Conditional |
| ConsumedQuantity | C | `consumed_quantity` | Present |
| ConsumedUnit | C | `consumed_unit` | Present |
| ContractedCost | M | Defaults to List Cost for PAYG; unknown for negotiated prepaid contracts | Missing: Mandatory (mixed: trivial for PAYG, substantive for contract accounts) |
| ContractedUnitPrice | C | Same as above | Missing: Conditional (mixed) |
| EffectiveCost | M | No (needs credit/commitment amortization against the ledger) | Missing: Mandatory (substantive) |
| InvoiceId | R | No | Missing: Recommended |
| InvoiceIssuerName | M | `invoice_issuer_name` (example `direct`) | Present, deviation to fix |
| ListCost | M | `list_cost` | Present |
| ListUnitPrice | C | `list_unit_price` | Present |
| PricingCategory | C | Derivable from `billing_account_type` (payg vs. prepaid contract) | Missing: Conditional (trivial-ish, tied to the commitment-discount gap) |
| PricingCurrency | C | `pricing_currency` (same "credits" issue as BillingCurrency) | Present, deviation to fix |
| PricingCurrencyContractedUnitPrice | C | No (no local-currency price sheets found) | N/A: null valid |
| PricingCurrencyEffectiveCost | C | No | N/A: null valid |
| PricingCurrencyListUnitPrice | C | No | N/A: null valid |
| PricingQuantity | M | `consumed_quantity` (flat-rate meters) | Missing: Mandatory (trivial) |
| PricingUnit | M | `consumed_unit` | Missing: Mandatory (trivial) |
| ProviderName | M | No (fixed literal) | Missing: Mandatory (trivial) |
| PublisherName | M | No (fixed literal, differs for marketplace resale) | Missing: Mandatory (trivial) |
| RegionId | C | `region_id` | Present |
| RegionName | C | Derivable via a static cloud-provider region-code lookup | Missing: Conditional (trivial) |
| ResourceId | C | `resource_id` | Present |
| ResourceName | C | `resource_name` | Present |
| ResourceType | C | `resource_type` (example `Instance`) | Present |
| ServiceCategory | M | Mostly fixed literal (`Databases`); Aura Graph Analytics/GraphQL API need review | Missing: Mandatory (trivial) |
| ServiceName | M | `service_name` | Present |
| ServiceSubcategory | R | Derivable from `base_sku` (primary/secondary DB, backup, session, GraphQL) | Missing: Recommended (trivial) |
| SkuId | C | `base_sku` | Present, deviation to fix |
| SkuMeter | C | Derivable from `base_sku` segments | Missing: Conditional (trivial) |
| SkuPriceDetails | C | No | Missing: Conditional |
| SkuPriceId | C | No | Missing: Conditional |
| SubAccountId | C | `project_id` | Present |
| SubAccountName | C | `project_name` | Present |
| SubAccountType | C | No (all projects are the same construct) | N/A: null valid |
| Tags | C | No (no user-defined tag or label field anywhere in the Aura API) | Missing: Conditional (substantive) |

**Reading the tally:** Of 57 v1.2 columns, 20 are Present (14 clean, 6 carrying a deviation to fix), 13 Mandatory are missing (10 trivially derivable or fixed-literal, 3 substantive: `BilledCost`, `ContractedCost`, `EffectiveCost`), 4 Recommended are missing (all trivially derivable), 14 Conditional are missing where the model plausibly triggers them (the full commitment-discount family, `Tags`, and SKU/region detail), and 6 Conditional columns are legitimately N/A (capacity reservations, the three pricing-currency conversion columns, and sub-account type).

### 1.4 What is solved, and what remains

**Solved (identity and granularity are the real strength):** Aura's Billing API already returns period-scoped usage rows with a clean organization-to-project-to-resource hierarchy. `organization_id` / `billing_account_id` map to the billing account, `project_id` / `project_name` map directly to `SubAccountId` / `SubAccountName`, and `resource_id` / `resource_name` / `resource_type` give resource identity. `charge_period_start` / `charge_period_end` are day-scoped in the documented examples, ahead of the monthly PAYG invoice cycle. `list_cost`, `list_unit_price`, `consumed_quantity`, `consumed_unit`, and `region_id` all map onto their FOCUS counterparts with no transformation beyond a field rename.

**The trivial Mandatory gaps (10 of 13):** derivable from fields already present, or fixed literals, so adding them is plumbing:

- `ChargeCategory`: the `/usage` endpoint returns usage rows only, so this is a fixed literal `Usage` for every row it returns; purchase, credit, and tax events are not evidenced in this endpoint today.
- `ChargeDescription`: composable from `service_name` and `base_sku`.
- `ChargeClass`: Mandatory but nullable, populated only to flag a correction to a previously invoiced period.
- `PricingQuantity` / `PricingUnit`: equal to `consumed_quantity` / `consumed_unit` for Aura's flat GB-hour and GB-minute meters; verify this holds for the storage-overage dimension, which is a step function above the free quota rather than a flat rate.
- `ProviderName`, `PublisherName`: fixed literals (`Neo4j`), except where a cloud marketplace resells Aura, where `PublisherName` should reflect the marketplace.
- `ServiceCategory`: `Databases` for AuraDB and AuraDS rows; Aura Graph Analytics and the GraphQL API may warrant a different category and should be reviewed against the current FOCUS `ServiceCategory` allowed-value list rather than assumed.
- `BillingPeriodStart` / `BillingPeriodEnd`: not returned per row, but recoverable as the calendar-month boundary containing `charge_period_start` for pay-as-you-go accounts. Confirm whether prepaid-contract billing periods follow the same calendar-month convention or the contract's own cycle.

**The substantive Mandatory gaps (3 of 13):**

- `BilledCost` and `EffectiveCost`: the API returns list cost only. There is no per-row discount, credit, or commitment-amortization figure. The `/billing/ledger` endpoint gives an aggregate `remaining_credit_quantity` per organization, not a per-usage-row credit draw, so producing `BilledCost` and `EffectiveCost` requires a real reconciliation step: converting ACU-denominated list cost into a settlement currency, then allocating ledger-level credit consumption and any negotiated discount back down to the usage rows. Marketplace-billed rows (`invoice_issuer_name` other than `direct`) should carry `BilledCost` of 0 per the FOCUS requirement that the paying party, not Neo4j, is invoicing.
- `ContractedCost`: FOCUS defines this as defaulting to `ListCost` when no negotiated discount applies, which makes it trivial for pay-as-you-go accounts. For prepaid-contract accounts, Aura's blended discount on committed ACUs is a real negotiated rate that the usage row does not expose, making this substantive for that customer segment specifically.

This is the list-cost trap in a more pronounced form than usual: unlike providers whose usage rows at least carry a per-line discount field, Aura's `UsageData` object exposes nothing beyond list price. Do not treat `BilledCost` and `EffectiveCost` as a trivial derivation of `ListCost`.

**The standout Conditional gap: commitment-discount attribution.** Aura's prepaid ACU contract, a minimum one-year commitment purchased up front at a blended rate, is a genuine commitment-discount construct under FOCUS's definition, not a business model that legitimately nulls the column family. But nothing in `UsageData` says whether a given charge drew against the prepaid commitment or spilled over to pay-as-you-go pricing, and the ledger only reports the aggregate remaining balance. The entire `CommitmentDiscount*` family (`CommitmentDiscountId`, `CommitmentDiscountStatus`, and the rest) is therefore correctly classified as Missing: Conditional, not N/A, for any organization with a prepaid contract. This is worth flagging distinctly from other gap analyses in this series where the equivalent family is legitimately N/A because the provider sells no commitment mechanic at all.

**`Tags`: a product gap, not just a reporting one.** Neither the Billing API nor the Instances, Projects, or Organizations resources (checked against both the stable v1 and the v2beta1 OpenAPI specifications) expose a user-defined tag or label field anywhere in the Aura platform. Closing this gap requires Aura to add tagging as a product feature before it can be surfaced in billing data; it cannot be solved by the billing pipeline alone.

### 1.5 Deviations to fix

- **`pricing_currency` is not a currency:** the field's documented example value is `"credits"`, Aura's internal ACU-derived unit, not an ISO 4217 code. Both `BillingCurrency` and `PricingCurrency` need a real settlement currency (Aura's published list prices are USD), which means resolving the credits-to-dollars rate rather than emitting the native value as-is.
- **`billing_account_type` and other native codes need display-value mapping:** FOCUS's `BillingAccountType` requires "a consistent, readable display value," and `payg` is a code, not a display string (compare "Pay As You Go"). The same applies to any other short internal codes surfaced verbatim.
- **`invoice_issuer_name` needs normalization:** the example value `direct` should map to the actual issuer's name (`Neo4j`); marketplace-billed rows need the marketplace's proper issuer name (e.g., `Amazon Web Services`), not a generic non-`direct` code.
- **`base_sku` is a composite string, not an opaque SKU ID:** using it directly for `SkuId` works, but its dotted-segment structure (tier, cloud provider, component, size) should be parsed once into `ServiceSubcategory`, `SkuMeter`, and pricing-detail fields rather than re-parsed downstream by every consumer.
- **`BillingAccountName` is sourced off the usage row:** it comes from the Organizations resource (`OrganizationDetails.name`), which is a join, not a native field on `UsageData`. Because `UsageData` also separately carries a `billing_account_id` distinct from `organization_id`, confirm whether they are always 1:1 before assuming the organization's name is the billing account's name.
- **`cloud_service_provider` (`aws`/`gcp`/`azure`) is not `ProviderName`:** it identifies the underlying hyperscaler hosting the instance, a useful attribute with no dedicated FOCUS v1.2 column. Emit it as a custom column (`x_CloudServiceProvider`) per FOCUS's custom-column convention rather than conflating it with `ProviderName`, which must remain the fixed literal `Neo4j`.

**Already done right:** day-scoped, period-bounded usage rows ahead of the monthly invoice cycle; a clean organization-to-project-to-resource hierarchy that maps directly to billing account, sub-account, and resource; a rich `base_sku` field; explicit `resource_type` and `region_id`; and an `invoice_issuer_name` field that already anticipates the marketplace-resale case FOCUS specifically calls out for `BilledCost`.

---

## Part 2: The path forward

### 2.1 Which FOCUS version to target

Baseline the build against v1.2, the current certification badge version, and design toward v1.4, the latest ratified release. The account hierarchy, granularity, and identity columns are all v1.2-stable. `ProviderName` and `PublisherName` are deprecated in v1.3 and removed in v1.4, so the fixed-literal adds for those two columns are v1.2-scoped work that should be dropped when a build targets v1.3 or later. v1.4's Invoice Detail and billing-period datasets are a natural fit for Aura's invoice cycle and the ledger's balance-tracking model, which is an advantage for Neo4j when it matures past v1.2.

### 2.2 What certification requires

FOCUS conformance for data generators runs through the FinOps Foundation. Neo4j is not currently listed as a Supported data generator, so the first milestone is producing a FOCUS export at all; the Conformant designation is earned later by submitting a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report (this analysis is its seed). Membership is required for certification; contributing to the spec is open and free. Contact `member-cert@finops.org` for the RFI. Validate output with the open-source FOCUS Validator against the Requirements Model, and consider the FOCUS Converter to accelerate the native-to-FOCUS transform.

### 2.3 Phased roadmap

**Phase 0: Validate what exists.** Pull real `/billing/usage` and `/billing/ledger` responses (the API is beta and rate-limited to 10 calls per organization per day, so plan test calls accordingly) across a pay-as-you-go account, a prepaid-contract account, and a marketplace-billed account. Confirm the day-scoped granularity holds in practice, confirm whether `billing_account_id` ever diverges from `organization_id`, and confirm the credits-to-USD conversion rate.

**Phase 1: Close the trivial Mandatory gaps and derive list cost.** Emit `ProviderName`, `PublisherName` (literals), `ServiceCategory` (mostly `Databases`), `ChargeCategory` (`Usage`, fixed for this endpoint), `ChargeDescription` (from `service_name` / `base_sku`), `ChargeClass` (nullable), `PricingQuantity` / `PricingUnit` (from `consumed_quantity` / `consumed_unit` for flat-rate meters), and `BillingPeriodStart` / `BillingPeriodEnd` (calendar-month boundary for PAYG). Map the identity columns: `BillingAccountId`, `SubAccountId` / `SubAccountName` (`project_id` / `project_name`), `ResourceId` / `ResourceName` / `ResourceType`.

**Phase 2: Close the substantive cost gap.** Resolve the credits-to-currency conversion, then build `BilledCost` and `EffectiveCost` by reconciling ledger-level credit consumption (and, for prepaid contracts, the negotiated ACU rate) back to the usage rows. Zero out `BilledCost` for marketplace-billed rows per the FOCUS requirement. This is the one real data-engineering step, and it is where this analysis would most benefit from a live Validator run against real account data.

**Phase 3: Attribute commitment-discount usage.** For prepaid-contract organizations, mark each usage row's `CommitmentDiscountStatus` (Used or Unused) and populate the rest of the `CommitmentDiscount*` family so committed-capacity waste becomes visible, the specific capability the FOCUS commitment-discount columns exist to support.

**Phase 4: Fix deviations and round out Conditional columns.** Map display values for `BillingAccountType` and `InvoiceIssuerName`, parse `base_sku` into `ServiceSubcategory` / `SkuMeter`, add a static region-name lookup for `RegionName`, and derive `PricingCategory` from `billing_account_type`.

**Phase 5: Mature toward the latest version, and pursue product-level tagging.** Track v1.3/v1.4, drop `Provider`/`Publisher`, align with the v1.4 Invoice Detail and billing-period datasets, and treat `Tags` as a roadmap item for the Aura product itself (instance labeling), since it cannot be solved in the billing pipeline alone.

### 2.4 FOCUS Use Cases unlocked

- **Available today (identity and granularity):** spend by organization and by project (`Analyze costs by sub-account`), day-level cost trending, and spend by service and instance once `service_name` / `base_sku` are mapped to `ServiceName` / `SkuId`.
- **Unlocked by Phase 1:** list-cost showback by project and instance, and corrections reporting once `ChargeClass` exists.
- **Unlocked by Phase 2:** effective-cost and savings analysis (`Determine Effective Savings Rate`), actuals-based budgeting, and invoice reconciliation, all of which need `BilledCost` and `EffectiveCost` reconciled to the row.
- **Unlocked by Phase 3:** commitment-discount coverage and utilization use cases (identifying under-used prepaid ACU commitments), which need per-row `CommitmentDiscountStatus`.
- **Out of scope until the product changes:** tag-based cost allocation and chargeback below the project level, since Aura has no tagging mechanism today.

---

## Part 3: Immediate next steps

1. Pull real `/billing/usage` and `/billing/ledger` responses across pay-as-you-go, prepaid-contract, and marketplace-billed accounts (respecting the 10-calls-per-organization-per-day rate limit) and map every field to a FOCUS column ID.
2. Emit the trivial Mandatory columns: the literals, `ServiceCategory`, `ChargeCategory`, `ChargeDescription`, `ChargeClass`, `PricingQuantity` / `PricingUnit`, and the billing-period boundaries.
3. Resolve the ACU-credits-to-currency conversion and design the ledger-to-usage-row reconciliation that produces `BilledCost` and `EffectiveCost`.
4. Design commitment-discount attribution for prepaid-contract organizations (`CommitmentDiscountStatus` and the rest of the family).
5. Fix the deviations: display-value mapping for `billing_account_type` and `invoice_issuer_name`, parsing `base_sku`, and adding `x_CloudServiceProvider` as a custom column.
6. Run the output through the FOCUS Validator, then engage `member-cert@finops.org` on Supported and then Conformant status. In parallel, raise `Tags` as a product feature request, since it blocks tag-based allocation regardless of billing-pipeline work.

---

## Confidence summary

- **Data source (high):** The Aura API v2beta1 OpenAPI specification (`https://api.neo4j.io/v2beta1/spec.json`) documents the exact `UsageData` and `LedgerData` field lists, types, and examples used throughout this report, and the Aura billing documentation (billing dimensions, payment options, cost explorer) corroborates the billing model. The Instances, Projects, and Organizations schemas were checked directly against both the v1 and v2beta1 specifications for a tags/labels field and found to have none.
- **Identity and granularity strong (high):** organization, project, and resource give a clean hierarchy, and day-scoped example periods support sub-monthly charge records, though this should be confirmed against a live account rather than the documented examples alone.
- **List cost derivable, billed/effective/contracted substantive (high):** `list_cost` and `list_unit_price` map directly to FOCUS. `BilledCost`, `EffectiveCost`, and (for prepaid-contract accounts) `ContractedCost` require a real reconciliation against the credit ledger and, where applicable, the negotiated contract rate.
- **Commitment-discount attribution as a triggered Conditional gap (medium-high):** the prepaid-ACU-contract mechanic is documented clearly enough to call this a genuine trigger rather than N/A, but the exact mechanics of how overage between committed and pay-as-you-go pricing is recorded internally were not observable from public documentation and should be confirmed with Neo4j directly.
- **`pricing_currency` as "credits" (high):** this is stated as the field's example value in the live OpenAPI specification, not an inference; the credits-to-USD conversion rate itself was not published and should be confirmed.
- **Tags absence (high):** confirmed by direct inspection of the full v1 and v2beta1 OpenAPI schemas for Instances, Projects, Organizations, and Usage; no tag or label field exists anywhere in the current API surface.
- **Feature levels (high):** verified against the bundled v1.2 reference and spot-checked live against the FOCUS specification via the FOCUS specification MCP on 2026-09-18; v1.2 remains the certification baseline and v1.4 the latest ratified version.

---

## Sources

- Neo4j Aura API v2beta1 OpenAPI specification: https://api.neo4j.io/v2beta1/spec.json
- Neo4j Aura API Specification (Swagger UI): https://neo4j.com/docs/aura/platform/api/specification/
- Neo4j Aura Changelog, "New Billing API in Aura API v2beta1": https://neo4j-aura.canny.io/changelog/new-billing-api-in-aura-api-v2beta1
- Neo4j Aura, "Billing dimensions": https://neo4j.com/docs/aura/billing/billing-dimensions/
- Neo4j Aura, "Payment options": https://neo4j.com/docs/aura/billing/payment-options/
- Neo4j Aura, "Cost explorer": https://neo4j.com/docs/aura/billing/cost-explorer/
- Neo4j Aura, "Cost explorer / usage report": https://neo4j.com/docs/aura/billing/usage-report/
- Neo4j Aura Billing FAQ: https://aura.support.neo4j.com/hc/en-us/articles/360037061854-Neo4j-Aura-Billing-FAQ
- Neo4j Aura pricing: https://console.neo4j.io/pricing
- FOCUS Specification v1.2: https://focus.finops.org/focus-specification/v1-2/
- FOCUS Specification v1.4: https://focus.finops.org/focus-specification/v1-4/
- FOCUS column library: https://focus.finops.org/focus-columns/
- FOCUS Validator and Requirements Model: https://focus.finops.org/

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
