from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
import requests

app = Flask(__name__)

draw_synonyms = ["draw", "paint", "image", "picture", "photo", "painting"]

def calculate_perplexity(text):
    perplexity_api_key = "perplexity_api_key"
    perplexity_api_url = "perplexity_api_url"
    
    headers = {
        "Authorization": f"Bearer {perplexity_api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "mistral-7b-instruct",
        "messages": [{"role": "system", "content": "System: Hi, how can I assist you?"},  
                     {"role": "user", "content": text}] 
    }
    
    response = requests.post(perplexity_api_url, headers=headers, json=data)
    
    if response.status_code == 200:
        try:
            json_response = response.json()
            choices = json_response.get('choices', [])
            if choices:
                first_choice = choices[0]
                message = first_choice.get('message', {})
                content = message.get('content', '')
                print("Response Content:", content)
                return content
            else:
                print("Error: No choices found in response JSON:", json_response)
                return None
        except Exception as e:
            print("Error:", e)
            return None
    else:
        print("Error:", response.text)
        return None





def generate_image(text_prompt):
    """Generate image from Dall.E2"""
    
    
    pass

@app.route("/whatsapp", methods=['POST'])
def wa_reply():
    query = request.form.get('Body').lower()
    print("User Query:", query)
    twilio_response = MessagingResponse()
    reply = twilio_response.message()
    
    if query.split(" ")[0].lower() in draw_synonyms:
        img_url = generate_image(query)
        if img_url:
            reply.media(img_url, caption=query)
        else:
            reply.body("Failed to generate image. Please try again later.")
    else:
        perplexity = calculate_perplexity(query)
        if perplexity is not None:
            reply.body(f"Perplexity of the query: {perplexity}")
        else:
            reply.body("Failed to calculate perplexity. Please try again later.")
    
    return str(twilio_response)

if __name__ == "__main__":
    app.run(debug=True)