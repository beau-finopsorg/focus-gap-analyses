# Akamai & FOCUS: Data Generator Gap Analysis (Linode)

*Analysis run: September 24, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** Akamai Technologies (Linode)  
**Prepared:** September 24, 2026 (Rev. 3)  
**Source:** Akamai Billing API v1, `Get daily compute usage` (documentation re-shared September 14, 2026)  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 23 Present, 2 Deviation, 6 Missing Mandatory, 14 Missing Conditional, 2 Missing Recommended, 10 N/A

---

## Executive Summary

Akamai has already built a FOCUS-aligned daily compute usage API. It emits per-instance, daily, tagged records and self-declares FOCUS alignment. The `Get daily compute usage` operation returns daily, per-instance, list-cost records carrying `ResourceId`, `ResourceName`, `Tags`, `RegionId`, and a FinOps service taxonomy, available as CSV, JSON, and Parquet. The structural problems flagged in the earlier self-service analysis (granularity, resource identity, and tags) are already solved. This revision re-verifies the analysis against the documentation Akamai re-shared on September 14, 2026: the schema, gaps, and deviations are unchanged. What is new is Akamai naming FOCUS v1.4 certification as the goal, and a billing SME (Saurabh Khare) joining the effort.

The remaining gap is concentrated. The dataset is list-price only: by design it excludes discounts, credits, and network-transfer pooling, which Akamai applies at final invoice. So the Mandatory cost columns `BilledCost`, `EffectiveCost`, and `ContractedCost` are absent. Three other Mandatory columns are missing but trivial: `PricingQuantity` and `PricingUnit` are derivable from the `ConsumedQuantity` and `ConsumedUnit` already emitted, and `ChargeClass` is Mandatory-but-nullable (populated only for corrections). Two present columns need format work: `Tags` is emitted as an array of bare strings rather than key-value pairs, and the example `ChargeCategory` value is not a valid FOCUS enum member.

**Recommendation:** Treat this as a near-conformant dataset to finish, not a greenfield build. Close the Mandatory gaps (chiefly the three cost columns, reconciling list cost to `BilledCost` and `EffectiveCost`, plus three trivial ones), fix the two format deviations, validate against the FOCUS Validator, and pursue FinOps Certified FOCUS v1.2 Conformant first. Build toward v1.4, whose Invoice Detail dataset is the natural home for the discount and credit data the cost columns need. v1.4 is not yet a certifiable target (Section 2.2).

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

**Akamai Billing API v1** (`GET /billing/v1/contracts/{contractId}/compute-customers/{computeCustomerId}/usage/daily-summary/{date}`): A purpose-built operation whose documentation states it "follows the FOCUS standard specification." The earlier revision analyzed the self-service Linode v4 Account Invoices endpoints, which was the wrong source.

