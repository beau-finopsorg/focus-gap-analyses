# Confluent & FOCUS: Data Generator Gap Analysis

*Analysis run: June 25, 2026*


> **About this report.** This is an unofficial community reading of public documentation on the "Analysis run" date above. It is not a certification result or an official project verdict, and it may be incomplete or out of date.
> Ratings use this scale: Aligned, Partially aligned, Not yet aligned (per public docs).
> It is not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
> To correct it, open an issue or pull request in this repository with public evidence. See [DISCLAIMER.md](../DISCLAIMER.md).

**Company:** Confluent  
**Prepared:** June 25, 2026  
**Source:** Confluent Cloud Usage API (`GET /billing/v1/costs`); Confluent billing dashboard  
**Baseline:** FOCUS v1.2 | **Build target:** FOCUS v1.4  
**Tally:** 28 Present, 10 Deviation, 0 Missing Mandatory, 2 Missing Conditional, 1 Missing Recommended, 16 N/A

---

## Executive Summary

Confluent Cloud bills by consumption across four dimensions: throughput (read/write bytes), storage (GB-hours), client connections, and cluster link hours. Kafka clusters are the ResourceId; environments (dev, staging, prod) map to SubAccounts. Confluent's Billing API provides per-resource cost data with cluster granularity. All 21 Mandatory columns have source data. Sixteen columns are N/A: no regional billing at the billing layer, and no FOCUS CommitmentDiscount constructs (Confluent Committed Use Discounts are pricing tiers). The 10 Deviations cover PricingUnit normalization, enum derivation, and enterprise ContractedCost.

**Recommendation:** Implement one FOCUS row per Confluent billing dimension (throughput, storage, connections, cluster links) × cluster × billing period. ResourceId = cluster ID. SubAccountId = environment ID. PricingUnit varies by dimension: "GB" for throughput/storage, "Connections" for client connections, "Hours" for cluster links.

---

## Part 1: The Conformance Gap

### 1.1 The Data Source

**Confluent Cloud Billing API** (`GET /billing/v1/costs`): Returns costs broken down by resource (cluster, connector, Schema Registry, ksqlDB application) and billing line item type. Key fields: resource ID, resource type, billing type, quantity, unit price, total cost, billing period. Data available with cluster granularity.

**Confluent Environments**: Confluent Cloud organizes clusters into environments (e.g., dev, prod). Environment ID maps to SubAccountId.

Key characteristics:
- **Multi-dimension metering:** Each Kafka cluster generates billing rows for read throughput, write throughput, storage, partition count, client connections, and cluster link hours.
- **Cluster as resource:** The Kafka cluster is the ResourceId. Connector IDs, Schema Registry IDs, and ksqlDB application IDs are also available.
- **Environment hierarchy:** Environments map to SubAccountId.
- **Public pricing:** Confluent publishes per-unit on-demand pricing for all dimensions. ListUnitPrice is derivable.
- **Committed Use Discounts (CUDs):** Annual spend commitments reduce unit rates. This is PricingCategory = "Committed", not FOCUS CommitmentDiscount.
- **No regional billing separation:** Multi-region clusters have a single billing record with a cluster region field, but this does not produce separate per-region billing rows.

### 1.2 How Conformance Is Judged

FOCUS conformance is column-driven. Confluent CUDs = PricingCategory "Committed". CommitmentDiscount columns are N/A.

### 1.3 Column-by-Column Status: All 57 FOCUS v1.2 Columns

