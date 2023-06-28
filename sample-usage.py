import mercury_nn as mc

# init is done when the module is imported
# mc.initialize()

custom_filter = mc.Filter(
    classes=["chat-completion", "text-continuation"],
    capabilities=["question-answering"],
    properties={"deployment-type": "local", "latency": "<=10ms"},
    input=str,
    output=str
)

models = mc.find_models(filter=custom_filter)

# select and instantiate the cheapest model
model = mc.instantiate(max(models, key=lambda x: x.properties.price))

# call the model
output = model.call("koalas are so cute!")
