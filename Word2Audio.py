# Invoke Baidu api to transfer words into mp3 format
from aip import AipSpeech

# Input Baidu api key
app_id = "15555270"
api_key = "TMQId6iN3xrjk6uIZnDlPT6G"
secret_key = "CEPVn1GiZk7rW8t1k22nXXprIzdX51hz"

client = AipSpeech(app_id, api_key, secret_key)

# Pass on parameter
result = client.synthesis("大哥大嫂新年好", "zh", 1, {
    "vol": 5,  # Volumn
    "spd": 3,  # Speed
    "pit": 6,  # Tone
    "per": 4   # Character 0:woman 1:man 3:cool man 4.lolita
})

#  If Identify correctly return speech(binary data) if error, return dict
if not isinstance(result, dict):
    with open("audio3.mp3", "wb") as f:
        # print(type(result))
        f.write(result)