| FOCUS Column | Level (v1.2) | Confluent source | Status |
|---|---|---|---|
| BilledCost | Mandatory | Invoice amount per billing line item | Present |
| EffectiveCost | Mandatory | = BilledCost | Present |
| ListCost | Mandatory | On-demand unit price × quantity from Confluent pricing page | Present |
| ContractedCost | Mandatory | CUD or enterprise negotiated rate × quantity; Deviation for custom contracts | Deviation |
| BillingAccountId | Mandatory | Confluent organization ID | Present |
| BillingAccountName | Mandatory | Organization name | Present |
| BillingCurrency | Mandatory | USD | Present |
| BillingPeriodStart | Mandatory | First day of billing month | Present |
| BillingPeriodEnd | Mandatory | Last day of billing month | Present |
| ChargePeriodStart | Mandatory | Start of usage period | Present |
| ChargePeriodEnd | Mandatory | End of usage period | Present |
| ChargeDescription | Mandatory | Derive: cluster + dimension (e.g., "Confluent Kafka Cluster · Write Throughput") | Deviation |
| ChargeCategory | Mandatory | Derive: "Usage" for all metered consumption | Deviation |
| ChargeClass | Mandatory (nullable) | null except for corrections | Present |
| InvoiceIssuerName | Mandatory | "Confluent, Inc." | Present |
| ProviderName | Mandatory (dep. v1.3) | "Confluent" | Present |
| PublisherName | Mandatory (dep. v1.3) | "Confluent" | Present |
| ServiceName | Mandatory | "Confluent Cloud Kafka", "Confluent Cloud Connectors", "Confluent Cloud Schema Registry", "Confluent ksqlDB" | Present |
| ServiceCategory | Mandatory | Derive: "Analytics" for streaming data platform | Deviation |
| PricingQuantity | Mandatory | Usage quantity per billing dimension | Present |
| PricingUnit | Mandatory | "GB" for throughput and storage; "Connections" for client connections; "Hours" for cluster links and connectors | Deviation |
| ConsumedQuantity | Conditional | = PricingQuantity | Present |
| ConsumedUnit | Conditional | = PricingUnit | Present |
| ListUnitPrice | Conditional | On-demand unit price from Confluent pricing page | Present |
| ContractedUnitPrice | Conditional | CUD or enterprise rate; Deviation for custom contracts | Deviation |
| PricingCategory | Conditional | "Standard" for on-demand; "Committed" for CUD plans | Deviation |
| ChargeFrequency | Conditional | "Usage-Based" | Deviation |
| BillingAccountType | Conditional | "Enterprise" or "Direct" | Present |
| SubAccountId | Conditional | Confluent environment ID | Present |
| SubAccountName | Conditional | Environment name | Present |
| SubAccountType | Conditional | "Environment" | Present |
| ResourceId | Conditional | Kafka cluster ID (lkc-xxxxx), connector ID, Schema Registry ID | Present |
| ResourceName | Conditional | Cluster name or resource name from Confluent Cloud | Present |
| ResourceType | Conditional | "Kafka Cluster", "Connector", "Schema Registry", "ksqlDB Application" | Present |
| SkuId | Conditional | Confluent billing type code (e.g., "kafka-read", "kafka-write", "kafka-storage") | Present |
| Tags | Conditional | N/A: Confluent billing does not expose custom tags at the billing layer | N/A |
| PricingCurrency | Conditional | USD | Present |
| PricingCurrencyListUnitPrice | Conditional | = ListUnitPrice | Present |
| PricingCurrencyContractedUnitPrice | Conditional | = ContractedUnitPrice; Deviation for enterprise | Deviation |
| PricingCurrencyEffectiveCost | Conditional | = EffectiveCost | Present |
| SkuMeter | Conditional | Billing dimension: "Write Throughput", "Read Throughput", "Storage", "Client Connections", "Cluster Link Hours" | Deviation |
| SkuPriceId | Conditional | No pricing catalog ID in Billing API | Missing: Conditional |
| SkuPriceDetails | Conditional | Not applicable (flat per-unit pricing) | Missing: Conditional |
| RegionId | Conditional | N/A: Confluent billing does not generate per-region rows | N/A |
| RegionName | Conditional | N/A | N/A |
| CommitmentDiscountId | Conditional | N/A: CUDs are pricing tiers, not FOCUS CommitmentDiscount | N/A |
| CommitmentDiscountName | Conditional | N/A | N/A |
| CommitmentDiscountType | Conditional | N/A | N/A |
| CommitmentDiscountCategory | Conditional | N/A | N/A |
| CommitmentDiscountStatus | Conditional | N/A | N/A |
| CommitmentDiscountQuantity | Conditional | N/A | N/A |
| CommitmentDiscountUnit | Conditional | N/A | N/A |
| CapacityReservationId | Conditional | N/A | N/A |
| CapacityReservationStatus | Conditional | N/A | N/A |
| InvoiceId | Recommended | Invoice number from Confluent billing dashboard | Present |
| ServiceSubcategory | Recommended | Map from resource type: "Kafka Streaming", "Kafka Connectors", "Schema Registry", "Stream Processing" | Missing: Recommended |
| AvailabilityZone | Recommended | N/A: Confluent billing does not produce per-AZ rows | N/A |

