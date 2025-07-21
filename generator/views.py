from django.shortcuts import render, redirect
from .models import Generation
from django.core.files.base import ContentFile
from io import BytesIO
import requests
import base64

STABILITY_API_KEY = "sk-jlz9Gfp8YXxKnZvUOauLUEKyKKLQiTuLCZlCBeTHbRS7C1aQ"

# Calls Stability AI API to generate an image from a prompt
def generate_image_from_prompt(prompt):
    url = "https://api.stability.ai/v1/generation/stable-diffusion-v1-6/text-to-image"
    headers = {
        "Authorization": f"Bearer {STABILITY_API_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    payload = {
        "text_prompts": [{"text": prompt}],
        "cfg_scale": 7,
        "clip_guidance_preset": "FAST_BLUE",
        "height": 512,
        "width": 512,
        "samples": 1,
        "steps": 30
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()
    # The API returns base64-encoded images
    image_b64 = data["artifacts"][0]["base64"]
    image_data = base64.b64decode(image_b64)
    return image_data

def generate(request):
    if request.method == 'POST':
        prompt = request.POST.get('prompt')
        image_data = generate_image_from_prompt(prompt)
        image_file = ContentFile(image_data, name='generated.png')
        generation = Generation.objects.create(prompt=prompt, image=image_file)
        return redirect('generation_result', pk=generation.pk)
    return render(request, 'generator/generate.html')

def generation_result(request, pk):
    generation = Generation.objects.get(pk=pk)
    return render(request, 'generator/result.html', {'generation': generation})
