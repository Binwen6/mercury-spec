# import libraries
import mercury_nn as mc
import matplotlib.pyplot as plt


chat_filter = mc.Filter.fromArgs(callScheme="chat-completion",
                                capabilities=["instruction-comprehension"])

image_generation_filter = mc.Filter.fromArgs(callScheme="image-generation")

# mercury was previous imported as mc
model_collection = mc.enumerateAvailableModels()

chat_models = model_collection.select(chat_filter)
image_generation_models = model_collection.select(image_generation_filter)

# `ModelCollection` implements `__getitem__` method
chat_model = chat_models[0]
image_generation_model = image_generation_models[0]

chat_model = mc.instantiateModel(chat_model)
image_generation_model = mc.instantiateModel(image_generation_model)

greeting = "Hi! I'm a chatbot. Let's chat!"
print(greeting)

messages = [("""
You are a chatbot talking to a user.
Although you are a text-based chatting model,
you now have the ability to generate images,
because each time you say something, I will analyze what you said and see if you intend to create an image.
Just speak normally as if you can generate images,
and when you do need to create an image, ALWAYS LEAVE A PLACEHOLDER in your response, e.g., "[image-placeholder]".
There is no delay in image generation; each time you show the intent to make an image, the image is generated instantly,
so there is no need to say things like "wait a moment".""", True)]

while True:
    # retrieve user input
    user_input = input('>>> ')
    # append user input to message history (boolean value indicates who sent the message, True for user and False for AI)
    messages.append((user_input, True))
    # retrieve AI's response
    ai_response = chat_model.call(messages)
    # append AI's response to message history
    messages.append((ai_response, False))

    # illustration generation
    illustration_decision_input = f"""
You are talking to a user. You decided to respond to the user:

{ai_response}

Do you think there is image content in the above response?
If yes, output a description for the image and NOTHING ELSE;
if you are SURE there is no image content, output "NO" and NOTHING ELSE.
If there is an image-placeholder in your response (e.g., [image-placeholder]), it is guaranteed that there is image content;
in this case, you should output the description for the image, and DO NOT output "NO".
"""

    illustration_decision = chat_model.call([(illustration_decision_input, True)])

    image = None
    if illustration_decision != "NO":
        # generate image
        image = image_generation_model.call(illustration_decision)

    # print AI's message
    print(ai_response)

    if image is not None:
        print(f"I also made an illustration.")
        plt.figure(figsize=(10, 10))
        plt.imshow(image)
        plt.title('illustration')
        plt.axis('off')
        plt.show()

    shutdown_decision_prompt = f"""
    You are chatting with a user. The user says:

    {user_input}

    Does the user want to end the conversation? Output "YES" or "NO" ONLY and NOTHING ELSE.
    """

    response = chat_model.call([(shutdown_decision_prompt, True)])

    if response == "YES":
        break