Key characteristics:
- **Daily granularity:** 24-hour blocks aligned to Eastern Time billing days.
- **Per-instance:** Each record carries `ResourceId` and `ResourceName`.
- **Tagged:** User-defined `Tags` on Linodes (including LKE nodes), Block Storage, NodeBalancers, and images flow into the dataset (format aside, see Section 1.5).
- **Region, service taxonomy, SKU, consumed quantity and unit:** All present.
- **Formats:** CSV, JSON, and Parquet. Pagination up to 5,000 records per page.
- **List-cost basis:** Values reflect list price and exclude discounts, credits, and network-transfer pooling, which are applied at final invoice. This is the crux of the remaining gap.
- **Limited Availability:** The operation is marked Limited Availability, and for compute the Billing API retains data for the current month only. Confirm the general-availability timeline, the historical-retention plan, and whether the dataset is offered to all contract customers or a subset.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven. Mandatory columns must exist and be populated where applicable; Conditional columns must exist and are populated when the provider's model creates the condition, otherwise null; Recommended columns are encouraged. Conformance is checked against the FOCUS Requirements Model (the machine-readable MUST/SHOULD/MAY rules), which the FOCUS Validator uses. Provider-specific columns are permitted when prefixed `x_`, and Akamai already does this correctly with `x_MTDConsumedQuantity`. Feature levels were verified column by column against the FOCUS v1.2 Content Constraints.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | Linode source | Status |
|---|---|---|---|
| BilledCost | Mandatory | No (list cost only) | Missing: Mandatory |
| EffectiveCost | Mandatory | No (list cost only) | Missing: Mandatory |
| ListCost | Mandatory | `ListCost` | Present |
| ContractedCost | Mandatory | No (list cost only) | Missing: Mandatory |
| BillingAccountId | Mandatory | Yes | Present |
| BillingAccountName | Mandatory | Yes | Present |
| BillingCurrency | Mandatory | Yes | Present |
| BillingPeriodStart | Mandatory | Yes | Present |
| BillingPeriodEnd | Mandatory | Yes | Present |
| ChargePeriodStart | Mandatory | Yes | Present |
| ChargePeriodEnd | Mandatory | Yes | Present |
| ChargeDescription | Mandatory | Yes | Present |
| ChargeCategory | Mandatory | Yes, but the example value ("Compute") is not a valid enum member | Deviation |
| ChargeClass | Mandatory (nullable) | No (corrections only) | Missing: Mandatory |
| InvoiceIssuerName | Mandatory | Yes | Present |
| ProviderName | Mandatory (dep. v1.3) | Yes | Present |
| PublisherName | Mandatory (dep. v1.3) | Yes | Present |
| ServiceName | Mandatory | Yes | Present |
| ServiceCategory | Mandatory | Yes (enum) | Present |
| PricingQuantity | Mandatory | No (derivable from ConsumedQuantity) | Missing: Mandatory |
| PricingUnit | Mandatory | No (derivable from ConsumedUnit) | Missing: Mandatory |
| ConsumedQuantity | Conditional | Yes | Present |
| ConsumedUnit | Conditional | Yes | Present |
| ListUnitPrice | Conditional | Yes | Present |
| ContractedUnitPrice | Conditional | No | Missing: Conditional |
| PricingCategory | Conditional | No | Missing: Conditional |
| ChargeFrequency | Recommended | Yes (enum) | Present |
| BillingAccountType | Conditional (1.2) | No | Missing: Conditional |
| SubAccountId | Conditional | No | Missing: Conditional |
| SubAccountName | Conditional | No | Missing: Conditional |
| SubAccountType | Conditional (1.2) | No | Missing: Conditional |
| ResourceId | Conditional | Yes | Present |
| ResourceName | Conditional | Yes | Present |
| ResourceType | Conditional | No | Missing: Conditional |
| SkuId | Conditional | Yes | Present |
| Tags | Conditional | Yes, but an array of strings, not key-value pairs | Deviation |
| PricingCurrency | Conditional (1.2) | No | Missing: Conditional |
| PricingCurrencyListUnitPrice | Conditional (1.2) | No | Missing: Conditional |
| PricingCurrencyContractedUnitPrice | Conditional (1.2) | No | Missing: Conditional |
| PricingCurrencyEffectiveCost | Conditional (1.2) | No | Missing: Conditional |
| SkuMeter | Conditional (1.1+) | No | Missing: Conditional |
| SkuPriceId | Conditional | No | Missing: Conditional |
| SkuPriceDetails | Conditional (1.1+) | No | Missing: Conditional |
| RegionId | Conditional | Yes | Present |
| RegionName | Conditional | Yes | Present |
| CommitmentDiscountId | Conditional | N/A: no commitments sold | N/A |
| CommitmentDiscountName | Conditional | N/A | N/A |
| CommitmentDiscountType | Conditional | N/A | N/A |
| CommitmentDiscountCategory | Conditional | N/A | N/A |
| CommitmentDiscountStatus | Conditional | N/A | N/A |
| CommitmentDiscountQuantity | Conditional (1.1+) | N/A | N/A |
| CommitmentDiscountUnit | Conditional (1.1+) | N/A | N/A |
| CapacityReservationId | Conditional (1.1+) | N/A | N/A |
| CapacityReservationStatus | Conditional (1.1+) | N/A | N/A |
| InvoiceId | Recommended | No | Missing: Recommended |
| ServiceSubcategory | Recommended | No | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: region only | N/A |

**Tally:** 23 Present, 2 Deviation, 6 Missing Mandatory, 14 Missing Conditional, 2 Missing Recommended, 10 N/A

Re-verified against FOCUS v1.4: every Mandatory column in this table was re-checked against the live v1.4 Cost and Usage dataset. All levels hold unchanged from v1.2 to v1.4 for the columns this API touches. The one structural change is that `ProviderName` and `PublisherName` are removed in v1.4 (deprecated in v1.3), so the API's current emission of both is a v1.2/v1.3 bridge, not a v1.4 end state.

### 1.4 What Is Solved, and What Remains

**Solved:** Granularity (daily, ET-aligned), resource identity (`ResourceId`, `ResourceName`), and tags (present, pending a format fix). A FinOps-grade service taxonomy and region detail are present too.

**Substantive (3 of 6 Mandatory gaps):** `BilledCost` (cash basis), `EffectiveCost` (amortized), and `ContractedCost`. The dataset is list-price only, so until these exist it supports list-cost reporting and allocation but not invoice reconciliation, budgeting on actuals, or effective-cost unit economics. Closing this means joining invoice-level adjustments (discounts, credits, network-transfer pooling) back to the daily usage lines. Once a monthly cap is reached, `ListCost` for the remaining days is 0, and list values are rounded to one cent; both matter when reconciling daily list cost against the final invoice.

