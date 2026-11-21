# SAP & FOCUS: Data Generator Gap Analysis

*Analysis run: June 25, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** SAP  
**Prepared:** June 25, 2026  
**Source:** SAP BTP Metering and Aggregates API; SAP Invoice API  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 22 Present, 14 Deviation, 2 Missing Mandatory, 3 Missing Conditional, 1 Missing Recommended, 15 N/A

---

## Executive Summary

SAP presents two structurally different billing models under one provider umbrella. SAP BTP (Business Technology Platform) is consumption-based: per-metric usage data, quantity, and a published public price list that makes FOCUS enrichment feasible. SAP's enterprise SaaS products (S/4HANA Cloud, SuccessFactors, Ariba, Concur) use flat-fee or per-user subscription licensing with enterprise-negotiated pricing that is not programmatically accessible. FOCUS conformance is achievable for BTP usage with moderate enrichment work. The SaaS subscription model has structural gaps in PricingQuantity and PricingUnit that cannot be resolved without SAP exposing per-unit pricing metadata in a format it does not currently publish.

All 19 Mandatory columns that have source data are present or need shaping work. The 2 Missing Mandatory (PricingQuantity, PricingUnit) are structurally absent for flat subscription line items, not a data-shaping problem. The 14 Deviation columns cover cost enrichment, enum mapping, and tag parsing across both billing models.

**Recommendation:** Build the BTP-side transform first. BTP has per-metric data and public pricing, so the full 57-column dataset is achievable with enrichment. Address the enterprise SaaS subscription model separately, with the understanding that PricingQuantity and PricingUnit will be null for those line items pending SAP publishing per-unit pricing metadata.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

SAP exposes billing data through two primary channels depending on the product.

**SAP BTP Metering and Aggregates API** (`GET /metering/v1/aggregates`): The primary consumption source for BTP services. Returns monthly aggregates per service plan and metric. Key fields: `service_id`, `plan_id`, `plan_name`, `metric_key`, `quantity`, `cost`, `currency`, `start_date`, `end_date`. SAP also publishes a BTP Service Catalog and a public pricing page that lists per-unit rates for BTP services.

**SAP Invoice API / SAP Billing Portal**: Provides invoice-level data for enterprise subscription products. Fields vary by product line and contract structure. S/4HANA Cloud, SuccessFactors, and other SaaS products appear as line items on enterprise invoices, typically as flat-fee or per-user amounts. Unit pricing and consumption quantities are not part of the API-accessible billing record.

**Authentication:** SAP S-user credentials for the SAP Support Portal and invoice APIs; OAuth 2.0 / API keys for BTP APIs. Access to BTP Metering API requires BTP global account admin.

Characteristics that matter for FOCUS:

- **Dual billing models:** BTP consumption-based (per-metric) and SaaS subscription-based (flat or per-user) coexist within the same SAP customer account.
- **Enterprise pricing opacity:** SAP enterprise software pricing is entirely negotiated. No public list price API exists for S/4HANA Cloud, SuccessFactors, Ariba, or Concur. BTP published pricing is an exception.
- **Account hierarchy:** SAP Global Account contains Subaccounts (BTP); enterprise SaaS licensing is tied to a SAP Customer Number (S-number) rather than a hierarchical account structure.
- **Tagging:** BTP supports user-defined tags on BTP resources. SAP SaaS products (S/4HANA Cloud, SuccessFactors, etc.) do not expose tagging at the billing data level.
- **Regional data:** BTP data centers are region-specific (AWS-like regions: US East, EU West, etc.). Most SAP SaaS products are global and do not expose billing data at a regional grain.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven. Each column carries a feature level: Mandatory (must exist and be populated where applicable), Conditional (must exist; populated when the provider's model triggers the condition, otherwise null), or Recommended. A conformant dataset presents the full column set under FOCUS column IDs, populates every Mandatory column, satisfies Conditional columns where applicable, and uses the correct types and allowed values. These rules live in the FOCUS Requirements Model, which the FOCUS Validator checks against. Provider-specific columns are allowed when prefixed `x_`.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | SAP source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Invoice amount (BTP: `cost`; SaaS: flat line item amount) | Present |
| EffectiveCost | Mandatory | = BilledCost for flat subscriptions; BTP prepaid credits require amortization of credit purchases across usage periods | Deviation |
| ListCost | Mandatory | BTP: compute from published BTP price list × `quantity`; SaaS: no public list price available; requires supplementary data for enterprise products | Deviation |
| ContractedCost | Mandatory | Enterprise-negotiated discount rates not accessible via API; requires supplementary pricing data file per customer | Deviation |
| BillingAccountId | Mandatory | SAP Customer Number (S-number) for enterprise; BTP Global Account ID for platform services | Present |
| BillingAccountName | Mandatory | Company name from SAP contract | Present |
| BillingCurrency | Mandatory | Invoice currency (typically EUR for German contracts; USD for US; varies by region) | Present |
| BillingPeriodStart | Mandatory | Invoice period start date | Present |
| BillingPeriodEnd | Mandatory | Invoice period end date | Present |
| ChargePeriodStart | Mandatory | Service period start (typically = BillingPeriodStart for monthly invoicing) | Present |
| ChargePeriodEnd | Mandatory | Service period end (typically = BillingPeriodEnd) | Present |
| ChargeDescription | Mandatory | Line item description from invoice or BTP plan name + metric | Present |
| ChargeCategory | Mandatory | Derive: "Usage" for BTP consumption charges; "Purchase" for subscription activations and credits; "Credit" for promotional credits; "Tax" for VAT/GST lines | Deviation |
| ChargeClass | Mandatory (nullable) | null except for correction charges | Present |
| InvoiceIssuerName | Mandatory | "SAP SE" (invoices issued by the SAP legal entity in the contract) | Present |
| ProviderName | Mandatory (dep. v1.3) | "SAP" | Present |
| PublisherName | Mandatory (dep. v1.3) | "SAP" for SAP-built services; third-party publisher name for SAP Store marketplace items | Deviation |
| ServiceName | Mandatory | SAP product name: "SAP BTP", "SAP S/4HANA Cloud", "SAP SuccessFactors", "SAP Ariba", "SAP Concur" | Present |
| ServiceCategory | Mandatory | Map SAP product to FOCUS enum: BTP → "Platform"; S/4HANA Cloud → "Business Applications"; SuccessFactors → "Business Applications"; BTP AI Core → "AI and Machine Learning" | Deviation |
| PricingQuantity | Mandatory | **Not available** for flat subscription line items (no per-unit quantity exposed in invoice API); present for BTP consumption metrics (`quantity`) | Missing: Mandatory |
| PricingUnit | Mandatory | **Not available** for flat subscription line items; present for BTP consumption metrics (e.g., "CALLS", "GB-HOURS", "HOURS") | Missing: Mandatory |
| ConsumedQuantity | Conditional | BTP: gross consumption quantity before rateability adjustments; not available for SaaS flat subscriptions | Present |
| ConsumedUnit | Conditional | BTP: consumption unit (same as PricingUnit for most BTP metrics) | Present |
| ListUnitPrice | Conditional | BTP: derive from published BTP price list (public); SaaS: not publicly available; requires supplementary data | Deviation |
| ContractedUnitPrice | Conditional | Enterprise discount rates not in API; = ListUnitPrice for PAYG BTP accounts | Deviation |
| PricingCategory | Conditional | Derive: "Standard" for BTP PAYG and flat-rate subscriptions; "Committed" for BTP credit-based consumption | Deviation |
| ChargeFrequency | Conditional | Derive: "Usage-Based" for BTP per-metric charges; "Recurring" for monthly subscription licenses; "One-Time" for setup and activation fees | Deviation |
| BillingAccountType | Conditional | Derive from contract type (PAYG BTP, Subscription, Enterprise License) | Present |
| SubAccountId | Conditional | BTP Subaccount ID (UUID); not applicable for SaaS licensing which is account-level | Present |
| SubAccountName | Conditional | BTP Subaccount name; not applicable for SaaS licensing | Present |
| SubAccountType | Conditional | "Subaccount" for BTP; not applicable for SaaS | Present |
| ResourceId | Conditional | N/A: SAP SaaS products do not expose resource-level IDs in billing data; BTP does not expose service instance IDs at the billing aggregate level | N/A |
| ResourceName | Conditional | N/A | N/A |
| ResourceType | Conditional | N/A | N/A |
| SkuId | Conditional | `plan_id` for BTP services; SAP material number (MATNR) for enterprise licensing | Present |
| Tags | Conditional | BTP user tags available for BTP resources; SAP SaaS products do not expose tags in billing data; tag format is key-value pairs | Deviation |
| PricingCurrency | Conditional | = BillingCurrency (SAP invoices in a single currency per contract) | Present |
| PricingCurrencyListUnitPrice | Conditional | = ListUnitPrice; Deviation because ListUnitPrice itself requires BTP price list integration or supplementary data | Deviation |
| PricingCurrencyContractedUnitPrice | Conditional | = ContractedUnitPrice; Deviation because ContractedUnitPrice requires enterprise pricing data | Deviation |
| PricingCurrencyEffectiveCost | Conditional | = EffectiveCost; Deviation because EffectiveCost requires amortization logic for BTP credit accounts | Deviation |
| SkuMeter | Conditional | Not exposed in the billing API; `metric_key` exists in BTP metering but does not map to a FOCUS SkuMeter display name format | Missing: Conditional |
| SkuPriceId | Conditional | Pricing plan rate identifier not exposed in the billing API | Missing: Conditional |
| SkuPriceDetails | Conditional | Tier details not exposed in a FOCUS-conformant format | Missing: Conditional |
| RegionId | Conditional | N/A: BTP region codes exist (`us10`, `eu10`, etc.) but most enterprise SaaS products do not expose a billing region; treating as N/A for the overall SAP provider | N/A |
| RegionName | Conditional | N/A | N/A |
| CommitmentDiscountId | Conditional | N/A: SAP subscription licenses are not modeled as CommitmentDiscount; prepaid BTP credits are not a FOCUS CommitmentDiscount construct | N/A |
| CommitmentDiscountName | Conditional | N/A | N/A |
| CommitmentDiscountType | Conditional | N/A | N/A |
| CommitmentDiscountCategory | Conditional | N/A | N/A |
| CommitmentDiscountStatus | Conditional | N/A | N/A |
| CommitmentDiscountQuantity | Conditional | N/A | N/A |
| CommitmentDiscountUnit | Conditional | N/A | N/A |
| CapacityReservationId | Conditional | N/A: no SAP capacity reservation construct in the IaaS/FOCUS sense | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | SAP invoice number from invoice API | Present |
| ServiceSubcategory | Recommended | No native field; requires mapping from SAP product identifier to FOCUS subcategory labels | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: SAP products do not expose availability zone at the billing level | N/A |

**Tally:** 22 Present, 14 Deviation, 2 Missing Mandatory, 3 Missing Conditional, 1 Missing Recommended, 15 N/A

### 1.4 What Is Solved, and What Remains

**Solved**

The invoicing and account framework is complete. SAP invoices expose a stable set of fields covering the billing-period, account identification, currency, service naming, and line-item description. For BTP, per-metric consumption data (quantity, cost, plan) gives a strong foundation for the 22 Present columns. BTP subaccount structure maps directly to FOCUS SubAccountId and SubAccountName. BTP user tags provide the basis for the Tags column.

**Remaining**

Two structural gaps require SAP to publish data it does not currently expose:

*PricingQuantity and PricingUnit for subscription line items.* Flat-fee SAP SaaS invoices do not include the unit of measure or quantity for the service. A per-user annual S/4HANA Cloud license appears as a lump-sum line item. FOCUS requires a non-null PricingQuantity and PricingUnit for every charge row. Until SAP exposes per-unit quantity in the invoice API, this is Missing: Mandatory for all subscription-based charges.

*Cost enrichment for enterprise accounts.* ListCost (from the published BTP price list) and ContractedCost (enterprise negotiated) are derivable for BTP; for enterprise SaaS, they require supplementary pricing data that SAP does not expose programmatically. The 14 Deviation columns cover the work of computing these from available sources, building enum mapping tables (ChargeCategory, ServiceCategory, ChargeFrequency), and implementing EffectiveCost amortization for BTP credit accounts.

### 1.5 Deviations to Fix

**EffectiveCost for BTP credit accounts**  
BTP customers can purchase prepaid "Cloud Credits" that are drawn down by consumption. FOCUS requires EffectiveCost to reflect amortized commitment cost, not the cash-flow amount. For usage charges covered by prepaid credits, EffectiveCost should be proportionally allocated from the credit purchase price. For PAYG BTP and flat subscription accounts, EffectiveCost = BilledCost.

**ListCost and ContractedCost**  
For BTP: ListCost = published BTP unit rate × PricingQuantity. ContractedCost = ListCost for PAYG accounts; enterprise discount rates require a supplementary data file. For enterprise SaaS: both require out-of-band pricing data. Without a programmatic source, these columns will be null for SaaS subscription line items (a Mandatory-column gap that remains after the Deviation fix).

**ChargeCategory**  
SAP does not emit a FOCUS-aligned charge type. Mapping rule: BTP usage charges → "Usage"; subscription activation or renewal → "Purchase"; credits and promotional discounts → "Credit"; VAT/GST invoice lines → "Tax". Build this mapping from invoice line-item type codes.

**ServiceCategory**  
SAP's product catalog must be mapped to the FOCUS ServiceCategory enum. Priority mappings: SAP BTP (general PaaS) → "Platform"; SAP AI Core, SAP AI Launchpad → "AI and Machine Learning"; SAP S/4HANA Cloud, SuccessFactors, Ariba, Concur → "Business Applications"; SAP Integration Suite → "Integration"; SAP HANA Cloud → "Databases". This is a one-time build that auto-applies for all subsequent charges.

**Tags**  
BTP user tags are available for BTP resources but are not present on SaaS product billing data. Apply tags only to BTP charge rows. Decide whether to include both user tags and entitlement tags, and document the decision.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build the transform to the FOCUS v1.4 column set (released June 4, 2026); certify at v1.2, which is the current FinOps Foundation certification baseline. Note that ProviderName and PublisherName are deprecated in v1.3 and removed in v1.4; the v1.4-aligned transform should omit them (though they can be retained as `x_` prefixed provider-specific columns).

### 2.2 What Certification Requires

Certification for data generators runs through the FinOps Foundation. Contact `member-cert@finops.org` for the RFI. Deliverables: a structurally conformant dataset under FOCUS column IDs, public sample data that passes the FOCUS Validator, a documented native-to-FOCUS mapping, and a Conformance Gap Report (this document is its seed). FinOps Foundation membership is required for certification. Note that the Missing: Mandatory gap in PricingQuantity and PricingUnit for subscription line items will need to be addressed or disclosed as a known gap during the certification process.

### 2.3 Phased Roadmap

**Phase 0: Scope and separate the billing streams**  
Identify whether BTP Metering API and the enterprise invoice API will be combined into a single FOCUS dataset or maintained as separate data generators. Separate data models require separate transforms and separate gap tracking. Confirm the account hierarchy mapping: S-number (enterprise) vs. BTP Global Account (platform).

**Phase 1: BTP core transform**  
Build the BTP-side transform. Emit FOCUS column IDs. Map BilledCost, ChargePeriod, BillingAccount, SubAccount (BTP subaccount), ServiceName, SkuId, PricingQuantity, PricingUnit, ConsumedQuantity, ConsumedUnit, InvoiceId. Add ChargeClass, InvoiceIssuerName, ProviderName (constant "SAP"). This delivers conformant output for the 22 Present columns on BTP usage data.

**Phase 2: BTP cost enrichment**  
Integrate the SAP BTP public price list to compute ListCost and ListUnitPrice per metric. Build ChargeCategory, ServiceCategory, ChargeFrequency, and PublisherName mapping tables. Implement EffectiveCost amortization for BTP credit accounts. Add Tags from BTP resource tag metadata. Add PricingCategory derivation. This makes BTP data largely conformant.

**Phase 3: SaaS subscription transform**  
Build the enterprise SaaS invoice transform. Address the structural PricingQuantity/PricingUnit gap: either push SAP to expose per-user/per-unit quantity in the invoice API, or populate null with a documented disclosure for those rows. Apply the same ChargeCategory, ServiceCategory, and other enum mappings. Derive EffectiveCost = BilledCost for flat subscriptions.

**Phase 4: Certify**  
Adopt the v1.4 column set (drop ProviderName, PublisherName). Add ServiceSubcategory mapping. Validate sample data with the FOCUS Validator. Submit for FinOps Certified FOCUS v1.2 Conformant designation.

### 2.4 FOCUS Use Cases SAP Customers Unlock

**After Phase 1 (BTP core transform):**
- Cost by BTP service and plan within each BTP subaccount.
- BTP consumption analysis: quantity vs. cost per metric.
- Invoice-level reporting with InvoiceId linkage.

**After Phase 2 (cost enrichment, BTP):**
- BTP list-versus-billed cost comparison to identify enterprise discounts.
- BTP ChargeCategory filtering to separate usage from credit purchases.
- ServiceCategory-based reporting to allocate BTP platform cost alongside other providers.

**After Phase 3 (enterprise SaaS):**
- Unified SAP cost reporting across BTP and enterprise SaaS under a single provider.
- Multi-product SAP cost allocation by business unit using subaccount or customer dimension.

**Out of scope for SAP's model:**  
Resource-level cost allocation (ResourceId N/A for SaaS). Availability-zone granularity. CommitmentDiscount use cases (SAP subscriptions are not modeled as FOCUS CommitmentDiscount). Capacity reservation analysis.

---

## Part 3: Immediate Next Steps

1. Confirm which billing streams (BTP Metering API, enterprise invoice API, or both) will be included in the SAP FOCUS data generator, and whether they will be a single combined dataset or two separate generators.
2. Establish access to the BTP Metering and Aggregates API and retrieve a sample monthly dataset. Confirm available fields and the account hierarchy (Global Account → Subaccount).
3. Download the current SAP BTP published price list and map each `metric_key` to a ListUnitPrice. Build the computation for ListCost = ListUnitPrice × PricingQuantity per metric.
4. Build the ChargeCategory, ServiceCategory, and ChargeFrequency mapping tables from SAP product and charge-type identifiers.
5. Engage SAP product management or the SAP S/4HANA Cloud billing team to determine whether per-unit quantity data (PricingQuantity, PricingUnit) can be added to the enterprise invoice API. Without this, the Missing: Mandatory gap on subscription line items is unresolvable.
6. Run a BTP-side sample through the FOCUS Validator and iterate to a clean pass. Open the RFI with `member-cert@finops.org`.

---

## Confidence Summary

- **High:** BTP Metering and Aggregates API exposes per-metric `quantity`, `cost`, `plan_id`, `service_id`, `currency`, and billing dates. The 22 Present columns are grounded in documented, stable API fields.
- **High:** BTP subaccount structure (Global Account → Subaccounts) maps cleanly to FOCUS BillingAccount and SubAccount. SubAccountId and SubAccountName are available from the BTP account management API.
- **Moderate:** ListCost derivation from the SAP BTP public price list. The BTP price list is publicly accessible but is a structured document rather than a machine-readable API; the derivation requires parsing and maintenance as SAP updates pricing.
- **Moderate:** ChargeCategory and ServiceCategory mapping tables. SAP's product catalog is large and changes with each release. A comprehensive mapping requires reviewing the full SAP service catalog and maintaining it over time.
- **Low:** Enterprise SaaS subscription PricingQuantity and PricingUnit. There is no indication from SAP's public APIs or documentation that invoice-level per-unit quantity data will be available in the near term. This gap is structurally imposed by SAP's invoice format.
- **Unknown:** ListCost and ContractedCost for enterprise SaaS. The availability of negotiated rate data depends on SAP providing a customer-specific pricing API or data export, which does not currently exist in the public SAP API catalog.

---

## Sources

- SAP BTP Metering and Aggregates API: [api.sap.com/api/Metering](https://api.sap.com/api/Metering)
- SAP BTP Published Pricing: [SAP Store BTP Pricing](https://www.sap.com/products/technology-platform/pricing.html)
- SAP BTP Account Hierarchy: [SAP BTP Documentation](https://help.sap.com/docs/btp)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
