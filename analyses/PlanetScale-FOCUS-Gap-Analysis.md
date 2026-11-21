# PlanetScale & FOCUS: Data Generator Gap Analysis

*Analysis run: November 17, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** PlanetScale, Inc.  
**Prepared:** November 17, 2026  
**Origin:** KubeCon NA 2026 booth outreach  
**Source:** PlanetScale API reference (List invoices, Get invoice, Get invoice line items, Get database); `pscale billing` CLI docs; PlanetScale billing, plans, pricing, Postgres pricing, Vitess pricing, regions, and Cloudflare docs; PlanetScale Terms of Service  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 14 Present, 15 Deviation, 4 Missing Mandatory, 8 Missing Conditional, 1 Missing Recommended, 15 N/A

---

## Executive Summary

PlanetScale is a managed database provider running Vitess (MySQL-compatible) and Postgres on AWS, GCP, and Azure, including the locally attached NVMe "Metal" tier. Plans apply per database, and each branch runs on its own cluster, billed at a monthly SKU rate (`PS-5` through `PS-2800`, `M-10` through `M-7680`) prorated to the millisecond. Storage, backups beyond the included amount, egress, extra replicas, read-only regions, dedicated PgBouncers, development branches, and SSO add separate charges. Invoices are monthly in USD, issued by PlanetScale, Inc. through Stripe, or by Cloudflare for databases created from the Cloudflare dashboard.

PlanetScale is ahead of most providers in this cohort on one point: it has a documented, customer-facing **invoice line-items API** (`GET /organizations/{organization}/invoices/{id}/line-items`, also `pscale billing invoice line-items --format csv`) that returns a subtotal, description, metric name, database ID and name, and a resource object per line. That gives FOCUS a real starting dataset with database-level and resource-level attribution.

**Public billing documentation is thin on the details that decide conformance.** The line item has no quantity, unit, unit price, SKU, region, charge period, or currency. The docs do not list the values `metric_name` can take, do not say what kind of object `resource` is, and do not say whether `subtotal` is before or after coupons and proration discounts. Coupons appear only as an invoice note, and no credit, discount, tax, or commitment fields exist anywhere in the API. Enterprise contract and AWS Marketplace terms are not public. There is no FOCUS, S3, or warehouse export, and no PlanetScale page mentions FOCUS or FinOps.

On that basis, of the 21 Mandatory columns, 9 map directly, 8 need derivation, and 4 are missing. **2 of the 4 missing Mandatory columns are substantive.** EffectiveCost requires allocating invoice-level coupons, proration discounts, and any Enterprise credits back to lines. PricingQuantity requires usage quantities (cluster hours, GB-months, GB transferred) that the line item does not carry. ListCost and PricingUnit are derivable from the public price catalog and `metric_name`.

**Recommendation:** Extend the existing line-items API rather than building a new surface. Add `quantity`, `unit`, `unit_price`, `sku` (for example `PS-40` or `M-320`), `region`, `branch_id` and `branch_name`, `charge_period_start` and `charge_period_end`, and `currency` to each line; emit coupons, proration discounts, credits, and tax as their own signed lines that sum to the invoice total; document the `metric_name` enumeration; and add a daily (or at least per-resize) grain. Then publish a FOCUS v1.2 CSV from the same pipeline.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

