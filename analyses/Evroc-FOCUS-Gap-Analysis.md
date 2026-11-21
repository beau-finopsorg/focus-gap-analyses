# evroc & FOCUS: Data Generator Gap Analysis

*Analysis run: July 6, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** evroc AB (Stockholm, Sweden)
**Prepared:** July 6, 2026
**Source:** evroc public documentation (docs.evroc.com), evroc CLI and API reference, evroc.com service and pricing pages. No billing, cost, or usage-export interface is documented.
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4
**Status:** evroc is not listed on the FOCUS Supported providers page, so this is a readiness assessment, not a conformance verdict.
**Tally:** 0 Present, 0 Deviation, 21 Missing Mandatory, 4 Missing Recommended, 21 Missing Conditional, 11 N/A

---

## Executive Summary

evroc is an early-stage European sovereign hyperscaler that went live in July 2025, operating from data centers in Stockholm (`se-sto`) and Mougins, France, with a stated plan to reach ten hyperscale sites by 2030. Its platform offers Compute (CPU and GPU virtual machines), Object Storage, File Store, Networking, IAM, and an inference product called Think. The platform primitives that FOCUS attribution depends on are already strong: a two-level Organization to Project account hierarchy, region and zone identifiers, per-resource IDs, and key-value labels on nearly every resource type.

The finding that governs this analysis is a structural one: evroc publishes no billing, cost, or usage-export interface. There is no cost and usage report, no billing API, no invoice export, and no published price list (pricing on the public site loads dynamically and is not retrievable, and the docs contain no pricing reference). Billing is administered at the Organization level through the console and through evroc support, not through a queryable data surface. As a result, none of the 57 FOCUS columns can be marked Present today: there is no cost record to map. Conformance for evroc is therefore a data-production effort, building a billing dataset that does not yet exist in a customer-consumable form, rather than a reshaping of an existing feed.

This is normal for a provider at evroc's stage and should not be read as a deficiency in the platform. The account, resource, and region primitives mean the eventual FOCUS build has a solid attribution spine to hang cost on once a rated billing record exists.

**Recommendation:** Treat FOCUS as a design input to evroc's billing engine, not a retrofit. The single highest-value step is to define a rated, resource-level daily charge record (one row per resource per day, carrying quantity, unit, rate, and cost in EUR, keyed to Organization, Project, region, zone, and resource ID). Once that record exists, evroc's existing hierarchy, region, and label primitives make the mandatory FOCUS spine largely mechanical to populate.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

There is no cost or usage data source to analyze. This section describes the platform primitives that a future FOCUS dataset would draw on, and states plainly where the billing data gap sits.

What exists today, from the public documentation:

- **Account hierarchy:** An Organization is the top-level entity (the company or team). Each Organization contains Projects, which are isolated containers for resources, users, and permission sets. Organization administrators "manage billing and account settings," and evroc advises using separate Organizations for business units that need "separate billing." This is a clean two-level hierarchy that maps to BillingAccount (Organization) and SubAccount (Project).
- **Resource identity:** Compute VMs, disks, snapshots, placement groups, buckets, bucket service accounts, file stores, public IPs, security groups, subnets, and VPCs are all first-class resources with IDs, addressable through the CLI and REST API (`get`, `list`, `update`).
- **Regions and zones:** A region such as `se-sto` (Stockholm) contains zones `se-sto-a`, `se-sto-b`, and `se-sto-c`. A second region operates in Mougins, France. Compute VMs and disks are zonal; VPCs, public IPs, and security groups are regional. This gives clean RegionId, RegionName, and AvailabilityZone values.
- **Labels (tags):** Most resource types expose a `label` subcommand that adds or removes labels as key-value pairs (`--add key=value`, a string-to-string map). This is the FOCUS key-value tag shape, not an array of bare strings, so the tag primitive is well formed at the resource layer.
- **Services:** Compute (CPU and GPU VMs), Object Storage (S3-compatible, regional, replicated across zones, 99.9% uptime), File Store, Networking, and Think (inference, with API keys, instances, and models). These map to FOCUS ServiceName and ServiceCategory values (Compute, Storage, Networking, AI and Machine Learning).
- **Currency:** evroc AB is a Swedish company serving European customers; billing currency is EUR.

Key limitations, which define the gap:

- **No billing or cost interface of any kind.** The documentation covers Compute, Storage, IAM, Think, Networking, and Quotas. There is no billing product, no cost and usage export, no billing or invoicing API, and no usage-metering export documented. The API reference lists IAM, Object Storage, Compute, Networking, Quotas, and Think, with no billing or cost endpoint.
- **No published pricing.** Public product pages render "Loading pricing data..." and expose no retrievable rate card, and the docs carry no pricing reference. Without published rates, ListUnitPrice and ListCost cannot be derived from public information.
- **No commitment or reservation mechanics documented.** No reserved instances, savings plans, committed-use discounts, or capacity reservations appear anywhere in the documentation. VMs are provisioned on demand; Quotas govern allocation, not commitment-based pricing.
- **Metadata retained for billing, but not exposed to the customer as data.** evroc's terms note that request metadata (timestamps, request and response sizes, error codes) is logged for "operational, security, and billing purposes." That is an internal metering signal, not a customer-facing cost dataset.

### 1.2 How Conformance Is Judged

FOCUS conformance is judged column by column against the feature level each column carries in the target version: Mandatory, Conditional, Recommended, or Optional. A conformant dataset must include and populate every Mandatory column, populate Conditional columns when the provider's business model triggers the condition, and may null Conditional or Recommended columns that do not apply. Because evroc emits no billing dataset, every column is currently absent. Feature levels below are taken from the verified FOCUS v1.2 reference, not from memory.

Two families are genuinely not applicable to evroc's documented model and are marked N/A (the columns should still exist and be null in a conformant dataset): the seven CommitmentDiscount columns and the two CapacityReservation columns, because evroc documents no commitment or reservation constructs. AvailabilityZone is not N/A: evroc has real zones (`se-sto-a/b/c`), so it should be populated for zonal resources.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

Because evroc publishes no billing dataset, no column can be marked Present. Each Mandatory, Conditional, and Recommended column is classified by whether the platform primitives to populate it exist (making the eventual build trivial) or whether the underlying data does not exist yet (making it substantive). The "evroc primitive" column names the source a future build would draw on.

