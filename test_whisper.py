from speech import transcribe

text = transcribe("command.wav")

print("You said:")
print(text)