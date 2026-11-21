# FOCUS gap analyses

Plain-language reports on how vendor billing and usage data lines up with the FinOps Open Cost and Usage Specification (FOCUS). The specification is published at https://focus.finops.org.

There are 98 reports. Each one has an "Analysis run" date and is based on public documentation only.

## What's in the repo

- Written analyses, one markdown file per vendor, in [analyses/](analyses/).
- The full red-amber-green readiness dashboard and a by-company index in [index/](index/). The dashboard currently covers 76 providers; the written set has 98 reports, so some newer analyses are not yet on the scorecard.

## What this repo is

- A set of written, dated readings of public vendor documentation against a version of the specification.
- A place to correct those readings with public evidence.

## What this repo is not

- Not a certification, a lab test, or a conformance result.
- Not an official FOCUS, FinOps Foundation, or Linux Foundation publication.
- Not a project position or an endorsement of any vendor.

## Who writes it

Beau Nelford, FOCUS Technical Community Architect, acting in a personal and community capacity. This is a personal and community project under the Beau-finopsorg handle. See [DISCLAIMER.md](DISCLAIMER.md).

## Rating scale

- **Aligned:** public documentation indicates the product's cost and usage data matches the relevant version of the specification for the columns and behaviors in scope of the analysis.
- **Partially aligned:** public documentation shows some of the required shape or columns, with documented gaps.
- **Not yet aligned (per public docs):** public documentation does not show a specification-shaped export, or the gaps are substantial.

## Read the ratings with care

Ratings are a reading of public documentation on the date shown in each report's "Analysis run" line. They may be incomplete or out of date. A vendor may have done more than it has published. Ratings are not a certification result or an official project verdict.

## Correct a report

Vendors and others can correct a report.

1. Open a [vendor correction issue](https://github.com/beau-finopsorg/focus-gap-analyses/issues/new?template=vendor-correction.yml), or send a pull request.
2. Cite public sources: docs, a changelog, or a sample export.
3. If you work for the vendor, say so.

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Request a new analysis

Open a [new data generator issue](https://github.com/beau-finopsorg/focus-gap-analyses/issues/new?template=new-data-generator.yml). Share the vendor's public documentation links and any public claim about the specification.

## License

The written analyses are under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). See [LICENSE](LICENSE). Any code later added is MIT unless a file says otherwise.

## Sibling repos

- https://github.com/beau-finopsorg/focus-ecosystem: a community link index.
- https://github.com/beau-finopsorg/focus-tools: community reference tools, including schema maps and reference architectures.
