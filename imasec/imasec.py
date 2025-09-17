from PIL import Image
import sys

MAX_LEN = 1024  # maksymalna długość wiadomości

def encode(input_image_path, output_image_path, message: str):
    if len(message) > MAX_LEN:
        raise ValueError(f"Maksymalna długość wiadomości to {MAX_LEN} znaków")

    # Dodaj znacznik końca wiadomości
    message += chr(0)
    binary_message = ''.join([format(ord(c), '08b') for c in message])

    img = Image.open(input_image_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')

    pixels = img.load()

    width, height = img.size
    total_pixels = width * height

    if len(binary_message) > total_pixels * 3:
        raise ValueError("Obraz jest za mały, aby pomieścić wiadomość.")

    data_index = 0
    for y in range(height):
        for x in range(width):
            if data_index >= len(binary_message):
                break

            r, g, b = pixels[x, y]
            rgb = [r, g, b]

            for n in range(3):
                if data_index < len(binary_message):
                    rgb[n] = (rgb[n] & ~1) | int(binary_message[data_index])
                    data_index += 1
            pixels[x, y] = tuple(rgb)

        if data_index >= len(binary_message):
            break

    img.save(output_image_path)
    print(f"✅ Zakodowano {len(message)-1} znaków w {output_image_path}")


def decode(image_path):
    img = Image.open(image_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')

    pixels = img.load()
    width, height = img.size

    binary_data = ""
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            for n in (r, g, b):
                binary_data += str(n & 1)

    # Konwersja na string dopóki nie trafimy na znak \0
    chars = []
    for i in range(0, len(binary_data), 8):
        byte = binary_data[i:i+8]
        if len(byte) < 8:
            continue
        char = chr(int(byte, 2))
        if char == chr(0):
            break
        chars.append(char)

    message = ''.join(chars)
    print(f"📜 Odczytana wiadomość: {message}")
    return message


if __name__ == "__main__":
    # Prosty interfejs CLI
    if len(sys.argv) < 3:
        print("Użycie:")
        print("  python steg.py encode input.jpg output.png 'wiadomość'")
        print("  python steg.py decode input.png")
        sys.exit(1)

    mode = sys.argv[1]

    if mode == "encode" and len(sys.argv) == 5:
        encode(sys.argv[2], sys.argv[3], sys.argv[4])
    elif mode == "decode" and len(sys.argv) == 3:
        decode(sys.argv[2])
    else:
        print("❌ Złe parametry.")
