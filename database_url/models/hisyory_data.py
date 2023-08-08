# -*- coding: utf-8 -*-

from odoo import models, fields, api
import xmlrpc.client
import base64
import logging
import paramiko
import subprocess
import logging
from odoo.exceptions import UserError
from pathlib import Path
from stat import S_ISDIR


import pwd
import os
_logger = logging.getLogger(__name__)
class HistoyUrlDt(models.Model):
    _name="database.history"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description="Historial base de datos"
    
    
    name  = fields.Char(string="Username database")
    
    url=fields.Char(string="IP", help='0.0.0.0', required=True)
    port= fields.Char(string="PORT", default="22")
    username=fields.Char(string="username sftp", required=True) 
    ssh_username = fields.Char(string="ssh username", default="root")
    password=fields.Char(string="PASSWORD sftp", required=True)
    sftp_path=fields.Char(string="file path", help="/path/")
    ssh_path =fields.Char(string="Ruta a guardar", help="/home/users/path/")
    file_na=fields.Char(string="filename")
    zip_file = fields.Char(string='Archivo ZIP')
    

    
    def sftp_fetch_and_save_zip(self):
        
        back = self.search([])
        
        for backups in back:      
            try:
               
                remote_folder = backups.sftp_path
                
                HOST = str(backups.url)#'157.245.84.13'
                PUERTO = int(backups.port)
                USUARIO = str( backups.username)#'rocket'
                PASSWORD = backups.password
                datos = dict(hostname=HOST, port=PUERTO, username=USUARIO,password=PASSWORD)
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
 
                
                client.connect(**datos)
                sftp = client.open_sftp()

                files_in_folder = sftp.listdir(remote_folder)


                for file_name in files_in_folder:
                    if file_name.endswith('.zip'):
                        new_record = self.env['obtener.backup']                
                        new_record.create({
                            'url':HOST,
                            'file_zip': file_name})
                
           
                client.close()


            except Exception as e:
                raise UserError("Error:", str(e))
        return {
                                'type': 'ir.actions.client',
                                'tag': 'display_notification',
                                'params': {
                    'title': 'Completado!!!',
                    'message': 'Extraidos con èxito',
                    'sticky': False,
                          },   }

            


    
    """def extraer_datos(self):
        my_models = self.search([])
        if not my_models:
            return False
        
        processed_totals = {}
     
        for my_model in my_models:
            db = my_model.name
            username = my_model.username
            url = my_model.url
            password = my_model.password
            
            
            try:
                common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
                models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
            except Exception as e:
                _logger.error('Error de conexión: %s', str(e))
                return True
            
            
            
            
            try:
                uid = common.authenticate(db,username, password ,[])
            except Exception as e:
                _logger.error('Error de autenticación en la base de datos %s: %s', db, str(e))
                continue
            
            try:
                backups = models.execute_kw(db, uid, password, 'db.backup.configure', 'search', [[]])
                company_ids = models.execute_kw(db, uid, password, 'res.company', 'search', [[]])
            except Exception as e:
                _logger.error('Error al obtener datos de la base de datos %s: %s', db, str(e)) 
                continue
            
            for bk in backups:
                try:
                    backup = models.execute_kw(db, uid, password, 'db.backup.configure', 'read', [bk, ['backup_filename']])
                    print(backup)  # Agregar esta línea para inspeccionar el valor de 'backup'
    
                    datos = self.env['obtener.backup'].create({
                    'name': db,
                    'url': url,
                    'file_name':backup[0]['backup_filename']
                        })
                    _logger.info('Datos guardados')
                except Exception as e:
                    _logger.error('Error al leer los datos del movimiento de cuenta en la base de datos %s: %s', db, str(e))
                    continue
               
               """
               