- **Invoices API** (`read_invoices` scope; `https://api.planetscale.com/v1`): `GET /organizations/{organization}/invoices` and `GET .../invoices/{id}` return `id`, `total` (stringified decimal), `billing_period_start`, `billing_period_end`, `paid`, and `overdue`. No currency, tax, or discount field.
- **Invoice line items** (`GET .../invoices/{id}/line-items`, paginated): each line has `id`, `subtotal` (number), `description`, `metric_name` ("the name of the billable item"), `cloudflare_billed` (boolean), `database_id`, `database_name`, and `resource` (`id`, `name`, `created_at`, `updated_at`, `deleted_at`).
- **CLI:** `pscale billing invoice list | show | line-items` with `--format human|json|csv`. This is the only documented CSV path.
- **Dashboard:** Settings > Billing shows usage per database and links each invoice to a Stripe-hosted PDF. Spend alerts fire at 75% and 100% of a customer-set budget.
- **Database API** (`GET .../databases/{database}`): a `region` object (`id`, `provider`, `slug`, `display_name`, `location`, `availability_zones[]`), plus `kind` (`mysql`, `postgresql`, `neki`), `plan`, `sharded`, and branch counts. Not joined to line items by PlanetScale; a consumer would join on `database_id`.
- **Public price catalog:** a read-only Postgres table, `public.planetscale_prices` (`product`, `provider`, `region`, `machine_sku`, `disk_sku`, `replication_factor`, `price` in whole USD per month, `network_transfer_gb`), plus unauthenticated egress-rate and storage-rate endpoints. List prices only; not customer billing.

Key characteristics:

- **Compute:** Monthly SKU rate per branch cluster, prorated to the millisecond, in HA (primary plus two replicas) and single-node forms on arm64 and x86-64. Resizes switch rates when the resize completes (PS-10 to PS-20 mid-month: $39/2 + $59/2 = $49).
- **Storage:** Network-attached storage has 10 GB included, then is billed per instance (Vitess $0.50/GB per instance, so $1.50/GB for an HA branch; Postgres at regional gp3 or Hyperdisk rates plus IOPS and throughput above baseline). Metal storage is in the SKU price. Storage is prorated by branch hours over billing-period hours.
- **Other meters:** Backups beyond 2x disk size at $0.023/GB-month; Postgres egress above 100 GB (production) or 10 GB (development) per branch at regional rates; private connections $0.01/GB; cross-region replica traffic $0.02 to $0.16/GB; extra replicas, read-only regions, VTGates, and `PGB-*` PgBouncers; Vitess development branch hours beyond the included 1,440; Postgres development branches $5/month; SSO $199/month per organization.
- **Discounts:** Coupons (one active, not stackable) shown as an invoice note; "Prorated discounts" on invoices for partial-period branches. Self-serve Postgres has "no upfront commitments." Enterprise terms are by contract and not public.
- **Hierarchy:** Organization, Database, Branch, then cluster or keyspace. Teams exist for access control only.
- **Regions:** Slugs are not uniform. Older AWS regions use short slugs (`us-east`, `eu-west`), newer ones are prefixed (`aws-us-east-2`, `gcp-us-central1`, `azure-eastus2`), and the price catalog uses native cloud IDs (`us-east-1`).
- **Tags:** No resource tags or labels for cost allocation. The only "tags" are SQL query tags in Query Insights.
- **Channels:** Direct (Stripe, card only), Cloudflare-billed (flagged per line by `cloudflare_billed`), AWS Marketplace for PlanetScale Managed, and Stripe Projects provisioning.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven: every Mandatory column must be present and valid, and Conditional columns are required when the provider's model triggers their condition. This analysis treats the invoice line-items API as the candidate dataset. A column is Present when a line-item or invoice field maps one-to-one, and Deviation when the value exists in that API or can be derived from a documented field or constant but is not emitted in FOCUS form. Missing means no documented customer surface carries it at line grain.

