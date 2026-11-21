# Google Cloud and FOCUS: Conformance Gap and Adoption Roadmap

*Analysis run: July 1, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Provider and product in scope:** Google Cloud (Cloud Billing), FOCUS usage cost export to BigQuery.
**Prepared:** 2026-07-01.
**Source analyzed:** Google Cloud "Structure of FOCUS data export" and "Set up FOCUS Cloud Billing data export to BigQuery" documentation, the FOCUS get-started page for Google Cloud, and the FinOps Foundation FOCUS column library.
**FOCUS baseline for this analysis:** v1.2 (the current certification baseline).
**Version Google ships:** a dedicated FOCUS export (Preview) that Google documents against v1.0, v1.1, and v1.2 gaps, plus a FOCUS v1.0 BigQuery view and Looker template.

---

## Executive summary

Google Cloud is an official FOCUS data generator and one of the specification's founding Steering Committee members. It ships a substantially complete FOCUS export today, so the question is not whether an export exists but how complete it is against the v1.2 baseline. Google delivers a dedicated, Google-managed FOCUS usage cost export to BigQuery (currently in Preview) alongside an established FOCUS v1.0 BigQuery view and Looker template. The dedicated export is normalized to FOCUS and comes with Google's own published conformance-gap register, which is unusually transparent.

The strongest finding: the full cost family is genuinely present and correctly derived. BilledCost, EffectiveCost, ContractedCost, and ListCost are all populated from real Google billing fields (cost, credits, and cost_at_list), so this is not a list-cost-only dataset. Daily charge periods, resource identity, region, sub-account (project) attribution, SKU identity, and both pricing and billing currency columns are all present. The gaps are concentrated and known: FOCUS Tags is delivered through Google-specific x_Tags and x_Labels columns rather than the standard column, commitment-discount (CUD) information lives in x_Credits rather than the CommitmentDiscount column family, and a handful of Mandatory descriptive columns (ServiceCategory, InvoiceIssuerName, BillingAccountName) are not yet populated.

- Total FOCUS v1.2 columns: 57.
- Present and conformant: 33.
- Present with a deviation to fix: 2 (ChargeCategory and PricingCategory enum coverage).
- Missing Mandatory columns: 3 (BillingAccountName, InvoiceIssuerName, ServiceCategory), all substantive-but-tractable rather than deep data gaps.

**Recommendation:** Treat this as a Conformant-track export that needs targeted finishing, not a rebuild. Close the three Mandatory descriptive columns, promote Tags and commitment-discount data from the x_ columns into the standard FOCUS columns, and complete the ChargeCategory and PricingCategory enum coverage. Run the resulting dataset through the FOCUS Validator against v1.2 to confirm before pursuing formal conformance.

**Readiness (data source reviewed, not a formal certification result):**

- Cost: Strong.
- Granularity: Strong.
- Allocation: Strong.
- Coverage: Partial.
- FOCUS shape: Partial.
- Overall band: **Aligned.**

---

## Part 1: The conformance gap

Google Cloud already publishes a FOCUS export and its own gap register. This section maps that export against the full FOCUS v1.2 column set and separates the concentrated, tractable gaps from the substantive ones.

### 1.1 The data source

Google Cloud exposes FOCUS data two ways:

- A dedicated FOCUS usage cost export to BigQuery (Preview): a Google-managed, immutable linked dataset (`gcp_billing_immutable_<account>_<location>`) with a FOCUS table (`gcp_billing_export_focus_<account>`). Google writes the data; the customer is not charged for storage, only for queries. Data loads run on a rolling basis with a multi-region backfill for the current and previous month, and a 2-year time-to-live.
- A FOCUS v1.0 BigQuery view and Looker template, layered on the existing Detailed Billing Export and Price Export. This is the longer-standing path referenced on the FOCUS get-started page.

Key characteristics:

