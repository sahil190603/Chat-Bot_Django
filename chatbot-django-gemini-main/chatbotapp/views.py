from django.shortcuts import redirect, render
from chatbot.settings import GENERATIVE_AI_KEY
from chatbotapp.models import ChatMessage
import google.generativeai as genai
import re
import requests
from django.core.files.base import ContentFile

import requests

def fetch_images(query):
    """Fetches a single image URL from Google Custom Search API."""
    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "searchType": "image",
        "cx": "Replace with Serachengine key",  
        "key": "Replace with a genrative Ai key",  
        "num": 1,
    }
    
    try:
        response = requests.get(search_url, params=params)
        response.raise_for_status()  
        
        data = response.json() 
        print("Full JSON Response:", data)
        
        if "items" in data and len(data['items']) > 0:
            return data['items'][0]['link']
        else:
            print("No image items found in the response.")
    except requests.RequestException as e:
        print(f"Request error: {e}")
    except ValueError as e:
        print(f"JSON decode error: {e}")

    return None



def save_image_from_url(image_url, filename):
    """Utility function to save an image from URL to a FileField."""
    response = requests.get(image_url)
    if response.status_code == 200:
        return ContentFile(response.content, name=filename)
    return None

def send_message(request):
    if request.method == 'POST':
        genai.configure(api_key=GENERATIVE_AI_KEY)
        model = genai.GenerativeModel("gemini-pro")

        user_message = request.POST.get('user_message')
        bot_response = model.generate_content(user_message)

        response_text = bot_response.text
        response_image_url = None

        if "<start_of_image>" in response_text or re.search(r'\[Image of .*\]', response_text):
            response_image_url = fetch_images(user_message)
            response_text = re.sub(r'<start_of_image>|\[Image of .*\]', '', response_text).strip()

        # Create the chat message
        chat_message = ChatMessage(
            user_message=user_message,
            bot_response=response_text,
        )

        if response_image_url:
            image_file = save_image_from_url(response_image_url, f"bot_response_{user_message}.jpg")
            if image_file:
                chat_message.bot_image.save(image_file.name, image_file)

        chat_message.save()

    return redirect('list_messages')

def list_messages(request):
    messages = ChatMessage.objects.all()
    return render(request, 'chatbot/list_messages.html', { 'messages': messages })
