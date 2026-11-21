# Nebius AI Cloud and FOCUS: Conformance Gap Analysis

*Analysis run: June 30, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Provider and product in scope:** Nebius B.V., Nebius AI Cloud (GPU/AI neocloud: NVIDIA H100, H200, B200/B300 compute, Object Storage, managed Kubernetes, managed databases).

**Source analyzed:** Nebius AI Cloud billing export documentation (hourly CSV billing export, "Exporting usage data as CSV"), PAYG and commitment-discounts billing-model docs, the Nebius blog post "FinOps efficiency for AI workloads with FOCUS-compliant billing data" (January 15, 2026), and the public pricing pages.

**FOCUS baseline:** v1.2 (current certification baseline, ratified 2025-05-29). **Build target:** v1.4 (latest, ratified 2026-06-04).

**Prepared:** 2026-06-30.

---

## Executive summary

Nebius AI Cloud already emits a native FOCUS billing export. Nebius ships an hourly CSV that it states follows the FOCUS 1.2 schema, delivered automatically to an Object Storage bucket, with one Nebius-specific column (`x_ContainerId`) correctly prefixed per the FOCUS custom-column rule. This is not a from-scratch mapping exercise: it is a conformance review of a dataset the provider already shaped to FOCUS.

The strongest finding is that the columns that most often constitute substantive gaps for neoclouds are present here. The export contains used and unused consumption, adjustments, taxes, and the effective price of resources after discounts, with hourly records that drill down to individual virtual machines. Commitment discounts surface with `CommitmentDiscountStatus = Unused` for prepaid-but-unconsumed quantity, which means the commitment-discount family is populated rather than null.

The work that remains is verification and version maturation, not data creation. Because the published documentation describes the export's coverage but does not enumerate every populated column or show a sample row, several Conditional and Recommended columns cannot be confirmed present from the documentation alone and are marked as such pending a sample export and a FOCUS Validator run. The single concrete deviation flagged here is the schema version: the export targets v1.2, so reaching the v1.4 build target requires dropping the removed `ProviderName` and `PublisherName` columns and adding the v1.3/v1.4 additions.

**Recommendation:** Treat Nebius as a near-conformant FOCUS 1.2 data generator. Run a real sample export through the FOCUS Validator to convert documentation-level confidence into column-level evidence, then sequence a v1.4 uplift.

---

## Part 1: The conformance gap

### 1.1 The data source

Nebius AI Cloud exposes billing data three ways:

- **Web console views:** Billing → Usage (PAYG) and Billing → Discounts (commitment discounts), with region, project, service, and product filters and hourly charts.
- **Invoices:** a monthly invoice for the previous month's PAYG usage, plus prepaid commitment orders (an order maps to an addendum and carries the addendum ID).
- **The FOCUS export:** a periodic CSV delivered once per hour to an Object Storage bucket, configured under Billing → Export, with the same workflow available via API. One CSV file is produced per month.

Key characteristics relevant to FOCUS:

- **Granularity:** hourly charge records, drillable to a specific virtual machine. This satisfies the sub-monthly granularity FOCUS expects and unlocks resource-level allocation.
- **Cost completeness:** the export covers used and unused consumption, adjustments, and taxes, and exposes the effective price after discounts. Adjustments appear as separate line items. This is the property that prevents the common neocloud list-cost trap.
- **Commitments:** the commitment-discount model is real (prepaid orders for compute, disks, and shared filesystems). Unused prepaid commitment surfaces as `CommitmentDiscountStatus = Unused` with remaining prepaid quantity or cost.
- **Attribution:** a resource hierarchy of containers (projects) is exposed through the custom column `x_ContainerId`, and the export can attribute to specific VMs.
- **Format:** CSV following the FOCUS Column Library, FOCUS 1.2 schema, with one extension column.

Key limitations for this analysis: the documentation describes the export's scope and a handful of behaviors (commitment status, adjustments, the container column) but does not publish the full populated column list, a data dictionary, or a sample row. Column-level confirmation therefore depends on a sample export.

