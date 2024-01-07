# GPT-Guardian
GptGuardian is a content moderation tool for discord that monitors for hate speech, harmful content & misinformation (or a user defined level of censorship) and fact-checks text, images, audio, video and hyperlinks. The application allows for varying degrees of customization for administrators monitoring their servers.

https://devpost.com/software/listy-city-lovers


# Venv setup
```
  $bash setup.sh
  OR
  $virtualenv venv --python=python3
  $source venv/bin/activate
  $pip install -r requirements.txt
```
# secret_values.py
needs file secret_values.py in root, file must have 
```
  BOT_TOKEN = "token of bot you want this to run on"
  GPT_KEY = "openAPI token"
  SEARCH_KEY = "bing search api token"
  VT_KEY = "virustotal api token"
  AUDIO_KEY = "speech-to-text token"
```

# bot setup + invite 

  https://discordpy.readthedocs.io/en/stable/discord.html 
