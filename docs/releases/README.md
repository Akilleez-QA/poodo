# Releases and version descriptions

No release has been tagged (`git tag --list` is empty). The CHANGELOG sections 3.0.0 and 3.1.0 have no matching tags. Until a tag exists, each documentation baseline gets a version description (VDD) and test report (STR) named after its commit. `tools/gen_release_docs.py` generates both; do not edit them by hand.

| Baseline | Version description | Test report |
|---|---|---|
| `34629aa` (main, untagged) | [VDD-main-34629aa](VDD-main-34629aa.md) | [STR-main-34629aa](../verification/reports/STR-main-34629aa.md) |

See [TP-3 in the test plan](../verification/test-plan.md#tp-3--generate-the-release-documents) to generate a new pair and the [SCMP](../configuration/configuration-management.md#7-release-management-and-delivery) for the release procedure.