**Tally:** 28 Present, 10 Deviation, 0 Missing Mandatory, 2 Missing Conditional, 1 Missing Recommended, 16 N/A

### 1.4 What Is Solved, and What Remains

**Solved:** Per-cluster, per-dimension consumption data, environment hierarchy, cluster IDs, billing period, public on-demand pricing, invoice numbers. All 21 Mandatory columns have source data.

**Remaining:** Enterprise CUD or negotiated ContractedCost requires supplementary data. SkuPriceId absent.

### 1.5 Deviations to Fix

**PricingUnit normalization:** "GB" for read/write throughput and storage; "Connections" for client connections; "Hours" for cluster links and connector runtime hours.

**ChargeCategory:** "Usage" for all metered consumption. "Credit" for CUD credits.

**ServiceCategory:** "Analytics" for Confluent Cloud streaming data platform. Confluent is a streaming data platform; "Analytics" is the closest FOCUS ServiceCategory.

**SkuMeter:** Billing dimension label. Build a billing-type-code → SkuMeter mapping table.

---

## Part 2: The Path Forward

### 2.1 Which FOCUS Version to Target

Build to FOCUS v1.4 (June 4, 2026); certify at FOCUS v1.2.

### 2.2 What Certification Requires

Contact `member-cert@finops.org` for the RFI. Document CUDs as PricingCategory = "Committed", not CommitmentDiscount.

### 2.3 Phased Roadmap

**Phase 0:** Enable Confluent Billing API access. Pull one month of per-resource, per-dimension cost data.

**Phase 1: Core Kafka transform.** Map read/write throughput and storage rows. Derive ChargeCategory, ServiceCategory, PricingUnit, SkuMeter, ResourceId, SubAccount.

**Phase 2: Full resource portfolio.** Extend to Connectors, Schema Registry, ksqlDB. Integrate CUD rates for ContractedCost.

**Phase 3: Certify.** Add ServiceSubcategory. Drop ProviderName, PublisherName (v1.4). Validate and certify.

---

## Part 3: Immediate Next Steps

1. Enable Confluent Billing API (`GET /billing/v1/costs`) access.
2. Pull one month of cost data across all active clusters, connectors, and resources.
3. Build billing-type-code → PricingUnit and SkuMeter mapping table.
4. Implement Phase 1 Kafka transform and run through FOCUS Validator.
5. Open the RFI with `member-cert@finops.org`.

---

## Confidence Summary

- **High:** Confluent Billing API provides cluster-level cost data with billing type breakdown. All 28 Present columns are grounded in documented API fields.
- **High:** Cluster ID maps cleanly to ResourceId. Environment ID maps to SubAccountId.
- **Moderate:** PricingUnit normalization. Multiple billing dimensions need a consistent unit mapping table.
- **Low:** Enterprise CUD ContractedCost. Custom negotiated rates require supplementary data.

---

## Sources

- Confluent Cloud Billing API: [docs.confluent.io/cloud/current/billing](https://docs.confluent.io/cloud/current/billing)
- Confluent Cloud Pricing: [confluent.io/confluent-cloud/pricing/](https://www.confluent.io/confluent-cloud/pricing/)
- FOCUS Specification v1.2: [focus.finops.org](https://focus.finops.org/focus-specification/v1-2/)
- FinOps Certified FOCUS v1.2 Conformant: [finops.org/certification](https://www.finops.org/certification-for-organizations/finops-certified-focus-conformant/)

---

Written by Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is an unofficial community report based on public documentation. It is not a FOCUS or FinOps Foundation deliverable.

Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Product names and marks belong to their owners.

The FinOps Open Cost and Usage Specification is published at https://focus.finops.org.

Found something wrong? Open an issue or pull request in this repository. Vendors and others are welcome to correct a report.