Because plans apply per database and every line carries `database_id` and `database_name`, the database maps to SubAccount and the line's `resource` (most likely the branch) maps to Resource. PlanetScale publishes no commitment or reservation program for self-serve, so the CommitmentDiscount and CapacityReservation families are N/A. Pricing and billing are USD only, so the PricingCurrency family is N/A. PlanetScale supports no user-defined resource tags, so Tags is N/A. HA clusters span three availability zones by design, so a per-line AvailabilityZone is not meaningful. Feature levels below follow the FOCUS v1.2 Content Constraints, spot-checked against the live spec on November 17, 2026.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | PlanetScale source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Line `subtotal`; coupons appear only as an invoice note and tax is not itemized, so lines may not sum to the invoice `total` | Deviation |
| EffectiveCost | Mandatory | Not emitted; needs coupon, proration-discount, and Enterprise credit allocation (and amortization if contracts include prepaid spend) | Missing: Mandatory |
| ListCost | Mandatory | Not emitted; = pre-coupon `subtotal` for self-serve, public price catalog × quantity for Enterprise | Missing: Mandatory |
| ContractedCost | Mandatory | Line `subtotal` is at the customer's rate before invoice-level coupons; emit as ContractedCost | Deviation |
| BillingAccountId | Mandatory | Organization ID | Present |
| BillingAccountName | Mandatory | Organization name | Present |
| BillingCurrency | Mandatory | Not emitted; constant "USD" | Deviation |
| BillingPeriodStart | Mandatory | Invoice `billing_period_start` | Present |
| BillingPeriodEnd | Mandatory | Invoice `billing_period_end` | Present |
| ChargePeriodStart | Mandatory | Not on line items; billing period only, bounded by `resource.created_at` | Deviation |
| ChargePeriodEnd | Mandatory | Not on line items; billing period only, bounded by `resource.deleted_at` | Deviation |
| ChargeDescription | Mandatory | Line `description` | Present |
| ChargeCategory | Mandatory | Derive: "Usage" for metered lines, "Purchase" for SSO, "Credit" for coupons and proration discounts, "Tax" where applied | Deviation |
| ChargeClass | Mandatory (nullable) | null; "Correction" for re-issued invoices | Present |
| InvoiceIssuerName | Mandatory | "PlanetScale, Inc." for direct; "Cloudflare, Inc." where `cloudflare_billed` is true; AWS for Marketplace purchases | Present |
| ProviderName | Mandatory (dep. v1.3) | "PlanetScale" | Present |
| PublisherName | Mandatory (dep. v1.3) | "PlanetScale" | Present |
| ServiceName | Mandatory | Not emitted; derive from database `kind`: "PlanetScale Vitess", "PlanetScale Postgres", "PlanetScale Neki" | Deviation |
| ServiceCategory | Mandatory | Not emitted; constant "Databases" | Deviation |
| PricingQuantity | Mandatory | No quantity on any line; cluster time derivable from resource lifecycle and resize history, but storage GB-months, egress GB above allowance, and backup overage are not | Missing: Mandatory |
| PricingUnit | Mandatory | Not emitted; derive from `metric_name` ("Hours", "GB-Months", "GB", "Branches") once the enumeration is documented | Missing: Mandatory |
| ConsumedQuantity | Conditional | Not emitted | Missing: Conditional |
| ConsumedUnit | Conditional | Not emitted | Missing: Conditional |
| ListUnitPrice | Conditional | Not emitted; public `planetscale_prices` catalog and rate endpoints | Missing: Conditional |
| ContractedUnitPrice | Conditional | Not emitted; = ListUnitPrice for self-serve, Enterprise contract otherwise | Missing: Conditional |
| PricingCategory | Conditional | Derive: "Standard" | Deviation |
| BillingAccountType | Conditional | Not emitted; "Organization", or "Cloudflare Account" for Cloudflare-billed lines | Deviation |
| SubAccountId | Conditional | Line `database_id` | Present |
| SubAccountName | Conditional | Line `database_name` | Present |
| SubAccountType | Conditional | Not emitted; constant "Database" | Deviation |
| ResourceId | Conditional | Line `resource.id` | Present |
| ResourceName | Conditional | Line `resource.name` | Present |
| ResourceType | Conditional | Not emitted; the `resource` object has no type field ("Branch", "Database", "PgBouncer") | Missing: Conditional |
| SkuId | Conditional | Not on line items; `machine_sku` (`PS-40`, `M-320`, `PGB-*`) exists in the price catalog | Missing: Conditional |
| Tags | Conditional | N/A: no user-defined resource tags or labels | N/A |
| PricingCurrency | Conditional | N/A: priced and billed in USD only | N/A |
| PricingCurrencyListUnitPrice | Conditional | N/A | N/A |
| PricingCurrencyContractedUnitPrice | Conditional | N/A | N/A |
| PricingCurrencyEffectiveCost | Conditional | N/A | N/A |
| SkuMeter | Conditional | Line `metric_name` ("the name of the billable item"); values undocumented | Deviation |
| SkuPriceId | Conditional | Not exposed | Missing: Conditional |
| SkuPriceDetails | Conditional | Not exposed; needed for architecture, HA vs. single-node, replication factor, and included allowances | Missing: Conditional |
| RegionId | Conditional | Not on line items; database `region.slug` via the Database API, with inconsistent slug formats | Deviation |
| RegionName | Conditional | Not on line items; database `region.display_name` | Deviation |
| CommitmentDiscountId | Conditional | N/A: no published commitment program | N/A |
| CommitmentDiscountName | Conditional | N/A | N/A |
| CommitmentDiscountType | Conditional | N/A | N/A |
| CommitmentDiscountCategory | Conditional | N/A | N/A |
| CommitmentDiscountStatus | Conditional | N/A | N/A |
| CommitmentDiscountQuantity | Conditional | N/A | N/A |
| CommitmentDiscountUnit | Conditional | N/A | N/A |
| CapacityReservationId | Conditional | N/A: no capacity reservations | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | Invoice `id` | Present |
| ChargeFrequency | Recommended | Derive: "Usage-Based" for prorated clusters and metered lines; "Recurring" for SSO | Deviation |
| ServiceSubcategory | Recommended | Not emitted; "Relational Databases" | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: HA clusters span three zones by design | N/A |

