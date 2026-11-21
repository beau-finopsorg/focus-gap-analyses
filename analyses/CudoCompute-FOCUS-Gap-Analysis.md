# Cudo Compute & FOCUS: Data Generator Gap Analysis

*Analysis run: July 1, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** CUDO Ventures (Cudo Compute)
**Prepared:** July 1, 2026
**Source:** Cudo Compute REST billing API (docs.cudocompute.com), OpenAPI schema; on-demand platform docs retained for reference
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4
**Tally:** 17 Present, 11 Deviation, 2 Missing Mandatory, 13 Missing Conditional, 2 Missing Recommended, 12 N/A

---

## Executive Summary

Cudo Compute is a distributed GPU cloud that aggregated independently operated data centers into a single API, CLI, and Terraform surface. Its public on-demand platform closed on March 31, 2026, and the company has pivoted to dedicated enterprise AI infrastructure sold under custom contracts. The billing data described here comes from the REST API that served the on-demand platform (docs retained for reference), which is the most concrete published schema and a fair proxy for how Cudo structures cost and usage.

The billing API exposes two relevant objects. The spend-details report (`BillingAccountSpendRow`) returns per-project rows with a description, a quantity, a unit (UNIT_HOUR, UNIT_GIB_HOUR), a unit price, and an amount for a requested time window. The invoice object carries period, currency, tax, and totals. Every FOCUS Mandatory column has a plausible source except the two that turn on Cudo's discount and credit mechanics. Commitment purchases (a lower hourly VM rate) and account credit balances both exist, and both land at the account or invoice level rather than on the spend row, so `EffectiveCost` and `ContractedCost` are a substantive reconciliation gap, not a copy of list cost.

Nineteen columns are N/A for the spend-report grain: no per-row resource identity, no tags, no region on the row, and (for the base report) no SKU codes. The nine Deviations are the FOCUS shaping work: native names, epoch and minor-unit numeric formats, unit relabeling, and enum derivation.

**Recommendation:** Treat the spend-details report as the FOCUS charge grain, one row per project per SKU per period, and enrich it. Set ServiceCategory = "Compute", derive ChargeCategory (Usage, Purchase for commitments, Credit for credit draws), relabel units (UNIT_HOUR to "Hours", UNIT_GIB_HOUR to "GiB-Hours"), and reconcile commitment and credit effects back to the row to produce EffectiveCost and ContractedCost. Join resource, region, and tag context from the VM, cluster, and project APIs to lift Allocation.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

**Cudo Compute REST billing API** (base `https://rest.compute.cudo.org/v1/`, bearer API-key auth). Relevant endpoints and fields:

- **Spend details** (`GET /billing-accounts/{id}/spend/details`, query `startTime`/`endTime`): returns an array of `BillingAccountSpendRow`. Fields: `projectId`, `description`, `quantity` (float), `unit` (enum UNIT_UNKNOWN, UNIT_HOUR, UNIT_GIB_HOUR), `unitAmount` (decimal string), `amount` (decimal string).
- **Invoices** (`GET /invoices`): `Invoice` object with `id`, `number`, `currency`, `periodStart`, `periodEnd` (Unix epoch seconds), `amountDue`, `amountPaid`, `amountRemaining`, `subtotal`, `subtotalExcludingTax`, `tax`, `total`, `totalExcludingTax` (int64 minor-unit strings), `status`, `billingReason`, `dueDate`, `paidDate`, `hostedInvoiceUrl`.
- **Billing account details** (`GET /billing-accounts/{id}/details`): `displayName`, `monthlySpend`, `hourlySpendRate`, `creditBalance`, `taxId`, `invoiceTime`, `nextInvoiceTotal`, `stripeRef`.
- **Projects** (`list-billing-account-projects`, project APIs): projects are namespaces for resources, billed to one billing account. Multiple projects per billing account.
- **Resource context** (VM, cluster, machine, disk, volume, network APIs): resource IDs, names, GPU models, data centers, and metadata live on the resource objects, not on the spend row.
- **Commitments** (`purchase-a-commitment-for-a-virtual-machine`): a VM can be committed to a longer term for a lower hourly rate.

Key characteristics:

- **Usage grain:** The spend report is per project per line description over a caller-chosen time window. It is not inherently daily, and it carries no per-row start and end timestamps.
- **Projects as sub-accounts:** `projectId` is the natural `SubAccountId`, sitting under the billing account. This is real allocation structure.
- **Distributed marketplace:** Cudo aggregates independent data centers. Data center identity exists on resources (region and availability-zone analog) but is not on the spend row.
- **Discounts and credits exist and land off the row:** Commitment purchases lower the hourly VM rate, and billing accounts carry a credit balance drawn down over time. Neither appears on the spend row, which reports quantity times unitAmount as a gross amount.
- **Single currency per account:** The invoice `currency` is the billing currency. There is no separate pricing currency in the data.
- **No FOCUS shaping:** Native field names, epoch timestamps, and minor-unit integer strings throughout.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven. Each column carries a feature level (Mandatory, Conditional, Recommended, Optional) verified against the FOCUS v1.2 Content Constraints tables. Mandatory columns must be present and populated; Conditional columns are required when the provider's model triggers the condition and may otherwise be null; Recommended columns are encouraged. Cudo's commitment purchases populate the CommitmentDiscount family (VM commitments = PricingCategory "Committed" plus a CommitmentDiscount construct). Its credit balance populates ChargeCategory "Credit" rows. Data-center-only geography means RegionId is applicable but AvailabilityZone maps only where zones are exposed.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | Cudo Compute source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Spend row `amount` (invoiced, gross of credit draw); reconcile to invoice `total` | Deviation |
| EffectiveCost | Mandatory | Not on row: requires reconciling commitment rate and credit draw back to the line | Missing: Mandatory |
| ListCost | Mandatory | `quantity` x on-demand `unitAmount` (list rate) | Present |
| ContractedCost | Mandatory | Not on row: committed VMs bill a lower negotiated rate applied off the spend row | Missing: Mandatory |
| BillingAccountId | Mandatory | Billing account `id` | Present |
| BillingAccountName | Mandatory | Billing account `displayName` | Present |
| BillingCurrency | Mandatory | Invoice `currency` | Present |
| BillingPeriodStart | Mandatory | Invoice `periodStart` (epoch to ISO 8601) | Deviation |
| BillingPeriodEnd | Mandatory | Invoice `periodEnd` (epoch to ISO 8601) | Deviation |
| ChargePeriodStart | Mandatory | Query `startTime`, or derive per row from resource run history | Deviation |
| ChargePeriodEnd | Mandatory | Query `endTime`, or derive per row from resource run history | Deviation |
| ChargeDescription | Mandatory | Spend row `description` | Present |
| ChargeCategory | Mandatory | Derive: "Usage"; "Purchase" for commitments; "Credit" for credit draws; "Tax" for tax lines | Deviation |
| ChargeClass | Mandatory (nullable) | null except invoice corrections | Present |
| InvoiceIssuerName | Mandatory | "CUDO Ventures" | Present |
| ProviderName | Mandatory (dep. v1.3) | "Cudo Compute" | Present |
| PublisherName | Mandatory (dep. v1.3) | "Cudo Compute" (aggregated third-party data centers make this an enrichment target) | Present |
| ServiceName | Mandatory | Product from `description` (e.g., "Virtual Machine", "Bare Metal", "Object Storage") | Present |
| ServiceCategory | Mandatory | Derive: "Compute" for VM/cluster/bare metal; "Storage" for disks/volumes/object storage | Deviation |
| PricingQuantity | Mandatory | Spend row `quantity` (flat-rate hourly and GiB-hour SKUs) | Present |
| PricingUnit | Mandatory | Relabel `unit`: UNIT_HOUR to "Hours", UNIT_GIB_HOUR to "GiB-Hours" | Deviation |
| ConsumedQuantity | Conditional | = `quantity` for hourly compute; distinct for tiered storage | Present |
| ConsumedUnit | Conditional | Relabel `unit` | Deviation |
| ListUnitPrice | Conditional | Spend row `unitAmount` (on-demand list rate) | Present |
| ContractedUnitPrice | Conditional | Committed hourly rate; not on the spend row | Missing: Conditional |
| PricingCategory | Conditional | Derive: "Standard" on-demand; "Committed" for commitment-priced VMs | Missing: Conditional |
| ChargeFrequency | Recommended | Derive: "Usage-Based" for metered rows; "One-Time" for credit purchases | Missing: Recommended |
| BillingAccountType | Conditional | "billing account" (single tier) | Missing: Conditional |
| SubAccountId | Conditional | `projectId` | Present |
| SubAccountName | Conditional | Project display name (join from projects API) | Deviation |
| SubAccountType | Conditional | "project" | Missing: Conditional |
| ResourceId | Conditional | Not on spend row; join VM/cluster/machine `id` via description or resource API | Missing: Conditional |
| ResourceName | Conditional | Not on spend row; join resource name | Missing: Conditional |
| ResourceType | Conditional | Not on spend row; derive (virtual-machine, cluster, bare-metal, disk, volume, bucket) | Missing: Conditional |
| SkuId | Conditional | Machine-type / GPU-model / volume-price code (join from resource-type APIs) | Missing: Conditional |
| SkuMeter | Conditional | Metered dimension (GPU-hour, vCPU-hour, GiB-hour) | Missing: Conditional |
| SkuPriceId | Conditional | Not exposed as a stable price ID | Missing: Conditional |
| SkuPriceDetails | Conditional | Not exposed | Missing: Conditional |
| Tags | Conditional | VM metadata (key-value) via update-metadata API; not on the spend row | Missing: Conditional |
| PricingCurrency | Conditional | = Invoice `currency` (single currency) | Present |
| PricingCurrencyListUnitPrice | Conditional | = ListUnitPrice (single currency) | Present |
| PricingCurrencyContractedUnitPrice | Conditional | = ContractedUnitPrice once reconciled | Missing: Conditional |
| PricingCurrencyEffectiveCost | Conditional | = EffectiveCost once reconciled | Deviation |
| RegionId | Conditional | Data-center ID (join from resource / list-data-centers) | N/A |
| RegionName | Conditional | Data-center name (join from resource) | N/A |
| AvailabilityZone | Recommended | N/A: data-center granularity, no separate zone layer | N/A |
| CommitmentDiscountId | Conditional | Commitment purchase identifier (VM commitment) | N/A |
| CommitmentDiscountName | Conditional | Commitment plan name | N/A |
| CommitmentDiscountType | Conditional | "Committed Use" for VM commitments | N/A |
| CommitmentDiscountCategory | Conditional | "Usage" (commitment lowers the usage rate) | N/A |
| CommitmentDiscountStatus | Conditional | Used / Unused | N/A |
| CommitmentDiscountQuantity | Conditional | Committed quantity | N/A |
| CommitmentDiscountUnit | Conditional | Commitment unit | N/A |
| CapacityReservationId | Conditional | N/A: no capacity-reservation construct in the API | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | Invoice `id` / `number` | Present |
| ServiceSubcategory | Recommended | "Virtual Machines", "Bare Metal", "GPU Cloud", "Object Storage" | Missing: Recommended |

