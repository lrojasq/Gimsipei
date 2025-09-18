# import asyncio
from os import getenv, remove, path, makedirs, listdir
from datetime import datetime
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

from werkzeug.utils import secure_filename

from app.utils.responses import Response

# load environment variables
load_dotenv('../../.env')

directory_local = 'recursos'

# create one class manege connection with database
class HelperSie:
    def get_blob_service_client_account_key(self):
        """Method to get the blob account client"""
        try:
            # Create the BlobServiceClient object which will be used to create a container client
            account_url = getenv("ACCOUNT_URL")
            shared_access_key = getenv("AZURE_STORAGE_ACOUNT_KEY")

            blob_service_client = BlobServiceClient(account_url=account_url, credential=shared_access_key)
            return Response.tuple_response(blob_service_client, 200)
        except Exception as e:
            return Response.tuple_response("Error al intentar obtener el cliente del blob account", 400)

    def get_content_type(self, file_name) -> str:
        """Method to get the content type of a file"""
        content_types = {
            'pdf': 'application/pdf',
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'webp': 'image/webp',
            'svg': 'image/svg+xml',
            'gif': 'image/gif',
            'bmp': 'image/bmp',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'doc': 'application/msword',
            'txt': 'text/plain',
            'odt': 'application/vnd.oasis.opendocument.text',
            'xls': 'application/vnd.ms-excel',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'ods': 'application/vnd.oasis.opendocument.spreadsheet',
            'ppt': 'application/vnd.ms-powerpoint',
            'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'key': 'application/vnd.apple.keynote',
            'avi': 'video/x-msvideo',
            'mp4': 'video/mp4',
            'mov': 'video/quicktime',
            'mkv': 'video/x-matroska',
            'zip': 'application/zip',
            'rar': 'application/x-rar-compressed',
            'tar': 'application/x-tar',
            'gz': 'application/gzip'
        }

        # Extract the file extension
        file_extension = file_name.split('/')[-1]
        return content_types.get(file_extension.lower(), 'application/octet-stream')

    def upload_file_to_azure(self, container_name: str, content_type: str, request) -> tuple:
        """Method to upload a file to Azure Blob Storage"""
        try:
            blob_service_client = self.get_blob_service_client_account_key()
            if blob_service_client[1] != 200:
                return Response.tuple_response(blob_service_client[0], blob_service_client[1])

            file = request.files["recurso"]
            # Get the BlobClient for the file you want to upload
            blob_client = blob_service_client[0].get_blob_client(container_name, f"{datetime.now().strftime('%Y%m%d%H%M%S')}-{secure_filename(file.filename)}")

            # Upload the file to Blob Storage with the content and content type specified
            blob_client.upload_blob(file, content_type=content_type, overwrite=True)

            # Validate if the file was uploaded correctly
            if not blob_client.exists():
                return Response.tuple_response("Precaución: El archivo no se subió correctamente", 200)

            return Response.tuple_response({"url": blob_client.url, "nombre": blob_client.blob_name}, 200)
        except Exception as e:
            return Response.tuple_response("Error al intentar subir el archivo a Azure Blob Storage", 400)


    def delete_resource_azure(self, container_name: str, name_cheild: str) -> tuple:
        """Method to delete a resource from Azure Blob Storage"""
        try:
            blob_service_client = self.get_blob_service_client_account_key()
            if blob_service_client[1] != 200:
                return Response.tuple_response(blob_service_client[0], blob_service_client[1])

            # Get the BlobClient for the file you want to delete
            blob_client = blob_service_client[0].get_blob_client(container_name, name_cheild)
            
            # Verify if the blob exists before deleting it
            if not blob_client.exists():
                return Response.tuple_response("The resource does not exist in Azure Blob Storage", 200)

            blob_client.delete_blob()

            return Response.tuple_response("Resource deleted successfully", 200)
        except Exception as e:
            return Response.tuple_response("Error al intentar eliminar el recurso de Azure Blob Storage", 400)


    def save_file(self, file, filename):
        """Method to save a file in the local directory resources"""
        try:
            # Create the directory if it doesn't exist
            if not path.exists(directory_local):
                makedirs(directory_local)

            # Define the complete file path
            file_path = path.join(directory_local, filename)

            # Save the file
            with open(file_path, 'wb') as folder:
                folder.write(file.read())

            return Response.tuple_response("File saved successfully", 200)
        except Exception as e:
            return Response.tuple_response("Error al intentar guardar el archivo", 400)


    def extension_file(self, filename) -> bool:
        """Method to validate the file extension"""
        ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'webp', 'svg', 'docx', 'doc', 'xls', 'xlsx', 'ppt', 'pptx', 'odt', 'key', 'ods',
                              'gif', 'bmp', 'avi', 'mp4', 'mov', 'mkv', 'zip', 'rar', 'tar', 'gz'}
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


    def upload_file(self, request) -> tuple:
        """Method to validate the file extension"""
        try:
            # Verify if the file is in the request
            if 'recurso' not in request.files:
                return Response.tuple_response("No se envió el archivo", 200)
            file = request.files['recurso']
            
            # Verify if the file is empty
            if file.filename == '':
                return Response.tuple_response("Se envió un archivo vacío", 200)
            
            # Verify if the file has a valid extension
            if not self.extension_file(file.filename):
                return Response.tuple_response("The file does not have a valid extension", 200)

            # Verify the maximum file size
            MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB -> MB to KB -> KB to Bytes
            file.seek(0, 2) # Seek to the end of the file
            file_size = file.tell() # Get the position of EOF
            file.seek(0) # Reset the file position to the beginning
            if file_size > MAX_FILE_SIZE:
                return Response.tuple_response("The file exceeds the maximum allowed size", 200)

            # Verify if the file has a valid name
            file_name = secure_filename(file.filename)
            if len(file_name) < 4 or len(file_name) > 40:
                return Response.tuple_response("The file name must have between 4 and 40 characters", 200)
            
            # Verify if the file has a content type
            content_type = file.content_type
            if not content_type:
                file.content_type = 'application/octet-stream'
                        
            return Response.tuple_response("Correct validation", 201)
        except Exception as e:
            return Response.tuple_response("Error al intentar subir el archivo", 400)

    