# -*- coding: utf-8 -*-

from odoo import models, fields, api
import xmlrpc.client
import base64
import logging
import paramiko
import subprocess
import logging
from odoo.exceptions import UserError

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
    ssh_path =fields.Char(string="Ruta de carpeta", help="/home/users/path/")
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
        server = self.record_ids.url
        username = self.record_ids.username
        folder = self.record_ids.sftp_path
        port = self.record_ids.port
        passw = self.record_ids.password

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
        remote_port=database_history_obj.port
        remote_folder = database_history_record.sftp_path
        remote_password=database_history_obj.password
            
        file_path = self.file_zip

        if not remote_server or not remote_username or not remote_folder or not file_path:
                _logger.error("Falta información necesaria en el registro.")
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Error',
                        'type': 'danger',
                        'message': 'Falta información necesaria en el registro.',
                },
            }
       
            # Establecer la conexión SFTP al servidor remoto
            
        HOST = str(remote_server)#'157.245.84.13'
        PUERTO =int(remote_port)#int(remote_port)
        USUARIO = str(username)#'rocket'
        PASSWORD = passw
       
        datos = dict(hostname=HOST, port=PUERTO, username=USUARIO,password=PASSWORD)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
        
        
        try:
        
            client.connect(**datos)
            
            sftp = client.open_sftp() 
            
            remote_folder_path = os.path.join(remote_folder, self.file_zip)
            local_folder_path = os.path.expanduser('~/Descargas')
            
            remote_file_path = remote_folder_path
            local_file_path = os.path.join(local_folder_path, self.file_zip)
            sftp.get(remote_file_path, local_file_path)

            # Cerrar la conexión SFTP
            
            sftp.close()
                # Devolver la acción que redirige a la URL de descarga
            return {
                    'type': 'ir.actions.act_url',
                    'url': f'/web/content/{str(self.id)}?download=true',
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
            client.close()
        

        
      
            
            
            
        

    """ except Exception as e:
            _logger.error('Error de conexión: %s', str(e))
            return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Error',
                'type': 'danger',
                'message': 'Error de conexión: %s' % str(e),
            },
    }"""