class ObtDatosBakc(models.Model):
    _name = "obtener.backup"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description ="Tablas backups"
    
    name = fields.Char(string="Nombre", readonly=True)
   
    file_zip= fields.Char(string="Backups List" , readonly=True)
    
    record_ids = fields.Many2one('database.history', 'fields')
    
    #url =fields.Char(related='record_ids.url', string='IP', readonly=True)
    #ssh_username=fields.Char(related='record_ids.ssh_username',string="ssh username" ,readonly=True)
    #ssh_path =fields.Char(related='record_ids.ssh_path', string="ssh path", readonly=True)
    
    url = fields.Char(string="IP", readonly=True)
   
            
            
            
    def download_db(self):
        database_history_obj = self.env['database.history']
      

        # Buscamos el registro específico en 'database.history' que queremos utilizar
        database_history_record = database_history_obj.search([], limit=1)
        if not database_history_record:
            _logger.error('datos no encontrados')
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error',
                    'type': 'danger',
                    'message': 'Datos no encontrados en la tabla "database.history".',
                          },   }

      
        remote_server = database_history_record.url
        remote_username = database_history_record.username
        remote_port=database_history_record.port
        remote_folder = database_history_record.sftp_path
        remote_password=database_history_record.password
        remoto_path = database_history_record.ssh_path
       #     
       # file_path = self.file_zip

      #  if not remote_server or not remote_username or not remote_folder or not file_path:
       #         _logger.error("Falta información necesaria en el registro.")
        #        return {
         #           'type': 'ir.actions.client',
         #           'tag': 'display_notification',
          #          'params': {
          #              'title': 'Error',
          #              'type': 'danger',
          #              'message': 'Falta información necesaria en el registro.',
          #      },
          #  }
       
            # Establecer la conexión SFTP al servidor remoto
            
        HOST = str(remote_server)#'157.245.84.13'
        PUERTO =int(remote_port)#int(remote_port)
        USUARIO = str(remote_username)#'rocket'
        PASSWORD =remote_password
        REMOTE_FOLDER = remote_folder
       # LOCAL_FOLDER = os.path.expanduser("~/Downloads")
        LOCAL_FOLDER = remoto_path
      #  LOCAL_FOLDER = os.path.join(str(Path.home()), "Downloads")

        
        datos = dict(hostname=HOST, port=PUERTO, username=USUARIO,password=PASSWORD)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
              
        
        try:
        
            client.connect(**datos)
            #sftp = client.open_sftp() 
          
                 
            with client.open_sftp() as sftp:
                ruta_completa_remota = (REMOTE_FOLDER + self.file_zip)
                _logger.info("Ruta carpeta remota: %s", ruta_completa_remota)
            
                # carpeta_local_descargas = os.path.expanduser("~/Descargas")
                ruta_completa_local = os.path.join(os.path.expanduser("~/"), "Descargas")          
                _logger.info("Ruta archivo local: %s", ruta_completa_local)

                 # Descargar el archivo zip que contiene la carpeta
                client.get(ruta_completa_remota, ruta_completa_local)
                _logger.info("Carpeta descargada como %s", self.file_zip)

            
              #  return {
               #     'type': 'ir.actions.act_url',
                #    'url': f'/web/content/{str(self.id)}/{self.file_zip}?download=true',
                #    'target': 'self',
                #}
           
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error',
                    'type': 'danger',
                    'message': f'Error: {e}',
                          },   }
        finally:
            sftp.close()
            client.close()
        

        
  
    def download_selected_folder(self):
        self.ensure_one()  # Asegura que solo estamos operando en un único registro
        database_history_obj = self.env['database.history']
      

        # Buscamos el registro específico en 'database.history' que queremos utilizar
        database_history_record = database_history_obj.search([], limit=1)
        
        remote_server = database_history_record.url
        remote_username = database_history_record.username
        remote_port=database_history_record.port
        remote_folder = database_history_record.sftp_path
        remote_password=database_history_record.password
        remoto_path = database_history_record.ssh_path

        hostname = str(remote_server)
        port = int(remote_port)
        username = str(remote_username)
        password = remote_password
        remote_base_folder = remote_folder # Ruta base de los backups en el servidor remoto
        local_folder = remoto_path  # Ruta local donde se guardarán los backups

        selected_folder = self.file_zip  # Nombre de la carpeta seleccionada

        #remote_folder = os.path.join(remote_base_folder, selected_folder)
        transport = paramiko.Transport((hostname, port))
        transport.connect(username=username, password=password)
        try:
            sftp = paramiko.SFTPClient.from_transport(transport)
            remote_zip = os.path.join(remote_base_folder, selected_folder)
            _logger.info(remote_zip)
            local_zip_path = os.path.join("/home/luis/Descargas", selected_folder)
            _logger.info(local_zip_path)
            
           
    
            sftp.get(remote_zip, local_zip_path)
            
            return {
                   'type': 'ir.actions.act_url',
                   'url': f'/web/content/{str(self.id)}/{self.file_zip}?download=true',
                    'target': 'self',
            }
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error',
                    'type': 'danger',
                    'message': f'Error: {e}',
                          },   }       
        finally:
            sftp.close()
            transport.close()

            
            
        

