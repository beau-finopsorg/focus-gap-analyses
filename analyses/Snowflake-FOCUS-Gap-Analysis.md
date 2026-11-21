# Snowflake and FOCUS: Compliance Gap and Adoption Roadmap

*Analysis run: July 6, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Provider and product in scope:** Snowflake, Inc. (the Snowflake Data Cloud), consumption-based credit billing.
**Prepared:** 2026-07-06.
**Source analyzed:** Snowflake `ORGANIZATION_USAGE` and `ACCOUNT_USAGE` schemas in the shared `SNOWFLAKE` database, primarily the `USAGE_IN_CURRENCY_DAILY` and `METERING_DAILY_HISTORY` views, with `WAREHOUSE_METERING_HISTORY`, `QUERY_ATTRIBUTION_HISTORY`, `TAG_REFERENCES`, and `RATE_SHEET_DAILY` as supporting sources.
**FOCUS baseline:** v1.2 (current certification baseline). **Build target:** v1.4 (latest ratified, 2026-06-04).

## Executive summary

Snowflake exposes a rich, queryable billing and usage layer, but it does so as a set of relational views a customer joins together, not as a single FOCUS-shaped record. The strongest asset is genuine daily currency data: `USAGE_IN_CURRENCY_DAILY` reports the amount charged per account, per service type, in a stated currency, alongside the credit quantity. Snowflake also carries the mechanics FOCUS cares about: an organization-and-account hierarchy, object tags and query tags as key-value pairs, capacity commitments with a documented drawdown order, and cloud-services adjustments. What it lacks natively is a normalized single dataset that resolves list, contracted, and effective cost onto each usage line, plus FOCUS column names, enums, and a consistent charge grain.

Snowflake is not listed on the FOCUS "get started" provider page, so it holds no FinOps Certified FOCUS designation. This analysis assesses readiness only; it reflects the data source reviewed, not a formal certification result.

- FOCUS columns (v1.2 baseline): 57.
- Already present (mappable from existing views, some with a transform): 24.
- Substantive Mandatory gaps: 3 of 6 missing Mandatory columns are substantive (`ContractedCost`, `EffectiveCost`, and reconciling `ListCost` to the usage line); the other 3 are trivial plumbing.
- Deviations to fix: 5.

**RAG readiness:** Cost Partial, Granularity Strong, Allocation Partial, Coverage Partial, FOCUS shape Gap. **Overall band: Not yet aligned (per public docs).**

**Recommendation:** Treat Snowflake as a strong usage-and-currency source that needs a FOCUS transformation layer. Build a consolidation view that pins the account/organization hierarchy, joins the daily currency data to the rate sheet for list and contracted rates, and emits FOCUS column IDs, key-value `Tags`, and valid enums. The cost reconciliation (capacity drawdown, cloud-services adjustments, and per-line list-to-effective) is the substantive work; the rest is naming and shaping.

## Part 1: The conformance gap

### 1.1 The data source

Snowflake bills on consumption of credits. A credit is the unit of compute; storage and data transfer are rated in their own units and converted to currency. Customers read their consumption from views in the shared, read-only `SNOWFLAKE` database, in two relevant schemas:

- `ORGANIZATION_USAGE`: organization-wide rollups, queryable from the organization account. `USAGE_IN_CURRENCY_DAILY` is the anchor: one row per organization, account, usage date, usage type, service type, rating type, and adjustment flag, carrying `USAGE` (the rated quantity, in credits for compute or terabytes for storage/transfer), `CURRENCY`, `USAGE_IN_CURRENCY` (the charged amount), plus `BALANCE_SOURCE` (capacity, rollover, free usage, overage, rebate) and `BILLING_TYPE` (consumption, rebate, priority support, and so on). `METERING_DAILY_HISTORY` gives daily credits per account and service type, including `CREDITS_USED_COMPUTE`, `CREDITS_USED_CLOUD_SERVICES`, `CREDITS_ADJUSTMENT_CLOUD_SERVICES` (a negative cloud-services rebate), and `CREDITS_BILLED`.
- `ACCOUNT_USAGE`: per-account detail. `WAREHOUSE_METERING_HISTORY` gives credits per warehouse (with `warehouse_id`), `QUERY_ATTRIBUTION_HISTORY` attributes compute credits per query and user, and `TAG_REFERENCES` resolves object and user tags. `RATE_SHEET_DAILY` exposes the effective per-credit and per-unit rates for the account.