**Tally:** 14 Present, 15 Deviation, 4 Missing Mandatory, 8 Missing Conditional, 1 Missing Recommended, 15 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** A documented, customer-facing line-item API with JSON and CSV output; organization, database, and resource attribution on every line; billing period and invoice ID; a Cloudflare-billed flag that identifies the invoice issuer per line; and a public, machine-readable price catalog. Few providers in this cohort start this close to a usable dataset.

**Substantive (2 of 4 Mandatory gaps):**

- **EffectiveCost.** Coupons are an invoice note, proration discounts are an invoice adjustment, and Enterprise credits are undocumented. Row-level EffectiveCost requires allocating each back to lines (proportionally to subtotal is the usual rule) and, if Enterprise contracts include prepaid or committed spend, amortizing it.
- **PricingQuantity.** No line carries a quantity. Cluster time can be reconstructed from resource lifecycle and resize events, but storage GB-months (prorated by branch hours), egress GB above the per-branch allowance, and backup overage cannot be rebuilt from public data. Storage, egress, and development branch hours are all tiered by an included allowance, so PricingQuantity must be computed against the rate basis, not copied from consumption.

**Trivial (2 of 4 Mandatory gaps):**

- **ListCost.** For self-serve, the pre-coupon `subtotal` is the list amount. For Enterprise, join the public catalog by SKU, region, and replication factor once quantity and SKU are on the line.
- **PricingUnit.** A lookup from `metric_name` once the enumeration is documented.

**Substantive, beyond the column table:**

- **Lines do not reconcile to the invoice.** The API has no coupon, credit, discount, or tax lines, so the sum of `subtotal` values and the invoice `total` can differ with no machine-readable explanation. BilledCost is listed as a Deviation because the field exists, but closing it is real work.
- **Monthly grain only.** Line items carry no charge period. A resize mid-month, or a branch created and deleted within the month, collapses into one subtotal. Daily or per-rate-segment lines are needed for anomaly detection and day-level allocation.
- **No region or SKU on the line.** Both live on other endpoints or in the catalog, and region slugs come in three formats. A consumer joining `database_id` to the Database API gets the database's primary region, not the region of a read-only replica line.
- **Channel coverage.** Cloudflare-billed lines appear in PlanetScale's API but are invoiced by Cloudflare; AWS Marketplace and PlanetScale Managed customers receive part of their bill from a hyperscaler. A FOCUS export must carry the correct InvoiceIssuerName per line, and Managed customers will need PlanetScale's rows alongside their own cloud's FOCUS data.