- Granularity: daily. ChargePeriodStart and ChargePeriodEnd bound single days; BillingPeriodStart and BillingPeriodEnd map to the invoice month.
- Formats: BigQuery-native types. Timestamps are ISO 8601, numeric costs are NUMERIC, and tag/label structures are REPEATED RECORD (key-value), which is the right shape for FOCUS key-value data.
- Cost derivation: BilledCost and EffectiveCost derive from cost plus credits.amount; ContractedCost maps to cost; ListCost maps to cost_at_list. When no negotiated discount applies, ContractedCost defaults to ListCost.
- Key limitations, per Google's own register: FOCUS Tags, the CommitmentDiscount column family, ServiceCategory, InvoiceIssuerName, BillingAccountName, ResourceType, SubAccountType, InvoiceId, ChargeFrequency, ServiceSubcategory, SkuMeter, SkuPriceDetails, and the capacity-reservation columns are not populated in the standard FOCUS columns. Some of that information is available in the Google-specific x_ columns.

### 1.2 How conformance is judged

FOCUS assigns every column a feature level: Mandatory, Conditional, Recommended, or Optional. A conformant dataset must include and populate every Mandatory column, must populate Conditional columns when the provider's business model triggers the condition, and is encouraged to populate Recommended columns. Conformance is judged column by column against the Requirements Model, so the analysis depends on getting each level right.

Feature levels in this report were verified against the FOCUS v1.2 specification and the FOCUS column library, not asserted from memory. Google's export documentation labels columns as supported or not but does not annotate feature levels, so the level column below comes from the specification.

### 1.3 Column-by-column status

Legend: Present (emitted and aligned); Present, deviation to fix (emitted, wrong format or invalid enum value); Missing: Mandatory (required and absent, blocks conformance); Missing: Recommended (encouraged, absent, does not block); Missing: Conditional (required when the model triggers it, absent and the condition applies); N/A: null valid (Conditional or Recommended column that does not apply to the model and may be null).

Feature levels verified against the FOCUS Specification v1.2.

