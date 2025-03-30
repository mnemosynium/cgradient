import sys
import math

def build_ansi_256_table():
    colors = {}

    # Standard colors (0-15)
    basic = [
        (0, 0, 0), (128, 0, 0), (0, 128, 0), (128, 128, 0),
        (0, 0, 128), (128, 0, 128), (0, 128, 128), (192, 192, 192),
        (128, 128, 128), (255, 0, 0), (0, 255, 0), (255, 255, 0),
        (0, 0, 255), (255, 0, 255), (0, 255, 255), (255, 255, 255),
    ]
    for i, rgb in enumerate(basic):
        colors[str(i).zfill(3)] = list(rgb)

    # 6x6x6 color cube (16-231)
    levels = [0, 95, 135, 175, 215, 255]
    index = 16
    for r in levels:
        for g in levels:
            for b in levels:
                colors[str(index).zfill(3)] = [r, g, b]
                index += 1

    # Grayscale (232-255)
    for i in range(24):
        v = 8 + i * 10
        colors[str(index).zfill(3)] = [v, v, v]
        index += 1

    return colors


ansi_colors = build_ansi_256_table()


def hex2rgb(hex_str):
    hex_str = hex_str.lstrip("#")
    return [int(hex_str[i:i+2], 16) for i in (0, 2, 4)]


def code2rgb(code):
    return ansi_colors.get(code)


def parse_mixed_color_args(args):
    grad_args = []
    for cc in args:
        if len(cc) == 7 and cc.startswith("#"):
            cparsed = hex2rgb(cc)
        else:
            cparsed = code2rgb(cc)
        if cparsed is not None:
            grad_args.append(cparsed)
    return grad_args


def _clamp(num1, num2, num3):
    smaller = min(num2, num3)
    larger = max(num2, num3)
    minimum = max(0, smaller)
    maximum = min(255, larger)
    return max(minimum, min(num1, maximum))


def _gradient(length, rgb1, rgb2):
    assert length > 0
    if length == 1:
        return [rgb1]
    elif length == 2:
        return [rgb1, rgb2]
    else:
        step = [(rgb2[i] - rgb1[i]) / (length - 2) for i in range(3)]
        gradient = [rgb1[:]]
        for i in range(1, length - 1):
            intermediate = [math.ceil(rgb1[j] + i * step[j]) for j in range(3)]
            gradient.append(intermediate)
        gradient.append(rgb2)
        for i, color in enumerate(gradient):
            gradient[i] = [_clamp(c, rgb1[j], rgb2[j]) for j, c in enumerate(color)]
        return gradient


def _gradients(length, *args):
    if len(args) == 0:
        return []
    elif len(args) == 1:
        return args[0]
    elif len(args) == 2:
        return _gradient(length, args[0], args[1])
    else:
        quotient = length // (len(args) - 1)
        remainder = length % (len(args) - 1)
        gradients = []
        for section in range(len(args) - 1):
            seg_length = quotient + 1 if section < remainder else quotient
            segment = _gradient(seg_length, args[section], args[section + 1])
            gradients.extend(segment)
        return gradients[:length]


def color_code(rgb):
    least_distance = float('inf')
    color_name = ""
    for name, color in ansi_colors.items():
        distance = math.sqrt(sum((c1 - c2) ** 2 for c1, c2 in zip(color, rgb)))
        if distance < least_distance:
            least_distance = distance
            color_name = name
    return color_name


def lotjgradient(text, *colors):
    gradients = _gradients(len(text), *colors)
    cgradient = ""
    for i, char in enumerate(text):
        cgradient += f"&{color_code(gradients[i])}{char}"
    return cgradient


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: cgradient \"your text here\" color1 color2 [color3 ...]")
        sys.exit(1)

    input_text = sys.argv[1]
    input_colors = sys.argv[2:]

    color_args = parse_mixed_color_args(input_colors)

    if len(color_args) < 2:
        print("Please provide at least two valid color codes.")
        sys.exit(1)

    result = lotjgradient(input_text, *color_args)
    print(result)
