"""Module for define APP plate process."""

import zipfile
import io
import base64

import os
import typing as tp
from pathlib import Path
from fpdf import FPDF

# from src.services.utils import PDFClassicPredictor, PDFDLPredictor
#
#
# class Storage:
#     def __init__(self, config: dict):
#         self._config = config
#         os.makedirs(config["dir_path"], exist_ok=True)
#         os.makedirs(config["dir_upload"], exist_ok=True)
#
#     # def get(self, content_id: str) -> tp.Optional[str]:
#     #     content_path = self._get_path(content_id)
#     #     if not os.path.exists(content_path):
#     #         return "Start process image first"
#     #     with open(content_path, "r") as json_data:
#     #         return json.load(json_data)
#
#     def save(self, input_file: bytes, file_name: str) -> None:
#         pdf_path = Path(self._config["dir_path"]) / f"{file_name}.pdf"
#         with open(pdf_path, "wb") as f:
#             f.write(input_file)
#
#
# class ProcessPDF:
#     """Class for storing processed"""
#     status = "Start process PDF first"
#
#     def __init__(
#         self,
#         storage: Storage,
#         pdf_classic_predictor: PDFClassicPredictor,
#         pdf_dl_predictor: PDFDLPredictor
#     ):
#         self.storage = storage
#         self.pdf_classic_predictor = pdf_classic_predictor
#         self.pdf_dl_predictor = pdf_dl_predictor
#         print("finish process plate init")
#
#     def process(self, pdf: np.ndarray, content_name: str) -> dict:
#         """
#         Process image
#         :param image: input image to process
#         :param content_id: id of input image
#         :return: dictionary with results in json format
#         """
#         self.storage.save(image, content_name)
#         granules_image, granules_mask = self.granules_mask_predictor.predict(
#             image,
#         )
#         return {
#             'type': 'prediction',
#             'data': [
#                 self.get_bytes_value(cv2.cvtColor(granules_image, cv2.COLOR_BGR2RGB)),
#                 self.get_bytes_value(granules_mask)
#             ]
#         }
#
#     def get_bytes_value(
#             self,
#             image: np.array
#     ) -> str:
#         image_pil = Image.fromarray(image)
#         img_byte_arr = io.BytesIO()
#         image_pil.save(img_byte_arr, format='JPEG')
#         return base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
#
#
# class GetGOA:
#     """Class for get GOA images"""
#     def __init__(self, config: dict):
#         self._config = config
#         self.goa_path = self._config['goa_path']
#         print('Start zip process')
#         self.zip_goa_data = self.zipfiles(self.goa_path)
#         print('Finish zip process')
#
#     def get(self, content_type: str) -> tp.Tuple[int, dict, str]:
#         """
#         Check and get early processed results
#         :param content_id: id of image to process (equal to image name)
#         :return: str or json object with results
#         """
#         goa_code, goa_data, goa_error = 500, {}, 'Can not get data'
#         if content_type == "zip":
#             goa_data = self.zip_goa_data
#             if goa_data != {}:
#                 goa_code = 200
#                 goa_error = 'No errors'
#         else:
#             numbers = content_type.split('-')
#             number1, number2 = 0, 0
#             try:
#                 number1 = int(numbers[0])
#             except ValueError:
#                 goa_error = "Invalid content type, first number not an integer"
#
#             if number1 and len(numbers) > 1:
#                 try:
#                     number2 = int(numbers[-1])
#                 except ValueError:
#                     goa_error = "Invalid content type, second number not an integer"
#             elif len(numbers) > 2:
#                 goa_error = "Invalid content type"
#
#             if number1:
#                 goa_data = self.get_goa_images(self.goa_path, number1, number2)
#                 if goa_data != {}:
#                     goa_code = 200
#                     goa_error = 'No errors'
#             else:
#                 goa_error = "Invalid content type"
#         return goa_code, goa_data, goa_error
#
#     def zipfiles(self, goa_path: str) -> dict:
#         zip_filename = "goa_data.zip"
#         s = io.BytesIO()
#         with zipfile.ZipFile(s, 'w') as zf:
#             for root, dirs, files in os.walk(goa_path):
#                 for file in files:
#                     zf.write(
#                         os.path.join(root, file),
#                         os.path.relpath(
#                             os.path.join(root, file),
#                             os.path.join(goa_path, '..'),
#                         )
#                     )
#         return {
#             'type': 'zip',
#             'data': [base64.b64encode(s.getvalue()).decode('utf-8')]
#         }
#
#     def get_goa_images(
#         self,
#         goa_path: str,
#         number1: int,
#         number2: int = 0
#     ) -> dict:
#         goa_names = list(
#             os.walk(Path(goa_path) / 'images')
#         )[0][-1]
#         sorted_goa_names = np.sort(goa_names)
#
#         if number1 < 0 or number1 > len(goa_names):
#             return {}
#
#         if not number2:
#             number2 = number1+1
#         response_images_name = sorted_goa_names[number1:number2]
#
#         return {
#             'type': 'images',
#             'data': [
#                 self.get_bytes_value(goa_path, image) for image in response_images_name
#             ]
#         }
#
#     def get_bytes_value(
#             self,
#             goa_path: str,
#             image_path: str
#     ) -> str:
#         image = jpeg.JPEG(Path(goa_path) / 'images' / image_path).decode()
#         image_pil = Image.fromarray(image)
#         img_byte_arr = io.BytesIO()
#         image_pil.save(img_byte_arr, format='JPEG')
#         return base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
