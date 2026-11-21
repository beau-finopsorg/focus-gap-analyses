# Traversal & FOCUS: Data Generator Gap Analysis

*Analysis run: November 17, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** Traversal  
**Prepared:** November 17, 2026  
**Origin:** KubeCon NA 2026 booth outreach  
**Source:** Traversal docs (docs.traversal.com: usage limits, BYOC architecture, API overview, Sessions API, Event Logs API, changelog); AWS Marketplace listing. Traversal publishes no pricing page, billing API, invoice API, or priced usage export.  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 14 Present, 8 Deviation, 2 Missing Mandatory, 12 Missing Conditional, 1 Missing Recommended, 20 N/A

---

## Executive Summary

Traversal sells an "AI SRE": an agent that triages alerts, finds root causes, and answers production questions by reading a customer's existing telemetry (Datadog, Splunk, Dynatrace, Prometheus, Grafana, CloudWatch, Kubernetes, and 25+ other integrations). It runs as multi-tenant SaaS, single-tenant SaaS, or BYOC in the customer's AWS account. Founded in 2023, it raised $120M at a $1B valuation on November 3, 2026, and was a Platinum sponsor of KubeCon NA 2026.

**Public billing documentation is thin.** Traversal publishes no pricing, no billing or invoice API, and no usage export with prices or currency. What is public: Traversal "meters every investigation in credits," without defining what a credit costs or how many credits an investigation consumes; a usage dashboard (released October 19, 2026) shows credit use by organization, member, and Worker; BYOC customers receive "metering-based invoices"; and the AWS Marketplace listing sells a single dimension, "AI SRE Capabilities," at $1,000,000 per 12-month contract, non-cancellable, with private offers. Everything in this analysis beyond those facts is inferred from standard SaaS invoice content and should be confirmed with Traversal.

Mapped against assumed invoice and contract content, 14 of 57 FOCUS v1.2 columns map directly and 19 of 21 Mandatory columns have a source. **EffectiveCost** is the substantive Mandatory gap: the annual contract is paid ahead of use and consumed as credits, so amortizing it requires per-period credit consumption that Traversal shows in its UI but does not export. **ListCost** is trivial once Traversal defines a list credit rate. The larger gaps sit outside the column table: no machine-readable delivery path, an undefined pricing unit, and no allocation of credits to the people, Workers, and alert sources that consume them, even though the dashboard already tracks all three.

**Recommendation:** Publish a monthly FOCUS export per customer organization: one Purchase row per contract or credit grant, one Usage row per investigation (or per day per member and Worker) with ConsumedQuantity in credits and EffectiveCost amortized from the contract, plus Tax and Credit rows so the dataset reconciles to the invoice. Carry the session ID as ResourceId and the trigger type, member, and Worker as Tags. Deliver it through the existing API (`api.traversal.com`) and the Analytics CSV export.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

Traversal publishes no billing data interface. The material available for a FOCUS mapping:

- **Usage limits and metering:** "Traversal meters every investigation in credits." Follow-up questions in an existing investigation are not charged again. Usage is grouped by trigger: human-initiated, automated (alerts, schedules, service-account API calls), and Traversal Worker. No credit price, credit-per-investigation rate, or grant size is published.
- **Usage dashboard (Settings → Usage):** Organization, Members, and Workers views; Worker limits reset daily and per monthly cycle; admins set limits beneath a ceiling Traversal controls; email alerts fire at spend percentages or credit amounts. UI only; no documented export.
- **Analytics export:** CSV export of sessions (October 20, 2026). The docs do not say whether it carries credits. The changelog also mentions "cost trends" charts without defining the cost.
- **Public API (`api.traversal.com`):** Sessions v1 returns `id, status, title, input, created_at, updated_at, messages`, with no credit, cost, or trigger-type field. Event Logs v0 (admin, beta) returns `id, time, type, user_id, user_email, data` for audit events only, with no usage or credit events.
- **BYOC invoices:** Traversal collects usage counts (investigations, follow-ups, Worker activity) from BYOC deployments and issues "metering-based invoices." The invoice format is not public.
- **AWS Marketplace:** "AI SRE" by Traversal, a SaaS contract with one dimension, "AI SRE Capabilities," at $1,000,000 for 12 months, plus private offers. These charges reach the buyer as AWS Marketplace line items in AWS billing data, invoiced by AWS. No usage-based dimension exists. No Azure or Google Cloud Marketplace listing could be verified.

