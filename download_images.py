import os
import urllib.request

images_dir = '/home/kali/Desktop/project/cafe website/app/static/images/menu_items'
os.makedirs(images_dir, exist_ok=True)

items_to_download = [
    ("paneer_wrap.jpg", "https://placehold.co/400x400/2ecc71/ffffff.png?text=Paneer+Wrap"),
    ("croissant.jpg", "https://placehold.co/400x400/f1c40f/ffffff.png?text=Croissant"),
    ("nachos.jpg", "https://placehold.co/400x400/e67e22/ffffff.png?text=Loaded+Nachos"),
    ("tiramisu.jpg", "https://placehold.co/400x400/8e44ad/ffffff.png?text=Tiramisu"),
    ("cheesecake.jpg", "https://placehold.co/400x400/f39c12/ffffff.png?text=New+York+Cheesecake"),
    ("lava_cake.jpg", "https://placehold.co/400x400/c0392b/ffffff.png?text=Lava+Cake"),
    ("gulab_jamun.jpg", "https://placehold.co/400x400/d35400/ffffff.png?text=Gulab+Jamun"),
]

for name, url in items_to_download:
    path = os.path.join(images_dir, name)
    try:
        # User-Agent header is sometimes required by placehold.co
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(path, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
        print(f"Downloaded {name}")
    except Exception as e:
        print(f"Failed to download {name}: {e}")