| FOCUS Column | Level (v1.2) | evroc primitive (future source) | Status |
|---|---|---|---|
| BilledCost | Mandatory | No billing record exists; rated cost must be produced | Missing: Mandatory |
| EffectiveCost | Mandatory | No billing record exists | Missing: Mandatory |
| ListCost | Mandatory | No published rate card; must be produced | Missing: Mandatory |
| ContractedCost | Mandatory | No billing record exists | Missing: Mandatory |
| BillingAccountId | Mandatory | Organization ID (exists as a primitive, no billing surface) | Missing: Mandatory |
| BillingAccountName | Mandatory | Organization name | Missing: Mandatory |
| BillingCurrency | Mandatory | EUR (constant) | Missing: Mandatory |
| BillingPeriodStart | Mandatory | No billing period is defined in any data surface | Missing: Mandatory |
| BillingPeriodEnd | Mandatory | No billing period is defined | Missing: Mandatory |
| ChargePeriodStart | Mandatory | No charge record exists | Missing: Mandatory |
| ChargePeriodEnd | Mandatory | No charge record exists | Missing: Mandatory |
| ChargeDescription | Mandatory | Derivable from service plus resource once a record exists | Missing: Mandatory |
| ChargeCategory | Mandatory | Derivable ("Usage" for on-demand consumption) | Missing: Mandatory |
| ChargeClass | Mandatory (nullable) | Null except corrections; trivial once a record exists | Missing: Mandatory |
| InvoiceIssuerName | Mandatory | "evroc AB" (constant) | Missing: Mandatory |
| ProviderName | Mandatory (dep. v1.3) | "evroc" (constant) | Missing: Mandatory |
| PublisherName | Mandatory (dep. v1.3) | "evroc" (constant) | Missing: Mandatory |
| ServiceName | Mandatory | Service catalog (Compute, Object Storage, File Store, Think, Networking) | Missing: Mandatory |
| ServiceCategory | Mandatory | Derivable (Compute, Storage, Networking, AI and Machine Learning) | Missing: Mandatory |
| PricingQuantity | Mandatory | Requires metered usage per rated line; not exposed | Missing: Mandatory |
| PricingUnit | Mandatory | Derivable per SKU (VM-Hours, GB-Month, tokens) once metering exists | Missing: Mandatory |
| ConsumedQuantity | Conditional | Requires metered usage; not exposed | Missing: Conditional |
| ConsumedUnit | Conditional | Derivable per service once metering exists | Missing: Conditional |
| ListUnitPrice | Conditional | No published rate card | Missing: Conditional |
| ContractedUnitPrice | Conditional | No rated record exists | Missing: Conditional |
| PricingCategory | Conditional | "Standard" (on-demand); trivial once records exist | Missing: Conditional |
| ChargeFrequency | Recommended | "Usage-Based" for consumption; derivable | Missing: Recommended |
| BillingAccountType | Conditional | Organization is the billing entity; derivable | Missing: Conditional |
| SubAccountId | Conditional | Project ID (exists as a primitive) | Missing: Conditional |
| SubAccountName | Conditional | Project name | Missing: Conditional |
| SubAccountType | Conditional | "Project" (constant); derivable | Missing: Conditional |
| ResourceId | Conditional | Resource IDs exist (VM, disk, bucket, filestore, IP) | Missing: Conditional |
| ResourceName | Conditional | Resource names exist | Missing: Conditional |
| ResourceType | Conditional | Resource kind exists (virtualmachine, disk, bucket, filestore) | Missing: Conditional |
| SkuId | Conditional | VM resource profile / instance type; exists as a primitive | Missing: Conditional |
| Tags | Conditional | Labels are key-value (`--add key=value`); correct shape, not on any billing line | Missing: Conditional |
| PricingCurrency | Conditional | EUR; trivial once records exist | Missing: Conditional |
| PricingCurrencyListUnitPrice | Conditional | No rated record exists | Missing: Conditional |
| PricingCurrencyContractedUnitPrice | Conditional | No rated record exists | Missing: Conditional |
| PricingCurrencyEffectiveCost | Conditional | No rated record exists | Missing: Conditional |
| SkuMeter | Conditional | Derivable per SKU once metering exists | Missing: Conditional |
| SkuPriceId | Conditional | No price catalog is published | Missing: Conditional |
| SkuPriceDetails | Conditional | No price catalog is published | Missing: Conditional |
| RegionId | Conditional | Region code exists (`se-sto`) | Missing: Conditional |
| RegionName | Conditional | Region name (Stockholm; Mougins, France) | Missing: Conditional |
| CommitmentDiscountId | Conditional | N/A: no commitment construct documented | N/A: null valid |
| CommitmentDiscountName | Conditional | N/A | N/A: null valid |
| CommitmentDiscountType | Conditional | N/A | N/A: null valid |
| CommitmentDiscountCategory | Conditional | N/A | N/A: null valid |
| CommitmentDiscountStatus | Conditional | N/A | N/A: null valid |
| CommitmentDiscountQuantity | Conditional | N/A | N/A: null valid |
| CommitmentDiscountUnit | Conditional | N/A | N/A: null valid |
| CapacityReservationId | Conditional | N/A: no reservation construct documented | N/A: null valid |
| CapacityReservationStatus | Conditional | N/A | N/A: null valid |
| InvoiceId | Recommended | No invoice data surface is exposed | Missing: Recommended |
| ServiceSubcategory | Recommended | Derivable (Virtual Machines, GPU VMs, Object Storage, File Store, Inference) | Missing: Recommended |
| AvailabilityZone | Recommended | Zone code exists (`se-sto-a`, `-b`, `-c`) for zonal resources | Missing: Recommended |

**Tally:** 0 Present, 0 Deviation, 21 Missing Mandatory, 4 Missing Recommended, 21 Missing Conditional, 11 N/A. The four Recommended columns are ChargeFrequency, InvoiceId, ServiceSubcategory, and AvailabilityZone. The eleven N/A columns are the seven CommitmentDiscount columns and the two CapacityReservation columns, plus none others; the remaining Conditional columns are genuinely Missing because the platform primitive exists but no billing line carries it.

### 1.4 What Is Solved, and What Remains

**What is solved (as primitives, not as billing data):** The attribution spine is in good shape. Organization and Project give a two-level account hierarchy. Regions and zones are explicit and cleanly named. Resource IDs, names, and types exist across compute, storage, and networking. Labels are key-value, which is the correct FOCUS tag shape. The service catalog maps cleanly to FOCUS service categories. Invoice issuer, provider, publisher, and billing currency are constants. None of these require new data collection; they require a billing record to attach to.

