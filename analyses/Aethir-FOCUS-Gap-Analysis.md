# Aethir & FOCUS: Data Generator Gap Analysis

*Analysis run: July 1, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** Aethir  
**Prepared:** July 1, 2026  
**Source:** Aethir enterprise GPU pricing page; Atlas Cloud on-demand pricing; Aethir docs (Cloud Host, Checker, tokenomics); public tokenomics and revenue disclosures  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 0 Present, 17 Deviation, 4 Missing Mandatory, 25 Missing Conditional, 3 Missing Recommended, 8 N/A

---

## Executive Summary

Aethir is a decentralized GPU-as-a-service network (a DePIN): enterprise and developer customers rent NVIDIA H100, H200, B200, and GB200 capacity that is physically supplied by independent Cloud Hosts across Tier 3 and Tier 4 data centers, coordinated by an on-chain protocol and a Checker verification layer. Two demand paths exist: an Enterprise AI track (reserved bare-metal clusters, monthly payment in advance against committed capacity) and Atlas, an on-demand marketplace with per-second and hourly containerized GPU billing. Fees are denominated in fiat (USD), and compute settlements are conducted on-chain in the ATH token.

The material finding is that Aethir has strong underlying billing mechanics (metered GPU hours, a clear unit price per GPU type, reserved-versus-on-demand pricing, a customer/tenant identity, and an SLA-backed service) but no documented customer-facing cost-and-usage export shaped anywhere near FOCUS. The public surfaces are a protocol dashboard (network utilization, uptime, node earnings) and enterprise invoicing, not a per-charge tabular dataset with FOCUS column IDs. Almost every mapping below is therefore "the data exists in the billing system, transform required," not "emitted and aligned."

The decentralized model creates one structural wrinkle worth naming up front: fees are quoted in USD but settled in a crypto token (ATH). FOCUS handles this cleanly through the pricing-currency family: `BillingCurrency` carries the invoiced/settled currency and the `PricingCurrency` columns carry the quoting currency, so the dual-currency reality is representable without bending the spec. It does mean an ATH-settled row should record ATH in `BillingCurrency` with an `x_` custom column for the USD-equivalent and the ATH/USD rate, since ATH is not an ISO 4217 code.

**Recommendation:** Model one FOCUS row per GPU instance (or reserved cluster) per charge period. `ServiceCategory` = "Compute", `ChargeCategory` = "Usage" for on-demand and "Purchase" for reserved-capacity commitments, `PricingUnit` = "GPU-Hour". Treat the four cost columns as a substantive build: reserved commitments, on-demand metering, and ATH settlement each price differently and must be reconciled to a single row. Begin with the Enterprise AI invoice path, where tenant identity and USD amounts are cleanest.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

Aethir does not publish a customer billing API or a documented cost-and-usage export schema. This analysis is built from the pricing surfaces, product documentation, and tokenomics that describe how compute is metered, priced, and settled. Field-level detail is therefore inferred from the billing model rather than read off an export.

Key characteristics:

- **Two demand models:** Enterprise AI sells reserved bare-metal GPU clusters (single node to 4,000+ GPU clusters) under enterprise agreements billed monthly in advance against a capacity commitment. Atlas Cloud sells on-demand containerized GPU instances with per-second and hourly billing and no minimum commitment.
- **Metered unit:** the billable unit is the GPU-hour (per-second granularity on Atlas). Pricing is per GPU per hour by GPU type, for example H100 around $2.95/hr on-demand and roughly $1.25/hr under enterprise reserved terms.
- **Dual currency:** fees are denominated in fiat (USD) and accepted in fiat, stablecoin, or ATH, while protocol-level compute settlement is conducted in ATH. The USD amount and the ATH-settled amount both exist for a given charge.
- **Marketplace supply side:** capacity is contributed by independent Cloud Hosts who earn 80% of client service fees (20% to the Aethir treasury) plus Proof of Capacity and Proof of Delivery token rewards. This host-side ledger is a separate economic flow from the customer invoice and is not the FOCUS dataset in scope; FOCUS models the customer's cost of consuming compute, not host payouts.
- **Tenant identity:** enterprise customers have accounts and SLAs; Atlas users deploy under an account and pay per usage. A billing-account identity exists on both paths.
- **Verification layer:** the Checker network validates GPU specs and uptime, so per-container performance and uptime data exist, but this is telemetry, not a billing column set.
- **Reporting surface:** the public dashboard reports network-level utilization, capacity, uptime, latency, throughput, and node earnings. It is protocol analytics, not a per-tenant, per-charge cost dataset.