### 1.2 How conformance is judged

FOCUS assigns every column a feature level: Mandatory, Conditional, Recommended, or Optional. A conformant dataset must include and populate all Mandatory columns, must populate Conditional columns when the provider's business model triggers the condition, should populate Recommended columns, and may include Optional ones. Conformance is judged column by column against the spec's Requirements Model, not by an overall impression.

Feature levels in this report were taken from the verified reference table and cross-checked against the live FOCUS Specification v1.2 via the FOCUS column service on 2026-06-30. The v1.2 column set (57 columns) and the commonly-misremembered levels (`ServiceSubcategory` Recommended, `ChargeClass` Mandatory-nullable, `PricingQuantity`/`PricingUnit` Mandatory, `ChargeFrequency` and `InvoiceId` Recommended) were confirmed against the live spec; the bundled cache was current.

### 1.3 Column-by-column status

Feature levels verified against the FOCUS Specification v1.2. Status reflects what the published documentation supports; columns the docs neither confirm nor deny on a FOCUS-shaped export are marked "Present (per FOCUS 1.2 schema, confirm in sample)" where the export's stated FOCUS-1.2 compliance implies the column is emitted, and as Conditional/Recommended gaps only where the provider model or documentation gives a reason.

Status legend: Present; Present, deviation to fix; Missing: Mandatory; Missing: Recommended; Missing: Conditional; N/A: null valid.

