from PIL import Image
import os

layer2_path = 'static/images/psd_layers/layer_2_Inserted Image.png'
layer3_path = 'static/images/psd_layers/layer_3_Inserted Image.png'
output_path = 'static/images/psd_layers/merged_2_3.png'

layer2 = Image.open(layer2_path).convert('RGBA')
layer3 = Image.open(layer3_path).convert('RGBA')

# Ensure both images are the same size (use the larger size)
width = max(layer2.width, layer3.width)
height = max(layer2.height, layer3.height)

base = Image.new('RGBA', (width, height), (0, 0, 0, 0))
base.paste(layer3, (0, 0), layer3)
base.paste(layer2, (0, 0), layer2)

base.save(output_path)
print(f'Merged image saved to {output_path}') 