The gap is not a data-availability gap so much as a data-shaping gap: the billing system knows the customer, the GPU type, the hours, the unit price, and the amount, but there is no evidence it externalizes those as FOCUS-shaped rows today.

### 1.2 How Conformance Is Judged

FOCUS conformance is judged column by column against feature levels (Mandatory, Conditional, Recommended, Optional) defined in the specification's Content Constraints. Feature levels in this report were verified against the FOCUS v1.2 specification and the FOCUS column library. Because Aethir sells commitment-based reserved capacity, the CommitmentDiscount family is in scope rather than automatically N/A: reserved-capacity terms are a candidate FOCUS commitment construct and should be evaluated, not nulled by default. The ATH settlement layer is handled through `BillingCurrency` plus custom `x_` columns, not by a bespoke schema.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | Aethir source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Invoiced/settled amount per instance per period; exists on the invoice but not exported as a FOCUS field, and reserved-vs-on-demand-vs-ATH settlement must reconcile to one row | Missing: Mandatory |
| EffectiveCost | Mandatory | Amortized cost after reserved commitment; derivable from enterprise terms but not emitted | Missing: Mandatory |
| ListCost | Mandatory | On-demand published rate × GPU-hours; computable from public pricing | Deviation |
| ContractedCost | Mandatory | Reserved-rate × committed GPU-hours; in enterprise agreement, not exported | Missing: Mandatory |
| BillingAccountId | Mandatory | Enterprise account / Atlas account identifier | Deviation |
| BillingAccountName | Mandatory | Customer organization name | Deviation |
| BillingCurrency | Mandatory | USD for fiat invoicing; ATH for on-chain settlement (record settlement currency; ATH is non-ISO, flag via x_ column) | Deviation |
| BillingPeriodStart | Mandatory | Monthly billing cycle start (enterprise); usage window start (Atlas) | Deviation |
| BillingPeriodEnd | Mandatory | Monthly billing cycle end | Deviation |
| ChargePeriodStart | Mandatory | Instance start timestamp (per-second on Atlas) | Deviation |
| ChargePeriodEnd | Mandatory | Instance stop / reserved-period end | Deviation |
| ChargeDescription | Mandatory | Derive: GPU type + instance + period (e.g., "NVIDIA H100 SXM on-demand, 72 GPU-hours") | Deviation |
| ChargeCategory | Mandatory | Derive: "Usage" on-demand, "Purchase" for reserved commitment | Deviation |
| ChargeClass | Mandatory (nullable) | null except for corrections | Missing: Mandatory |
| InvoiceIssuerName | Mandatory | "Aethir" | Deviation |
| ProviderName | Mandatory (dep. v1.3) | "Aethir" | Deviation |
| PublisherName | Mandatory (dep. v1.3) | "Aethir" (compute delivered by third-party Cloud Hosts; Publisher still Aethir as marketplace) | Deviation |
| ServiceName | Mandatory | "Aethir Enterprise AI" or "Aethir Atlas Cloud" | Deviation |
| ServiceCategory | Mandatory | Derive: "Compute" | Deviation |
| PricingQuantity | Mandatory | GPU-hours (flat-rate per GPU type; equals consumed hours) | Deviation |
| PricingUnit | Mandatory | "GPU-Hour" | Deviation |
| ConsumedQuantity | Conditional | GPU-hours consumed (per-second precision on Atlas) | Missing: Conditional |
| ConsumedUnit | Conditional | "GPU-Hour" | Missing: Conditional |
| ListUnitPrice | Conditional | Published per-GPU-hour rate by GPU type | Missing: Conditional |
| ContractedUnitPrice | Conditional | Reserved per-GPU-hour rate from enterprise agreement | Missing: Conditional |
| PricingCategory | Conditional | "On-Demand" (Atlas) or "Committed" (reserved enterprise) | Missing: Conditional |
| ChargeFrequency | Recommended | "Usage-Based" on-demand; "Recurring" for monthly reserved | Missing: Recommended |
| BillingAccountType | Conditional | "Enterprise" or "Individual/Developer" | Missing: Conditional |
| SubAccountId | Conditional | N/A: no documented sub-account or project hierarchy below the billing account | N/A |
| SubAccountName | Conditional | N/A | N/A |
| SubAccountType | Conditional | N/A | N/A |
| ResourceId | Conditional | GPU container ID / instance ID (exists at the container layer) | Missing: Conditional |
| ResourceName | Conditional | Instance or cluster name | Missing: Conditional |
| ResourceType | Conditional | GPU model (e.g., "NVIDIA H100 SXM") | Missing: Conditional |
| SkuId | Conditional | GPU-type + term code (e.g., "h100-sxm-ondemand") | Missing: Conditional |
| Tags | Conditional | N/A: no documented user-defined resource tagging | N/A |
| PricingCurrency | Conditional | USD (the quoting currency, distinct from ATH settlement) | Missing: Conditional |
| PricingCurrencyListUnitPrice | Conditional | Published USD rate per GPU-hour | Missing: Conditional |
| PricingCurrencyContractedUnitPrice | Conditional | Reserved USD rate per GPU-hour | Missing: Conditional |
| PricingCurrencyEffectiveCost | Conditional | USD-denominated effective cost | Missing: Conditional |
| SkuMeter | Conditional | "GPU-Hour, H100 SXM" | Missing: Conditional |
| SkuPriceId | Conditional | Not documented | Missing: Conditional |
| SkuPriceDetails | Conditional | GPU spec / SLA tier details | N/A |
| RegionId | Conditional | Data-center location exists internally; not exposed as a billing region | N/A |
| RegionName | Conditional | N/A: no per-region billing rows documented | N/A |
| CommitmentDiscountId | Conditional | Reserved-capacity agreement ID (enterprise) | Missing: Conditional |
| CommitmentDiscountName | Conditional | Reserved-capacity plan name | Missing: Conditional |
| CommitmentDiscountType | Conditional | "Committed capacity" (reserved GPU cluster) | Missing: Conditional |
| CommitmentDiscountCategory | Conditional | "Spend" or "Usage" commitment per enterprise terms | Missing: Conditional |
| CommitmentDiscountStatus | Conditional | "Used" / "Unused" against reserved capacity | Missing: Conditional |
| CommitmentDiscountQuantity | Conditional | Committed GPU-hours | Missing: Conditional |
| CommitmentDiscountUnit | Conditional | "GPU-Hour" | Missing: Conditional |
| CapacityReservationId | Conditional | Reserved cluster reservation ID (enterprise) | Missing: Conditional |
| CapacityReservationStatus | Conditional | "Used" / "Unused" | Missing: Conditional |
| InvoiceId | Recommended | Enterprise invoice number | Missing: Recommended |
| ServiceSubcategory | Recommended | "GPU Compute" / "AI Infrastructure" | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: no zone-level billing | N/A |