**What remains, and the split between substantive and trivial:**

Twenty-one Mandatory columns are missing. The split matters more than the count:

- **Substantive (the real work):** the four cost columns (BilledCost, EffectiveCost, ListCost, ContractedCost) plus the two metered quantity columns (PricingQuantity, PricingUnit) and the period columns (BillingPeriodStart/End, ChargePeriodStart/End). These depend on rated, metered, time-bounded charge records that do not exist in any customer-facing form today. This is the core data-production effort: build a billing engine that meters usage per resource, applies a rate card, and emits a daily rated charge record in EUR.
- **Trivial once records exist (plumbing):** BillingAccountId/Name (Organization), InvoiceIssuerName, ProviderName, PublisherName, BillingCurrency (EUR), ServiceName, ServiceCategory, ChargeCategory, ChargeDescription, and ChargeClass (null except corrections). Each is a constant, a lookup, or a straightforward derivation. They are only "missing" because there is no row to place them on.

Because evroc has no discounts, credits, commitments, or amortization documented anywhere, the list-cost trap resolves in the simpler direction: once a rated record exists, ListCost = BilledCost = EffectiveCost = ContractedCost for standard on-demand usage. The substantive difficulty is producing the rated record at all, not reconciling later invoice-time adjustments back to usage lines. If evroc introduces enterprise contracts, credits, or commitment pricing later, EffectiveCost and ContractedCost would become a substantive reconciliation gap at that point.

### 1.5 Deviations to Fix

There are no deviations to fix, because there is no emitted billing data to deviate. This is the one silver lining of a greenfield state: evroc can adopt FOCUS column IDs, key-value tags, valid enums, and ISO formats (ISO 4217 EUR, ISO 8601 timestamps, inclusive-start exclusive-end periods) natively in the first version of its billing export, rather than reshaping a legacy schema. What evroc already does right at the primitive layer: labels are key-value (not bare strings), region and zone codes are stable and well formed, and the account hierarchy is clean.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (June 4, 2026), the latest ratified version, and certify at the current certification baseline, FOCUS v1.2. Because evroc is greenfield on billing, there is no legacy schema to migrate: it can build directly to v1.4 column semantics and simply omit the columns v1.4 removed (ProviderName and PublisherName, removed in v1.4; retained here only for the v1.2 baseline table). Confirm the certification badge version against the program page before finalizing.

### 2.2 What Certification Requires

FOCUS conformance for data generators runs through the FinOps Foundation. The deliverables are a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report (this analysis is its seed). Contact `member-cert@finops.org` for the RFI. Membership is required for certification, though contributing to the spec is open and free. Open-source tooling supports the build: the FOCUS Validator (checks data against the Requirements Model), the FOCUS Converter (provider-native to FOCUS), and the FOCUS Requirements Model (machine-readable MUST/SHOULD/MAY rules). For evroc, certification is downstream of a prerequisite that does not yet exist: a customer-consumable billing dataset.

### 2.3 Phased Roadmap

Ordered by dependency. Phase 1 is the gate; nothing else is possible until a rated charge record exists.

**Phase 0: Confirm scope and design to FOCUS.** Decide the grain (recommended: one rated charge record per resource per day), the currency (EUR), and the target version (build v1.4, certify v1.2). Adopt FOCUS column IDs in the export schema from the start.

**Phase 1: Produce a rated, resource-level charge record (the substantive build).** Meter usage per resource per day (VM-Hours, GB-Month, inference tokens), apply a rate card, and emit BilledCost, EffectiveCost, ListCost, ContractedCost in EUR with ChargePeriodStart/End and BillingPeriodStart/End. Key each row to Organization (BillingAccountId), Project (SubAccountId), region, zone, and resource ID. This single phase moves the substantive Mandatory columns and, mechanically, most of the trivial ones.

**Phase 2: Attach the attribution spine.** Populate BillingAccountId/Name from Organization, SubAccountId/Name from Project, RegionId/Name and AvailabilityZone from the zone code, ResourceId/Name/Type from the resource, and Tags from resource labels (already key-value). Derive ServiceName, ServiceCategory, ChargeCategory, ChargeDescription, PricingUnit, and ConsumedQuantity/Unit.