### 1.5 Deviations to Fix

**BilledCost and ContractedCost:** Emit `subtotal` as ContractedCost, and emit BilledCost net of line-allocated coupons and proration discounts, with separate Credit and Tax lines so the dataset sums to the invoice `total`.

**ChargePeriodStart and ChargePeriodEnd:** Emit per line, splitting lines at resizes and at day boundaries.

**RegionId and RegionName:** Put region on each line and normalize to one slug scheme. Using the native cloud region ID (`us-east-1`), as the price catalog already does, makes cross-provider joins easiest.

**SkuMeter:** Publish the `metric_name` enumeration and keep it stable.

**ServiceName, ServiceCategory, ChargeCategory, ChargeFrequency, PricingCategory, BillingCurrency, BillingAccountType, SubAccountType:** Derive as shown in the table.

**Already right:** Organization, database, and resource identifiers; invoice ID and billing period; line descriptions; and the per-line Cloudflare billing flag.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (ratified June 4, 2026); certify at FOCUS v1.2, the version the conformance program currently names. FOCUS v1.5 is in release candidate with ratification scheduled for December 3, 2026; its SKU Price dataset (a preview, not evaluated for conformance) is a natural fit for the `planetscale_prices` catalog PlanetScale already publishes. The v1.4 Invoice Detail dataset maps onto the existing invoices endpoint.

### 2.2 What Certification Requires

FinOps Certified FOCUS v1.2 Conformant runs through the FinOps Foundation (contact `member-cert@finops.org` for the RFI; membership is required for certification). Deliverables: a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report seeded by this analysis. Tooling: FOCUS Validator, FOCUS Converter, and the FOCUS Requirements Model. Document the N/A rationale (no tags, commitments, reservations, alternate currencies, or per-line zones) and the database-as-SubAccount mapping.

### 2.3 Phased Roadmap

**Phase 0: Validate.** Pull one month of line items for a test organization with resizes, a coupon, and Postgres egress overage. Hand-build a FOCUS file from line items, the Database API, and the price catalog; run it through the Validator; and record which columns cannot be filled.

**Phase 1: Enrich the line item.** Add `quantity`, `unit`, `unit_price`, `sku`, `region`, `branch_id`, `branch_name`, `resource_type`, `charge_period_start`, `charge_period_end`, and `currency`. Document `metric_name` values. Split lines at resizes.

**Phase 2: Close Mandatory gaps.** Emit coupon, proration-discount, credit, and tax lines; allocate them for BilledCost and EffectiveCost; compute ListCost from the catalog for Enterprise rates; publish a FOCUS v1.2 CSV and API response from the same pipeline.

**Phase 3: Fill Conditional and Recommended.** Add SkuPriceId and SkuPriceDetails from the catalog, ServiceSubcategory, and daily grain. Consider provider-defined tags (branch role `production` or `development`, `kind`, architecture) and, if requested, user-defined database or branch labels.

**Phase 4: Mature and certify.** Drop ProviderName and PublisherName for v1.4; add recency and completeness metadata (v1.3) and the Invoice Detail dataset (v1.4); expose the catalog as a v1.5 SKU Price dataset; certify at v1.2 and re-certify as the program advances.

### 2.4 FOCUS Use Cases Unlocked

- **Today:** Monthly spend by organization, database, and resource from line items; invoice tracking; budget alerts at the organization level.
- **After Phase 1:** Unit cost per cluster SKU and per GB, resize impact analysis, regional cost comparison, and development versus production branch spend.
- **After Phase 2:** Invoice reconciliation, database-level showback and chargeback at net cost, and actuals-based budgeting and forecasting.
- **After Phase 3:** Daily anomaly detection, cross-provider managed database comparison (PlanetScale vs. RDS, Aurora, Cloud SQL, Neon), and attribute-based allocation via provider tags.
- **Out of scope:** Commitment utilization, capacity reservation management, availability zone analysis, and multi-currency reporting.