**Tally:** 0 Present, 17 Deviation, 4 Missing Mandatory, 25 Missing Conditional, 3 Missing Recommended, 8 N/A

Note on "zero Present": because Aethir emits no FOCUS-shaped export today, nothing is aligned as-is, so no column is marked Present. The 17 Deviation columns are the ones whose underlying data clearly exists in the billing system and needs only shaping plus correct enum/currency values; these are the low-effort wins. The 4 Missing Mandatory columns block conformance, 3 of them substantively (the cost columns).

### 1.4 What Is Solved, and What Remains

**The genuinely substantive gaps (4 Mandatory missing, 3 of them substantive):**

- **BilledCost:** the invoiced/settled amount exists, but producing a per-row FOCUS value means reconciling three pricing regimes (on-demand metered, reserved commitment drawdown, ATH on-chain settlement at a point-in-time rate) onto a single charge line. Substantive.
- **EffectiveCost:** for reserved enterprise capacity, effective cost is the amortized commitment allocated to usage. This requires the commitment terms and an allocation rule; it does not fall out of a usage feed. Substantive.
- **ContractedCost:** reserved-rate × committed quantity lives in the enterprise agreement, not in any public or dashboard surface. Substantive.
- **ChargeClass:** Mandatory but nullable, populated only for corrections. Trivial plumbing once rows exist.

