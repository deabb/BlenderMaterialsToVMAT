from PIL import Image
import os

def extract_alpha_channel(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.png'):  # only PNG files
            file_path = os.path.join(input_dir, filename)
            with Image.open(file_path) as img:
                if img.mode == 'RGBA':

                    alpha = img.getchannel('A')

                    base_name, _ = os.path.splitext(filename)
                    alpha_file_name = f"{base_name}_alpha.jpg"
                    alpha_file_path = os.path.join(output_dir, alpha_file_name)

                    alpha.save(alpha_file_path, 'JPEG')

                    print(f"Processed {filename} -> {alpha_file_name}")

    print("Processing complete.")

desktop_path = os.path.expanduser("~/Desktop")
input_directory = os.path.join(desktop_path, 'cool_mats')
output_directory = os.path.join(input_directory, 'alphas')

extract_alpha_channel(input_directory, output_directory)
