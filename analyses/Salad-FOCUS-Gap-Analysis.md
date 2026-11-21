# Salad (SaladCloud) and FOCUS: Compliance Gap and Adoption Roadmap

*Analysis run: July 1, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Provider and product:** Salad Technologies, SaladCloud (distributed/community GPU cloud). Primary billable product analyzed: Salad Container Engine (SCE), the per-second GPU/CPU container service. References to the Transcription API and AI Gateway are noted where relevant.

**Prepared:** July 1, 2026

**Source analyzed:** SaladCloud public documentation (Billing, Container Engine Billing, Priority Pricing, API Reference and OpenAPI index) and the salad.com pricing page. No billing or cost-and-usage export API, and no sample cost record, is published; the mapping below is inferred from the prepaid-credit model, the per-second pricing structure, and the Portal Billing & Usage surfaces.

**FOCUS baseline:** v1.2 (current certification baseline). **Build target:** v1.4 (latest, ratified June 4, 2026).

---

## Executive summary

SaladCloud today has no structured cost-and-usage dataset to map to FOCUS. Billing is a prepaid-credit ledger managed at the organization level: buyers top up credits, usage draws them down per second, and the Portal exposes a current balance, monthly invoices, per-project usage graphs, and a credit purchase history. There is a rich resource API (container groups, instances, projects, organizations) but no billing or usage-record endpoint and no cost export in any machine-readable form. FOCUS conformance is judged against a per-charge-record dataset, so the honest starting point is that the record itself does not yet exist.

That is a clean-sheet situation, not a broken one. The underlying economic events are unusually well-defined: per-second consumption of a specific GPU class plus vCPU and RAM, at a known priority-level rate, drawn against prepaid credits, scoped to an organization and a project. Those are exactly the fields FOCUS needs. The gap is that Salad has never had to serialize them into a line-item feed, because prepaid credits let the platform bill without one. Building a FOCUS dataset here is a data-engineering exercise over telemetry Salad already has, not a pricing-model redesign.

Because there is no dataset, every FOCUS column is scored as missing or not-yet-applicable against a hypothetical export. The counts below describe what a first SCE cost feed would need to populate, and separate the columns that are genuinely hard (the four cost columns under a prepaid-discount model) from the columns that are straightforward serializations of data the platform already holds.

**4-stat strip:**

- FOCUS columns (v1.2): 57
- Already present in a mappable export: 0
- Substantive Mandatory gaps: 4 of 21 (the cost family, under prepaid volume discounts)
- Deviations to fix on present columns: 0 (no dataset exists yet to deviate)

**RAG readiness:**

- Cost: Gap
- Granularity: Partial
- Allocation: Partial
- Coverage: Gap
- FOCUS shape: Gap
- Overall band: **Not yet aligned (per public docs)**

**Recommendation:** Treat this as a greenfield build. Stand up a per-charge-record export for Salad Container Engine keyed on organization, project, and container group, emit the per-second consumption already tracked for billing, and resolve prepaid volume discounts down to the usage line so `EffectiveCost` is real rather than a copy of list. That single dataset unlocks most of the FOCUS Mandatory set at once.

---

## Part 1: The conformance gap

SaladCloud is a distributed GPU cloud: compute runs on a worldwide network of community nodes (personal computers, esports arenas, and similar), which is what lets Salad price GPUs far below hyperscaler rates. That marketplace shape matters for FOCUS in two specific ways, both addressed in the column analysis: the buyer never sees a node identity or a cloud region, and capacity is preemptible by priority level rather than reserved. Neither blocks conformance; both simply null a family of columns that do not apply to the model.

### 1.1 The data source

What SaladCloud exposes today, from the public documentation:

- **Prepaid credit ledger, organization-scoped:** Billing, payment methods, and credits are managed per organization. Buyers purchase credits (auto or manual recharge), and usage draws the balance down. Credits expire twelve months from purchase.
- **Per-second usage tracking:** SCE bills for the time hardware is dedicated to a container group, tracked per second though displayed as an hourly rate. No charge accrues during allocation, image download, or cold boot.
- **Component-based rates:** CPU-only groups are billed as vCPU ($0.004/vCPU/hr) plus RAM ($0.001/GB/hr). GPU groups are billed at a per-GPU-class hourly rate that bundles vCPU and RAM. Rates vary by one of four priority levels (High, Medium, Low, Lowest).
- **Portal surfaces:** The Billing & Usage page shows the current credit balance, a Billing Information tab (payment card, contacts, historical payment invoices), an Invoice tab (current and historical invoices), a Usage tab (graphs broken down by project, consumption over time), and a Credits tab (purchase history).
- **Volume discounts:** Prepaid purchases from $10,000 to $150,000 earn tiered discounts (2% to 10%); above that is a sales negotiation. These discounts attach to the credit purchase, not to individual usage lines.
- **Resource API:** A REST API keyed on organization and project exposes container groups, instances, queues, inference endpoints, logs, quotas, and GPU/CPU availability.

