def test_template():
    from packs._template.rules import TemplatePolicyEvaluator
    ev = TemplatePolicyEvaluator({}, {})
    assert ev.evaluate([1, 2])["status"] == "TEMPLATE_READY"
