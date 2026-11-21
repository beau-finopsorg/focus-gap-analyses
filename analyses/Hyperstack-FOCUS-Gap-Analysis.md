# Hyperstack (NexGen Cloud) and FOCUS: Conformance Gap and Adoption Roadmap

*Analysis run: June 30, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

Prepared: 2026-06-30
Provider and product in scope: Hyperstack, the GPU cloud operated by NexGen Cloud.
Source analyzed: Hyperstack public documentation (Accounts, Billing Policies, and Usage Monitoring; Contracts; Organization), the Infrahub API reference (billing and pricebook resources, virtual machine labels), and public GPU pricing pages.
FOCUS baseline: v1.2 (current certification baseline). Build target: v1.4 (latest ratified, 2026-06-04).

Feature levels in this report were verified against the FOCUS Specification v1.2 via the FOCUS MCP server on 2026-06-30. The bundled reference table (SPEC_VERSIONS_AS_OF 2026-06-23) was confirmed current: v1.2 remains the certification baseline and no newer ratified version supersedes the v1.4 build target.

---

## Executive summary

Hyperstack exposes a real-time, per-minute billing model for GPU virtual machines, volumes, containers, and clusters, with an API that returns per-resource hourly pricing broken down by component (GPU, RAM, public IP) both before and after discounts. That component-level, post-discount pricing is a genuine strength: it means the effective-versus-list cost distinction already exists in the rate data. The blocking limitation is shape, not substance. Hyperstack publishes a live rate and balance view, not a FOCUS-style usage dataset of dated, per-resource charge records carrying cost, quantity, account, and service columns. There is no documented cost-and-usage export covering the full FOCUS column set.

The verdict: a billing system with the right economic primitives (per-component rates, pre- and post-discount pricing, organization-level accounts, resource labels) but no conformant cost-and-usage dataset to map. Producing one is a build, not a transform, though the inputs to build it largely exist.

Stat strip:
- 57 FOCUS columns (v1.2)
- 12 already present or trivially derivable from documented data
- 3 of 4 Mandatory cost-family gaps are substantive (BilledCost, EffectiveCost, ContractedCost reconciled to usage lines; ListCost derivable from published rates)
- 1 deviation to fix (Tags emitted as an array of bare string labels, not key-value pairs)

RAG readiness: Cost Partial, Granularity Partial, Allocation Partial, Coverage Gap, FOCUS shape Gap. Overall band: Not yet aligned (per public docs).

Recommendation: stand up a daily, per-resource cost-and-usage export keyed on the existing organization account and resource IDs, populate the cost family from the component rates already computed (the pre-discount component price feeds ListCost, the post-discount price feeds EffectiveCost and ContractedCost), convert labels to key-value Tags, and validate a sample against the FOCUS Validator. The economic data exists; the work is assembling it into dated charge records with FOCUS column IDs.

---

## Part 1: The conformance gap

### 1.1 The data source

Hyperstack bills through NexGen Cloud's Infrahub platform. The relevant surfaces are:

- Billing and pricing model: hourly rates for VMs and volumes, billed on a per-minute structure with the balance updating in real time. Billing starts when a resource is successfully created and stops on deletion. Three account types exist: Prepaid (default), Postpaid, and Premium Postpaid. On-demand, Reserved (longer commitments invoiced monthly), and Spot (interruptible, roughly twenty percent cheaper) pricing models are offered.
- Billing API (Infrahub): the "Retrieve Billing Rate for Resource" endpoint returns, for a given resource type (instance, volume, container, cluster) and ID, the resource status, the total hourly price, and a list of components (GPU, RAM, public IP) each with pricing before and after any discounts applied.
- Organization and accounts: resource costs and billing attach to the organization account. Resources created by any user in an organization bill to that organization, and payments from any member affect the shared credit balance.
- Payment History: a Billing-page tab listing Payment Date, Amount, Status, Stripe ID, and an internal NexGen Payment ID. This is a record of payments, not of usage line items.
- Resource labels: virtual machines carry an array of labels for organization and identification, updatable after deployment.
- Currency: pricing and balances are presented in US dollars; payments are processed through Stripe.

