# MongoDB Atlas and FOCUS: Conformance Gap Analysis

*Analysis run: July 6, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Provider:** MongoDB (MongoDB Atlas)
**Product in scope:** MongoDB Atlas consumption billing, exposed through the Atlas Administration API v2 Invoices endpoints (invoice objects and their `lineItems`)
**Prepared:** 2026-07-06
**Source analyzed:** Atlas Administration API v2 Invoices resource (Return One Invoice, Return All Line Items for One Invoice, invoice CSV), plus the Atlas billing documentation and the Atlas Architecture Center billing-data guidance
**FOCUS baseline:** v1.2 (current certification baseline)
**Build target:** v1.4 (latest ratified)
**Status:** MongoDB is not listed as a Supported FOCUS data generator on focus.finops.org/get-started. This analysis assesses readiness only; it is not a conformance result and does not reflect any FinOps Certified FOCUS designation.

---

## Executive summary

MongoDB Atlas already carries most of what a FOCUS dataset needs, but in a native billing shape rather than a FOCUS-shaped export. The Atlas Administration API returns invoices whose `lineItems` array is the natural charge record: each line item carries a `sku`, a `quantity` and `unit`, a `unitPriceDollars`, a `totalPriceCents`, and a `startDate` and `endDate`. Atlas tabulates costs daily, and line items are period-scoped, so sub-monthly charge records are available. The account and allocation story is genuinely strong: the organization is the billing account, each project (the `groupId` / `groupName`) is a clean sub-account, each `clusterName` identifies the deployment, and user-applied `tags` arrive as key-value pairs on the line item.

The one substantive gap is the cost family. Line items give list cost directly (`unitPriceDollars` times `quantity`), and line-level `discountCents` and `percentDiscount` fields provide a contracted or discounted view. But credits, starting balances, sales tax, and elastic or committed-use adjustments are reconciled at the invoice level, not on the usage lines, so a true `EffectiveCost` and `BilledCost` per line require pushing invoice-level adjustments back down to the line items. This is the list-cost trap: the daily line-item feed is close to list-only, and the billed and effective figures live one level up on the invoice.

**Stat strip:** 57 FOCUS columns (v1.2). 33 present or trivially derivable from line-item and invoice fields. 2 of the 21 Mandatory columns are substantive gaps (`BilledCost`, `EffectiveCost`). 6 deviations to fix (chiefly cents-to-decimal cost scaling, native field names, and enum mapping).

**Recommendation:** Treat the Atlas invoice `lineItems` as the FOCUS charge record, derive the list cost and pricing columns from fields already present, and build the effective and billed cost columns by reconciling invoice-level credits and adjustments back to the lines. The data to become conformant largely exists; the work is a native-to-FOCUS transform plus one real reconciliation step.

### Readiness (RAG)

| Dimension | Rating |
|---|---|
| Cost | Partial |
| Granularity | Strong |
| Allocation | Strong |
| Coverage | Partial |
| FOCUS shape | Partial |
| **Overall band** | **Structured** |

---

## Part 1: The conformance gap

MongoDB Atlas exposes rich billing data through a stable API, but as a native schema. This section walks what it exposes, how conformance is judged, and where it sits column by column.

### 1.1 The data source

Billing in Atlas is configured at the organization level and applies to all projects within that organization. Atlas charges by the hour for clusters, tabulates costs daily, and exposes them through the Atlas Administration API v2 Invoices endpoints:

- **Invoice object** (Return One Invoice for One Organization): carries `id`, `orgId`, `created`, `startDate`, `endDate`, `subtotalCents`, `salesTaxCents`, `startingBalanceCents`, `amountBilledCents`, `amountPaidCents`, `statusName`, `payments`, `refunds`, `linkedInvoices`, and the `lineItems` array.
- **Line items** (Return All Line Items for One Invoice): the charge-record grain. Each line item carries `sku`, `groupId`, `groupName`, `clusterName`, `quantity`, `unit`, `unitPriceDollars`, `totalPriceCents`, `discountCents`, `percentDiscount`, `startDate`, `endDate`, `created`, `note`, `stitchAppName`, and `tags`.

Characteristics relevant to FOCUS:

- **Native field names:** The schema is MongoDB's own, not FOCUS column IDs. A native-to-FOCUS transform is required.
- **Granularity:** Costs are tabulated daily and line items are period-scoped by `startDate` and `endDate`, so sub-monthly charge records are available even though the invoice aggregates them monthly.
- **Currency:** USD is the default billing currency; non-USD billing is available only under a subscription arrangement. Cost fields are expressed in US cents (`totalPriceCents`, `discountCents`) or dollars (`unitPriceDollars`).
- **Account hierarchy:** Organization (the `orgId` on the invoice) is the billing account; project (`groupId` / `groupName`) is a clean sub-account; `clusterName` is the deployment.
- **Tags:** User-applied resource tags surface on the line item as key-value pairs, the correct FOCUS shape.
- **SKU:** Every line item carries a `sku` (instance type, support charge, advanced security, backup, data transfer, and so on), a strong basis for `SkuId`, `ServiceName`, and `ChargeDescription`.
- **Discounts and credits:** Line-level `discountCents` and `percentDiscount` express per-line discounting. Credits, starting balances, and sales tax are reconciled at the invoice level (`startingBalanceCents`, `salesTaxCents`, `amountBilledCents`), not on the usage lines.

### 1.2 How conformance is judged

FOCUS assigns every column a feature level: Mandatory (must be present and populated), Conditional (required when the provider's business model triggers the condition), Recommended, or Optional. Conformance is judged column by column against the FOCUS Requirements Model. A dataset is conformant when every Mandatory column is present and correctly typed, every applicable Conditional column is populated, and values honor FOCUS allowed-value sets and formats.

Feature levels in this report were taken from the verified v1.2 reference and spot-checked live against the FOCUS specification (`ServiceSubcategory` Recommended at section 3.49, `ChargeClass` Mandatory-nullable, the cost family Mandatory) on 2026-07-06. The bundled reference was current: v1.2 remains the certification baseline and v1.4 (ratified 2026-06-04) is the latest ratified version, matching the reference stamp.

### 1.3 Column-by-column status

Legend: Present; Present, deviation to fix; Missing: Mandatory; Missing: Recommended; Missing: Conditional; N/A: null valid.

| FOCUS Column | Level | In the source? | Status |
|---|---|---|---|
| AvailabilityZone | R | No | Missing: Recommended |
| BilledCost | M | Invoice `amountBilledCents` (invoice grain only) | Missing: Mandatory |
| BillingAccountId | M | `orgId` | Present, deviation to fix |
| BillingAccountName | M | Organization name | Present, deviation to fix |
| BillingAccountType | C | No | Missing: Conditional |
| BillingCurrency | M | USD (implicit) | Present, deviation to fix |
| BillingPeriodEnd | M | Invoice `endDate` | Present |
| BillingPeriodStart | M | Invoice `startDate` | Present |
| CapacityReservationId | C | No | N/A: null valid |
| CapacityReservationStatus | C | No | N/A: null valid |
| ChargeCategory | M | Derivable from `sku` | Missing: Mandatory (trivial) |
| ChargeClass | M | No | Missing: Mandatory (trivial) |
| ChargeDescription | M | `sku` / `note` | Present, deviation to fix |
| ChargeFrequency | R | Derivable from `sku` | Missing: Recommended |
| ChargePeriodEnd | M | Line-item `endDate` | Present |
| ChargePeriodStart | M | Line-item `startDate` | Present |
| CommitmentDiscountCategory | C | No | N/A: null valid |
| CommitmentDiscountId | C | No | N/A: null valid |
| CommitmentDiscountName | C | No | N/A: null valid |
| CommitmentDiscountQuantity | C | No | N/A: null valid |
| CommitmentDiscountStatus | C | No | N/A: null valid |
| CommitmentDiscountType | C | No | N/A: null valid |
| CommitmentDiscountUnit | C | No | N/A: null valid |
| ConsumedQuantity | C | `quantity` | Present, deviation to fix |
| ConsumedUnit | C | `unit` | Present |
| ContractedCost | M | Derivable (`totalPriceCents` minus `discountCents`) | Missing: Mandatory (trivial) |
| ContractedUnitPrice | C | Derivable from `unitPriceDollars` and `percentDiscount` | Missing: Conditional |
| EffectiveCost | M | No (invoice-level credits not on lines) | Missing: Mandatory |
| InvoiceId | R | Invoice `id` | Present |
| InvoiceIssuerName | M | No (fixed literal) | Missing: Mandatory (trivial) |
| ListCost | M | Derivable (`unitPriceDollars` times `quantity`) | Missing: Mandatory (trivial) |
| ListUnitPrice | C | `unitPriceDollars` | Present, deviation to fix |
| PricingCategory | C | Derivable from `sku` | Missing: Conditional |
| PricingCurrency | C | USD (implicit) | Missing: Conditional (trivial) |
| PricingCurrencyContractedUnitPrice | C | No | N/A: null valid |
| PricingCurrencyEffectiveCost | C | No | N/A: null valid |
| PricingCurrencyListUnitPrice | C | No | N/A: null valid |
| PricingQuantity | M | `quantity` (flat-rate SKUs) | Present, deviation to fix |
| PricingUnit | M | `unit` | Present |
| ProviderName | M | No (fixed literal) | Missing: Mandatory (trivial) |
| PublisherName | M | No (fixed literal) | Missing: Mandatory (trivial) |
| RegionId | C | Derivable from `sku` (region-suffixed) | Missing: Conditional |
| RegionName | C | Derivable from `sku` | Missing: Conditional |
| ResourceId | C | `clusterName` (name, not ID) | Present, deviation to fix |
| ResourceName | C | `clusterName` | Present |
| ResourceType | C | Derivable from `sku` | Missing: Conditional |
| ServiceCategory | M | `Databases` (fixed) | Missing: Mandatory (trivial) |
| ServiceName | M | Derivable from `sku` | Missing: Mandatory (trivial) |
| ServiceSubcategory | R | Derivable from `sku` | Missing: Recommended |
| SkuId | C | `sku` | Present |
| SkuMeter | C | Derivable from `sku` | Missing: Conditional |
| SkuPriceDetails | C | No | Missing: Conditional |
| SkuPriceId | C | No | Missing: Conditional |
| SubAccountId | C | `groupId` | Present |
| SubAccountName | C | `groupName` | Present |
| SubAccountType | C | No | N/A: null valid |
| Tags | C | `tags` (key-value) | Present |

**Reading the tally:** Of 57 v1.2 columns, 16 are Present (10 of them carrying a deviation to fix), 9 Mandatory are missing (7 of them trivially derivable from fields already present, 2 substantive), 3 Recommended are missing, 12 Conditional are missing where the model plausibly triggers them (SKU-derived region, service, and pricing detail plus contracted unit price), and 12 Conditional are legitimately N/A (the commitment-discount family, capacity reservations, pricing-currency conversions that collapse because billing and pricing are both USD, and sub-account type).

### 1.4 What is solved, and what remains

**Solved (the substantive work is mostly identity and granularity, and both are strong):** MongoDB Atlas gives a clean account hierarchy for allocation. Organization maps to the billing account, project (`groupId` / `groupName`) maps directly to `SubAccountId` and `SubAccountName`, and `clusterName` gives resource identity. Tags arrive as key-value pairs. Line items are day-scoped, so charge-level granularity is available today. The `sku` field is a rich basis for deriving `ServiceName`, `ServiceCategory` (`Databases`), `ChargeCategory`, `ChargeFrequency`, `RegionId` / `RegionName`, and `ResourceType`.

**The trivial Mandatory gaps (7 of 9):** these are derivable from data already present or are fixed literals, so adding them is plumbing:

- `ListCost`: `unitPriceDollars` times `quantity`, for flat-rate SKUs. Atlas cluster pricing is largely flat hourly rates, so this holds for most lines; tiered SKUs such as data transfer must compute list cost against the rate basis rather than a flat multiply.
- `ContractedCost`: `totalPriceCents` less `discountCents`, converted to a decimal dollar value.
- `ServiceCategory`: the fixed literal `Databases`.
- `ServiceName`: derived from the `sku` family (for example, cluster compute, backup, data transfer).
- `ChargeCategory`: derived from the `sku` (usage lines map to `Usage`; support or one-time SKUs map to `Purchase`; credit lines map to `Credit`).
- `ProviderName`, `PublisherName`, `InvoiceIssuerName`: fixed literals (`MongoDB`), with `PublisherName` and `InvoiceIssuerName` differing only where a cloud marketplace resells Atlas.
- `ChargeClass`: Mandatory but nullable, populated only to flag corrections to a previously invoiced period.

**The substantive Mandatory gaps (2 of 9):**

- `EffectiveCost`: the true cost after all discounts, credits, and adjustments. Line-level `discountCents` covers per-line discounting, but credits, starting balances, and other adjustments are reconciled at the invoice level (`startingBalanceCents`, `amountBilledCents`), not on the usage lines. Producing a per-line `EffectiveCost` requires allocating those invoice-level adjustments back down to the line items.
- `BilledCost`: the amount actually invoiced. The invoice exposes `amountBilledCents` at the invoice grain, but FOCUS needs it per charge record, so the same invoice-to-line reconciliation applies.

This is the list-cost trap in its common form: the daily line-item feed is close to list-only, and the billed and effective figures live one level up on the invoice. Do not treat `BilledCost` and `EffectiveCost` as a trivial copy of the derived `ListCost`.

**Conditional gaps worth closing:** `ContractedUnitPrice`, `RegionId` / `RegionName`, `ResourceType`, `PricingCategory`, `SkuMeter`, `SkuPriceId`, and `SkuPriceDetails` are all either present in raw form in the `sku` string or in the price catalog and can be surfaced. `PricingCurrency` is a trivial USD literal.

### 1.5 Deviations to fix

- **Cost scaling:** `totalPriceCents` and `discountCents` are integer US cents; FOCUS cost columns are decimal currency amounts. Divide by 100 and emit as decimals in `BillingCurrency`.
- **Native field names:** the schema uses MongoDB names (`groupId`, `clusterName`, `unitPriceDollars`). Map each to its FOCUS column ID rather than emitting the native name.
- **`ResourceId` versus `ResourceName`:** `clusterName` is a display name, not a stable identifier. Use it for `ResourceName` and source a stable cluster identifier for `ResourceId` where available.
- **`BillingCurrency` / `PricingCurrency`:** USD is implicit in the API rather than an explicit ISO 4217 field. Emit `USD` explicitly.
- **`PricingQuantity` on tiered SKUs:** `quantity` equals the FOCUS pricing quantity only for flat-rate SKUs. For tiered SKUs (data transfer, some storage), compute pricing quantity against the rate basis rather than copying `quantity`.
- **`ChargeCategory` enum:** ensure derived values map only to the FOCUS set (`Usage`, `Purchase`, `Tax`, `Credit`, `Adjustment`). Sales tax rows (from `salesTaxCents`) should carry `ChargeCategory: Tax`, and credit rows `ChargeCategory: Credit`, rather than being folded into usage.

**Already done right:** daily cost tabulation and period-scoped line items, a clean organization to project to cluster hierarchy that maps to billing account, sub-account, and resource, key-value tags, a rich `sku` field, an invoice `id` for `InvoiceId`, and inclusive-start line-item periods.

---

## Part 2: The path forward

### 2.1 Which FOCUS version to target

Baseline the build against v1.2, the current certification badge version, and design toward v1.4, the latest ratified release. The account hierarchy, granularity, and identity columns are all v1.2-stable. Note that `Provider` and `Publisher` are deprecated in v1.3 and removed in v1.4, so the `ProviderName` and `PublisherName` adds are v1.2-scoped and should be dropped when moving past v1.2. v1.4 also adds Invoice Detail and billing-period datasets that align naturally with the Atlas invoice object (`statusName`, `created`, `startingBalanceCents`), which is an advantage for MongoDB when it matures toward the latest version.

### 2.2 What certification requires

FOCUS conformance for data generators runs through the FinOps Foundation. MongoDB is not currently listed as a Supported data generator, so the first milestone is producing a FOCUS export at all; the Conformant designation is earned later by submitting a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report (this analysis is its seed). Membership is required for certification; contributing to the spec is open and free, and MongoDB already contributes to FOCUS. Contact `member-cert@finops.org` for the RFI. Validate output with the open-source FOCUS Validator against the Requirements Model, and consider the FOCUS Converter to accelerate the native-to-FOCUS transform.

### 2.3 Phased roadmap

**Phase 0: Validate what exists.** Pull a real invoice and its line items (JSON and CSV) and map the fields against FOCUS. Confirm line-item granularity is day-level in practice and confirm which SKUs are flat-rate versus tiered.

**Phase 1: Close the trivial Mandatory gaps and derive list cost.** Emit `ProviderName`, `PublisherName`, `InvoiceIssuerName` (literals), `ServiceCategory` (`Databases`), `ServiceName` and `ChargeCategory` (from `sku`), `ChargeClass` (nullable), `ListCost` (from `unitPriceDollars` times `quantity`, flat-rate SKUs), and `ContractedCost` (`totalPriceCents` less `discountCents`). Map the identity columns: `BillingAccountId` (`orgId`), `SubAccountId` / `SubAccountName` (`groupId` / `groupName`), `ResourceName` (`clusterName`), `Tags`.

**Phase 2: Close the substantive cost gap.** Build `EffectiveCost` and `BilledCost` per line by reconciling invoice-level credits, starting balances, sales tax, and adjustments back to the line items. This is the one real data-engineering step.

**Phase 3: Fix deviations and round out Conditional columns.** Scale cents to decimals, emit currencies explicitly, split `ResourceId` from `ResourceName`, handle tiered `PricingQuantity`, and add SKU-derived `RegionId` / `RegionName`, `ResourceType`, `PricingCategory`, `ContractedUnitPrice`, `SkuMeter`, `SkuPriceId`, and `SkuPriceDetails`.

**Phase 4: Mature toward the latest version.** Track v1.3/v1.4, drop `Provider`/`Publisher`, align the Atlas invoice object with the v1.4 Invoice Detail dataset, and pursue Supported then Conformant status.

### 2.4 FOCUS Use Cases unlocked

- **Available today (identity and granularity):** spend by project and by cluster (`Analyze costs by sub-account`, allocation by resource), tag-based cost allocation, day-level cost trending, and spend by service once `sku` is mapped to `ServiceName`.
- **Unlocked by Phase 1:** list-cost reporting and showback by project, and corrections reporting once `ChargeClass` exists.
- **Unlocked by Phase 2:** effective-cost and savings analysis (`Determine Effective Savings Rate`, discount effectiveness), actuals-based budgeting, and invoice reconciliation, all of which need `EffectiveCost` and `BilledCost` reconciled to the line.
- **Out of scope for this model:** commitment-discount and capacity-reservation use cases; Atlas consumption billing sells neither as FOCUS commitment constructs, so that column family is correctly N/A.

---

## Part 3: Immediate next steps

1. Pull a real Atlas invoice and its line items (JSON and CSV) and map every field to a FOCUS column ID.
2. Emit the trivial Mandatory columns: the three literals, `ServiceCategory`, `ServiceName`, `ChargeCategory`, `ChargeClass`, plus derived `ListCost` and `ContractedCost`.
3. Map the identity columns from `orgId`, `groupId` / `groupName`, `clusterName`, and `tags`.
4. Design the invoice-to-line reconciliation that produces per-line `EffectiveCost` and `BilledCost`.
5. Fix the deviations: cents-to-decimal scaling, explicit currency, `ResourceId` versus `ResourceName`, tiered `PricingQuantity`.
6. Run the output through the FOCUS Validator, then engage `member-cert@finops.org` on Supported and then Conformant status.

---

## Confidence summary

- **Data source (high):** The Atlas Administration API documents the invoice and line-item fields, and the billing documentation confirms daily cost tabulation and the organization to project hierarchy. The per-line-item field list (`sku`, `groupId`, `clusterName`, `unitPriceDollars`, `totalPriceCents`, `discountCents`, `percentDiscount`, `startDate`, `endDate`, `tags`) rests on published schema. Data quality for this analysis is solid.
- **Allocation and granularity strong (high):** Organization, project, and cluster give a clean hierarchy, tags are key-value, and daily tabulation with period-scoped line items supports sub-monthly charge records.
- **List cost derivable, effective and billed substantive (high):** List cost falls out of `unitPriceDollars` and `quantity` for flat-rate SKUs. `EffectiveCost` and `BilledCost` require reconciling invoice-level credits and adjustments to the line, which is a real engineering step, not a copy.
- **Trivial Mandatory gaps (high):** The three literals, the two `sku`-derived columns, `ServiceCategory`, and nullable `ChargeClass` are plumbing.
- **SKU-derived Conditional columns (medium):** Region, service subcategory, resource type, and pricing detail are encoded in the `sku` string and price catalog and are recoverable, but the exact `sku` grammar was not fully enumerated from the documentation and should be confirmed against live data.
- **Feature levels (high):** Verified against the bundled v1.2 reference and spot-checked live against the FOCUS specification on 2026-07-06; v1.2 remains the certification baseline and v1.4 the latest ratified version.

---

## Sources

- MongoDB Atlas Administration API v2, Invoices resource (Return One Invoice, Return All Line Items for One Invoice): https://www.mongodb.com/docs/api/doc/atlas-admin-api-v2/group/endpoint-invoices
- MongoDB Atlas, "Manage Billing": https://www.mongodb.com/docs/atlas/billing/
- MongoDB Atlas, "Manage Invoices": https://www.mongodb.com/docs/atlas/billing/invoices/
- MongoDB Atlas Architecture Center, "Features for Atlas Billing Data": https://www.mongodb.com/docs/atlas/architecture/current/billing-data/
- FOCUS Specification v1.2: https://focus.finops.org/focus-specification/v1-2/
- FOCUS Specification v1.4: https://focus.finops.org/focus-specification/v1-4/
- FOCUS column library: https://focus.finops.org/focus-columns/
- FOCUS Validator and Requirements Model: https://focus.finops.org/

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