**Tally:** 17 Present, 11 Deviation, 2 Missing Mandatory, 13 Missing Conditional, 2 Missing Recommended, 12 N/A (57 columns).

Note on the CommitmentDiscount and Region families: these are marked N/A in the base spend-report grain because that report carries neither commitment context nor a data-center column. They are applicable to Cudo's model and become populated columns once the spend row is joined to the commitment record and the resource's data center. The report should carry these columns and populate them on the relevant rows rather than dropping them.

### 1.4 What Is Solved, and What Remains

**Solved:** Billing account identity, currency, invoice period, project (SubAccountId), charge description, list unit price, consumed quantity, and invoice ID all have direct sources. ListCost is a clean quantity times unit-price product for flat-rate hourly and GiB-hour SKUs.

**Substantive gaps (2 of 2 Missing Mandatory):** `EffectiveCost` and `ContractedCost`. Commitment purchases lower the effective VM rate and credit balances draw down actual paid amounts, but both effects are applied at the account or invoice level and are absent from the spend row. Producing these columns requires reconciling commitment terms and credit draws back to individual usage lines. This is real data work, not a copy of ListCost.

**Trivial Mandatory adds:** `ChargeClass` is null outside corrections. `PricingQuantity` and `PricingUnit` derive directly from the row's `quantity` and `unit` for the flat-rate hourly and GiB-hour SKUs that dominate the platform.

**Conditional and Recommended remainder:** Resource identity, SKU codes, tags, sub-account type, and service subcategory all require joining the spend row to the resource and project APIs. They lift allocation and reporting value but do not block conformance.

### 1.5 Deviations to Fix

- **Numeric formats:** Invoice amounts are int64 minor-unit strings and periods are Unix epoch seconds. Convert to decimal currency values and ISO 8601 timestamps.
- **PricingUnit / ConsumedUnit:** Relabel the `unit` enum (UNIT_HOUR to "Hours", UNIT_GIB_HOUR to "GiB-Hours").
- **ChargeCategory:** Derive from row type: "Usage" for metered consumption, "Purchase" for commitment purchases, "Credit" for credit draws, "Tax" for tax lines. Do not emit "Compute" (that is a ServiceCategory value).
- **ServiceCategory:** Derive "Compute" or "Storage" from the product in `description`.
- **BilledCost:** The spend `amount` is gross; reconcile against invoice totals so BilledCost reflects the invoiced figure after credit application.
- **SubAccountName:** Join the project display name rather than emitting only `projectId`.