Key limitations for FOCUS:

- **No billing or usage-record API and no cost export.** The OpenAPI index lists no cost, billing, invoice, or usage-line endpoint. Cost data lives only as Portal invoices and per-project graphs, neither of which is a downloadable per-charge dataset.
- **Discounts are decoupled from usage.** Volume discounts reduce the price of purchased credits, so the discount is realized at top-up time, not on the usage line. Reconciling an effective per-record rate requires allocating the purchase-time discount across the credits it funded.
- **No line-item currency or SKU serialization.** There is no published per-record currency field, SKU identifier, or unit-price field, because the platform has never emitted a usage line.

### 1.2 How conformance is judged

FOCUS defines a common billing-and-usage schema of 57 columns in v1.2. Each column carries a feature level: Mandatory (must be present and populated), Conditional (required when the provider's model triggers the condition), Recommended (encouraged), or Optional. Conformance is judged column by column against a dataset of charge records. Feature levels for this analysis were taken from the verified FOCUS v1.2 reference and spot-checked against the live specification; they were not stated from memory.

Because SaladCloud publishes no charge-record dataset, the analysis scores each column against the export Salad would need to build. A column is "missing" when the target export has no field to carry it, and "N/A: null valid" when the provider's model means the column legitimately does not apply and should exist but be null.

### 1.3 Column-by-column status

Feature levels verified against the FOCUS Specification v1.2. Status legend: Present (emitted and aligned); Present, deviation to fix (emitted, wrong shape or value); Missing: Mandatory (required, absent, blocks conformance); Missing: Recommended (encouraged, absent); Missing: Conditional (condition applies, absent); N/A: null valid (does not apply to this model, should exist and be null).

| FOCUS Column | Level | In the source? | Status |
|---|---|---|---|
| AvailabilityZone | R | No | Missing: Recommended |
| BilledCost | M | No | Missing: Mandatory |
| BillingAccountId | M | Organization (Portal only) | Missing: Mandatory |
| BillingAccountName | M | Organization name (Portal only) | Missing: Mandatory |
| BillingAccountType | C | No | Missing: Conditional |
| BillingCurrency | M | USD (implicit) | Missing: Mandatory |
| BillingPeriodEnd | M | Monthly invoice period (Portal) | Missing: Mandatory |
| BillingPeriodStart | M | Monthly invoice period (Portal) | Missing: Mandatory |
| CapacityReservationId | C | No commitments/reservations | N/A: null valid |
| CapacityReservationStatus | C | No commitments/reservations | N/A: null valid |
| ChargeCategory | M | No | Missing: Mandatory |
| ChargeClass | M | No | Missing: Mandatory |
| ChargeDescription | M | No | Missing: Mandatory |
| ChargeFrequency | R | No | Missing: Recommended |
| ChargePeriodEnd | M | Per-second usage window (internal) | Missing: Mandatory |
| ChargePeriodStart | M | Per-second usage window (internal) | Missing: Mandatory |
| CommitmentDiscountCategory | C | No commitment discounts | N/A: null valid |
| CommitmentDiscountId | C | No commitment discounts | N/A: null valid |
| CommitmentDiscountName | C | No commitment discounts | N/A: null valid |
| CommitmentDiscountQuantity | C | No commitment discounts | N/A: null valid |
| CommitmentDiscountStatus | C | No commitment discounts | N/A: null valid |
| CommitmentDiscountType | C | No commitment discounts | N/A: null valid |
| CommitmentDiscountUnit | C | No commitment discounts | N/A: null valid |
| ConsumedQuantity | C | Per-second runtime (internal) | Missing: Conditional |
| ConsumedUnit | C | Seconds / GPU-hours (internal) | Missing: Conditional |
| ContractedCost | M | No | Missing: Mandatory |
| ContractedUnitPrice | C | No | Missing: Conditional |
| EffectiveCost | M | No | Missing: Mandatory |
| InvoiceId | R | Monthly invoice (Portal) | Missing: Recommended |
| InvoiceIssuerName | M | Salad (implicit) | Missing: Mandatory |
| ListCost | M | No | Missing: Mandatory |
| ListUnitPrice | C | Published hourly rate | Missing: Conditional |
| PricingCategory | C | Standard / priority-based | Missing: Conditional |
| PricingCurrency | C | USD (implicit) | Missing: Conditional |
| PricingCurrencyContractedUnitPrice | C | No | Missing: Conditional |
| PricingCurrencyEffectiveCost | C | No | Missing: Conditional |
| PricingCurrencyListUnitPrice | C | Published hourly rate | Missing: Conditional |
| PricingQuantity | M | No | Missing: Mandatory |
| PricingUnit | M | No | Missing: Mandatory |
| ProviderName | M | Salad (implicit) | Missing: Mandatory |
| PublisherName | M | Salad (implicit) | Missing: Mandatory |
| RegionId | C | Distributed nodes, no region exposed | N/A: null valid |
| RegionName | C | Distributed nodes, no region exposed | N/A: null valid |
| ResourceId | C | Container group ID (API) | Missing: Conditional |
| ResourceName | C | Container group name (API) | Missing: Conditional |
| ResourceType | C | Container group / instance | Missing: Conditional |
| ServiceCategory | M | No | Missing: Mandatory |
| ServiceName | M | Salad Container Engine (implicit) | Missing: Mandatory |
| ServiceSubcategory | R | No | Missing: Recommended |
| SkuId | C | GPU class + priority (internal) | Missing: Conditional |
| SkuMeter | C | No | Missing: Conditional |
| SkuPriceDetails | C | No | Missing: Conditional |
| SkuPriceId | C | No | Missing: Conditional |
| SubAccountId | C | Project (Portal/API) | Missing: Conditional |
| SubAccountName | C | Project name (Portal/API) | Missing: Conditional |
| SubAccountType | C | Project | Missing: Conditional |
| Tags | C | No user tags on billing | Missing: Conditional |

**Reading the tally:** Of 57 v1.2 columns, 0 are present in a mappable export (none exists), 21 are Mandatory and all 21 are missing, 4 are Recommended and all missing, and 32 are Conditional, of which 9 legitimately null out under Salad's model (capacity reservations, commitment discounts, and cloud regions), leaving 23 Conditional columns that a real export would populate. No deviations are recorded because there is no dataset yet to carry a wrong shape or value.

### 1.4 What's solved, and what remains

Nothing is solved in the sense of an emitted, conformant column, because no dataset exists. But most of the missing Mandatory columns are trivial once an export exists, and only the cost family is genuinely hard. Separating the two is the point of this section.

**Substantive gaps (real data or real reconciliation, not plumbing):**

- **BilledCost, EffectiveCost, ListCost, ContractedCost (the cost family).** This is the one substantive block, and it is substantive precisely because of the prepaid volume discounts. `ListCost` is derivable from the published hourly rate times runtime. But volume discounts (2% to 10%) attach to the credit purchase, not the usage line, so `EffectiveCost` and `BilledCost` cannot be a copy of `ListCost`: producing them means allocating the purchase-time discount across the credits that funded each usage record. This is the classic list-cost trap. Because discounts exist and are applied away from the usage line, the cost columns are a reconciliation problem, not a copy. Where a customer has no volume discount, all four costs converge and the gap collapses to plumbing; where they do, it is real work.

**Trivial gaps (serialize data the platform already holds):**

- **Identity and service columns:** `ProviderName` and `PublisherName` are constants ("Salad"). `ServiceName` is "Salad Container Engine"; `ServiceCategory` is "Compute" (or "AI and Machine Learning" for inference-oriented products). `InvoiceIssuerName` is "Salad".
- **Account and period columns:** `BillingAccountId` / `BillingAccountName` map to the organization; `BillingPeriodStart` / `BillingPeriodEnd` to the monthly invoice window; `ChargePeriodStart` / `ChargePeriodEnd` to the per-second usage window the platform already meters. `BillingCurrency` is USD.
- **Charge descriptors:** `ChargeCategory` is "Usage" for SCE consumption (with "Purchase" available for credit top-ups if those are represented); `ChargeClass` is null except on corrections; `ChargeDescription` is a generated label.
- **Pricing columns:** `PricingQuantity` and `PricingUnit` are derivable from the per-second runtime and the rate basis. Because SCE is flat-rate per GPU-class-and-priority (no tiering on the usage line), `PricingQuantity` equals the consumed quantity, so this is a genuine derivation rather than a computation against tiers.

**Conditional columns a real export would populate (not blocking, but expected):**

- **Allocation:** `ResourceId` / `ResourceName` / `ResourceType` map to the container group and instance; `SubAccountId` / `SubAccountName` / `SubAccountType` map to the project (Salad's native sub-organization unit, already the axis of the Portal usage graphs).
- **SKU and pricing:** `SkuId` can encode the GPU class plus priority level; `ListUnitPrice` and the pricing-currency unit prices come from the published rate card; `PricingCategory` reflects the priority-based standard pricing.

**Conditional columns that null out under Salad's model (N/A: null valid):**

- **Commitment discounts (7 columns):** Salad sells no reserved or committed-use discounts; prepaid credits are not a commitment discount in the FOCUS sense.
- **Capacity reservations (2 columns):** Capacity is preemptible by priority, not reserved.
- **Regions (RegionId, RegionName):** The distributed node network exposes no region or zone to the buyer; `AvailabilityZone` (Recommended) is likewise not applicable.

### 1.5 Deviations to fix

None. Deviations are wrong-shape or wrong-value data on columns that are actually emitted, and SaladCloud emits no billing dataset yet. The most likely future deviation to watch for, once an export exists, is the `Tags` column: FOCUS expects key-value pairs, and providers frequently emit bare-string arrays. Salad does not currently attach user tags to billing at all, so `Tags` is scored Missing: Conditional rather than a deviation, but the key-value shape should be designed in from the start rather than retrofitted.

---

## Part 2: The path forward

### 2.1 Which FOCUS version to target

Build to **v1.4** (latest, ratified June 4, 2026) and validate against the **v1.2** certification baseline, which remains the version anchoring the "FinOps Certified FOCUS v1.2 Conformant" badge. Because Salad is building a dataset from scratch, there is no legacy schema to migrate: design directly to v1.4 column IDs and shapes, then confirm conformance against whichever version the certification program requires at submission time. Two v1.4 details help here: `ProviderName` and `PublisherName` are removed in v1.4 (deprecated in v1.3), so a greenfield v1.4 build simply omits them rather than emitting and later dropping them. Validator support for v1.4 is expected later in Q3 2026; until then, validate against v1.3, which the Validator supports today.

### 2.2 What certification requires

FOCUS conformance for data generators runs through the FinOps Foundation. The deliverables are a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report (this analysis is its seed). Membership is required for certification, though contributing to the specification is open and free; contact `member-cert@finops.org` for the RFI. Open-source tooling supports the build: the FOCUS Validator checks a dataset against the machine-readable Requirements Model, the FOCUS Converter maps provider-native data to FOCUS, and the Requirements Model itself encodes the MUST/SHOULD/MAY rules. The specification is published at https://focus.finops.org and is licensed under CC BY 4.0.

### 2.3 Phased roadmap

**Phase 0: Scope and confirm.** Decide the grain of the export (per container group per day is the natural fit for a per-second-metered service) and confirm the target version. Model the mapping on paper against a handful of real invoices before building. Establish that projects are the sub-account axis and organizations the billing account.

**Phase 1: Build the charge-record export and close the Mandatory set.** This is the phase that unlocks conformance. Emit a per-charge dataset from the per-second telemetry Salad already meters, populating the trivial Mandatory columns (identity, service, account, period, charge descriptors, pricing quantity/unit) directly. In the same phase, solve the cost family: derive `ListCost` from rate times runtime, and reconcile prepaid volume discounts down to the usage line to produce real `EffectiveCost`, `BilledCost`, and `ContractedCost`. Where a customer has no discount, all four converge.

**Phase 2: Populate applicable Conditional columns.** Add the allocation columns (resource = container group/instance, sub-account = project), the SKU columns (GPU class plus priority as `SkuId`, rate card as `ListUnitPrice`), and `PricingCategory`. Design `Tags` as key-value from the outset if user tagging is added to billing.

**Phase 3: Round out Recommended columns and null the N/A families explicitly.** Add `ChargeFrequency`, `ServiceSubcategory`, and `InvoiceId`, and make sure the commitment-discount, capacity-reservation, and region columns exist as explicit nulls rather than being absent.

**Phase 4: Validate and certify.** Run sample data through the FOCUS Validator (v1.3 today, v1.4 when supported), fix what it flags, then pursue the certification RFI. Because the build targets v1.4, no deprecated-column cleanup is needed.

### 2.4 FOCUS Use Cases unlocked

Once the Phase 1 export exists at container-group and project grain, the everyday allocation and reporting use cases work immediately: cost by project, cost by resource, usage trend over time, and chargeback to internal teams (the Portal already graphs usage by project, so the underlying data is present). Anomaly detection and unit-economics reporting (cost per GPU-hour, cost per inference job) follow from the same records.

Reconciliation and actuals-based budgeting use cases depend on Phase 1's cost reconciliation: they need real `EffectiveCost` and `BilledCost`, not list, which is where the prepaid-discount work pays off. Commitment-tracking, reservation-utilization, and region-based use cases are out of scope for Salad's model, since it sells no commitments or reservations and exposes no regions.

---

## Part 3: Immediate next steps

1. Confirm the target grain (per container group per day) and target version (build v1.4, certify against v1.2 baseline) with the team that owns SaladCloud billing telemetry.
2. Pull three to five representative monthly invoices and their underlying per-second usage, and map them by hand to FOCUS v1.4 column IDs to validate the field-level mapping before any code.
3. Decide how prepaid volume discounts are allocated to usage records, since that decision determines whether `EffectiveCost` is real or a list-cost copy.
4. Draft the native-to-FOCUS mapping document and a synthetic sample dataset, and run it through the FOCUS Validator (v1.3 today).
5. If pursuing certification, contact `member-cert@finops.org` for the RFI and confirm the current certification badge version.

---

## Confidence summary

- **No structured cost dataset exists (high confidence).** The public OpenAPI index and billing documentation show a prepaid-credit ledger, Portal invoices, and per-project usage graphs, but no billing, cost, or usage-record API endpoint and no cost export. The column-by-column analysis is therefore scored against a hypothetical future export, not an emitted dataset.
- **Provisional field mapping (moderate confidence).** Because Salad publishes no per-record billing schema or sample, the mapping of native concepts (organization, project, container group, GPU class, priority level, per-second runtime) to FOCUS columns is inferred from the pricing model and Portal structure. It should be confirmed against real invoice and usage data before build.
- **Cost family is substantive (high confidence).** Prepaid volume discounts are applied at credit-purchase time and are documented (2% to 10% tiers), so `EffectiveCost` and `BilledCost` require reconciling those discounts to usage lines. This is the list-cost trap and is not trivial where discounts apply.
- **N/A classifications (high confidence).** Commitment discounts, capacity reservations, and cloud regions do not exist in Salad's distributed, preemptible, priority-priced model, so those column families legitimately null out.
- **Feature levels (high confidence).** Taken from the verified FOCUS v1.2 reference (stamp 2026-06-23) and consistent with the live specification; v1.2 remains the certification baseline and v1.4 the latest ratified version. Validator support for v1.4 was noted as expected later in Q3 2026 and should be confirmed before a v1.4 Validator run.
- **Overall readiness: Nascent.** The score reflects the data source reviewed (no conformant dataset published), not a formal certification result. Salad has not been assessed by the FinOps Foundation and holds no FOCUS certification.

---

## Sources

- SaladCloud, Salad Container Engine Billing: https://docs.salad.com/container-engine/explanation/billing-pricing/billing
- SaladCloud, Billing (prepaid credits, volume discounts, payment types): https://docs.salad.com/general/explanation/billing
- SaladCloud, Priority Pricing: https://docs.salad.com/container-engine/explanation/billing-pricing/priority-pricing
- SaladCloud, Using the API: https://docs.salad.com/reference/api-usage
- SaladCloud, documentation and OpenAPI index: https://docs.salad.com/llms.txt
- Salad GPU Cloud pricing: https://salad.com/pricing
- FOCUS Specification: https://focus.finops.org/focus-specification/
- FOCUS Specification v1.2: https://focus.finops.org/focus-specification/v1-2/
- FOCUS Specification v1.4: https://focus.finops.org/focus-specification/

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