Key characteristics:

- **Unit:** Credits, consumed per investigation; value undefined publicly.
- **Contract:** Annual, prepaid on Marketplace, with a credit ceiling enforced in-product.
- **Pricing:** Quote-only; no public rate.
- **Hierarchy:** One customer organization; within it, members and Workers. No documented workspace or project hierarchy.
- **Model costs:** In SaaS, Traversal absorbs inference cost. In BYOC, the customer pays the model provider (Anthropic, OpenAI, or Amazon Bedrock) directly, so part of Traversal's total cost of ownership appears in another provider's billing data.
- **No regions, zones, or capacity reservations** in Traversal's pricing.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven: every Mandatory column must be present and valid, and Conditional columns are required when the provider's model triggers their condition. Two modeling decisions drive this analysis:

- **The annual contract is a prepaid purchase of credits, not a commitment discount.** FOCUS defines a commitment discount as reduced rates in exchange for a commitment. Traversal publishes no uncommitted rate, so no discount is visible; the seven CommitmentDiscount columns are N/A. EffectiveCost still has to amortize the prepayment over credits consumed. From v1.3 the Contract Commitment dataset is the right home for the contract itself.
- **Investigations are the billable resource; trigger, member, and Worker are allocation keys.** Each investigation has a session ID in the Sessions API and consumes credits, so the Resource columns and Tags are Missing, not N/A. Traversal documents no sub-organization hierarchy, so the SubAccount columns are N/A; team attribution belongs in Tags until such a hierarchy exists.

Traversal has no regions, zones, capacity reservations, alternate pricing currencies, or multiple billing-account types; those columns are N/A and should exist as null. Feature levels follow the FOCUS v1.2 Content Constraints, spot-checked against the live spec on November 17, 2026.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | Traversal source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Invoice line amount (direct and BYOC contracts) | Present |
| EffectiveCost | Mandatory | Not available: needs the annual prepayment amortized over per-period credit consumption, plus credit allocation | Missing: Mandatory |
| ListCost | Mandatory | Not available: no list credit rate; join a rate card × PricingQuantity | Missing: Mandatory |
| ContractedCost | Mandatory | Contract amount from the order form or Marketplace offer | Present |
| BillingAccountId | Mandatory | Traversal organization or customer ID on the invoice | Present |
| BillingAccountName | Mandatory | Customer organization name | Present |
| BillingCurrency | Mandatory | "USD" | Present |
| BillingPeriodStart | Mandatory | Invoice service period start | Present |
| BillingPeriodEnd | Mandatory | Invoice service period end | Present |
| ChargePeriodStart | Mandatory | Contract term start only; usage rows need daily or monthly periods from metering | Deviation |
| ChargePeriodEnd | Mandatory | Contract term end only; same fix | Deviation |
| ChargeDescription | Mandatory | Invoice line description (e.g., "AI SRE Capabilities, 12 months") | Present |
| ChargeCategory | Mandatory | Derive: "Purchase" for the contract; "Usage" for investigations; "Tax" and "Credit" rows from the invoice | Deviation |
| ChargeClass | Mandatory (nullable) | null; "Correction" for re-issued charges | Present |
| InvoiceIssuerName | Mandatory | Traversal's invoicing entity for direct and BYOC contracts (AWS for Marketplace) | Present |
| ProviderName | Mandatory (dep. v1.3) | "Traversal" | Present |
| PublisherName | Mandatory (dep. v1.3) | "Traversal" | Present |
| ServiceName | Mandatory | "Traversal AI SRE" | Present |
| ServiceCategory | Mandatory | Derive: "Management and Governance" | Deviation |
| PricingQuantity | Mandatory | Contract quantity on the order form; usage rows need metered credits | Deviation |
| PricingUnit | Mandatory | Define "Credits" as a documented unit and publish credits per investigation, follow-up, and Worker run | Deviation |
| ConsumedQuantity | Conditional | Not exposed: credits or investigations per period (UI dashboard only) | Missing: Conditional |
| ConsumedUnit | Conditional | Not exposed: "Credits" or "Investigations" | Missing: Conditional |
| ListUnitPrice | Conditional | Not available: no public or list credit rate | Missing: Conditional |
| ContractedUnitPrice | Conditional | Not available: contracts are priced as a lump sum; no per-credit rate published | Missing: Conditional |
| PricingCategory | Conditional | Derive: "Standard" for all rows (no commitment discount) | Deviation |
| BillingAccountType | Conditional | N/A: one billing-account type | N/A |
| SubAccountId | Conditional | N/A: no documented workspace or project hierarchy within an organization | N/A |
| SubAccountName | Conditional | N/A | N/A |
| SubAccountType | Conditional | N/A | N/A |
| ResourceId | Conditional | Not on any charge record; Sessions API `id` is the natural key | Missing: Conditional |
| ResourceName | Conditional | Not on any charge record; Sessions API `title` | Missing: Conditional |
| ResourceType | Conditional | Not exposed (e.g., "Investigation", "Worker") | Missing: Conditional |
| SkuId | Conditional | Not exposed; internal plan code or Marketplace dimension key | Missing: Conditional |
| Tags | Conditional | Not exposed: trigger type, member, and Worker are tracked in the dashboard but emitted with no charge | Missing: Conditional |
| PricingCurrency | Conditional | N/A: priced and billed in USD only | N/A |
| PricingCurrencyListUnitPrice | Conditional | N/A | N/A |
| PricingCurrencyContractedUnitPrice | Conditional | N/A | N/A |
| PricingCurrencyEffectiveCost | Conditional | N/A | N/A |
| SkuMeter | Conditional | Not exposed: "Investigations" | Missing: Conditional |
| SkuPriceId | Conditional | Not exposed | Missing: Conditional |
| SkuPriceDetails | Conditional | Not exposed; needed to state credits per investigation, follow-up exemption, and Worker metering | Missing: Conditional |
| RegionId | Conditional | N/A: no region-based pricing | N/A |
| RegionName | Conditional | N/A | N/A |
| CommitmentDiscountId | Conditional | N/A: annual contract carries no visible rate discount | N/A |
| CommitmentDiscountName | Conditional | N/A | N/A |
| CommitmentDiscountType | Conditional | N/A | N/A |
| CommitmentDiscountCategory | Conditional | N/A | N/A |
| CommitmentDiscountStatus | Conditional | N/A | N/A |
| CommitmentDiscountQuantity | Conditional | N/A | N/A |
| CommitmentDiscountUnit | Conditional | N/A | N/A |
| CapacityReservationId | Conditional | N/A: no capacity reservations | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | Invoice number | Present |
| ChargeFrequency | Recommended | Derive: "One-Time" or "Recurring" for the contract; "Usage-Based" for investigations | Deviation |
| ServiceSubcategory | Recommended | Not exposed; map to "Observability" | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: no zones | N/A |

