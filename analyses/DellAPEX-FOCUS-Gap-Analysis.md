# Dell APEX & FOCUS: Data Generator Gap Analysis

*Analysis run: July 6, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** Dell Technologies (Dell APEX)  
**Prepared:** July 6, 2026  
**Source:** Dell APEX Console / Dell Premier (Software & Subscriptions > Usage & Reporting, Subscription Invoices); public Dell APEX subscription documentation  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Status:** Not a listed FOCUS data provider on focus.finops.org/get-started. This is a readiness assessment, not a conformance result.  
**Tally:** 17 Present, 12 Deviation, 3 Missing Mandatory, 7 Missing Conditional, 2 Missing Recommended, 16 N/A

---

## Executive Summary

Dell APEX is Dell Technologies' as-a-service infrastructure portfolio: customers commit a base capacity (typically priced on a $/GB basis), Dell deploys the hardware on-premises or in a colocation site with a buffer above the baseline, meters actual consumption at roughly five-minute intervals, and bills monthly for base plus on-demand usage above the commitment. The billing surface is the APEX Console within Dell Premier, which exposes Usage & Reporting views (Schedule Summary, Daily Schedule History, Monthly Schedule History, Product Summary) and Subscription Invoices. This gives Dell APEX the structural bones of a metered dataset: a measured quantity per schedule (TotalGiB, CommitGiB, ConsumedGiB), a client and product hierarchy, daily consumption history, and a clean monthly invoice.