| § | FOCUS Column | Level | In the source? | Status |
|---|---|---|---|---|
| 3.1 | AvailabilityZone | R | Regions exposed; zones not documented | N/A: null valid (regions, no documented zones) |
| 3.2 | BilledCost | M | Yes (export covers invoice-affecting consumption, taxes, adjustments) | Present |
| 3.3 | BillingAccountId | M | Yes (tenant/account in FOCUS export) | Present |
| 3.4 | BillingAccountName | M | Yes | Present |
| 3.5 | BillingAccountType | C | FOCUS 1.2 schema | Present (confirm in sample) |
| 3.6 | BillingCurrency | M | Yes (invoiced currency) | Present |
| 3.7 | BillingPeriodEnd | M | Yes (monthly file) | Present |
| 3.8 | BillingPeriodStart | M | Yes (monthly file) | Present |
| 3.9 | CapacityReservationId | C | Not documented; commitments modeled as discounts, not reservations | N/A: null valid (commitment model, not capacity reservations) |
| 3.10 | CapacityReservationStatus | C | Not documented | N/A: null valid |
| 3.11 | ChargeCategory | M | Yes (usage, adjustments, taxes as line items) | Present |
| 3.12 | ChargeClass | M | FOCUS 1.2 schema; adjustments are separate line items | Present (confirm correction handling in sample) |
| 3.13 | ChargeDescription | M | FOCUS 1.2 schema | Present (confirm in sample) |
| 3.14 | ChargeFrequency | R | FOCUS 1.2 schema | Present (confirm in sample) |
| 3.15 | ChargePeriodEnd | M | Yes (hourly records) | Present |
| 3.16 | ChargePeriodStart | M | Yes (hourly records) | Present |
| 3.17 | CommitmentDiscountCategory | C | Commitment discounts exist | Present (confirm in sample) |
| 3.18 | CommitmentDiscountId | C | Orders carry addendum IDs | Present (confirm in sample) |
| 3.19 | CommitmentDiscountName | C | Commitment discounts exist | Present (confirm in sample) |
| 3.20 | CommitmentDiscountQuantity | C | Remaining prepaid quantity exposed | Present (confirm in sample) |
| 3.21 | CommitmentDiscountStatus | C | Yes (Used / Unused documented) | Present |
| 3.22 | CommitmentDiscountType | C | Commitment discounts exist | Present (confirm in sample) |
| 3.23 | CommitmentDiscountUnit | C | Remaining prepaid quantity/cost exposed | Present (confirm in sample) |
| 3.24 | ConsumedQuantity | C | Yes (usage-based billing) | Present |
| 3.25 | ConsumedUnit | C | Yes | Present |
| 3.26 | ContractedCost | M | Yes (effective price after discounts in export) | Present |
| 3.27 | ContractedUnitPrice | C | Effective price per VM-hour exposed | Present (confirm in sample) |
| 3.28 | EffectiveCost | M | Yes (effective price after discounts, amortization of unused commitment) | Present |
| 3.29 | InvoiceId | R | Monthly invoices issued; FOCUS 1.2 schema | Present (confirm in sample) |
| 3.30 | InvoiceIssuerName | M | Yes (Nebius B.V.) | Present |
| 3.31 | ListCost | M | Yes (List prices tab; export tracks list vs effective) | Present |
| 3.32 | ListUnitPrice | C | List prices exposed | Present (confirm in sample) |
| 3.33 | PricingCategory | C | PAYG vs commitment distinction exists | Present (confirm in sample) |
| 3.34 | PricingCurrency | C | FOCUS 1.2 schema | Present (confirm in sample) |
| 3.35 | PricingCurrencyContractedUnitPrice | C | FOCUS 1.2 schema | Present (confirm in sample) |
| 3.36 | PricingCurrencyEffectiveCost | C | FOCUS 1.2 schema | Present (confirm in sample) |
| 3.37 | PricingCurrencyListUnitPrice | C | FOCUS 1.2 schema | Present (confirm in sample) |
| 3.38 | PricingQuantity | M | Yes (usage measured hourly) | Present |
| 3.39 | PricingUnit | M | Yes | Present |
| 3.40 | ProviderName | M (deprecated v1.3, removed v1.4) | Yes (FOCUS 1.2) | Present, deviation to fix (remove for v1.4 target) |
| 3.41 | PublisherName | M (deprecated v1.3, removed v1.4) | Yes (FOCUS 1.2) | Present, deviation to fix (remove for v1.4 target) |
| 3.42 | RegionId | C | Region filter exists | Present (confirm in sample) |
| 3.43 | RegionName | C | Region filter exists | Present (confirm in sample) |
| 3.44 | ResourceId | C | Yes (drill to specific VM) | Present |
| 3.45 | ResourceName | C | Resource-level attribution | Present (confirm in sample) |
| 3.46 | ResourceType | C | Resource-level attribution | Present (confirm in sample) |
| 3.47 | ServiceCategory | M | Yes (Compute, Storage, etc.) | Present (confirm valid enum members in sample) |
| 3.48 | ServiceName | M | Yes (service-level usage) | Present |
| 3.49 | ServiceSubcategory | R | FOCUS 1.2 schema | Present (confirm in sample) |
| 3.50 | SkuId | C | SKU-level pricing exists | Present (confirm in sample) |
| 3.51 | SkuMeter | C | FOCUS 1.2 schema | Present (confirm in sample) |
| 3.52 | SkuPriceDetails | C | FOCUS 1.2 schema | Present (confirm in sample) |
| 3.53 | SkuPriceId | C | SKU-level pricing exists | Present (confirm in sample) |
| 3.54 | SubAccountId | C | Yes (project/container via x_ContainerId; map to SubAccountId) | Present, deviation to fix (confirm container maps to SubAccountId, not only x_ColumnId) |
| 3.55 | SubAccountName | C | Container/project names exposed | Present (confirm in sample) |
| 3.56 | SubAccountType | C | FOCUS 1.2 schema | Present (confirm in sample) |
| 3.57 | Tags | C | Not documented for the export | Missing: Conditional (confirm whether resource labels are emitted as key-value Tags) |

### 1.4 What's solved, and what remains

**Solved (the hard parts):**