Already done right: single billing currency is consistent, list pricing is transparent (quantity times published unit rate), and `projectId` provides genuine sub-account structure.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (June 4, 2026); certify at FOCUS v1.2, the current certification baseline. On v1.4, drop `ProviderName` and `PublisherName` (removed) and adopt the Invoice Detail and billing-period datasets, which fit Cudo's invoice-level reconciliation model well.

### 2.2 What Certification Requires

FOCUS conformance for data generators runs through the FinOps Foundation. Contact `member-cert@finops.org` for the RFI. Membership is required for certification, though contributing to the spec is open and free. Deliverables: a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report (this analysis is its seed). Tooling: the FOCUS Validator (checks data against the Requirements Model), the FOCUS Converter (provider-native to FOCUS), and the FOCUS Requirements Model (machine-readable MUST/SHOULD/MAY rules).

### 2.3 Phased Roadmap

**Phase 0: Validate and scope.** Confirm the target billing surface for the current enterprise-contract model versus the retained on-demand API. Pull a sample spend-details response and invoice, and run them through the FOCUS Validator to baseline.

**Phase 1: Close the substantive Mandatory gaps and trivial adds.** Reconcile commitment rates and credit draws to the spend row to produce EffectiveCost and ContractedCost. Emit ListCost, PricingQuantity, PricingUnit, and ChargeClass. This unlocks the bulk of conformance.

**Phase 2: Fix format and value deviations.** Convert epoch and minor-unit fields, relabel units, derive ChargeCategory and ServiceCategory enums, and reconcile BilledCost to invoice totals.

**Phase 3: Round out Conditional and Recommended columns.** Join resource identity (ResourceId, ResourceName, ResourceType), SKU codes, tags, and data-center region from the resource APIs. Populate the CommitmentDiscount family on committed rows. Add SubAccountType, SubAccountName, ChargeFrequency, and ServiceSubcategory.

**Phase 4: Mature and certify.** Move to v1.4, drop ProviderName and PublisherName, adopt the Invoice Detail dataset, validate, and open the RFI.

### 2.4 FOCUS Use Cases Unlocked

- **As soon as the transform ships (Phase 1 to 2):** cost reporting by project (Cost by SubAccount), invoice reconciliation (with the reconciled cost columns), and unit-economics reporting on GPU-hours.
- **After Phase 3 enrichment:** resource-level allocation (Cost by Resource), tag-based showback and chargeback (Cost by Tag), region reporting (Cost by Region, relabeled to data center), and commitment coverage and utilization (Commitment Discount Analysis).
- **Out of scope for the current model:** capacity-reservation use cases (no reservation construct in the API).

---

## Part 3: Immediate Next Steps

1. Confirm which billing surface certification should target: the enterprise-contract invoicing model or the retained on-demand REST API.
2. Pull a sample spend-details response and a sample invoice, and run both through the FOCUS Validator to baseline conformance.
3. Prototype the commitment-and-credit reconciliation that produces EffectiveCost and ContractedCost from the spend row.
4. Design the resource-join that lifts ResourceId, ResourceType, Tags, and data-center Region onto the spend row.
5. Open the RFI with `member-cert@finops.org`.

---

## Confidence Summary

- **Moderate:** The mapping rests on the retained on-demand REST API and OpenAPI schema. The schema is concrete (field names, types, enums are verified), but the public platform closed on March 31, 2026, and the current enterprise-contract billing surface is not publicly documented. Treat the analysis as provisional pending confirmation of the live billing surface.
- **High:** Feature levels were verified against the FOCUS v1.2 reference (bundled table stamped 2026-06-23; v1.2 spec page confirmed live). ServiceSubcategory and ChargeFrequency are Recommended, PricingQuantity and PricingUnit are Mandatory, ChargeClass is Mandatory-nullable.
- **High:** `projectId` is a genuine sub-account, and ListCost is a clean quantity times unit-price product for the flat-rate hourly and GiB-hour SKUs.
- **Moderate:** EffectiveCost and ContractedCost are a substantive reconciliation gap. This rests on the documented commitment (lower hourly rate) and credit-balance mechanics; confirm exactly where each is applied in the current billing pipeline.
- **Moderate:** The CommitmentDiscount and Region families are N/A only in the base spend-report grain and are applicable once resource and commitment joins are in place. Confirm the commitment record exposes quantity, unit, and status.
- **Low:** SkuPriceId and SkuPriceDetails. The API does not expose a stable price ID.

---

## Sources

- Cudo Compute API reference and billing endpoints: [docs.cudocompute.com](https://docs.cudocompute.com)
- Cudo Compute OpenAPI schema: [docs.cudocompute.com/openapi.json](https://docs.cudocompute.com/openapi.json)
- Cudo Compute (company): [cudocompute.com](https://www.cudocompute.com)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