| FOCUS Column | Level | In the source? | Status |
|---|---|---|---|
| AvailabilityZone | Recommended | Yes (zone data) | Present |
| BilledCost | Mandatory | Yes (cost + credits.amount) | Present |
| BillingAccountId | Mandatory | Yes | Present |
| BillingAccountName | Mandatory | No (in gap register) | Missing: Mandatory |
| BillingAccountType | Conditional | Yes (Google-unique mapping) | Present |
| BillingCurrency | Mandatory | Yes | Present |
| BillingPeriodEnd | Mandatory | Yes (invoice month) | Present |
| BillingPeriodStart | Mandatory | Yes (invoice month) | Present |
| CapacityReservationId | Conditional | No | Missing: Conditional |
| CapacityReservationStatus | Conditional | No | Missing: Conditional |
| ChargeCategory | Mandatory | Yes (Usage, Tax, Adjustment) | Present, deviation to fix |
| ChargeClass | Mandatory | Yes (correction flag) | Present |
| ChargeDescription | Mandatory | Yes | Present |
| ChargeFrequency | Recommended | No (in gap register) | Missing: Recommended |
| ChargePeriodEnd | Mandatory | Yes (daily) | Present |
| ChargePeriodStart | Mandatory | Yes (daily) | Present |
| CommitmentDiscountCategory | Conditional | No (in x_Credits) | Missing: Conditional |
| CommitmentDiscountId | Conditional | No (in x_Credits) | Missing: Conditional |
| CommitmentDiscountName | Conditional | No (in x_Credits) | Missing: Conditional |
| CommitmentDiscountQuantity | Conditional | No | Missing: Conditional |
| CommitmentDiscountStatus | Conditional | No (in x_Credits) | Missing: Conditional |
| CommitmentDiscountType | Conditional | No (in x_Credits) | Missing: Conditional |
| CommitmentDiscountUnit | Conditional | No | Missing: Conditional |
| ConsumedQuantity | Conditional | Yes | Present |
| ConsumedUnit | Conditional | Yes | Present |
| ContractedCost | Mandatory | Yes (cost) | Present |
| ContractedUnitPrice | Conditional | Yes (price.effective_price) | Present |
| EffectiveCost | Mandatory | Yes (cost + credits.amount) | Present |
| InvoiceId | Recommended | No (in gap register) | Missing: Recommended |
| InvoiceIssuerName | Mandatory | No (in gap register) | Missing: Mandatory |
| ListCost | Mandatory | Yes (cost_at_list) | Present |
| ListUnitPrice | Conditional | Yes (price.list_price) | Present |
| PricingCategory | Conditional | Yes (Committed, Standard) | Present, deviation to fix |
| PricingCurrency | Conditional | Yes | Present |
| PricingCurrencyContractedUnitPrice | Conditional | Yes | Present |
| PricingCurrencyEffectiveCost | Conditional | Yes | Present |
| PricingCurrencyListUnitPrice | Conditional | Yes | Present |
| PricingQuantity | Mandatory | Yes | Present |
| PricingUnit | Mandatory | Yes | Present |
| ProviderName | Mandatory | Yes (FOCUS-unique) | Present |
| PublisherName | Mandatory | Yes | Present |
| RegionId | Conditional | Yes | Present |
| RegionName | Conditional | Yes | Present |
| ResourceId | Conditional | Yes | Present |
| ResourceName | Conditional | Yes | Present |
| ResourceType | Conditional | No (in gap register) | Missing: Conditional |
| ServiceCategory | Mandatory | No (in gap register) | Missing: Mandatory |
| ServiceName | Mandatory | Yes | Present |
| ServiceSubcategory | Recommended | No (in gap register) | Missing: Recommended |
| SkuId | Conditional | Yes | Present |
| SkuMeter | Conditional | No (in gap register) | Missing: Conditional |
| SkuPriceDetails | Conditional | No (in gap register) | Missing: Conditional |
| SkuPriceId | Conditional | Yes (sku.id + tier_start) | Present |
| SubAccountId | Conditional | Yes (project) | Present |
| SubAccountName | Conditional | Yes (project) | Present |
| SubAccountType | Conditional | No (in gap register) | Missing: Conditional |
| Tags | Conditional | No (in x_Tags, x_Labels) | Present, deviation to fix |

Reading the tally: of 57 v1.2 columns, 33 are present and conformant, 2 are present with a deviation to fix (ChargeCategory and PricingCategory enum coverage), and 22 are missing. Of the 21 Mandatory columns, 18 are present and 3 are missing (BillingAccountName, InvoiceIssuerName, ServiceCategory). Tags is counted as a deviation rather than fully missing because the key-value data exists in x_Tags and x_Labels and needs promotion into the standard column.

### 1.4 What's solved, and what remains

**Solved (the hard parts):**

- The cost family. BilledCost, EffectiveCost, ContractedCost, and ListCost are all derived from real Google billing fields, with credits folded into billed and effective cost and a documented list-price basis. This avoids the common list-cost trap, where a feed carries only list price and the discounted costs are a substantive later reconciliation. Google reconciles credits into the cost columns at export time.
- Daily granularity, resource identity (ResourceId, ResourceName), region (RegionId, RegionName), zone, and project-level sub-account attribution (SubAccountId, SubAccountName).
- Full pricing-currency column family, SKU identity, and unit-price columns.

**Remaining substantive gaps (tractable):**

- Three Mandatory descriptive columns are not populated: ServiceCategory (the FOCUS service taxonomy), InvoiceIssuerName, and BillingAccountName. These are real additions, but they are descriptive metadata Google already holds elsewhere (service catalog, billing account record), not measurements that must be reconstructed. They block conformance until populated.

**Remaining shape and coverage gaps:**

