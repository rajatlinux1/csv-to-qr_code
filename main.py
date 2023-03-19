import shutil
import os, sys
import glob
from pathlib import Path
import pandas as pd
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from tqdm import tqdm
import config

BASE_DIR = Path(__file__).resolve().parent

if config.OUTPUT_DIR not in os.listdir():
    os.mkdir(config.OUTPUT_DIR)

try:
    file_path = f"{BASE_DIR}/input_files/{config.CSV_FILE_NAME}"
except FileNotFoundError:
    raise f"\"{config.CSV_FILE_NAME}\" file put in \"input_files\" directory"
file_name = ((file_path.split('/')[-1]).split('.')[0]).replace(' ', '-')

try:
    if f"{config.OUTPUT_DIR}/{file_name}" not in os.listdir():
        os.makedirs(f"{config.OUTPUT_DIR}/{file_name}")
except FileExistsError:
    pass

def qr_code_genration():
    print("Qr code generating...")
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"\33[91m >> \"{config.CSV_FILE_NAME}\" file put in \"input_files\" directory\33[0m")
        sys.exit()

    for channel_name in tqdm(df[config.TARGET_COLUMN_NAME]):


        qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
        )
        qr.add_data(f"{channel_name}")
        qr.make(fit=True)
        channel_name = channel_name.replace(" ", "-")
        channel_name = channel_name.replace("/", "-")

        img = qr.make_image(fill_color=config.QR_CODE_FILL_COLOR, back_color=config.QR_CODE_BACK_COLOR)

        try:
            img.save(f"{config.OUTPUT_DIR}/{file_name}/{channel_name}.{config.OUTPUT_QR_CODE_EXTENTSION}")
        except Exception as e:
            print(f"\033[91mQR Code Not Generated for this name \"{channel_name}\"\033[0m")

    print(f"\033[92mQR Code Successfully Created! for \"{config.CSV_FILE_NAME}\"\033[0m")

    if (config.AFTER_PROCESS_CSV_MOVE).lower() == 'yes':
        if config.PROCESSED_DIR not in os.listdir() and (config.AFTER_PROCESS_CSV_MOVE).lower() == 'yes':
            os.mkdir(config.PROCESSED_DIR)
        shutil.move(file_path, config.PROCESSED_DIR)


def gen_pdf_sheet(file_name=None):
    print("PDF sheet generating...")
    if not file_name:
        raise "Provide file name"
    try:
        os.makedirs(f"{config.OUTPUT_DIR}/{file_name}/pdf_file")
    except FileExistsError:
        pass
    c = canvas.Canvas(f"{config.OUTPUT_DIR}/{file_name}/pdf_file/{file_name}_codes.pdf",pagesize=A4)
    c.setTitle="QR-Codes"
    codes = glob.glob(f"{BASE_DIR}/{config.OUTPUT_DIR}/{file_name}/*.{config.OUTPUT_QR_CODE_EXTENTSION}")

    left_step = 35
    down_step = 720

    for code in tqdm(codes):

        if left_step > 435:
            left_step = 35
            down_step = down_step - 100
        
        if down_step < 20:
            down_step = 720
            c.showPage()

        c.drawImage(code, left_step, down_step, width=100, height=100)
        # image_name = ((((code.split("/")[-1]).split(".")[0]).replace("-", " ")).title()).replace(' ', '')
        # print("image_name == ", image_name)
        left_step = left_step + 100
        if (config.AFTER_SHEET_IMAGE_FILE_SHOULD_DELETE).lower() == "yes":
            os.remove(code)

    c.save()
    print("\033[92mPDF Generated Successfully!\033[0m")


if __name__ == "__main__":
    qr_code_genration()
    if (config.WANT_PDF_SHEET).lower() == 'yes':
        gen_pdf_sheet(file_name=file_name)