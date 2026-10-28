import os
import random

MOTIVATION_MESSAGES = [
    "Small changes can make a huge difference!",
    "The future depends on what you do today.",
    "Difficult roads often lead to beautiful destinations.",
    "Success is the sum of small efforts, repeated day in and day out.",
    "It's amazing to find out what happens when you don't give up!",
    "Work spares us from three evils: boredom, vice, and need.",
    "If you're going through hell, at least act like you own the place.",
    "I am a work in progress!",
    "Two things you can control today: attitude and effort.",
]

# Get all images from the local folder
MOTIVATION_IMAGE_PATH = "media/motivation"
MOTIVATION_IMAGES = [
    f"/media/motivation/{img}" for img in os.listdir(MOTIVATION_IMAGE_PATH) if img.endswith(("jpg", "png", "jpeg"))
]

def get_random_motivation():
    """Get a random motivational message and image."""
    return {
        "message": random.choice(MOTIVATION_MESSAGES),
        "image_url": random.choice(MOTIVATION_IMAGES),
    }