`ListCost` is the one Mandatory cost column that is computable today, since on-demand per-GPU-hour rates are public. That is why it is marked Deviation rather than Missing.

**Trivial once a transform exists:** `ChargeClass` (null default), and the metadata Mandatories (`ServiceCategory` = "Compute", `PricingUnit` = "GPU-Hour", `ServiceName`, `InvoiceIssuerName`, `ProviderName`, `PublisherName`) are constant or single-valued. `PricingQuantity` equals consumed GPU-hours because pricing is flat-rate per GPU type, so it is a clean copy of the metered hours, not a tiered computation.

**Structurally solid, needs shaping:** GPU-hour metering, per-GPU-type unit pricing, reserved-vs-on-demand distinction, a customer/tenant identity, timestamps, and container/instance IDs all exist in the platform. Turning them into FOCUS rows is an ETL and schema exercise, not a data-collection one.

**The commitment family is in scope, not N/A.** Unlike a pure on-demand provider, Aethir's Enterprise AI track sells reserved capacity billed monthly in advance. That is a real commitment construct, so the seven CommitmentDiscount columns and the two CapacityReservation columns are marked Missing: Conditional (the condition applies) rather than N/A. Deciding whether reserved capacity is modeled as a CommitmentDiscount, a CapacityReservation, or simply `PricingCategory` = "Committed" is a design decision to confirm against the Requirements Model.

### 1.5 Deviations to Fix

- **BillingCurrency and the ATH settlement:** record the settlement currency per row. For fiat/stablecoin invoices use "USD". For on-chain ATH settlement, ATH is not an ISO 4217 code, so carry the USD-equivalent and the settlement rate in custom columns (for example `x_SettlementToken` = "ATH", `x_SettlementTokenAmount`, `x_AthUsdRate`) and keep `PricingCurrency` = "USD" for the quoted price. Confirm the intended representation against the FOCUS Requirements Model.
- **ChargeCategory:** "Usage" for on-demand Atlas consumption, "Purchase" for reserved-capacity purchases. Do not use "Compute" (that is a `ServiceCategory` value).
- **ServiceCategory:** "Compute" for all GPU rental.
- **PricingUnit / PricingQuantity:** "GPU-Hour" and metered GPU-hours.
- **PricingCategory:** "On-Demand" for Atlas, "Committed" for reserved enterprise capacity.
- **Custom columns:** prefix any Aethir-specific fields (settlement token, ATH/USD rate, Cloud Host region, Checker uptime) with `x_`.

Already right in substance: a clear metered unit (GPU-hour), a public unit price, a genuine tenant identity, and SLA-backed service definitions. These are the hard parts many providers lack.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (June 4, 2026, the latest ratified version); certify at FOCUS v1.2 (the current certification baseline). Building to v1.4 means not investing in `ProviderName` and `PublisherName`, which are deprecated in v1.3 and removed in v1.4. The v1.4 Invoice Detail and billing-period datasets are a natural fit for Aethir's monthly-in-advance enterprise invoicing and its dual fiat/ATH settlement reconciliation.

### 2.2 What Certification Requires

FOCUS conformance for data generators runs through the FinOps Foundation. Contact `member-cert@finops.org` for the RFI. Membership is required for certification, though contributing to the spec is open and free. Deliverables are a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report (this analysis is its seed). Use the open-source tooling: the FOCUS Validator (checks data against the Requirements Model), the FOCUS Converter (provider-native to FOCUS), and the FOCUS Requirements Model (machine-readable MUST/SHOULD/MAY rules). The dual-currency and reserved-capacity design choices should be validated against the Requirements Model before certification.

### 2.3 Phased Roadmap

**Phase 0: Establish the export.** Aethir has no FOCUS-shaped dataset today, so the first task is producing one at all. Decide the grain (one row per instance per charge period), confirm which internal system holds the metered GPU-hours and the tenant identity, and pull a sample month for both the Enterprise AI and Atlas paths.

**Phase 1: Close the substantive cost gaps.** Build `BilledCost`, `EffectiveCost`, and `ContractedCost`, including the ATH-to-USD reconciliation and the reserved-commitment amortization. Add the trivial Mandatories (`ChargeClass` null default, constant metadata columns). This unlocks actuals-based reporting.

