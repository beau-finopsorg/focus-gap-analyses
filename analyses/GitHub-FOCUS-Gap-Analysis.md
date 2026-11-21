# GitHub as a FOCUS Data Generator: Compliance Gap Analysis

*Analysis run: June 23, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

Prepared: June 23, 2026
Subject: GitHub's Enhanced Billing Platform usage report (usage reports and the billing usage REST API)
Baseline: FOCUS v1.2 (certification baseline). Build target: v1.4 (latest ratified).
Feature levels verified against the FOCUS v1.2 specification on 2026-06-23.

## Executive summary

GitHub is unusually well positioned to become a FOCUS data generator, and the reason is the part most providers get wrong: cost. GitHub's usage report already carries `gross_amount`, `discount_amount`, and `net_amount`, which means list, discount, and billed amounts are all present in the source. The hard, expensive column most providers lack (a true post-discount billed cost) is here on day one.

The work is therefore not "find missing cost data," it is "shape existing data into FOCUS form." GitHub's report uses native field names (`net_amount`, `gross_amount`, `unit_type`, `cost_center_name`), not FOCUS column IDs, and there is no FOCUS-named output today. So every column needs a transform layer, but the underlying data exists for all 21 Mandatory v1.2 columns. There are no missing-Mandatory data gaps. The substantive work is the FOCUS-shaping transform itself, a product-to-`ServiceCategory` mapping, and one pricing clarification (what `applied_cost_per_quantity` represents for negotiated accounts).

Of 57 v1.2 columns: 33 map directly or by trivial derivation, 7 are present but need shaping or clarification, 3 are missing Conditional (the SKU price family), 2 are missing Recommended (`InvoiceId`, `ServiceSubcategory`), and 12 are legitimately N/A for GitHub's SaaS model (region, availability zone, commitment discounts, capacity reservations).

Recommendation: treat this as a transform-and-certify effort, not a data-collection effort. Build the FOCUS-shaping transform over the usage report, settle the list-versus-contracted rate question, publish sample data, validate, and pursue the FinOps Certified FOCUS v1.2 Conformant designation while building toward 1.4.

## Part 1: The conformance gap

### 1.1 The data source

GitHub's Enhanced Billing Platform exposes usage two ways: a summarized usage report (available via the billing usage REST API and the web UI) and a detailed usage report (web UI only). Both share a common field set; the detailed report adds `username` and `workflow_path`.

Usage report fields: `date`, `product`, `sku`, `quantity`, `unit_type`, `applied_cost_per_quantity`, `gross_amount`, `discount_amount`, `net_amount`, `username` (detailed only), `organization`, `repository`, `workflow_path` (detailed only), `cost_center_name`. A separate premium-requests report adds `model`, `exceeds_quota`, and `total_monthly_quota`.

Characteristics that matter for FOCUS:

- Daily granularity: usage is logged per `date` (UTC).
- Full cost trio: `gross_amount` (pre-discount), `discount_amount` (included-usage and other reductions), and `net_amount` (billed, where `gross_amount - discount_amount = net_amount`).
- Allocation dimensions: `organization`, `repository`, `cost_center_name`, and (detailed only) `username` and `workflow_path`.
- SKU-level detail: `product`, `sku`, `unit_type`, `quantity`, `applied_cost_per_quantity`.
- Multi-product: Actions, Packages, Codespaces, Copilot, Advanced Security, Git LFS, Models, and licensed seats.

Two scope notes to confirm with GitHub: the detailed report (with `username` and `workflow_path`) is web-only and not available through the REST `/usage` endpoint, so a fully resource-attributed FOCUS feed may depend on the web CSV rather than the API; and billing currency is assumed USD, though accounts billed through an Azure subscription may settle in another currency.

### 1.2 How conformance is judged

