import mercury_nn as mc
import matplotlib.pyplot as plt


entry = next(iter(filter(lambda x: mc.MetadataUtils.getModelName(x.metadata) == 'DALL E', mc.enumerateAvailableModels())))
model = mc.instantiateModel(entry)

plt.figure(figsize=(10, 10))
plt.imshow(model.call('a cute little koala.'))
plt.show()