- Tags: the FOCUS Tags column is not populated; the key-value data lives in x_Tags, x_Labels, x_SystemLabels, and x_ProjectLabels. Promoting or aliasing this into the standard Tags column is a mapping task, not a data-collection task.
- Commitment discounts (CUDs): the entire CommitmentDiscount column family is unpopulated. CUD information is carried in the x_Credits record. Populating CommitmentDiscountId, Name, Category, Type, and Status is a transform from x_Credits; Quantity and Unit are a genuine data gap where Google's register lists no current mitigation.
- Conditional descriptive columns: ResourceType, SubAccountType, SkuMeter, and SkuPriceDetails are unpopulated but applicable, and Recommended columns ChargeFrequency, InvoiceId, and ServiceSubcategory are absent. None block conformance.

### 1.5 Deviations to fix

- ChargeCategory: populated from cost_type with supported values Usage, Tax, and Adjustment. FOCUS v1.2 allows Usage, Purchase, Tax, Credit, and Adjustment. Google's register notes Purchase is not supported and Credit information is redirected to x_Credits. Rows that should carry Purchase or Credit therefore fall outside the standard enum, which a validator will flag. Completing the enum coverage is the fix.
- PricingCategory: populated with Committed and Standard; the Dynamic value is not supported and that information might appear in ChargeDescription instead. Add Dynamic where applicable.
- Tags: present as data but not in the FOCUS Tags column (see 1.4). The x_ columns are correctly shaped as key-value RECORD, so the fix is exposing them under the standard column.

Already done right: key-value tag structure, ISO 8601 timestamps, ISO 4217 currency codes, daily charge periods, NUMERIC cost types, and correct use of the x_ prefix for all Google-specific columns, which is exactly what FOCUS asks providers to do for non-standard fields.

---

## Part 2: The path forward

### 2.1 Which FOCUS version to target

Build target: FOCUS v1.2, which is the current certification baseline and the version Google's dedicated export already tracks in its gap register. The specification has since progressed to v1.3 (December 2025), which deprecates ProviderName and PublisherName and adds split-cost-allocation columns, and v1.4 (June 2026), which removes ProviderName and PublisherName and adds invoice-detail and billing-period datasets. Google should baseline v1.2 for conformance today and design the same export to carry forward cleanly to v1.3 and v1.4, given the deprecations will affect two columns currently populated.

### 2.2 What certification requires

FOCUS conformance for data generators runs through the FinOps Foundation. The current program is "FinOps Certified FOCUS v1.2 Conformant" (contact member-cert@finops.org for the RFI). Membership is required for certification, though contributing to the specification is open and free. The deliverables are a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report. Google already publishes a native-to-FOCUS mapping and a conformance-gap table in its documentation, which are effectively the seed of two of those deliverables.

Open-source tooling supports the work: the FOCUS Validator (checks data against the Requirements Model), the FOCUS Converter (provider-native to FOCUS), and the FOCUS Requirements Model (machine-readable MUST/SHOULD/MAY rules). The FOCUS get-started page for Google Cloud does not assert a formal certification badge, so this report does not claim one.

### 2.3 Phased roadmap

**Phase 0: Validate what exists.** Run a sample of the dedicated FOCUS export through the FOCUS Validator against v1.2. Confirm the present-column set validates cleanly and pin the exact gap list to validator output rather than documentation alone.

**Phase 1: Close the three Mandatory descriptive columns.** Populate ServiceCategory (map Google services to the FOCUS service taxonomy), InvoiceIssuerName, and BillingAccountName. These three unblock conformance and draw on metadata Google already holds.

**Phase 2: Fix the enum and shape deviations.** Complete ChargeCategory coverage (add Purchase and Credit) and PricingCategory coverage (add Dynamic). Promote the key-value tag data from x_Tags and x_Labels into the standard FOCUS Tags column.

**Phase 3: Round out applicable Conditional and Recommended columns.** Derive the CommitmentDiscount family from x_Credits (Id, Name, Category, Type, Status), and populate ResourceType, SubAccountType, SkuMeter, SkuPriceDetails, ChargeFrequency, InvoiceId, and ServiceSubcategory. Note CommitmentDiscountQuantity and CommitmentDiscountUnit as a genuine data gap to scope with the billing team.