The gap to FOCUS is that the exposed data is a capacity-utilization report, not a cost-and-usage ledger with FOCUS column IDs. Three Mandatory columns are substantive gaps: ListCost and ContractedCost require the enterprise-negotiated rate card, which the console does not expose, and EffectiveCost requires reconciling committed-tier and on-demand charges from that rate. The remaining Mandatory columns have source data and are Deviations (derivation or reshaping) rather than absences. Sixteen columns are N/A: the entire CommitmentDiscount family (APEX's base commitment is a pricing tier, not a per-resource discount), CapacityReservation, AvailabilityZone, and the pricing-currency sub-family that follows from the missing unit prices. Granularity is mixed: daily consumption exists in the console, but the billed record is monthly.

**Recommendation:** Treat the APEX Console Daily Schedule History export as the source event stream and build a metered-consumption transform first, mapping the GiB meters to PricingQuantity and PricingUnit, the client and product hierarchy to BillingAccount and SubAccount, and the invoice to the cost columns. Add the negotiated rate card as a supplementary data step to populate ListCost, ContractedCost, and EffectiveCost. Structural conformance is reachable; the binding constraint is programmatic access to pricing and a stable resource identity.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

Dell APEX exposes billing and usage through two console surfaces inside Dell Premier, reached at Account > Software & Subscriptions:

**Usage & Reporting.** Four views:
- **Schedule Summary** (default): Client name, Billing Period, Product, Device, Schedule, Commit %, Consumed %, TotalGiB, ConsumedGiB.
- **Daily Schedule History**: per-schedule daily TotalGiB, CommitGiB, ConsumedGiB, with 60 days of history and a 30-day forecast. The data table is exportable (More Options > Export Data).
- **Monthly Schedule History**: the same meters rolled to the month, six months back and three months forward.
- **Product Summary**: consumed capacity by product across correlated schedules.

**Subscription Invoices.** Monthly invoices and, for APEX Flex On Demand, a pre-invoice usage report that the customer has 15 days to review. Invoices, credit memos, and pre-invoice usage reports are downloadable as PDF documents. Billing information is tied to the Bill To Entity; channel-partner purchases route billing through the partner.

Key characteristics for FOCUS:
- **Metered capacity model:** APEX meters storage or memory capacity (GiB) on average every five minutes, averages per day, and bills monthly. The consumption meter maps to PricingQuantity and PricingUnit.
- **Commitment as a pricing tier:** the customer commits a base capacity at a $/GB rate. The same rate applies to base and to on-demand usage above the commitment. Billing is capped at 85% of total installed capacity. This is a tier, not a per-resource commitment discount.
- **Enterprise-negotiated pricing:** the $/GB rate is contract-specific and is not exposed as a machine-readable rate card in the console. List and contracted unit prices require supplementary data.
- **Account hierarchy:** the Bill To Entity is the billing account anchor; Client, Product, Device, and Schedule provide a sub-account and resource hierarchy.
- **Physical deployment:** APEX systems are installed at customer data centers or Dell-managed colocation sites, which map to Region rather than cloud Region/AvailabilityZone.
- **No native tagging or FOCUS-shaped export:** the console offers a tabular data export, not a cost-and-usage feed under FOCUS column IDs, and no customer-facing tag construct is documented.

The billing docs are thin on record-level field definitions. Field names below are drawn from the documented console views; anything not directly attested is marked provisional in the Confidence Summary.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven. Each column carries a feature level: Mandatory (must exist and be populated where applicable), Conditional (must exist; populated when the provider's model triggers the condition, otherwise null), or Recommended. A conformant dataset presents the full column set under FOCUS column IDs, populates every Mandatory column, satisfies Conditional columns where applicable, and uses the correct types and allowed values. Feature levels below were verified against the FOCUS v1.2 specification, not recalled from memory.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | Dell APEX source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Monthly invoice amount per schedule / line item | Deviation |
| EffectiveCost | Mandatory | Requires committed-tier plus on-demand reconciliation from the negotiated $/GB rate; not directly exposed | Missing: Mandatory |
| ListCost | Mandatory | List (MSRP) $/GB rate not exposed in the console; requires rate card | Missing: Mandatory |
| ContractedCost | Mandatory | Negotiated $/GB rate not exposed in the console; requires rate card | Missing: Mandatory |
| BillingAccountId | Mandatory | Bill To Entity identifier | Deviation |
| BillingAccountName | Mandatory | Client / Bill To Entity name | Present |
| BillingCurrency | Mandatory | Invoice currency (contract currency) | Deviation |
| BillingPeriodStart | Mandatory | Billing Period (monthly) start | Present |
| BillingPeriodEnd | Mandatory | Billing Period (monthly) end | Present |
| ChargePeriodStart | Mandatory | Daily Schedule History date (day-level) or billing period start | Deviation |
| ChargePeriodEnd | Mandatory | Daily Schedule History date + 1 day, or billing period end | Deviation |
| ChargeDescription | Mandatory | Product + Schedule label (e.g., "APEX Data Storage Services - Block") | Deviation |
| ChargeCategory | Mandatory | Derive: "Usage" for metered consumption; "Credit" for credit memos; "Adjustment" for corrections | Deviation |
| ChargeClass | Mandatory (nullable) | null except for correction / credit-memo lines | Present |
| InvoiceIssuerName | Mandatory | "Dell Technologies" (or channel partner for partner-billed subscriptions) | Present |
| ProviderName | Mandatory (dep. v1.3) | "Dell APEX" | Present |
| PublisherName | Mandatory (dep. v1.3) | "Dell Technologies" | Present |
| ServiceName | Mandatory | APEX product name (e.g., "APEX Data Storage Services", "APEX Compute", "APEX Flex On Demand") | Present |
| ServiceCategory | Mandatory | Map APEX product to FOCUS enum: storage products -> "Storage"; compute -> "Compute" | Deviation |
| PricingQuantity | Mandatory | ConsumedGiB per schedule per day | Deviation |
| PricingUnit | Mandatory | "GiB" (or "GiB-Month" / "GiB-Day" once normalized to the rate basis) | Deviation |
| ConsumedQuantity | Conditional | ConsumedGiB (measured consumption) | Present |
| ConsumedUnit | Conditional | "GiB" | Present |
| ListUnitPrice | Conditional | List $/GB rate; not exposed in the console | Missing: Conditional |
| ContractedUnitPrice | Conditional | Negotiated $/GB rate; not exposed in the console | Missing: Conditional |
| PricingCategory | Conditional | Derive: "Committed" for usage within the base commitment; "Standard" for on-demand usage above it | Deviation |
| ChargeFrequency | Recommended | "Usage-Based" for metered consumption; "Recurring" for flat subscription fees | Deviation |
| BillingAccountType | Conditional | Derive from the Bill To Entity agreement type (e.g., "Enterprise") | Deviation |
| SubAccountId | Conditional | Client / Product / Schedule identifier below the Bill To Entity | Deviation |
| SubAccountName | Conditional | Client or Product name | Deviation |
| SubAccountType | Conditional | "Schedule" or "Product" | Deviation |
| ResourceId | Conditional | Device or Schedule identifier | Deviation |
| ResourceName | Conditional | Device name | Present |
| ResourceType | Conditional | APEX system / device type | Present |
| SkuId | Conditional | APEX product SKU or offer code | Missing: Conditional |
| Tags | Conditional | No native customer tag construct documented in the console | Missing: Conditional |
| PricingCurrency | Conditional | = BillingCurrency (contract currency) | Present |
| PricingCurrencyListUnitPrice | Conditional | Follows ListUnitPrice; not exposed | Missing: Conditional |
| PricingCurrencyContractedUnitPrice | Conditional | Follows ContractedUnitPrice; not exposed | Missing: Conditional |
| PricingCurrencyEffectiveCost | Conditional | Follows EffectiveCost; requires rate reconciliation | Missing: Conditional |
| SkuMeter | Conditional | Meter concept exists (GiB) but no FOCUS SkuMeter display value | Missing: Conditional |
| SkuPriceId | Conditional | Rate-card price identifier not exposed | N/A |
| SkuPriceDetails | Conditional | Tiered / committed-vs-overage pricing detail not exposed | N/A |
| RegionId | Conditional | Deployment site / data-center location code | Deviation |
| RegionName | Conditional | Site display name (customer site or Dell colocation) | Deviation |
| CommitmentDiscountId | Conditional | N/A: base commitment is a pricing tier, not a per-resource commitment discount | N/A |
| CommitmentDiscountName | Conditional | N/A | N/A |
| CommitmentDiscountType | Conditional | N/A | N/A |
| CommitmentDiscountCategory | Conditional | N/A | N/A |
| CommitmentDiscountStatus | Conditional | N/A | N/A |
| CommitmentDiscountQuantity | Conditional | N/A | N/A |
| CommitmentDiscountUnit | Conditional | N/A | N/A |
| CapacityReservationId | Conditional | N/A: on-premises installed capacity is not a FOCUS capacity reservation | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | Invoice number from Subscription Invoices | Present |
| ServiceSubcategory | Recommended | No native field; requires mapping from APEX product to subcategory | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: on-premises / colocation deployment has no cloud availability zone | N/A |

**Tally:** 17 Present, 12 Deviation, 3 Missing Mandatory, 7 Missing Conditional, 2 Missing Recommended, 16 N/A

### 1.4 What Is Solved, and What Remains

**Solved**

The metered model gives Dell APEX a measured quantity for every schedule: ConsumedGiB feeds ConsumedQuantity and PricingQuantity, and the unit is a clean GiB. The Bill To Entity anchors the billing account, and the Client / Product / Device / Schedule hierarchy supplies sub-account and resource identity. The monthly invoice supplies InvoiceId and the billing period. Daily Schedule History provides day-level consumption, which supports a sub-monthly ChargePeriod. InvoiceIssuerName, ServiceName, ChargeClass, and the consumed-quantity family have direct source data.

**Remaining (substantive)**

Three Mandatory columns are genuine data gaps rather than reshaping work. ListCost and ContractedCost depend on the enterprise-negotiated $/GB rate card, which the console does not expose, so both require a supplementary pricing data source. EffectiveCost is not a copy of any exposed field: APEX bills base plus on-demand at a contract rate with an 85% cap, so producing an amortized effective cost per usage line means reconciling the invoice total back to the metered consumption using that rate. These three drive the cost family and the pricing-currency sub-family that follows from them.

**Remaining (trivial)**

Most Mandatory columns marked Deviation are reshaping, not missing data: BilledCost from the invoice line, ChargePeriod from the daily date, ChargeCategory and ServiceCategory from lookup mappings, PricingQuantity and PricingUnit from ConsumedGiB. These are plumbing once the rate reconciliation is in place. The list-cost trap applies here: because credit memos and enterprise-negotiated rates exist and are applied at invoice time, the cost columns are treated as substantive, not as a trivial copy of a single list figure.

### 1.5 Deviations to Fix

**BilledCost**  
Present as the monthly invoice amount but not published under a FOCUS column ID at the usage-line grain. Allocate the invoiced amount to schedule / day lines.

**ChargePeriodStart and ChargePeriodEnd**  
Daily Schedule History carries day-level dates; emit inclusive-start, exclusive-end 24-hour periods. For invoice-only lines, use the monthly billing period.

**ChargeCategory and ServiceCategory**  
Derive ChargeCategory from line type (metered -> "Usage", credit memo -> "Credit", correction -> "Adjustment"). Map APEX products to the ServiceCategory enum (storage -> "Storage", compute -> "Compute").

**PricingQuantity and PricingUnit**  
Use ConsumedGiB and a GiB-based unit normalized to the rate basis (for example GiB-Month if the $/GB rate is monthly). Confirm the rate basis so the quantity matches the priced unit rather than the raw meter.

**SubAccount and Resource families**  
Assign the Client / Product / Schedule hierarchy to SubAccountId/Name/Type and the Device / Schedule identifier to ResourceId. Define a stable identifier convention, since the console surfaces display names more consistently than durable IDs.

**RegionId and RegionName**  
Map the deployment site (customer data center or Dell colocation) to Region. There is no availability-zone concept.

**BillingCurrency and PricingCurrency**  
Emit the contract currency as an ISO 4217 code.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (June 4, 2026); baseline the analysis at v1.2, the current certification version. ProviderName and PublisherName are deprecated in v1.3 and removed in v1.4, so treat them as transitional. Because the APEX cost columns depend on reconciliation, the v1.4 Invoice Detail and billing-period datasets are a natural fit and worth designing toward.

### 2.2 What Certification Requires

Dell APEX is not currently a listed FOCUS data provider, so this is a readiness assessment. To pursue conformance, contact `member-cert@finops.org` for the RFI. Certification deliverables are a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report (this analysis seeds it). Membership is required for certification, though contributing to the spec is open and free. The open-source tooling applies: the FOCUS Validator (checks data against the Requirements Model), the FOCUS Converter (native to FOCUS), and the FOCUS Requirements Model.

### 2.3 Phased Roadmap

**Phase 0:** Confirm the source of record. Decide whether the FOCUS dataset is generated from the Daily Schedule History export or from an upstream billing system, and pull a sample month across storage and compute schedules. Validate field availability for schedule IDs, device IDs, and dates.

**Phase 1: Core metered consumption transform.** Map BillingAccount (Bill To Entity), SubAccount (Client / Product / Schedule), Resource (Device), Region (site), ServiceName, ChargePeriod (daily), PricingQuantity/Unit and ConsumedQuantity/Unit (ConsumedGiB), InvoiceId, InvoiceIssuerName, ChargeClass. Derive ChargeCategory, ServiceCategory, ChargeFrequency, PricingCategory. Delivers conformant structure for the present and reshaping columns.

**Phase 2: Cost enrichment.** Integrate the negotiated $/GB rate card for ListCost, ContractedCost, ListUnitPrice, and ContractedUnitPrice. Reconcile the invoice total to metered lines to produce EffectiveCost and BilledCost at the usage grain, honoring the base-vs-on-demand tier and the 85% cap. Populate the pricing-currency sub-family.

**Phase 3: Round out Conditional and Recommended.** Add SkuId and SkuMeter from the APEX product catalog, ServiceSubcategory mapping, and a tag mechanism if APEX introduces customer tagging.

**Phase 4: Mature and certify.** Drop ProviderName and PublisherName (v1.4), adopt the Invoice Detail dataset for reconciliation, validate with the FOCUS Validator, and open the RFI.

### 2.4 FOCUS Use Cases Unlocked

**After Phase 1:** Analyze service costs by service name; Analyze service costs by subaccount (by Client / Product); Analyze service costs by region (by deployment site); Analyze tag coverage (once tagging exists); resource-level consumption reporting from ConsumedGiB.

**After Phase 2:** Compare billed cost per subaccount to budget; Calculate unit economics ($/GiB); list-vs-contracted-vs-billed comparison to verify the negotiated rate; committed-vs-on-demand consumption cost via PricingCategory; invoice reconciliation and Analyze credit memos.

**Out of scope:** the CommitmentDiscount use cases (APEX's base commitment is a pricing tier, not a FOCUS commitment discount); capacity-reservation analysis; availability-zone cost distribution.

---

## Part 3: Immediate Next Steps

1. Decide the source of record for the FOCUS dataset: the APEX Console Daily Schedule History export or an upstream billing system. Pull one sample month across storage and compute schedules.
2. Obtain the negotiated $/GB rate card in machine-readable form and design the pricing join for ListCost, ContractedCost, and the unit-price columns.
3. Specify the EffectiveCost reconciliation: allocate the monthly invoice total to metered daily lines using the base-vs-on-demand rate and the 85% cap.
4. Build the ChargeCategory, ServiceCategory, and ServiceSubcategory mapping tables from the APEX product catalog, and define stable SubAccount and Resource identifiers.
5. Run a Phase 1 sample through the FOCUS Validator and, if pursuing conformance, open the RFI with `member-cert@finops.org`.

---

## Confidence Summary

- **High:** Dell APEX is a metered as-a-service model with a base commitment, buffer, ~5-minute metering, and monthly billing, exposed through the APEX Console Usage & Reporting views and Subscription Invoices. Documented console fields (TotalGiB, CommitGiB, ConsumedGiB, Client, Product, Device, Schedule, Billing Period) are attested by Dell's public subscription documentation.
- **High:** The cost columns (ListCost, ContractedCost, EffectiveCost) are substantive gaps. The negotiated $/GB rate is not exposed in the console, and effective cost requires reconciling the invoice to metered lines.
- **Moderate:** SubAccount and Resource mapping. The Client / Product / Device / Schedule hierarchy is documented, but which level is the durable identifier versus a display name is not fully specified in public docs.
- **Moderate:** ServiceCategory coverage across the full APEX portfolio (Data Storage Services, Compute, Flex On Demand, Cloud Platforms). A complete mapping needs the current product catalog.
- **Low / provisional:** Record-level field names and types for a machine-readable export. The console documents tabular exports and PDF invoices, not a FOCUS-style feed or a public billing API, so exact field names and the presence of a stable resource ID and tag construct are provisional and should be confirmed against an actual export.
- **Note:** Feature levels were verified against the live FOCUS specification via the FOCUS MCP on July 6, 2026; the bundled v1.2 table matched (57 columns, Provider/Publisher deprecated v1.3 and removed v1.4). Dell APEX is not a listed FOCUS data provider; this is a readiness assessment, not a conformance result.

---

## Sources

- Dell APEX Subscriptions, Usage and Reporting: [dell.com/support](https://www.dell.com/support/manuals/en-us/apex-custom-solutions/apex_subscript_user_guide_pub/usage-and-reporting?guid=guid-acf5306c-d1b5-4e39-a8ce-20dd20078f7d&lang=en-us)
- Dell APEX Subscriptions, Subscription Invoices: [dell.com/support](https://www.dell.com/support/manuals/en-us/apex-custom-solutions/apex_subscript_user_guide_pub/subscription-invoices?guid=guid-2c67bda8-8ae2-4e16-829c-e5d032353aa4&lang=en-us)
- Dell APEX Infrastructure / Subscriptions overview: [dell.com/en-us/dt/apex/subscriptions.htm](https://www.dell.com/en-us/dt/apex/subscriptions.htm)
- Dell APEX Flex On Demand (metered pay-per-use): [dell.com](https://www.dell.com/en-us/dt/payment-solutions/flexible-consumption/flex-on-demand.htm)
- Dell APEX subscription solution brief (PDF): [delltechnologies.com](https://www.delltechnologies.com/asset/en-th/solutions/apex/briefs-summaries/dell-apex-subscription-solution-brief.pdf)
- FOCUS Specification v1.2: [focus.finops.org/focus-specification/v1-2/](https://focus.finops.org/focus-specification/v1-2/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
