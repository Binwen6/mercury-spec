import mercury_nn as mc


model_entries = mc.enumerateAvailableModels()

print([mc.MetadataUtils.getModelName(entry.metadata) for entry in model_entries])

from lxml import etree as ET
from mercury_nn import manifest_validation


base_model_filter = mc.Filter.fromXMLElement(ET.parse(mc.config.Config.baseModelFilterPath.value).getroot())

for entry in model_entries:
    assert manifest_validation.checkSyntax(entry.metadata).isValid
    assert mc.filtering.matchFilter(base_model_filter, entry.metadata).isSuccess