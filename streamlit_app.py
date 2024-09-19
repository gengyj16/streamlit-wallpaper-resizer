import streamlit as st
from PIL import Image
from io import BytesIO
import zipfile

size_list = [
    (1920, 1080),
    (2160, 1080),
    (2280, 1080),
    (2340, 1080),
    (3168, 1440),
    (2400, 1080),
    (3216, 1440),
    (2520, 1080),
    (1612, 720),
    (2408, 1080),
    (2772, 1240),
]


def process_image(image, alignV, align, selected_resolutions):
    zip_buffer = BytesIO()

    with Image.open(image) as im:
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            for height, width in selected_resolutions:
                folder = (
                    f"drawable-xxhdpi-{height}x{width}" if height != 1920 else "drawable-xxhdpi"
                )
                if im.size[1] / im.size[0] > height / width:
                    new_img = Image.new(
                        "RGBA", (im.size[0], int(height / width * im.size[0])), (0, 0, 0, 0)
                    )
                    if alignV == 0:
                        new_y = (height / width * im.size[0] - im.size[1]) / 2
                    elif alignV == 2:
                        new_y = height / width * im.size[0] - im.size[1]
                    else:
                        new_y = 0
                    new_img.paste(im, (0, int(new_y)))
                else:
                    new_img = Image.new(
                        "RGBA", (int(width / height * im.size[1]), im.size[1]), (0, 0, 0, 0)
                    )
                    if align == 0:
                        new_x = (width / height * im.size[1] - im.size[0]) / 2
                    elif align == 2:
                        new_x = width / height * im.size[1] - im.size[0]
                    else:
                        new_x = 0
                    new_img.paste(im, (int(new_x), 0))

                new_img = new_img.resize((width, height), Image.Resampling.LANCZOS)
                new_img = new_img.convert("RGB")
                img_byte_arr = BytesIO()
                new_img.save(img_byte_arr, format="JPEG", quality=92)
                img_byte_arr.seek(0)
                zip_file.writestr(f"{folder}/{pic_name}.jpg", img_byte_arr.read())

    zip_buffer.seek(0)
    return zip_buffer


st.title("多分辨率壁纸生成")
uploaded_file = st.file_uploader(
    "选择一张图片...",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=False,
)
selected_resolutions = st.multiselect(
    "壁纸分辨率",
    options=size_list,
    default=size_list[0:8],
    format_func=lambda x: f"{x[0]}x{x[1]}",
)
pic_name = st.text_input("图片名称", "oppo_default_wallpaper")
alignV = st.selectbox("竖向对齐", ["居中", "顶部", "底部"])
align = st.selectbox("横向对齐", ["居中", "居左", "居右"])
if uploaded_file is not None:
    if st.button("生成"):
        alignV_value = 0 if alignV == "居中" else (1 if alignV == "顶部" else 2)
        align_value = 0 if align == "居中" else (1 if align == "居左" else 2)
        zip_buffer = process_image(
            uploaded_file, alignV_value, align_value, selected_resolutions
        )
        st.success("处理完成！")
        st.download_button(
            label="下载多分辨率壁纸",
            data=zip_buffer,
            file_name="wallpaper_res.zip",
            mime="application/zip",
        )