---

## Part 3: Immediate Next Steps

1. Follow up with the PlanetScale contact from KubeCon NA 2026 to identify the owner of billing and the invoices API.
2. Ask PlanetScale to document the `metric_name` enumeration, what `resource` represents, and whether `subtotal` is before or after coupons and proration discounts.
3. Confirm whether Enterprise contracts include committed or prepaid spend, how AWS Marketplace and Cloudflare-billed usage is invoiced, and how tax is applied.
4. Build a v1.2 sample from one month of line items plus the Database API and price catalog, and run it through the FOCUS Validator.
5. Open the RFI with `member-cert@finops.org`.

---

## Confidence Summary

- **High:** Invoice and line-item field names, types, and endpoints, from the PlanetScale API reference and CLI docs.
- **High:** Billing model (per-branch clusters, monthly SKU rates prorated to the millisecond, storage, egress, development branch, and SSO charges), from PlanetScale plans and pricing docs.
- **High:** No currency, quantity, unit, SKU, region, charge period, discount, or tax field on invoice line items, and no FOCUS or warehouse export.
- **High:** Feature levels match the FOCUS v1.2 Content Constraints; spot-checked against the live spec on November 17, 2026 (ServiceSubcategory and ChargeFrequency Recommended, PricingQuantity Mandatory, Tags Conditional), and v1.4 remains the latest ratified version.
- **High:** "PlanetScale, Inc." as InvoiceIssuerName for direct billing, from the Terms of Service and site terms.
- **Moderate:** `resource` represents the branch. The API describes it only as a generic object with timestamps.
- **Moderate:** No commitment program. None is published, but Enterprise terms are by contract; if they include committed spend, the seven CommitmentDiscount columns become applicable.
- **Moderate:** Database as SubAccount. Defensible because plans apply per database, but PlanetScale could reasonably model the database as the resource and the branch as a child.
- **Low:** Whether `subtotal` is pre- or post-coupon and pre- or post-proration discount, the `metric_name` values, tax handling, and AWS Marketplace and Stripe Projects billing routes. None is documented.

---

## Sources

- PlanetScale API: [List invoices](https://planetscale.com/docs/api/reference/list_invoices) · [Get invoice](https://planetscale.com/docs/api/reference/get_invoice) · [Get invoice line items](https://planetscale.com/docs/api/reference/get_invoice_line_items) · [Get database](https://planetscale.com/docs/api/reference/get_database)
- PlanetScale CLI billing: [planetscale.com/docs/cli/billing](https://planetscale.com/docs/cli/billing)
- PlanetScale Billing: [planetscale.com/docs/concepts/billing](https://planetscale.com/docs/concepts/billing)
- PlanetScale Plans: [planetscale.com/docs/planetscale-plans](https://planetscale.com/docs/planetscale-plans)
- PlanetScale Pricing: [planetscale.com/pricing](https://planetscale.com/pricing) · [Postgres pricing](https://planetscale.com/docs/postgres/pricing) · [Vitess pricing](https://planetscale.com/docs/vitess/pricing)
- PlanetScale Regions: [planetscale.com/docs/plans/regions](https://planetscale.com/docs/plans/regions)
- PlanetScale with Cloudflare: [planetscale.com/docs/connect/cloudflare](https://planetscale.com/docs/connect/cloudflare)
- PlanetScale Terms of Service: [planetscale.com/legal/agreement](https://planetscale.com/legal/agreement)
- PlanetScale on AWS Marketplace: [aws.amazon.com/marketplace](https://aws.amazon.com/marketplace/pp/prodview-luy3krhkpjne4)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FOCUS 1.5 Release Scope: [focus.finops.org/focus-1-5-release-scope/](https://focus.finops.org/focus-1-5-release-scope/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