**Trivial (3 of 6 Mandatory gaps):** `PricingQuantity` and `PricingUnit` are derivable from the `ConsumedQuantity` and `ConsumedUnit` already present (in the example, `ListUnitPrice` 0.52 × 24 = `ListCost` 12.48), which holds for flat-rate usage. `ChargeClass` is Mandatory-but-nullable, so a column that is null except on corrections satisfies it.

**Secondary (Conditional and Recommended):** `PricingCategory`, `ContractedUnitPrice`, `SubAccountId`/`SubAccountName`/`SubAccountType`, and `ResourceType` are Conditional and absent. `ServiceSubcategory` and `InvoiceId` are Recommended and would round out the dataset.

### 1.5 Deviations to Fix

**Tags:** The example emits an array of bare strings (`["infra pin_netv4", "test_tag"]`). FOCUS expects `Tags` as a structured set of key-value pairs. Emit key-value tags and decide how to represent untagged or value-less tags. Confirm the target representation against the Requirements Model.

**ChargeCategory:** The schema correctly defines the enum (`Usage`, `Purchase`, `Tax`, `Credit`, `Adjustment`), but the example record shows `"ChargeCategory": "Compute"`, which is a `ServiceCategory` value. Confirm production data emits only valid enum members.

**Already right:** `ChargeFrequency` and `ServiceCategory` use valid FOCUS enums, timestamps are ISO 8601, and the month-to-date field is correctly namespaced as `x_MTDConsumedQuantity`.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Live versions: v1.1 (Nov 7, 2024), v1.2 (May 29, 2025, the current certification baseline), v1.3 (Dec 5, 2025), and v1.4 (June 4, 2026, latest, adding an Invoice Detail dataset and a billing-period dataset built for reconciliation). As of September 24, 2026, the FOCUS Validator supports v1.2 and v1.3 conformance checks; v1.4 support is not yet available.

**Build target: FOCUS v1.4.** The cost gap is an invoice-reconciliation problem, which the v1.4 Invoice Detail dataset addresses. Pairing the daily usage dataset (list cost, resource-level) with a v1.4 invoice dataset (discounts, credits, pooling, billed and effective cost) is the cleanest route to the missing cost columns. v1.4 removes `ProviderName` and `PublisherName`, which the API currently emits.

**Certification target: FOCUS v1.2 first.** The FinOps Certified FOCUS Conformant program still validates against v1.2 only, and each future version gets its own certification window once the Foundation opens it (certification does not roll forward automatically). Certify at v1.2 to get Linode listed now, keep building toward v1.4, and re-certify the moment that track opens.

### 2.2 What Certification Requires

As of September 24, 2026, certification requires: FinOps Foundation and Linux Foundation membership; 2 to 10 Akamai staff (scaled to company size) holding the FinOps Certified FOCUS Analyst credential; support for every Mandatory column, including `BilledCost`, `EffectiveCost`, and `BillingCurrency`; anonymized sample data covering at least one complete billing cycle; publicly accessible conformance-gap and native-to-FOCUS mapping documentation (this report is the seed); and self-attestation to the semantic validation criteria, with deviations disclosed. There is no separate certification fee for members. Contact `member-cert@finops.org` for the RFI and to ask when a v1.3 or v1.4 track will open.

Tooling: the FOCUS Requirements Model (machine-readable conformance rules), the FOCUS Validator (run the daily usage CSV/JSON through it now; it will flag the missing Mandatory columns and the `Tags` and `ChargeCategory` issues), and the FOCUS Converter (less central for a provider that already emits FOCUS shape, but a path to contribute a Linode profile back).

### 2.3 Phased Roadmap

**Phase 0: Validate and scope.** Pull a sample from `Get daily compute usage` and run it through the FOCUS Validator against v1.2/v1.3. Confirm membership, the GA and retention plan for the Limited Availability endpoint, and the v1.4-build / v1.2-certify decision. Open the RFI with `member-cert@finops.org`.

**Phase 1: Close the Mandatory gap.** Add `BilledCost`, `EffectiveCost`, and `ContractedCost` by reconciling invoice-level discounts, credits, and network-transfer pooling back to the daily list-cost lines (accounting for monthly caps). Add the three trivial Mandatory columns: `PricingQuantity`, `PricingUnit`, and a nullable `ChargeClass`.

**Phase 2: Quick fixes.** Emit `Tags` as key-value pairs, and confirm `ChargeCategory` only carries valid enum values in production. Re-run the Validator to a clean pass on the present columns.

**Phase 3: Conditional and Recommended columns.** Add `PricingCategory`, `ContractedUnitPrice`, account hierarchy (`SubAccountId`, `SubAccountName`, `SubAccountType`) for multi-account customers, `SkuPriceId`, `ResourceType`, `ServiceSubcategory`, and `InvoiceId` (which aids reconciliation).