FOCUS conformance is column-driven. Each column carries a feature level: Mandatory (must exist and be populated where applicable), Conditional (must exist; populated when the provider's model triggers the condition, otherwise null), or Recommended. A conformant dataset presents the full column set under FOCUS column IDs, populates every Mandatory column, satisfies Conditional columns where applicable, and uses the correct types and allowed values. These rules live in the FOCUS Requirements Model, which the FOCUS Validator checks against. Provider-specific columns are allowed when prefixed `x_`.

### 1.3 Column-by-column status (all 57 FOCUS v1.2 columns)

Because GitHub's report is not yet in FOCUS shape, "Present" here means the data exists and maps to the column (a rename or trivial derivation), not that a conformant column ships today.

Status legend: Present (data maps directly or by trivial derivation); Present, deviation to fix (data present but needs shaping, an enum mapping, or a semantic clarification); Missing: Conditional; Missing: Recommended; N/A: null valid (does not apply to GitHub's model).

| FOCUS Column | Level (1.2) | GitHub source | Status |
| --- | --- | --- | --- |
| BilledCost | Mandatory | `net_amount` | Present |
| EffectiveCost | Mandatory | `net_amount` (no amortization) | Present |
| ListCost | Mandatory | `gross_amount` | Deviation |
| ContractedCost | Mandatory | `gross_amount` at applied rate | Deviation |
| BillingAccountId | Mandatory | account / enterprise (context) | Present |
| BillingAccountName | Mandatory | account / enterprise name | Present |
| BillingCurrency | Mandatory | constant USD (verify Azure-billed) | Present |
| BillingPeriodStart | Mandatory | derive from monthly cycle | Present |
| BillingPeriodEnd | Mandatory | derive from monthly cycle | Present |
| ChargePeriodStart | Mandatory | `date` | Present |
| ChargePeriodEnd | Mandatory | `date` + 1 day | Present |
| ChargeDescription | Mandatory | `product` + `sku` | Present |
| ChargeCategory | Mandatory | derive (Usage / Purchase) | Deviation |
| ChargeClass | Mandatory (nullable) | null except corrections | Present |
| InvoiceIssuerName | Mandatory | constant "GitHub, Inc." | Present |
| ProviderName | Mandatory (dep. 1.3) | constant "GitHub" | Present |
| PublisherName | Mandatory (dep. 1.3) | constant "GitHub" | Present |
| ServiceName | Mandatory | `product` | Present |
| ServiceCategory | Mandatory | map `product` to FOCUS enum | Deviation |
| PricingQuantity | Mandatory | `quantity` (flat-rate SKUs) | Present |
| PricingUnit | Mandatory | `unit_type` | Present |
| ConsumedQuantity | Conditional | `quantity` | Present |
| ConsumedUnit | Conditional | `unit_type` | Present |
| ListUnitPrice | Conditional | `applied_cost_per_quantity` | Deviation |
| ContractedUnitPrice | Conditional | `applied_cost_per_quantity` | Deviation |
| PricingCategory | Conditional | constant "Standard" | Present |
| BillingAccountType | Conditional (1.2) | derive | Present |
| SubAccountId | Conditional | `organization` | Present |
| SubAccountName | Conditional | `organization` | Present |
| SubAccountType | Conditional (1.2) | derive | Present |
| ResourceId | Conditional | `repository` (or `username`) | Present |
| ResourceName | Conditional | `repository` (or `username`) | Present |
| ResourceType | Conditional | derive (Repository / User / Org) | Present |
| SkuId | Conditional | `sku` | Present |
| Tags | Conditional | shape `cost_center_name` as key-value | Deviation |
| PricingCurrency | Conditional (1.2) | = BillingCurrency | Present |
| PricingCurrencyListUnitPrice | Conditional (1.2) | = ListUnitPrice | Present |
| PricingCurrencyContractedUnitPrice | Conditional (1.2) | = ContractedUnitPrice | Present |
| PricingCurrencyEffectiveCost | Conditional (1.2) | = EffectiveCost | Present |
| SkuMeter | Conditional (1.1+) | not exposed | Missing: Conditional |
| SkuPriceId | Conditional | not exposed | Missing: Conditional |
| SkuPriceDetails | Conditional (1.1+) | not exposed | Missing: Conditional |
| InvoiceId | Recommended | not in usage report | Missing: Recommended |
| ServiceSubcategory | Recommended | map `product` / `sku` | Missing: Recommended |
| AvailabilityZone | Recommended | global SaaS, no zone | N/A |
| RegionId | Conditional | global SaaS, no region | N/A |
| RegionName | Conditional | global SaaS, no region | N/A |
| CommitmentDiscountId | Conditional | no commitment discounts sold | N/A |
| CommitmentDiscountName | Conditional | N/A | N/A |
| CommitmentDiscountType | Conditional | N/A | N/A |
| CommitmentDiscountCategory | Conditional | N/A | N/A |
| CommitmentDiscountStatus | Conditional | N/A | N/A |
| CommitmentDiscountQuantity | Conditional (1.1+) | N/A | N/A |
| CommitmentDiscountUnit | Conditional (1.1+) | N/A | N/A |
| CapacityReservationId | Conditional (1.1+) | N/A | N/A |
| CapacityReservationStatus | Conditional (1.1+) | N/A | N/A |

Tally: 33 Present, 7 Deviation, 3 Missing Conditional, 2 Missing Recommended, 12 N/A. All 21 Mandatory columns have a source: 17 map directly or by trivial derivation, and 4 need shaping or clarification (`ChargeCategory`, `ServiceCategory`, `ListCost`, `ContractedCost`). There are zero missing-Mandatory data gaps.

### 1.4 What's solved, and what remains

Solved, and notable: the cost trio. `gross_amount`, `discount_amount`, and `net_amount` give `ListCost`, the discount, and `BilledCost`. Because GitHub has no prepaid commitments to amortize, `EffectiveCost` equals `net_amount`, so it is solved too. The list-cost trap (where a list-only feed hides the billed cost behind invoice-time discounts) does not bite here, because GitHub already exposes the discount and the net.

Solved: daily granularity, SKU detail, and rich allocation (organization, repository, cost center, and user in the detailed report).

The remaining work is shaping, not collection:

- The FOCUS-shaping transform. GitHub's report is not in FOCUS form. Producing a conformant dataset means emitting FOCUS column IDs, one charge record per `date` x `sku` x `organization` x `repository` x `cost_center_name`, deriving the period and constant columns, and serializing tags as key-value. This is the core engineering task.
- Service categorization. There is no native `ServiceCategory` field. GitHub must map each `product` (Actions, Packages, Codespaces, Copilot, Advanced Security, Git LFS, Models, licenses) to a FOCUS `ServiceCategory` allowed value, and ideally a `ServiceSubcategory`.
- The list-versus-contracted clarification (see 1.5).

### 1.5 Deviations and clarifications to fix

- ListCost and ContractedCost (and their unit prices). `gross_amount` is computed at `applied_cost_per_quantity`. For accounts on public pricing, that rate is the public list price, so `gross_amount` is `ListCost`. For accounts on negotiated or Enterprise Agreement pricing, the applied rate is the contracted rate, so `gross_amount` is `ContractedCost` and the true public `ListCost` is not in the data. GitHub should confirm what `applied_cost_per_quantity` represents per account type and populate `ListCost` versus `ContractedCost` accordingly, rather than mapping both to `gross_amount` unconditionally.
- ChargeCategory. Must be a FOCUS enum value (Usage, Purchase, Tax, Credit, Adjustment). Metered products map to Usage; licensed seats map to Purchase. Derive from `product` / `sku` and validate against the enum.
- ServiceCategory. Must be a FOCUS enum value. Build and maintain a `product` to category map.
- Tags. FOCUS expects key-value pairs. `cost_center_name` is the natural allocation tag and should be serialized as a key-value (for example `{"cost_center": "..."}`), or carried as `SubAccount` if GitHub prefers to model cost centers as the sub-account. Decide one representation and apply it consistently.
- PricingQuantity for tiered SKUs. `PricingQuantity` equals `quantity` for flat per-unit SKUs (the common GitHub case). For any tiered or multiplier-based SKU (for example Actions minutes with runner multipliers), compute `PricingQuantity` against the rate basis rather than copying `quantity`.

## Part 2: The path forward

### 2.1 Which FOCUS version to target

Live versions: 1.1 (Nov 7, 2024), 1.2 (May 29, 2025, the current certification baseline), 1.3 (Dec 5, 2025), and 1.4 (June 4, 2026, the latest, adding Invoice Detail and billing-period datasets). The FOCUS Validator supports v1.3 conformance today; v1.4 support is expected later in Q3 2026.

Build the transform to the 1.4 column set (it removes `ProviderName` and `PublisherName`, which GitHub would otherwise carry as constants), and certify at v1.2, which is the offered badge. Re-certify upward as the program expands.

### 2.2 What certification requires

Certification for data generators runs through the FinOps Foundation. Contact `member-cert@finops.org` for the RFI. Deliverables: a structurally conformant dataset under FOCUS column IDs, public sample data that passes the FOCUS Validator, a documented native-to-FOCUS mapping, and a Conformance Gap Report (this document is its seed). Membership is required for certification, though contributing to the spec is open and free.

Tooling: the FOCUS Validator (run a sample of the transform output through it to get an objective pass or fail), the FOCUS Converter (its AWS, Azure, GCP, and OCI provider patterns are a useful reference, and a GitHub profile could be contributed back), and the FOCUS Requirements Model (the authoritative machine-readable requirements).

### 2.3 Phased roadmap

Phase 0, validate and scope. Build a small sample of the FOCUS-shaping transform and run it through the FOCUS Validator. Confirm the source of record (summarized REST API versus detailed web CSV), the billing currency for Azure-billed accounts, and the 1.4-build / 1.2-certify decision. Open the RFI.

Phase 1, build the transform and settle pricing. Emit FOCUS column IDs, one charge record per date and SKU and allocation key. Map the cost trio (`net_amount` to `BilledCost` and `EffectiveCost`, `gross_amount` to `ListCost` or `ContractedCost` per the clarification), derive period and constant columns, derive `ChargeCategory` and `ChargeFrequency`, and populate `PricingQuantity` and `PricingUnit`. Stand up the `product` to `ServiceCategory` mapping.

Phase 2, fix deviations. Serialize Tags from `cost_center_name` as key-value, validate `ChargeCategory` and `ServiceCategory` against the enums, and confirm the list-versus-contracted handling per account type.

Phase 3, round out conditionals. Add the SKU price family (`SkuPriceId`, `SkuMeter`, `SkuPriceDetails`) if the data exists, `ResourceType`, the pricing-currency columns, and the Recommended `ServiceSubcategory` and `InvoiceId`.

Phase 4, mature to 1.4 and certify. Adopt the 1.4 column set, drop `ProviderName` and `PublisherName`, decide how to represent Marketplace apps and Sponsors (third-party publishers) conformantly, validate, and certify.

### 2.4 FOCUS Use Cases GitHub customers unlock

Achievable as soon as the transform ships (daily, allocation-rich, full cost trio): allocate and charge back by cost center and repository, report cost by service (product) and by organization, identify anomalous daily spending, budget and forecast on billed cost, and reconcile against the invoice (since `net_amount` is the billed amount). Calculate unit economics on effective cost.

Out of scope for GitHub's model: commitment-discount use cases, capacity-reservation use cases, availability-zone analysis, and multi-currency analysis (unless Azure-billed accounts introduce a second currency).

## Part 3: Immediate next steps

1. Confirm the source of record: whether the conformant feed is built from the summarized billing usage REST API or the detailed web CSV (the latter carries `username` and `workflow_path` for fuller resource attribution).
2. Settle the pricing question: what `applied_cost_per_quantity` represents for public versus negotiated accounts, so `ListCost` and `ContractedCost` are populated correctly.
3. Decide the cost-center representation: FOCUS `Tags` (key-value) versus `SubAccount`.
4. Build a sample FOCUS-shaping transform and run it through the FOCUS Validator; iterate to a clean pass.
5. Draft the native-to-FOCUS mapping and finalize this Conformance Gap Report; open the RFI with `member-cert@finops.org`; publish sample data; request listing as a FOCUS-supporting provider.

## Confidence summary

- High: GitHub's usage report carries `gross_amount`, `discount_amount`, and `net_amount`, so `ListCost`, `BilledCost`, and `EffectiveCost` are all available; there are no missing-Mandatory data gaps.
- High: feature levels were verified column-by-column against the FOCUS v1.2 spec on 2026-06-23 (21 Mandatory, 32 Conditional, 4 Recommended).
- High: GitHub's report is not yet in FOCUS shape, so a transform layer is required for every column.
- Moderate: billing currency is assumed USD; confirm whether Azure-billed accounts settle in another currency, which would activate the pricing-currency columns in earnest.
- Moderate: whether `applied_cost_per_quantity` is public list or negotiated rate per account type; this determines correct `ListCost` versus `ContractedCost` population.
- Moderate: SKU price family (`SkuPriceId`, `SkuMeter`, `SkuPriceDetails`) availability; treated as missing Conditional pending confirmation.
- Moderate: representation of Marketplace apps and Sponsors (third-party publishers), which may warrant separate handling for `PublisherName`.

## Sources

- GitHub Docs, Billing reports reference (usage report fields): https://docs.github.com/en/billing/reference/billing-reports
- GitHub Docs, Billing usage REST API: https://docs.github.com/en/rest/billing/usage
- GitHub Docs, Product and SKU names: https://docs.github.com/en/billing/reference/product-and-sku-names
- GitHub Docs, Cost centers: https://docs.github.com/en/billing/concepts/cost-centers
- GitHub Changelog, API access to billing usage reports now generally available (2026-06-04): https://github.blog/changelog/2026-06-04-api-access-to-billing-usage-reports-now-generally-available/
- FOCUS Specification v1.2: https://focus.finops.org/focus-specification/v1-2/
- FinOps Certified FOCUS v1.2 Conformant: https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