- **The cost columns.** `BilledCost`, `EffectiveCost`, `ListCost`, and `ContractedCost` are the usual substantive gap for neoclouds because daily or hourly feeds often carry list cost only and push discounts and credits to invoice time. Nebius avoids this: the export covers used and unused consumption, adjustments, and taxes, and exposes the effective price after discounts, including amortization of unused prepaid commitment. The list-cost trap does not apply here.
- **Granularity and resource identity.** Hourly records drillable to a specific VM give the granularity and `ResourceId` that allocation and anomaly use cases require.
- **Commitment discounts.** The commitment-discount family is populated, not null, with explicit `CommitmentDiscountStatus = Unused` for prepaid-but-unconsumed amounts. For a neocloud, this is a meaningful maturity signal.
- **FOCUS shaping.** The provider emits FOCUS column IDs and follows the custom-column rule (`x_ContainerId`), so there is no native-to-FOCUS transform for the consumer to write.

**Remaining (verification and maturation, not data creation):**

- **Documentation-to-evidence gap.** The docs assert FOCUS 1.2 compliance and describe behavior, but do not publish the full column list or a sample. Roughly two-thirds of the v1.2 columns are marked "Present (confirm in sample)" on that basis. A Validator run converts this to evidence.
- **Tags.** The export's handling of resource labels as FOCUS key-value `Tags` is not documented. If Nebius resources carry labels, they should map to `Tags`; if they do not, the column is legitimately null.
- **Version target.** The export is v1.2. The v1.4 build target removes `ProviderName` and `PublisherName` and adds the v1.3/v1.4 columns.

Of the 21 Mandatory columns, the documentation supports all 21 as present (two of them, `ProviderName` and `PublisherName`, are present-but-removed at the v1.4 target). There are no substantive Mandatory data gaps: the export already carries the cost, quantity, time, and identity data that Mandatory columns require. The qualifier is evidentiary, not structural.

### 1.5 Deviations to fix

- **Schema version (v1.2 to v1.4):** the only concrete, documented deviation. `ProviderName` and `PublisherName` are present in the v1.2 export and are removed at v1.4; the v1.3 split-cost-allocation columns and the v1.4 Invoice Detail and billing-period dataset columns are not yet present. This is a planned uplift, not a defect in the v1.2 export.
- **Container-to-SubAccount mapping:** `x_ContainerId` correctly carries the project/container hierarchy as a custom column. Confirm that the same hierarchy also populates the standard `SubAccountId`/`SubAccountName` columns so allocation works without relying on the extension column. If containers already populate `SubAccountId`, this is resolved and `x_ContainerId` is a useful supplement.
- **Enum and key-value checks:** confirm `ServiceCategory` emits valid FOCUS members, `ChargeCategory` uses the allowed set (Usage, Purchase, Tax, Credit, Adjustment), and any `Tags` are key-value pairs rather than bare strings. These are routine validation checks, expected to pass given the provider already follows the Column Library.

What is already done right: FOCUS column IDs, the `x_` custom-column convention, hourly resource-level records, real `EffectiveCost` after discounts, and a populated commitment-discount family.

---

## Part 2: The path forward

### 2.1 Which FOCUS version to target

Baseline the certification version (v1.2), which is what the export already targets and the version the FinOps Certified FOCUS conformance badge has historically been anchored to. Design the next iteration toward v1.4 (latest). The v1.4 uplift is small in column terms because the v1.2 foundation is already in place: remove `ProviderName`/`PublisherName`, add the v1.3 split-cost-allocation columns and v1.4 Invoice Detail and billing-period datasets, and re-verify the new columns' levels against the live spec at build time.

### 2.2 What certification requires

FOCUS conformance for data generators runs through the FinOps Foundation. The program has been the "FinOps Certified FOCUS v1.2 Conformant" designation (confirm the current badge version against the program page before finalizing). Membership is required for certification, though contributing to the spec is open and free; contact `member-cert@finops.org` for the RFI. Deliverables are a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report (this analysis is its seed).

Open-source tooling: the **FOCUS Validator** (checks data against the Requirements Model), the **FOCUS Converter** (provider-native to FOCUS), and the **FOCUS Requirements Model** (machine-readable MUST/SHOULD/MAY rules). Because Nebius already emits FOCUS, the Validator is the most relevant tool: it turns the documentation-level confidence in this report into column-level pass/fail evidence.

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