Key characteristics and limits:

- Daily granularity: `USAGE_DATE` is a UTC calendar day. This is finer than monthly and satisfies the sub-monthly charge-record expectation. Finer-than-daily attribution (per warehouse, per query) exists but only in `ACCOUNT_USAGE`, one account at a time.
- Currency present, list and contracted rates separate: the currency view gives the amount actually charged and the fund source, but list price and the negotiated contract rate live in `RATE_SHEET_DAILY`, not on the usage line.
- Discounts and commitments exist: capacity commitments draw down credits at a negotiated rate, cloud-services usage under 10% of daily warehouse credits is rebated, and data-sharing rebates apply. These are real discounts and adjustments, applied through balance sources and adjustment columns rather than as a single effective-cost figure per line.
- No native resource identity or tags on the currency view: `USAGE_IN_CURRENCY_DAILY` has no warehouse, database, or tag column. Resource-level and tag-level attribution requires joining `ACCOUNT_USAGE` views, and query-level attribution is single-account only.
- Late-arriving data: currency data can change until month close for adjustments, amendments, and account transfers; latency up to 72 hours.

### 1.2 How conformance is judged

FOCUS assigns every column a feature level: Mandatory (must be present and populated), Conditional (required when the provider's model triggers the condition), Recommended (encouraged), or Optional. Conformance is judged column by column against the Requirements Model. A dataset conforms when every Mandatory column is present and correctly populated, every applicable Conditional column is handled, tags are key-value pairs, enumerated columns carry valid members, and types and currency and date formats follow the spec. Feature levels for this report were verified against the FOCUS v1.2 specification content-constraint tables.

### 1.3 Column-by-column status

Status legend: Present (emitted and aligned, allowing a documented transform from native views); Present, deviation to fix (emitted, wrong format or invalid enum); Missing: Mandatory (required and absent, blocks conformance); Missing: Recommended (encouraged, absent); Missing: Conditional (required when the model triggers it, absent); N/A: null valid (Conditional or Recommended column that does not apply, should exist and be null).

| FOCUS Column | Level | In the source? | Status |
|---|---|---|---|
| AvailabilityZone | R | No (region only, no zone) | N/A: null valid |
| BilledCost | M | Partial (USAGE_IN_CURRENCY, needs reconciliation) | Present, deviation to fix |
| BillingAccountId | M | Yes (ACCOUNT_LOCATOR / account name) | Present |
| BillingAccountName | M | Yes (ACCOUNT_NAME) | Present |
| BillingAccountType | C | No | Missing: Conditional |
| BillingCurrency | M | Yes (CURRENCY) | Present |
| BillingPeriodEnd | M | No (daily usage, no billing period bounds) | Missing: Mandatory |
| BillingPeriodStart | M | No (daily usage, no billing period bounds) | Missing: Mandatory |
| CapacityReservationId | C | No | N/A: null valid |
| CapacityReservationStatus | C | No | N/A: null valid |
| ChargeCategory | M | No (derivable from BILLING_TYPE / IS_ADJUSTMENT) | Missing: Mandatory |
| ChargeClass | M | Partial (IS_ADJUSTMENT flags adjustments) | Present, deviation to fix |
| ChargeDescription | M | No (derivable from SERVICE_TYPE) | Missing: Mandatory |
| ChargeFrequency | R | No | Missing: Recommended |
| ChargePeriodEnd | M | Yes (USAGE_DATE + 1 day) | Present |
| ChargePeriodStart | M | Yes (USAGE_DATE) | Present |
| CommitmentDiscountCategory | C | Partial (capacity commitments exist) | Missing: Conditional |
| CommitmentDiscountId | C | Partial (CONTRACT_NUMBER) | Missing: Conditional |
| CommitmentDiscountName | C | Partial | Missing: Conditional |
| CommitmentDiscountQuantity | C | Partial (credits from capacity balance) | Missing: Conditional |
| CommitmentDiscountStatus | C | Partial (BALANCE_SOURCE) | Missing: Conditional |
| CommitmentDiscountType | C | Partial (capacity commitment) | Missing: Conditional |
| CommitmentDiscountUnit | C | Partial (credits) | Missing: Conditional |
| ConsumedQuantity | C | Yes (USAGE) | Present |
| ConsumedUnit | C | Partial (implied by RATING_TYPE) | Present, deviation to fix |
| ContractedCost | M | No (rate sheet separate, not on line) | Missing: Mandatory |
| ContractedUnitPrice | C | Partial (RATE_SHEET_DAILY) | Missing: Conditional |
| EffectiveCost | M | No (no amortized effective per line) | Missing: Mandatory |
| InvoiceId | R | No | Missing: Recommended |
| InvoiceIssuerName | M | No (constant "Snowflake") | Missing: Mandatory |
| ListCost | M | No (list rate in rate sheet, not on line) | Missing: Mandatory |
| ListUnitPrice | C | Partial (RATE_SHEET_DAILY) | Missing: Conditional |
| PricingCategory | C | No (On-Demand vs Committed derivable) | Missing: Conditional |
| PricingCurrency | C | Yes (CURRENCY) | Present |
| PricingCurrencyContractedUnitPrice | C | Partial (RATE_SHEET_DAILY) | Missing: Conditional |
| PricingCurrencyEffectiveCost | C | No | Missing: Conditional |
| PricingCurrencyListUnitPrice | C | Partial (RATE_SHEET_DAILY) | Missing: Conditional |
| PricingQuantity | M | Partial (USAGE, flat-rate only) | Present, deviation to fix |
| PricingUnit | M | Partial (credits/TB by RATING_TYPE) | Present, deviation to fix |
| ProviderName | M (removed v1.4) | No (constant "Snowflake") | Missing: Mandatory |
| PublisherName | M (removed v1.4) | No (constant "Snowflake") | Missing: Mandatory |
| RegionId | C | Yes (REGION) | Present |
| RegionName | C | Yes (REGION) | Present |
| ResourceId | C | Partial (warehouse_id in ACCOUNT_USAGE only) | Missing: Conditional |
| ResourceName | C | Partial (warehouse name in ACCOUNT_USAGE only) | Missing: Conditional |
| ResourceType | C | Partial (derivable from SERVICE_TYPE) | Missing: Conditional |
| ServiceCategory | M | No (derivable from SERVICE_TYPE) | Missing: Mandatory |
| ServiceName | M | No (constant "Snowflake" or by SERVICE_TYPE) | Missing: Mandatory |
| ServiceSubcategory | R | No | Missing: Recommended |
| SkuId | C | Partial (SERVICE_TYPE as a proxy) | Missing: Conditional |
| SkuMeter | C | Partial (RATING_TYPE) | Missing: Conditional |
| SkuPriceDetails | C | Partial (RATE_SHEET_DAILY) | Missing: Conditional |
| SkuPriceId | C | No | Missing: Conditional |
| SubAccountId | C | Yes (account within organization) | Present |
| SubAccountName | C | Yes (ACCOUNT_NAME) | Present |
| SubAccountType | C | No | Missing: Conditional |
| Tags | C | Partial (object/query tags, not on usage line) | Present, deviation to fix |

### 1.4 What's solved, and what remains

**Solved or near-solved.** The organization-and-account hierarchy is clean: organization maps to the billing account, each account maps to a sub-account, and both carry a stable ID and a name. Daily charge periods are directly available from `USAGE_DATE`. Currency and consumed quantity are present. Region is present. Object tags and query tags are native key-value constructs. The credit-based consumption model is well documented, and the fund-source and adjustment columns describe the discount mechanics precisely.

**Substantive gaps (real data or real reconciliation work).**

- Cost columns: `ListCost`, `ContractedCost`, and `EffectiveCost` are the core substantive gap. `USAGE_IN_CURRENCY_DAILY` gives the charged amount, but that amount already reflects the balance source (capacity, rollover, free, overage). Producing a clean FOCUS cost quartet means joining the rate sheet for list and contracted rates, applying the capacity drawdown and cloud-services adjustment to derive effective cost per line, and reconciling all four so they tie back to the invoice. This is the classic list-cost trap: discounts, commitments, and adjustments exist and are applied through balance sources rather than a single per-line effective figure, so the cost columns are substantive, not a trivial copy.
- Billing period bounds: `BillingPeriodStart` and `BillingPeriodEnd` are not in the daily usage feed. Snowflake bills monthly, so these are derivable from the calendar month, but the value must be supplied because the source omits it.

**Trivial gaps (plumbing, derivable from data already present).**

- `ChargeCategory`: derivable from `BILLING_TYPE` and `IS_ADJUSTMENT` (consumption maps to Usage, adjustments to Adjustment or Credit).
- `ChargeDescription`, `ServiceCategory`, `ServiceName`: derivable from `SERVICE_TYPE` with a lookup table.
- `InvoiceIssuerName`, `ProviderName`, `PublisherName`: constants ("Snowflake").
- `PricingQuantity` and `PricingUnit`: equal `USAGE` and its unit for flat-rate credit consumption; tiered or blended rates (for example capacity-tier pricing) must be computed against the rate basis, not copied.

Of the 6 missing Mandatory columns, 3 are substantive (`ListCost`, `ContractedCost`, `EffectiveCost`, treated as one reconciliation) and 3 are trivial (`ServiceCategory`, `ServiceName`, `ChargeCategory`), with `ChargeDescription`, the invoice/provider constants, and the billing-period bounds as additional trivial adds.

### 1.5 Deviations to fix

- `Tags`: Snowflake tags are true key-value pairs, which matches FOCUS shape, but they live in `TAG_REFERENCES` and are not attached to the currency view. The deviation is join-and-attach, not reformat.
- `ChargeClass`: FOCUS uses `ChargeClass` = "Correction" (or null) for corrections. Snowflake's `IS_ADJUSTMENT` boolean must be mapped to that enum, not passed through as a boolean.
- `ConsumedUnit` and `PricingUnit`: the unit is implied by `RATING_TYPE` (credits for compute, terabytes for storage and transfer) rather than stated explicitly, so a lookup is needed to emit an explicit unit string.
- `PricingQuantity`: correct for flat-rate credit usage; flag tiered and capacity-tier SKUs for computation against the rate basis.
- `BilledCost`: `USAGE_IN_CURRENCY` is close to billed cost but must be reconciled against the balance source so overage-versus-committed and rebate lines are represented correctly.

Already done right: key-value tags, ISO-style daily dates, an explicit currency code, a stable account and organization hierarchy, and a documented service and rating taxonomy.

## Part 2: The path forward

### 2.1 Which FOCUS version to target

Baseline the current certification version, v1.2, for any conformance conversation, and build toward v1.4 (ratified 2026-06-04). Building to v1.4 means dropping `ProviderName` and `PublisherName` (removed in v1.4) and adopting the Invoice Detail and billing-period datasets, which suit Snowflake's monthly invoice and its month-close adjustment behavior well. A practical path is to construct the transformation against v1.2 semantics, then layer the v1.3 and v1.4 additions.

### 2.2 What certification requires

FinOps Certified FOCUS conformance for data generators runs through the FinOps Foundation. The historical badge is "FinOps Certified FOCUS v1.2 Conformant"; confirm the current badge version on the program page. Contact `member-cert@finops.org` for the RFI. Membership is required for certification, though contributing to the spec is open and free. Deliverables are a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report, which this analysis seeds. Open-source tooling includes the FOCUS Validator (checks data against the Requirements Model), the FOCUS Converter (provider-native to FOCUS), and the FOCUS Requirements Model (machine-readable MUST/SHOULD/MAY rules).

### 2.3 Phased roadmap

**Phase 0: Validate and scope.** Build a single consolidation view over `USAGE_IN_CURRENCY_DAILY` (or `METERING_DAILY_HISTORY` where credits are the grain), run a sample through the FOCUS Validator to establish a baseline, and confirm the v1.2 baseline and v1.4 build target.

**Phase 1: Close the substantive and trivial Mandatory gaps.** Join the rate sheet to derive `ListCost` and `ContractedCost`; compute `EffectiveCost` by applying capacity drawdown and cloud-services adjustments per line; reconcile `BilledCost` against balance source. Add the trivial constants and lookups (`ServiceCategory`, `ServiceName`, `ChargeCategory`, `ChargeDescription`, `InvoiceIssuerName`) and derive `BillingPeriodStart`/`End` from the calendar month.

**Phase 2: Fix deviations.** Attach key-value `Tags` from `TAG_REFERENCES`, map `IS_ADJUSTMENT` to `ChargeClass`, emit explicit `ConsumedUnit` and `PricingUnit`, and flag tiered SKUs for `PricingQuantity` computation.

**Phase 3: Round out Conditional and Recommended columns.** Populate the CommitmentDiscount family from capacity-commitment data, the SKU family from service and rate-sheet detail, `ResourceId`/`ResourceName`/`ResourceType` by joining warehouse-level `ACCOUNT_USAGE` views, `PricingCategory` (On-Demand versus Committed from balance source), and the pricing-currency columns. Add Recommended `ChargeFrequency`, `InvoiceId`, `ServiceSubcategory`.

**Phase 4: Mature to the target version.** Adopt v1.3 and v1.4 additions, drop `ProviderName`/`PublisherName`, wire in the Invoice Detail dataset for month-close reconciliation, and pursue certification.

### 2.4 FOCUS Use Cases unlocked

- Unlocked once the consolidation view and daily grain exist (Phases 0 to 1): account-level and organization-level cost reporting and showback, service-level spend analysis, day-level trend and anomaly detection.
- Unlocked with the cost quartet (Phase 1): effective-cost reconciliation, committed-versus-on-demand analysis, invoice reconciliation, actuals-based budgeting.
- Unlocked with tags and resource identity (Phases 2 to 3): tag-based chargeback and showback (by cost center), resource-level cost allocation (by warehouse), shared-warehouse and query-level cost attribution (single-account scope).
- Out of scope for now: capacity-reservation use cases in the cloud sense do not apply; Snowflake's commitments are prepaid capacity credits, better modeled through the CommitmentDiscount family than the CapacityReservation columns.

## Part 3: Immediate next steps

1. Stand up the consolidation view over `USAGE_IN_CURRENCY_DAILY` from the organization account and confirm the account/organization hierarchy maps to billing account and sub-account.
2. Model the cost quartet: join `RATE_SHEET_DAILY`, apply capacity drawdown and cloud-services adjustment, and reconcile `Billed`, `List`, `Contracted`, and `Effective` cost against a known invoice.
3. Add the trivial Mandatory constants and `SERVICE_TYPE` lookups, and derive billing-period bounds.
4. Attach key-value `Tags` and resource identity by joining `TAG_REFERENCES` and warehouse-level views.
5. Run the transformed sample through the FOCUS Validator and iterate.

## Confidence summary

- Data source structure (views, columns, daily grain, hierarchy): high confidence, taken from current Snowflake documentation for `USAGE_IN_CURRENCY_DAILY`, `METERING_DAILY_HISTORY`, and the cost-attribution and object-tagging guides.
- Feature-level classifications: high confidence. Levels were checked against the FOCUS v1.2 content-constraint reference; the bundled table was cache-validated on 2026-07-06 against the live spec index, which confirmed v1.2 exists and v1.4 (2026-06-04) is the latest ratified version, with no refresh needed.
- Cost reconciliation as substantive: high confidence. Capacity commitments, cloud-services adjustments, and data-sharing rebates are documented discounts and adjustments applied through balance sources, so list, contracted, and effective cost require reconciliation, not a copy.
- Overall readiness band (Emerging): moderate to high confidence. Snowflake has strong daily currency data and the right allocation primitives, but no FOCUS-shaped dataset, no consolidated cost quartet per line, and native names and enums throughout.
- Certification status: Snowflake is not on the FOCUS provider "get started" page and holds no FinOps Certified FOCUS designation; this report assesses readiness only and is not a certification result.
- Items to confirm on a live run: exact reconciliation of `USAGE_IN_CURRENCY` to a billing statement including overage lines, and the current certification badge version on the program page.

## Sources

- Snowflake, USAGE_IN_CURRENCY_DAILY view: https://docs.snowflake.com/en/sql-reference/organization-usage/usage_in_currency_daily
- Snowflake, METERING_DAILY_HISTORY view: https://docs.snowflake.com/en/sql-reference/organization-usage/metering_daily_history
- Snowflake, Attributing cost (object tags, query tags, WAREHOUSE_METERING_HISTORY, QUERY_ATTRIBUTION_HISTORY, TAG_REFERENCES): https://docs.snowflake.com/en/user-guide/cost-attributing
- Snowflake, Introduction to object tagging: https://docs.snowflake.com/en/user-guide/object-tagging/introduction
- FOCUS Specification: https://focus.finops.org/focus-specification/
- FOCUS tooling: FOCUS Validator, FOCUS Converter, FOCUS Requirements Model.

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
