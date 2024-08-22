from datetime import datetime
import json
import logging
import os
from utils.DB import fetch_query_as_json, execute_query

async def get_user_profile_data(user_id: str):
    # Consulta para obtener la información de Persona y Usuarios
    user_query = f"""
        SELECT 
            p.idPersona, p.Pnombre, p.Snombre, p.Papellido, p.Sapellido, p.email, p.telefono, p.fechaNacimiento,
            u.idUsuario, u.perfiPhotoRuta, u.Bibliografia, u.Artist
        FROM ArtAFolio.Persona p
        JOIN ArtAFolio.Usuarios u ON p.idPersona = u.idPersona
        WHERE u.idUsuario = '{user_id}'
    """
    user_info_json = await fetch_query_as_json(user_query)
    user_info = json.loads(user_info_json)
    if not user_info:
        return None

    # Consulta para obtener las galerías del usuario
    galleries_query = f"""
        SELECT 
            g.idGaleria, g.GaleriaNom
        FROM ArtAFolio.Galerias g
        WHERE g.idUsuario = '{user_id}'
    """
    galleries_json = await fetch_query_as_json(galleries_query)
    galleries = json.loads(galleries_json)

    # Consulta para obtener las obras de arte del usuario
    arts_query = f"""
        SELECT 
            a.idArte, a.imgNombre, a.imgRuta, a.descripcion, a.fecha, a.downloadPermision, a.IsAnimation
        FROM ArtAFolio.Artes a
        WHERE a.idUsuario = '{user_id}'
    """
    arts_json = await fetch_query_as_json(arts_query)
    arts = json.loads(arts_json)

    # Contar ilustraciones y animaciones
    illustration_count = sum(1 for art in arts if art["IsAnimation"] == '0')
    animation_count = sum(1 for art in arts if art["IsAnimation"] == '1')

    return {
        "user_info": user_info[0] if user_info else {},  # Se toma el primer resultado si existe
        "galleries": galleries,
        "arts": arts,
        "art_counts": {
            "illustrations": illustration_count,
            "animations": animation_count,
        }
    }

async def update_user_social_networks(id_user: str, social_net_list: list):
    try:
        # Paso 1: Eliminar redes sociales existentes del usuario
        delete_query = f"""
            DELETE FROM ArtAFolio.Usuarios_Redes
            WHERE idUsuario = '{id_user}'
        """
        await execute_query(delete_query)

        # Paso 2: Insertar redes sociales nuevas
        insert_queries = []
        for social_net in social_net_list:
            id_red = social_net['idRed']
            url = social_net['url']
            insert_query = f"""
                INSERT INTO ArtAFolio.Usuarios_Redes (idUsuario, idRedes, URL_Red)
                VALUES ('{id_user}', {id_red}, '{url}')
            """
            insert_queries.append(insert_query)

        # Ejecutar todas las consultas en una transacción
        try:
            await execute_query('BEGIN TRANSACTION;', is_procedure=True)
            for query in insert_queries:
                await execute_query(query)
            await execute_query('COMMIT;', is_procedure=True)
        except Exception as e:
            await execute_query('ROLLBACK;', is_procedure=True)
            raise e

        return True
    except Exception as e:
        print(f"Error updating user social networks: {str(e)}")
        return False
    
async def update_user_birthdate(user_id: str, new_birthdate: str):
    try:
        query = f"""
        UPDATE ArtAFolio.Persona
        SET fechaNacimiento = '{new_birthdate}'
        WHERE idPersona = (
            SELECT idPersona FROM ArtAFolio.Usuarios WHERE idUsuario = '{user_id}'
        )
        """
        result = await execute_query(query)
        
        # Verificar si la consulta fue exitosa
        if result is None or not json.loads(result).get("status") == 200:
            raise Exception("El usuario no existe o no se pudo actualizar la fecha de nacimiento.")
        
    except Exception as e:
        raise Exception(f"Error updating birthdate: {str(e)}")
    
async def get_profile_data(user_id: str):
    # Consulta para obtener la información de Persona y Usuarios
    user_query = f"""
        SELECT 
            p.idPersona, p.Pnombre, p.Snombre, p.Papellido, p.Sapellido, p.email, p.telefono, p.fechaNacimiento,
            u.idUsuario, u.perfiPhotoRuta, u.Bibliografia, u.Artist
        FROM ArtAFolio.Persona p
        JOIN ArtAFolio.Usuarios u ON p.idPersona = u.idPersona
        WHERE u.idUsuario = '{user_id}'
    """
    user_info_json = await fetch_query_as_json(user_query)
    user_info = json.loads(user_info_json)
    if not user_info:
        return None

    # Consulta para obtener las galerías del usuario
    galleries_query = f"""
        SELECT 
            g.idGaleria, g.GaleriaNom
        FROM ArtAFolio.Galerias g
        WHERE g.idUsuario = '{user_id}'
    """
    galleries_json = await fetch_query_as_json(galleries_query)
    galleries = json.loads(galleries_json)

    # Consulta para obtener las obras de arte del usuario
    arts_query = f"""
        SELECT 
            a.idArte, a.imgNombre, a.imgRuta, a.descripcion, a.fecha, a.downloadPermision, a.IsAnimation
        FROM ArtAFolio.Artes a
        WHERE a.idUsuario = '{user_id}'
    """
    arts_json = await fetch_query_as_json(arts_query)
    arts = json.loads(arts_json)

    # Contar ilustraciones y animaciones
    illustration_count = sum(1 for art in arts if art["IsAnimation"] == '0')
    animation_count = sum(1 for art in arts if art["IsAnimation"] == '1')

    return {
        "user_info": user_info[0] if user_info else {},  # Se toma el primer resultado si existe
        "galleries": galleries,
        "arts": arts,
        "art_counts": {
            "illustrations": illustration_count,
            "animations": animation_count,
        }
    }

async def search_artists_by_name(search_value: str):
    try:
        query = f"""
        SELECT u.idUsuario, u.perfiPhotoRuta, p.Pnombre, p.Papellido
        FROM ArtAFolio.Usuarios u
        JOIN ArtAFolio.Persona p ON u.idPersona = p.idPersona
        WHERE u.idUsuario LIKE '%{search_value}%'
        """
        result_json = await fetch_query_as_json(query)
        result = json.loads(result_json)
        return result
    except Exception as e:
        raise Exception(f"Error searching artists: {str(e)}")
    
async def follow_artist(current_user_id: str, artist_id: str) -> bool:
    try:
        # Obtener la fecha actual
        today_date = datetime.now().strftime('%Y-%m-%d')
        
        # Consulta para seguir al artista
        query = f"""
        INSERT INTO ArtAFolio.Usuarios_Seguidores (idUsuario, idSeguidor, fechaSeguimiento, Activo)
        VALUES ('{artist_id}', '{current_user_id}', '{today_date}', '1')
        """
        
        result = await execute_query(query)
        
        # Verificar si la consulta afectó alguna fila
        if result != '{"status": 200, "message": "Query executed successfully"}':
            raise Exception("No se pudo seguir al artista.")
        
        return True
    except Exception as e:
        raise Exception(f"Error siguiendo al artista: {str(e)}")