**Phase 4: Mature toward the latest version and certify.** Move the export off the Preview stage, plan for the v1.3 deprecation and v1.4 removal of ProviderName and PublisherName, and pursue the FinOps Certified FOCUS v1.2 Conformant designation.

### 2.4 FOCUS Use Cases unlocked

Unlocked today by the present columns: multi-cloud cost normalization and comparison, effective-cost and amortized-cost reporting, cost allocation by project and resource, service and region breakdowns, unit-economics analysis on ConsumedQuantity and PricingQuantity, and anomaly detection on daily charge records. The effective-cost columns mean actuals-based budgeting and discount-inclusive showback work now, not after a reconciliation step.

Unlocked by Phase 1 to 3: allocation and reporting by ServiceCategory and by standardized Tags, commitment-discount coverage and utilization reporting once the CommitmentDiscount family is populated, and invoice-level reconciliation once InvoiceIssuerName and InvoiceId are present.

Out of scope for now: capacity-reservation use cases, since those columns are not populated. Commitment-discount quantity and utilization-rate use cases are partially out of scope until CommitmentDiscountQuantity and Unit are addressed.

---

## Part 3: Immediate next steps

1. Run a current sample of the dedicated FOCUS export through the FOCUS Validator against v1.2 and record the exact failing columns.
2. Populate the three Mandatory descriptive columns: ServiceCategory, InvoiceIssuerName, and BillingAccountName.
3. Complete ChargeCategory and PricingCategory enum coverage, and expose the key-value tag data under the standard FOCUS Tags column.
4. Derive the CommitmentDiscount column family from x_Credits, and scope CommitmentDiscountQuantity and Unit with the billing team.
5. Confirm the target representation against the FOCUS Requirements Model, then engage member-cert@finops.org on the FinOps Certified FOCUS v1.2 Conformant RFI.

---

## Confidence summary

- FOCUS v1.2 feature levels: high confidence. Verified against the FOCUS column library and the bundled reference (SPEC_VERSIONS_AS_OF 2026-06-23), with a live spot-check of Tags, ServiceCategory, and ServiceSubcategory against the specification. No refresh of the bundled table was required.
- Present-column classification: high confidence for the cost, pricing, resource, and account families, which Google documents field by field with explicit Google-source mappings.
- Missing-column classification: high confidence, because it draws directly on Google's own published conformance-gap table rather than inference.
- Version shipped: high confidence that the get-started page lists v1.0 (BigQuery view and Looker template) and that the dedicated export is documented against v1.2 gaps in Preview. Moderate confidence on the precise Preview-to-GA status at any given date, since the dedicated export carries a Pre-GA banner that can change.
- Tags treated as a deviation rather than fully missing: moderate-to-high confidence, on the basis that the key-value data demonstrably exists in x_Tags and x_Labels and needs promotion, not collection.
- A live FOCUS Validator run against a real sample is the objective arbiter and is recommended before any formal conformance claim; this analysis is a documentation-based assessment, not a validator result.

---

## Sources

- Google Cloud, "Structure of FOCUS data export" (docs.cloud.google.com/billing/docs/how-to/export-data-bigquery-tables/focus-export), including the FOCUS conformance report and conformance-gaps table.
- Google Cloud, "Set up FOCUS Cloud Billing data export to BigQuery" (docs.cloud.google.com/billing/docs/how-to/export-data-bigquery-focus-setup).
- FOCUS get-started page for Google Cloud (focus.finops.org/get-started/google-cloud/) and the FOCUS provider record.
- Google Cloud Blog, "Normalize billing data across clouds with new Looker template and BigQuery views" (FOCUS v1.0 GA).
- FOCUS Specification v1.2 and the FOCUS column library (focus.finops.org/focus-specification/, focus.finops.org/focus-columns/).
- FinOps Certified FOCUS Conformant program (finops.org).

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