**Tally:** 14 Present, 8 Deviation, 2 Missing Mandatory, 12 Missing Conditional, 1 Missing Recommended, 20 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Billing account, currency, service periods, invoiced and contracted amounts, line descriptions, and invoice numbers should exist on Traversal's invoices and order forms.

**Substantive (1 of 2 Mandatory gaps):**

- **EffectiveCost.** The annual contract is paid ahead of use and drawn down in credits. Producing EffectiveCost means amortizing that prepayment across credits consumed in each period and allocating any invoice credits back to the charges they offset. Traversal holds the consumption data (the usage dashboard shows it) but exposes none of it in machine-readable form.

**Trivial (1 of 2 Mandatory gaps):**

- **ListCost.** Traversal owns its price book. Define a list credit rate (or document that ListUnitPrice equals the contracted rate) and multiply by PricingQuantity.

**Substantive, beyond the column table:**

- **No delivery path.** No billing API, invoice API, or priced usage export is documented. The Sessions API and Analytics CSV are the obvious carriers, but neither includes credits or cost today.
- **Undefined unit.** A customer cannot convert investigations to credits or credits to dollars from public material. Until Traversal publishes credits per investigation and the credit price, PricingUnit and SkuPriceDetails cannot be populated meaningfully.
- **Allocation.** The dashboard already splits credits by member, Worker, and trigger type (human, automated, Worker). Emitting those per investigation as ResourceId and Tags is the most useful single addition: it lets platform teams charge back AI SRE spend to the on-call teams and alert sources that drive it.
- **Two channels.** Marketplace buyers see Traversal charges in AWS billing data, invoiced by AWS; direct and BYOC customers get a Traversal invoice. A Traversal FOCUS export should cover consumption for both, with InvoiceIssuerName set per channel so neither double-counts the purchase.
- **Split total cost of ownership (BYOC).** BYOC customers pay inference to Anthropic, OpenAI, or Bedrock and run the Connector and Processor on their own compute. Those costs land in other providers' FOCUS data. Documenting a standard resource tag (e.g., `traversal:deployment`) for BYOC infrastructure and Bedrock usage would let customers join them to Traversal's own charges.