**Phase 2: Fix deviations.** Apply FOCUS column IDs, correct `ChargeCategory` and `ServiceCategory` enums, ISO currency handling, and the `x_` settlement-token columns.

**Phase 3: Round out Conditional and Recommended columns.** Add resource identity (`ResourceId`, `ResourceName`, `ResourceType` from the GPU container), the SKU family, the pricing-currency columns, `ConsumedQuantity`/`ConsumedUnit`, and the commitment/capacity-reservation family for reserved capacity. Add `InvoiceId` and `ServiceSubcategory`.

**Phase 4: Mature and certify.** Target v1.4, drop `ProviderName`/`PublisherName`, adopt the Invoice Detail dataset for the fiat/ATH reconciliation, validate, and open certification.

### 2.4 FOCUS Use Cases Unlocked

- **Unlocked after Phase 1 (cost columns exist):** cost reporting and showback by GPU type, on-demand-versus-reserved spend analysis, invoice reconciliation across fiat and ATH settlement, actuals-based budgeting.
- **Unlocked after Phase 3 (resource and commitment columns exist):** allocation and chargeback by instance or cluster, commitment-utilization and reserved-capacity coverage analysis, anomaly detection on GPU-hour spend.
- **Out of scope for now:** tag-based allocation (no documented user tagging) and sub-account rollups (no documented project hierarchy) until Aethir adds those constructs. Availability-zone and per-region use cases do not apply without zone/region billing.

---

## Part 3: Immediate Next Steps

1. Identify the internal system of record for metered GPU-hours, tenant identity, and settlement amounts, and confirm whether an export can be generated.
2. Decide the FOCUS row grain and pull a sample month for both the Enterprise AI and Atlas paths.
3. Design the dual-currency representation (USD `BillingCurrency`/`PricingCurrency` plus `x_` ATH settlement columns) and validate it against the FOCUS Requirements Model.
4. Decide how reserved capacity maps to the CommitmentDiscount versus CapacityReservation versus `PricingCategory` = "Committed" constructs.
5. Run the sample through the FOCUS Validator and open the RFI with `member-cert@finops.org`.

---

## Confidence Summary

- **High:** Aethir meters compute in GPU-hours, prices per GPU per hour by GPU type, and distinguishes on-demand (Atlas) from reserved enterprise capacity. This is well documented across the pricing pages and product docs.
- **High:** fees are USD-denominated and settlement occurs on-chain in ATH; the dual-currency reality is real and maps to FOCUS via `BillingCurrency`/`PricingCurrency` plus custom columns.
- **Moderate:** the absence of a customer-facing FOCUS-style cost-and-usage export. Aethir publishes a protocol dashboard and enterprise invoicing but no documented per-charge tabular export was found; if a customer billing API exists behind the enterprise portal, several Deviation/Missing rows would move toward Present.
- **Moderate:** the exact tenant-identity fields and whether any sub-account or project hierarchy exists. No documentation confirmed a hierarchy, hence the SubAccount N/A calls.
- **Provisional:** field-level mappings are inferred from the billing model, not read from a published schema. This report is marked provisional on data quality for that reason. Resource-ID, SKU, and commitment mappings should be confirmed against Aethir's internal billing system.
- **Cache note:** FOCUS v1.2 feature levels were validated against the live FOCUS column library on July 1, 2026; the bundled reference (stamped 2026-06-23) matched, including the 57-column count and the v1.3 deprecation of Provider/Publisher.

---

## Sources

- Aethir Enterprise GPU Pricing: [enterprise.aethir.com/Pricing](https://enterprise.aethir.com/Pricing)
- Atlas Cloud GPU Pricing: [atlascloud.ai/pricing/gpu](https://www.atlascloud.ai/pricing/gpu)
- Aethir documentation (Cloud Host, Checker, operational requirements): [docs.aethir.com](https://docs.aethir.com/)
- Aethir ATH token use cases and settlement: [ecosystem.aethir.com](https://ecosystem.aethir.com/blog-posts/exploring-innovative-ath-token-use-cases-the-backbone-of-aethirs-gpu-cloud)
- Aethir GPU dashboard: [dashboard.aethir.com/protocol/overview](https://dashboard.aethir.com/protocol/overview)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