Key limitations for FOCUS purposes: the documented data is a live rate-and-balance view plus a payment ledger. There is no published cost-and-usage dataset of dated, per-resource charge records spanning the FOCUS schema (cost, quantity, unit, service, account, period columns on each line). The component pre- and post-discount prices are the raw material for the cost columns, but they are exposed as current rates, not as dated charges aggregated per resource per day.

### 1.2 How conformance is judged

FOCUS assigns each column a feature level: Mandatory (must be present and populated), Conditional (required when the provider's model triggers the condition), Recommended (encouraged), or Optional. Conformance is judged column by column against the Requirements Model, which encodes the MUST, SHOULD, and MAY rules and the allowed-value enums. A dataset conforms when every Mandatory column is present and correctly populated, every applicable Conditional column is present, and formats and enum values match the spec. Columns that do not apply to a provider's model are still expected to exist and be null.

### 1.3 Column-by-column status

Status legend: Present (emitted and aligned); Present, deviation to fix (emitted, wrong format or enum); Missing: Mandatory (required, absent, blocks conformance); Missing: Recommended (encouraged, absent); Missing: Conditional (required when the model triggers it, absent); N/A: null valid (does not apply, should exist and be null).

Feature levels verified against the FOCUS Specification v1.2.

| FOCUS Column | Level | In the source? | Status |
|---|---|---|---|
| AvailabilityZone | Recommended | No (regions, no documented zones) | N/A: null valid |
| BilledCost | Mandatory | No (rates and balance only) | Missing: Mandatory |
| BillingAccountId | Mandatory | Organization account | Present |
| BillingAccountName | Mandatory | Organization name | Present |
| BillingAccountType | Conditional | Prepaid / Postpaid / Premium Postpaid | Present, deviation to fix |
| BillingCurrency | Mandatory | USD (implied, not labeled) | Present, deviation to fix |
| BillingPeriodEnd | Mandatory | No FOCUS billing period in data | Missing: Mandatory |
| BillingPeriodStart | Mandatory | No FOCUS billing period in data | Missing: Mandatory |
| CapacityReservationId | Conditional | No capacity-reservation construct documented | N/A: null valid |
| CapacityReservationStatus | Conditional | No capacity-reservation construct documented | N/A: null valid |
| ChargeCategory | Mandatory | No (no charge records) | Missing: Mandatory |
| ChargeClass | Mandatory | No (nullable, corrections only) | Missing: Mandatory |
| ChargeDescription | Mandatory | No charge records | Missing: Mandatory |
| ChargeFrequency | Recommended | Implied by model (Usage-Based / Recurring) | Missing: Recommended |
| ChargePeriodEnd | Mandatory | Per-minute internally, not in a charge record | Missing: Mandatory |
| ChargePeriodStart | Mandatory | Per-minute internally, not in a charge record | Missing: Mandatory |
| CommitmentDiscountCategory | Conditional | Reserved commitments exist | Missing: Conditional |
| CommitmentDiscountId | Conditional | Reserved commitments exist | Missing: Conditional |
| CommitmentDiscountName | Conditional | Reserved commitments exist | Missing: Conditional |
| CommitmentDiscountQuantity | Conditional | Reserved commitments exist | Missing: Conditional |
| CommitmentDiscountStatus | Conditional | Reserved commitments exist | Missing: Conditional |
| CommitmentDiscountType | Conditional | Reserved commitments exist | Missing: Conditional |
| CommitmentDiscountUnit | Conditional | Reserved commitments exist | Missing: Conditional |
| ConsumedQuantity | Conditional | Runtime is metered per minute | Missing: Conditional |
| ConsumedUnit | Conditional | Derivable (hours) | Missing: Conditional |
| ContractedCost | Mandatory | No (post-discount rate exists, not as cost) | Missing: Mandatory |
| ContractedUnitPrice | Conditional | Post-discount component price | Present, deviation to fix |
| EffectiveCost | Mandatory | No (post-discount rate exists, not as cost) | Missing: Mandatory |
| InvoiceId | Recommended | Postpaid invoices; not in usage data | Missing: Recommended |
| InvoiceIssuerName | Mandatory | NexGen Cloud / Hyperstack (constant) | Present |
| ListCost | Mandatory | No (pre-discount rate exists, not as cost) | Missing: Mandatory |
| ListUnitPrice | Conditional | Pre-discount component price | Present, deviation to fix |
| PricingCategory | Conditional | On-Demand / Reserved / Spot | Present, deviation to fix |
| PricingCurrency | Conditional | USD | Present, deviation to fix |
| PricingCurrencyContractedUnitPrice | Conditional | Post-discount price, USD | Missing: Conditional |
| PricingCurrencyEffectiveCost | Conditional | No (no cost record) | Missing: Conditional |
| PricingCurrencyListUnitPrice | Conditional | Pre-discount price, USD | Missing: Conditional |
| PricingQuantity | Mandatory | Derivable from runtime for flat-rate hourly SKUs | Missing: Mandatory |
| PricingUnit | Mandatory | Derivable (hours) | Missing: Mandatory |
| ProviderName | Mandatory | Hyperstack / NexGen Cloud (constant) | Present |
| PublisherName | Mandatory | Hyperstack / NexGen Cloud (constant) | Present |
| RegionId | Conditional | Region of resource | Present |
| RegionName | Conditional | Region of resource | Present |
| ResourceId | Conditional | Resource ID in billing API path | Present |
| ResourceName | Conditional | VM / volume name | Present |
| ResourceType | Conditional | instance / volume / container / cluster | Present, deviation to fix |
| ServiceCategory | Mandatory | Derivable (Compute / Storage) | Missing: Mandatory |
| ServiceName | Mandatory | Derivable (e.g. GPU VM, Volume) | Missing: Mandatory |
| ServiceSubcategory | Recommended | Derivable (GPU Compute) | Missing: Recommended |
| SkuId | Conditional | GPU / flavor identifier exists | Missing: Conditional |
| SkuMeter | Conditional | Component (GPU, RAM, public IP) | Missing: Conditional |
| SkuPriceDetails | Conditional | Per-component rate breakdown exists | Missing: Conditional |
| SkuPriceId | Conditional | Pricebook entry per resource | Missing: Conditional |
| SubAccountId | Conditional | No tier below organization documented | N/A: null valid |
| SubAccountName | Conditional | No tier below organization documented | N/A: null valid |
| SubAccountType | Conditional | No tier below organization documented | N/A: null valid |
| Tags | Conditional | VM labels (array of strings) | Present, deviation to fix |

Reading the tally: of 57 v1.2 columns, 9 are Present and conformant, 7 are Present with a deviation to fix, 13 are Missing: Mandatory, 3 are Missing: Recommended, 18 are Missing: Conditional, and 7 are N/A null-valid. The Present and Present-with-deviation columns (16 total) are mostly the resource-identity, account, provider, and rate fields the API and organization model already carry. The Missing-Mandatory count is high because there is no charge-record dataset at all: the cost, charge-period, charge-category, service, and pricing-quantity columns are absent not because the data cannot exist but because no FOCUS-shaped line item is published to carry them.

### 1.4 What's solved, and what remains

Solved or near-solved: the identity and account spine is in good shape. ProviderName, PublisherName, and InvoiceIssuerName are constants. BillingAccountId and BillingAccountName map to the organization account. ResourceId, ResourceName, RegionId, RegionName, ResourceType, BillingAccountType, and the on-demand/reserved/spot PricingCategory all exist in the API or organization model. ListUnitPrice and ContractedUnitPrice are directly available as the per-component pre- and post-discount prices.

Substantive gaps (real data that no documented source emits as a record):
- BilledCost, EffectiveCost, ContractedCost: Hyperstack exposes pre- and post-discount component rates, but not dated cost amounts per resource per period. EffectiveCost and ContractedCost would be the post-discount rate multiplied by metered runtime; BilledCost would reconcile to what the prepaid balance was actually drawn down (or what a postpaid invoice charged). Because discounts (Reserved, Spot) and the prepaid-balance mechanic apply outside any published usage line, producing these three is a reconciliation build, not a copy.
- ChargePeriodStart and ChargePeriodEnd: per-minute metering exists internally, but no charge record carries the dated interval. This must be emitted.
- ChargeCategory, ChargeDescription, ServiceCategory, ServiceName: there are no charge records to carry them, so each must be generated as part of building the dataset.

Trivial gaps (derivable from data already present, once a charge record exists):
- ListCost: the published pre-discount component rate times runtime, for flat-rate hourly SKUs.
- PricingQuantity and PricingUnit: runtime in hours for flat-rate hourly GPU and volume SKUs. Scope this to flat-rate SKUs; if any tiered or blended rate exists, PricingQuantity must be computed against the rate basis, not copied from runtime.
- ConsumedQuantity and ConsumedUnit: metered runtime and its unit.
- ChargeClass: nullable, populated only for corrections.
- ServiceSubcategory and ChargeFrequency: derivable Recommended columns.

The list-cost trap applies directly here. Hyperstack does have discounts (Reserved and Spot pricing) and a prepaid-balance drawdown, so ListCost, BilledCost, EffectiveCost, and ContractedCost are not a single repeated value. ListCost is derivable from the published list rate, but BilledCost and EffectiveCost require reconciling the post-discount rate and the balance mechanic back to each usage line. Treat the three post-discount cost columns as substantive.

### 1.5 Deviations to fix

These columns carry the right data in the wrong shape or position:
- Tags: VM labels are an array of bare strings. FOCUS requires key-value pairs. Convert label to a key-value structure.
- BillingCurrency and PricingCurrency: USD is implied by the pricing pages but not emitted as a labeled ISO 4217 field on a record. Emit "USD" explicitly.
- BillingAccountType: the Prepaid / Postpaid / Premium Postpaid values are a native vocabulary. FOCUS BillingAccountType expects a normalized value; map these to the FOCUS-allowed set.
- ResourceType: instance / volume / container / cluster are native type names; map to FOCUS-consistent resource type values.
- PricingCategory: On-Demand / Reserved / Spot map to the FOCUS PricingCategory enum (for example Standard, Committed, Dynamic); confirm the mapping against the spec enum.
- ListUnitPrice and ContractedUnitPrice: present as component rates but only in the live billing-rate response, not on a charge record. They need to land on the per-line dataset.

Done right already: constant provider and issuer identity, organization account identity, resource and region identity, and the existence of pre- and post-discount component pricing (the hard economic primitive most thin billing systems lack).

---

## Part 2: The path forward

### 2.1 Which FOCUS version to target

Baseline the build against v1.2, the current certification baseline, since that is what the "FinOps Certified FOCUS v1.2 Conformant" program checks today. Design the schema toward v1.4, the latest ratified version (2026-06-04), so the dataset does not need rework as certification advances. In practice this means dropping the v1.4-removed ProviderName and PublisherName from the long-term target while still populating them for a v1.2 submission, and planning for the v1.4 invoice-detail and billing-period datasets that suit Hyperstack's monthly postpaid invoicing. Confirm Validator support for the chosen version before submission; v1.3 is supported today and v1.4 support is expected later in 2026.

### 2.2 What certification requires

FOCUS conformance for data generators runs through the FinOps Foundation. The program is "FinOps Certified FOCUS v1.2 Conformant"; contact member-cert@finops.org for the RFI. Membership is required for certification, though contributing to the spec is open and free. The deliverables are a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report (this analysis is its seed). Open-source tooling supports the work: the FOCUS Validator checks data against the Requirements Model, the FOCUS Converter maps provider-native data to FOCUS, and the FOCUS Requirements Model encodes the MUST/SHOULD/MAY rules.

### 2.3 Phased roadmap

Phase 0, validate and scope: confirm the exact billing-API fields and the pricebook structure against a live account, confirm whether any tiered or blended rates exist (which would change the PricingQuantity treatment), and confirm the currency and the organization-account semantics. Run any existing sample through the FOCUS Validator to baseline.

Phase 1, build the charge-record dataset and close the Mandatory cost gaps: emit a daily, per-resource line item carrying ChargePeriodStart and ChargePeriodEnd, ResourceId, the organization BillingAccountId, and the cost family. Populate ListCost from the published list rate times runtime; populate EffectiveCost and ContractedCost from the post-discount component rate times runtime; reconcile BilledCost to the prepaid drawdown or postpaid invoice. Add the trivial Mandatory columns at the same time: PricingQuantity, PricingUnit, ChargeCategory, ChargeDescription, ServiceCategory, ServiceName, ChargeClass, and the BillingPeriod columns.

Phase 2, fix deviations: convert labels to key-value Tags, emit BillingCurrency and PricingCurrency as ISO 4217 USD, and map BillingAccountType, ResourceType, and PricingCategory to FOCUS enum values.

Phase 3, round out applicable Conditional and Recommended columns: ConsumedQuantity and ConsumedUnit, the SKU family (SkuId, SkuMeter, SkuPriceDetails, SkuPriceId) from the component breakdown, the pricing-currency cost columns, the commitment-discount family for Reserved purchases, and the Recommended ServiceSubcategory, ChargeFrequency, and InvoiceId.

Phase 4, mature toward v1.4 and certify: drop ProviderName and PublisherName from the forward schema, adopt the v1.4 invoice-detail and billing-period datasets for the monthly postpaid path, re-validate, and pursue certification.

### 2.4 FOCUS Use Cases unlocked

Unlocked once Phase 1 lands dated, per-resource, per-day cost records (Phases 0 to 1): cost reporting and trend analysis by resource and region, GPU spend tracking over time, chargeback and showback at the organization-account level, and budget tracking against actuals. Resource-level allocation works as soon as ResourceId and the cost columns coexist.

Unlocked after Phase 2 and 3 (Tags as key-value, SKU family populated): tag-based allocation and cost-driver analysis, rate and unit-cost analysis across on-demand versus reserved versus spot, and effective-rate reporting.

Out of scope for now: multi-tier sub-account allocation (no documented tier below the organization account) and capacity-reservation use cases (no capacity-reservation construct documented). Commitment-based use cases become applicable only after the commitment-discount family is populated for Reserved purchases.

---

## Part 3: Immediate next steps

1. Pull a live billing-API response and a pricebook entry for a running GPU VM to confirm exact field names, component structure, and currency labeling.
2. Confirm whether any Hyperstack SKU uses tiered or blended pricing, since that changes the PricingQuantity treatment from a runtime copy to a computed value.
3. Decide the certification target version (v1.2 to certify now, schema designed toward v1.4) and confirm Validator support.
4. Prototype a daily, per-resource charge record populating the cost family from the component pre- and post-discount rates, and run it through the FOCUS Validator.
5. Convert VM labels to key-value Tags and map the BillingAccountType, ResourceType, and PricingCategory native values to FOCUS enums.

---

## Confidence summary

- Billing model (per-minute, real-time balance, prepaid/postpaid, on-demand/reserved/spot): high confidence, stated directly in Hyperstack billing documentation.
- Component-level pre- and post-discount pricing via the billing API: high confidence, described in the Infrahub billing-rate endpoint documentation. The exact field names and JSON structure were not captured from a live response, so the mapping detail is moderate confidence.
- Absence of a FOCUS-style cost-and-usage export: moderate to high confidence. No such export is documented publicly; it is possible an unlisted or account-gated export exists. Confirm against a live account.
- Currency as USD: moderate confidence, inferred from pricing pages rather than a labeled field.
- Organization as the only billing tier (no sub-account hierarchy): moderate confidence from the organization-billing documentation; confirm whether projects or sub-organizations exist.
- Feature levels: high confidence, verified against FOCUS v1.2 via the FOCUS MCP server on 2026-06-30; bundled reference confirmed current.
- Overall: this analysis rests on public documentation only and should be treated as provisional. A live billing-API sample and a pass through the FOCUS Validator would convert the provisional mapping into a verified one.

Data quality: provisional.

---

## Sources

- Hyperstack: Accounts, Billing Policies, and Usage Monitoring. https://docs.hyperstack.cloud/docs/billing/billing-policies/
- Hyperstack: Retrieve Billing Rate for Resource (Infrahub API). https://docs.hyperstack.cloud/docs/api-reference/pricebook-resources/retrieve-billing-rate-for-resource/
- Hyperstack: Contracts. https://docs.hyperstack.cloud/docs/billing/contracts/
- Hyperstack: Organization. https://docs.hyperstack.cloud/docs/resource-management/organization/
- Hyperstack: GPU Pricing. https://www.hyperstack.cloud/gpu-pricing
- FOCUS Specification v1.2. https://focus.finops.org/focus-specification/v1-2/
- FOCUS Specification (program and tooling). https://focus.finops.org/

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