### 1.5 Deviations to Fix

**ChargePeriodStart and ChargePeriodEnd:** Emit Usage rows per day or month, not per contract term. Keep the Purchase row on the term.

**ChargeCategory:** "Purchase" for the annual contract; "Usage" for credits consumed by investigations; "Tax" and "Credit" from the invoice, so that BilledCost summed per InvoiceId equals the invoice total.

**ServiceCategory:** "Management and Governance" for the platform.

**PricingQuantity and PricingUnit:** "Credits" is a Traversal-defined unit with no published conversion. Document credits per investigation (and confirm follow-ups are zero), express PricingUnit in FOCUS unit format, and populate PricingQuantity on every Usage row, not only the Purchase row.

**ChargeFrequency and PricingCategory:** "One-Time" or "Recurring" for the contract, depending on how it is invoiced, and "Usage-Based" for investigations; "Standard" pricing throughout.

**Already right:** A single customer organization per contract, a discrete billable event (the investigation) with a stable session ID, consumption already broken out by member, Worker, and trigger in the product, and spend-based alerting that implies Traversal already prices credits internally.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (ratified June 4, 2026); certify at FOCUS v1.2, the version the conformance program currently names. FOCUS v1.5 is in release candidate with ratification scheduled for December 3, 2026. The Contract Commitment dataset (v1.3) fits Traversal's annual credit contract, and the Invoice Detail dataset (v1.4) fits BYOC metering-based invoice reconciliation.

### 2.2 What Certification Requires

FinOps Certified FOCUS v1.2 Conformant runs through the FinOps Foundation (contact `member-cert@finops.org` for the RFI; membership is required for certification). Deliverables: a conformant dataset, public sample data, a native-to-FOCUS mapping, and a Conformance Gap Report seeded by this analysis. Tooling: FOCUS Validator, FOCUS Converter, and the FOCUS Requirements Model. Document the N/A rationale (no regions, reservations, sub-organization hierarchy, alternate currencies, or rate-discounted commitments) and the decision to treat the annual contract as a prepaid purchase.

### 2.3 Phased Roadmap

**Phase 0: Validate.** Define the credit: credits per investigation, follow-up, and Worker run, and the list and contracted price per credit. Pull one month of internal metering for a SaaS customer, a BYOC customer, and a Marketplace customer. Hand-build a FOCUS file from it plus the invoice and run it through the Validator.

**Phase 1: Close Mandatory gaps.** Publish the list credit rate for ListCost and ListUnitPrice. Emit per-period Usage rows and amortize the annual contract across them for EffectiveCost. Add Tax and Credit rows so BilledCost reconciles to the invoice.

**Phase 2: Fix deviations.** Derive ChargeCategory, ServiceCategory, ChargeFrequency, and PricingCategory; normalize PricingUnit; populate PricingQuantity and per-period charge periods on every Usage row.

**Phase 3: Allocation and delivery.** Add ResourceId, ResourceName, and ResourceType per investigation or Worker; Tags for trigger type, member, Worker, and originating alert source; ConsumedQuantity and ConsumedUnit; SkuId, SkuMeter, SkuPriceId, and SkuPriceDetails; ContractedUnitPrice; ServiceSubcategory. Add credits to the Sessions API and Analytics CSV, then ship a scheduled FOCUS export or API endpoint. Publish a BYOC tagging convention.

**Phase 4: Mature and certify.** Drop ProviderName and PublisherName for v1.4; add the Contract Commitment and Invoice Detail datasets; certify at v1.2 and re-certify as the program advances.

### 2.4 FOCUS Use Cases Unlocked

