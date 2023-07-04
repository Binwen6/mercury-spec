import mercury.src.bindings.python.src as mc

import logging

model_collection = mc.enumerateAvailableModels()

try:
    # get all models that fits the application
    chat_completion_models = model_collection.select(
        mc.buildFilter(usageScheme="chat-completion",
                       capabilities="imagination"))
    
    # find the cheapest model available
    selected_model = sorted(chat_completion_models,
                            key=lambda model: model.price)[0]

except mc.exceptions.ModelNotFoundException:
    logging.critical("Failed to find compatible model!")

model = mc.instantiateModel(selected_model)

request = input('Please tell me what kind of story you want to create: ')

# "True" indicates that the message is user-sent
response = model.call([
    f"""A user has made a request to create a story. Here is the user's request:

{request}

Please generate a story for the user. Output the story ONLY and NOTHING ELSE.""", True
])

print(f'Here is your story:\n{response}')

