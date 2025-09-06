import json
import urllib.request

# Скачати список класів ImageNet
url = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
classes_txt = urllib.request.urlopen(url).read().decode("utf-8").splitlines()

# Зробимо словник: {id: class}
classes_dict = {str(i): c for i, c in enumerate(classes_txt)}

with open("imagenet_classes.json", "w") as f:
    json.dump(classes_dict, f)

print("imagenet_classes.json створено!")