**Phase 4: Mature to v1.4 and certify.** Adopt the v1.4 Invoice Detail and billing-period datasets, drop `ProviderName` and `PublisherName`, move the endpoint out of Limited Availability with a defined retention window, and re-certify at the highest version the program supports.

After Phases 1 and 2, Akamai has a v1.2-conformant Linode dataset with daily, resource-, and tag-level detail and reconciled cost.

### 2.4 FOCUS Use Cases Unlocked

- **Achievable now (list-cost basis):** Analyze costs of components of a resource; analyze cost per compute service; compare resource usage month over month; identify anomalous daily spending by region and service; analyze costs by service name and by service category; analyze resource costs by SKU.
- **After the cost columns are added (actuals basis):** Verify accuracy of service provider invoices (needs `BilledCost`); update budgets with billed costs; forecast cashflow month over month by service; calculate unit economics (on effective cost); analyze credit memos (needs credit data).
- **Out of scope:** Commitment-discount, capacity-reservation, virtual-currency, availability-zone, and marketplace third-party SaaS use cases depend on mechanics Linode does not have. The related columns are legitimately null.

---

## Part 3: Immediate Next Steps

1. Akamai runs a `Get daily compute usage` sample through the FOCUS Validator (v1.2/v1.3) and shares the result.
2. Hold a joint working session on the cost-column approach with Saurabh Khare (Akamai's billing SME) and the FinOps Foundation team: how invoice-level discounts, credits, and pooling will be reconciled back to daily lines to produce `BilledCost` and `EffectiveCost`.
3. Akamai confirms FinOps Foundation and Linux Foundation membership, starts the required staff FinOps Certified FOCUS Analyst credentials, and emails `member-cert@finops.org` to request the RFI and ask when a v1.3 or v1.4 track opens.
4. Fix the `Tags` format, confirm `ChargeCategory` emits valid enum values, and add the trivial Mandatory columns (`PricingQuantity`, `PricingUnit`, nullable `ChargeClass`).
5. Confirm the Limited Availability GA timeline and historical-retention plan (currently current-month-only for compute).
6. Finalize the native-to-FOCUS mapping and Conformance Gap Report; submit for v1.2 certification; publish sample data; request listing on the FOCUS supported-provider page.

---

## Confidence Summary

- **High:** The daily compute usage API exists, self-declares FOCUS alignment, and provides daily, per-resource, tagged, list-cost records (per the documentation Akamai supplied and re-shared September 14, 2026; no fields, types, or examples changed).
- **High:** 23 Present and 2 Deviation (25 of 57 columns emitted); six Mandatory missing, of which only the three cost columns are substantive. Cost is the dominant gap because the dataset is list-price only.
- **High:** Feature levels were verified column by column against the FOCUS v1.2 spec, and re-verified September 24, 2026 against v1.4: every Mandatory column analyzed carries the same level in both, and `ProviderName` and `PublisherName` are removed in v1.4.
- **High:** `Tags` as an array of strings is a format deviation from FOCUS key-value tags.
- **High:** As of September 24, 2026, the certification program certifies against v1.2 only and the Validator checks v1.2 and v1.3, so Akamai's stated goal of "v1.4 certification" is not yet an available track.
- **Moderate:** The `ChargeCategory: "Compute"` example is likely a documentation error; confirm production values.
- **Moderate:** Exact target representation for `Tags` and a few feature-level edge cases; confirm against the Requirements Model and a live Validator run.
- **Moderate:** GA timeline, retention beyond the current month, and customer coverage of the Limited Availability endpoint; pending Akamai confirmation.

---

## Sources

- Akamai Billing API v1, Get daily compute usage: [techdocs.akamai.com/billing-app/reference/get-daily-compute-usage](https://techdocs.akamai.com/billing-app/reference/get-daily-compute-usage)
- FinOps Certified FOCUS Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)
- Introducing FOCUS 1.4: [finops.org/insights/introducing-focus-1-4](https://www.finops.org/insights/introducing-focus-1-4/)
- Introducing FOCUS 1.3: [finops.org/insights/introducing-focus-1-3](https://www.finops.org/insights/introducing-focus-1-3/)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FOCUS Specification v1.4: [focus.finops.org](https://focus.finops.org/docs/specification/v1-4/)
- FOCUS Validator: [focus.finops.org/focus-validator](https://focus.finops.org/focus-validator/)
- FOCUS Converter: [github.com/finopsfoundation/focus_converters](https://github.com/finopsfoundation/focus_converters)
- FOCUS Requirements Model: [github.com/FinOps-Open-Cost-and-Usage-Spec/FOCUS_Spec](https://github.com/FinOps-Open-Cost-and-Usage-Spec/FOCUS_Spec)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