- **After Phase 1:** Invoice reconciliation, amortized spend reporting, and actuals-based budgeting for the Traversal line item.
- **After Phase 2:** Spend by service category across providers, and contract burn-down and credit-exhaustion forecasting.
- **After Phase 3:** Chargeback and showback of AI SRE spend to the teams, members, and alert sources that trigger investigations; unit economics (cost per investigation, cost per incident resolved); and anomaly detection on automated-investigation volume, the trigger most likely to run away from a noisy alert.
- **Out of scope:** Region-based analysis, capacity reservation management, and commitment-discount utilization (no rate-discounted commitment).

---

## Part 3: Immediate Next Steps

1. Follow up with the Traversal contact from KubeCon NA 2026 to identify the owner of billing and credit metering.
2. Ask Traversal to define the credit publicly: credits per investigation, follow-up, and Worker run; list and contracted price per credit; and whether unused credits roll over.
3. Confirm the invoicing legal entity, billing currencies, and whether any non-AWS marketplace listing exists.
4. Build a v1.2 sample from one month of metering plus the invoice and run it through the FOCUS Validator.
5. Open the RFI with `member-cert@finops.org`.

---

## Confidence Summary

- **High:** Traversal meters investigations in credits, exposes usage by organization, member, and Worker in a UI dashboard, issues metering-based invoices to BYOC customers, and documents no billing API, invoice API, or priced usage export. The Sessions and Event Logs APIs carry no credit or cost fields.
- **High:** The AWS Marketplace listing sells one contract dimension, "AI SRE Capabilities," at $1,000,000 for 12 months, with private offers and no usage dimension.
- **High:** Traversal was a Platinum sponsor of KubeCon NA 2026 and raised $120M at a $1B valuation on November 3, 2026.
- **High:** Feature levels match the FOCUS v1.2 Content Constraints; spot-checked against the live spec on November 17, 2026, and v1.4 remains the latest ratified version.
- **Moderate:** Present status for the 14 invoice-sourced columns. Traversal's invoice layout is not public, so these follow standard SaaS invoice content.
- **Moderate:** Treating the annual contract as a prepaid credit purchase. If credit grants are priced below an on-demand credit rate, the seven CommitmentDiscount columns become applicable and PricingCategory becomes "Committed" for drawn-down usage.
- **Moderate:** "Observability" as the ServiceSubcategory value and "Management and Governance" as ServiceCategory. Confirm both against the v1.2 allowed values before mapping.
- **Moderate:** SubAccount columns as N/A. If Traversal supports multiple workspaces or teams within an organization, they become applicable.
- **Low:** Whether the Analytics session CSV or "cost trends" charts carry credits or dollars. Neither is described in the docs.
- **Low:** USD-only billing. Traversal publishes no currency terms; non-USD contracts would make the PricingCurrency columns applicable.
- **Unknown:** Whether Traversal is listed on Azure or Google Cloud Marketplace. Neither listing could be verified.

---

## Sources

- Traversal: [traversal.com](https://traversal.com)
- Traversal Docs (index): [docs.traversal.com/llms.txt](https://docs.traversal.com/llms.txt)
- Traversal Usage Limits: [docs.traversal.com/using-traversal/usage-limits](https://docs.traversal.com/using-traversal/usage-limits.md)
- Traversal Architecture: [docs.traversal.com/architecture/intro](https://docs.traversal.com/architecture/intro.md)
- Traversal BYOC: [docs.traversal.com/architecture/byoc](https://docs.traversal.com/architecture/byoc.md)
- Traversal API Overview: [docs.traversal.com/api/overview](https://docs.traversal.com/api/overview.md)
- Traversal Sessions API: [docs.traversal.com/api/sessions](https://docs.traversal.com/api/sessions.md)
- Traversal Event Logs API: [docs.traversal.com/api/event-logs](https://docs.traversal.com/api/event-logs.md)
- Traversal Changelog: [docs.traversal.com/changelog](https://docs.traversal.com/changelog.md)
- Traversal on AWS Marketplace: [aws.amazon.com/marketplace/pp/prodview-wlenyad5u6fs6](https://aws.amazon.com/marketplace/pp/prodview-wlenyad5u6fs6)
- Traversal $120M raise: [SiliconANGLE](https://siliconangle.com/?p=852978)
- KubeCon + CloudNativeCon NA 2026 sponsors: [events.linuxfoundation.org](https://events.linuxfoundation.org/kubecon-cloudnativecon-north-america/sponsor-list/)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FOCUS 1.5 Release Scope: [focus.finops.org/focus-1-5-release-scope/](https://focus.finops.org/focus-1-5-release-scope/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