**Phase 3: Round out Conditional and Recommended columns.** Add ServiceSubcategory, InvoiceId (once invoicing is a data surface), ChargeFrequency, SkuId/SkuMeter, and the pricing-currency columns. Publish a rate card so ListUnitPrice and SkuPriceId/SkuPriceDetails become populatable.

**Phase 4: Validate and certify.** Run sample data through the FOCUS Validator, build the native-to-FOCUS mapping, and open the RFI. Build to v1.4 semantics; omit ProviderName/PublisherName under v1.4.

### 2.4 FOCUS Use Cases Unlocked

Because there is no cost data today, no FOCUS Use Case is currently supported. The sequencing below shows what each phase unlocks:

- **Unlocked by Phase 1 and 2 (cost data plus attribution):** cost reporting and showback by Organization and Project, allocation by resource, allocation by tag, cost reporting by region and zone, and service-level cost breakdowns. evroc's clean hierarchy and label primitives make these strong as soon as a rated record with those keys exists.
- **Unlocked by Phase 3 (SKU and rate detail):** unit-cost and rate analysis, and effective-rate reporting per SKU.
- **Out of scope for evroc's current model:** commitment-based discount tracking, commitment utilization and coverage, and capacity-reservation reporting, because evroc documents no commitment or reservation constructs. These would come into scope only if evroc introduces those mechanics.

---

## Part 3: Immediate Next Steps

1. Confirm the billing-record grain and target versions (build v1.4, certify v1.2), and adopt FOCUS column IDs in the billing export schema from the outset.
2. Stand up the Phase 1 rated charge record: meter usage per resource per day, apply a rate card, and emit the four cost columns in EUR with charge and billing periods.
3. Attach the attribution spine (Organization, Project, region, zone, resource ID, labels) to each charge record.
4. Run a sample export through the FOCUS Validator and open the RFI with `member-cert@finops.org`.

---

## Confidence Summary

- **High:** evroc publishes no billing, cost, or usage-export interface. The documentation, CLI, and API reference contain no billing product or endpoint, and no rate card is published. This is the load-bearing finding, and it is well supported by the public sources reviewed.
- **High:** The account hierarchy (Organization to Project), regions and zones (`se-sto-a/b/c`; Mougins), resource identity, and key-value labels exist as platform primitives. These are directly documented.
- **High:** No commitment-discount or capacity-reservation mechanics are documented, so the eleven columns in those two families are correctly N/A.
- **Moderate:** Billing currency is EUR (inferred from evroc AB being a Swedish company serving European customers; not confirmed on a billing artifact, because none is published).
- **Moderate:** The mapping of platform primitives to specific FOCUS columns is sound in principle, but is provisional until an actual billing record exists to validate field names, types, and grain against. Every "Present" verdict is deferred precisely because no such record could be inspected.
- **Provisional overall:** This is a readiness assessment based on public documentation for an early-stage provider, not a review of a billing dataset. evroc is not on the FOCUS Supported providers list, and nothing here should be read as a conformance result. The bundled FOCUS feature-level table (v1.2) was cache-validated on July 6, 2026: all versions v1.0 through v1.4 were confirmed present against the live spec, with v1.4 (June 4, 2026) the latest ratified version, matching the reference stamp.

---

## Sources

- evroc: [evroc.com](https://evroc.com/)
- evroc User Documentation: [docs.evroc.com](https://docs.evroc.com/)
- evroc IAM Organizations: [docs.evroc.com/products/iam/concepts/organizations.html](https://docs.evroc.com/products/iam/concepts/organizations.html)
- evroc Regions and Zones: [docs.evroc.com/products/compute/concepts/regions-and-zones.html](https://docs.evroc.com/products/compute/concepts/regions-and-zones.html)
- evroc Virtual Machines: [evroc.com/cloud-services/virtual-machines](https://evroc.com/cloud-services/virtual-machines/)
- evroc launch coverage: [datacenterdynamics.com](https://www.datacenterdynamics.com/en/news/sovereign-european-cloud-evroc-launches/)
- FOCUS Specification v1.2: [focus.finops.org/focus-specification/v1-2](https://focus.finops.org/focus-specification/v1-2/)
- FOCUS Specification v1.4: [focus.finops.org/focus-specification/v1-4](https://focus.finops.org/focus-specification/v1-4/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
