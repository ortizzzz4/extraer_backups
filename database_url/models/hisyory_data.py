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
import io

import zipfile

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
    username=fields.Char(string="username sftp", required=True,default="root") 
    ssh_username = fields.Char(string="ssh username", default="root")
   # password=fields.Char(string="PASSWORD sftp")
    sftp_path=fields.Char(string="file path sftp", help="ruta donde esta almacenados los backups")
    ssh_path =fields.Char(string="file path ssh", help="ruta para almacenar los backups")
    ssh_ids=fields.Many2one('add.pkey.ids','ssh')
    pkey_private = fields.Text(related='ssh_ids.pkey_private',string="Clave privada",readonly=True)
    password_pkey=fields.Char(string="Password pkey",related='ssh_ids.password_pkey', readonly=True)
    file_na=fields.Char(string="filename")
    zip_file = fields.Char(string='Archivo ZIP')
    

    
    def sftp_fetch_and_save_zip(self):
        
        back = self.search([])
        
        for backups in back:      
            try:
                
                private_pke=paramiko.RSAKey(file_obj=io.StringIO(backups.pkey_private), password=backups.password_pkey)
                
                remote_folder = backups.sftp_path
                
                HOST = str(backups.url)#'157.245.84.13'
                PUERTO = int(backups.port)
                USUARIO = str( backups.username)#'rocket'
               # PASSWORD = backups.password
                datos = dict(hostname=HOST, port=PUERTO, username=USUARIO,pkey=private_pke)
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
 
                
                client.connect(**datos)
                sftp = client.open_sftp()

                files_in_folder = sftp.listdir(remote_folder)


                for file_name in files_in_folder:
                    if file_name.endswith('.zip'):              
                        existing_record = self.env['obtener.backup'].search([('file_zip','=' ,file_name)])           
                        if not existing_record:
                            self.env['obtener.backup'].create({
                                'url':HOST,
                                'file_zip': file_name,                           
                                })
                            _logger.info('Datos guardados')
                
           
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

    @api.model
    def schedule_file(self):
        functio = self.search_read([])
        
        for rec in self:
            rec.sftp_fetch_and_save_zip()
        return True 


    
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
   
            
    
  
    def download_selected_folder(self):
        database_history_obj = self.env['database.history']
      
        # Buscamos el registro específico en 'database.history' que queremos utilizar
        database_history_record = database_history_obj.search([], limit=1)
        
        selected_zip_name = self.file_zip  # Nombre del archivo .zip
        
        ip_server = database_history_record.url
        username=database_history_record.ssh_username
        file_path = database_history_record.sftp_path
        pkey_private = database_history_record.pkey_private
        password_pke = database_history_record.password_pkey
        
        download_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        ruta_destino = "/home/luis/Descargas/"

        HOST=ip_server
        USERNAME = username
        PORT=22
       
        
        private_key = paramiko.RSAKey(file_obj=io.StringIO(pkey_private),password=password_pke)
       
        
        datos = dict(hostname=HOST, port=PORT, username=USERNAME,pkey=private_key)
        _logger.info(datos)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
             
            client.connect(**datos)
            
            sftp = client.open_sftp()


            os.makedirs(download_folder, exist_ok=True)
            for item in sftp.listdir(file_path):
                remote_item_path = f"{file_path}/{item}"
                local_item_path = os.path.join(download_folder, item)
            
                if sftp.stat(remote_item_path).st_mode & 0o4000:
                    continue  # Skip symbolic links
                elif sftp.stat(remote_item_path).st_mode & 0o40000:
                # If it's a directory, recursively download it
                    self.download_selected_folder()
                else:
                 # If it's a file, download it
                    sftp.get(remote_item_path, local_item_path)
        
                _logger.info(f"Downloaded folder '{file_path}' to '{download_folder}'")

        except paramiko.AuthenticationException:
            _logger.exception("Error de autenticación. Verifica las credenciales SSH.")
        except paramiko.SSHException as e:
            _logger.exception("Error al establecer la conexión SSH: %s", str(e))
        except Exception as e:
            _logger.exception("Ocurrió un error: %s", str(e))
        finally:
            client.close()
        


       # return {
        #        'type': 'ir.actions.act_url',
         #       'url':f'/web/content/{str(self.id)}/{selected_zip_name}?download=true',
          #      'target': 'self',
           #         }
   
    def file_zip_dow(self):
        for rec in self:
            zip_file =rec.file_zip

            # Leer el archivo y codificarlo en base64
            with open(zip_file, "rb") as reader:
                result = base64.b64encode(reader.read())

            attachment_obj = self.env['ir.attachment'].sudo()
            name = zip_file
            attachment_id = attachment_obj.create({
                'name': name,
                'datas': result,
                'public': False,
               # 'res_model': 'obtener.backup',  # Reemplaza 'tu.modelo' con el nombre de tu modelo
                'res_id': rec.id,
                'mimetype': 'application/zip',  # Cambiar según el tipo de archivo
            })

            download_url = '/web/content/' + str(attachment_id.id) + '?download=true'
            return {
                'type': 'ir.actions.act_url',
                'url': download_url,
                'target': 'self',
            }
            
class AddPkey(models.Model):
    _name = "add.pkey.ids"
    _description = "Guardar Clave privada database url"
    
   
    name = fields.Char(string="nombre")
    pkey_private = fields.Text(string="Clave privada")
    password_pkey=fields.Char(string="password pkey")
    edit = fields.Boolean(default=True)
    
    
    def Guardar(self):
        existing_record = self.search([
            ('name', '=', self.name),  
            ('pkey_private', '=', self.pkey_private),
            ('password_pkey', '=', self.password_pkey)
        ])
        
        if not existing_record:
            self.create({
                'name': self.name,
                'pkey_private': self.pkey_private,
                'password_pkey': self.password_pkey,
                'edit':False
            })
    