from datetime import date
import json
from utils.DB import fetch_query_as_json, execute_query

async def get_gallery_details(gallery_id: int):
    try:
        # Consulta para obtener la información de la galería
        gallery_query = f"""
        SELECT 
            g.idGaleria, g.GaleriaNom, u.idUsuario, u.perfiPhotoRuta, u.Bibliografia
        FROM ArtAFolio.Galerias g
        JOIN ArtAFolio.Usuarios u ON g.idUsuario = u.idUsuario
        WHERE g.idGaleria = {gallery_id}
        """
        gallery_json = await fetch_query_as_json(gallery_query)
        gallery_info = json.loads(gallery_json)
        if not gallery_info:
            return None

        # Consulta para obtener las obras de arte en la galería
        arts_query = f"""
        SELECT 
            a.idArte, a.imgNombre, a.imgRuta, a.descripcion, a.fecha, a.downloadPermision, a.IsAnimation
        FROM ArtAFolio.Galerias_Artes ga
        JOIN ArtAFolio.Artes a ON ga.idArte = a.idArte
        WHERE ga.idGaleria = {gallery_id}
        """
        arts_json = await fetch_query_as_json(arts_query)
        arts = json.loads(arts_json)

        return {
            "gallery_info": gallery_info[0] if gallery_info else {},
            "arts": arts
        }
    except Exception as e:
        raise Exception(f"Error fetching gallery details: {str(e)}")


async def get_artwork_details(gallery_id: int, artwork_id: int):
    try:
        # Consulta para obtener la información de la obra de arte y del usuario al que pertenece
        artwork_query = f"""
        SELECT 
            a.idArte, a.imgNombre, a.imgRuta, a.descripcion, a.fecha, a.downloadPermision, a.IsAnimation,
            u.idUsuario, u.perfiPhotoRuta, u.Bibliografia
        FROM ArtAFolio.Artes a
        JOIN ArtAFolio.Usuarios u ON a.idUsuario = u.idUsuario
        WHERE a.idArte = {artwork_id} AND a.idUsuario IN (
            SELECT idUsuario FROM ArtAFolio.Galerias WHERE idGaleria = {gallery_id}
        )
        """
        artwork_json = await fetch_query_as_json(artwork_query)
        artwork_info = json.loads(artwork_json)
        if not artwork_info:
            return None

        # Consulta para obtener los hashtags asociados a la obra de arte
        hashtags_query = f"""
        SELECT 
            h.nombreHashtag
        FROM ArtAFolio.Hashtags_Artes ha
        JOIN ArtAFolio.Hashtags h ON ha.idHashtag = h.idHashtag
        WHERE ha.idArte = {artwork_id}
        """
        hashtags_json = await fetch_query_as_json(hashtags_query)
        hashtags = json.loads(hashtags_json)

        # Consulta para obtener las estadísticas de likes
        likes_query = f"""
        SELECT 
            COUNT(*) as total_likes
        FROM ArtAFolio.Likes
        WHERE idArte = {artwork_id}
        """
        likes_json = await fetch_query_as_json(likes_query)
        likes = json.loads(likes_json)

        return {
            "artwork_info": artwork_info[0] if artwork_info else {},
            "hashtags": hashtags,
            "likes": likes[0]['total_likes'] if likes else 0
        }
    except Exception as e:
        raise Exception(f"Error fetching artwork details: {str(e)}")
    

async def get_artwork_comments(gallery_id: int, artwork_id: int):
    try:
        # Consulta para obtener los comentarios de la obra de arte
        comments_query = f"""
        SELECT 
            c.idComentario, c.textoComentario, c.Fecha, u.idUsuario, u.perfiPhotoRuta
        FROM ArtAFolio.Comentarios c
        JOIN ArtAFolio.Usuarios u ON c.idUsuario = u.idUsuario
        WHERE c.idArte = {artwork_id} AND c.idArte IN (
            SELECT idArte FROM ArtAFolio.Artes WHERE idUsuario IN (
                SELECT idUsuario FROM ArtAFolio.Galerias WHERE idGaleria = {gallery_id}
            )
        )
        """
        comments_json = await fetch_query_as_json(comments_query)
        comments = json.loads(comments_json)

        return comments
    except Exception as e:
        raise Exception(f"Error fetching artwork comments: {str(e)}")
    
async def update_artwork_description(gallery_id: int, artwork_id: int, new_description: str) -> bool:
    try:
        # Consulta para actualizar la descripción de la obra de arte
        update_query = f"""
        UPDATE ArtAFolio.Artes
        SET descripcion = '{new_description}'
        WHERE idArte = {artwork_id} AND idArte IN (
            SELECT idArte FROM ArtAFolio.Galerias_Artes WHERE idGaleria = {gallery_id}
        )
        """
        result = await execute_query(update_query)
        
        # Verificar si se afectaron filas
        if result != 1:
            raise Exception("No se pudo actualizar la descripción de la obra de arte.")
        
        return True
    except Exception as e:
        raise Exception(f"Error updating artwork description: {str(e)}")
    

async def add_comment_to_artwork(gallery_id: int, artwork_id: int, user_id: str, comment_text: str) -> bool:
    try:
        # Consulta para agregar un comentario
        insert_query = f"""
        INSERT INTO ArtAFolio.Comentarios (idUsuario, idArte, textoComentario, Fecha)
        VALUES ('{user_id}', {artwork_id}, '{comment_text}', '{date.today()}')
        """
        result = await execute_query(insert_query)
        
        # Verificar si se afectaron filas
        if result != 1:
            raise Exception("No se pudo agregar el comentario.")
        
        return True
    except Exception as e:
        raise Exception(f"Error adding comment: {str(e)}")
    
async def add_like_to_artwork(gallery_id: int, artwork_id: int, user_id: str) -> bool:
    try:
        # Consulta para agregar un like
        insert_query = f"""
        INSERT INTO ArtAFolio.Likes (idArte, idUsuario, fecha)
        VALUES ({artwork_id}, '{user_id}', '{date.today()}')
        """
        result = await execute_query(insert_query)
        
        # Verificar si se afectaron filas
        if result != 1:
            raise Exception("No se pudo agregar el like.")
        
        return True
    except Exception as e:
        raise Exception(f"Error adding like: {str(e)}")