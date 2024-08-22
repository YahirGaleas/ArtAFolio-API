from fastapi import Body, FastAPI, Query, Request, Response, File, UploadFile, HTTPException

from fastapi.middleware.cors import CORSMiddleware
from controllers.profiles import follow_artist,search_artists_by_name, get_profile_data,get_user_profile_data, update_user_social_networks, update_user_birthdate
from controllers.google import login_google , auth_callback_google
from controllers.portfolio import add_like_to_artwork,add_comment_to_artwork,update_artwork_description, get_artwork_comments,get_gallery_details, get_artwork_details

from utils.DB import get_db_connection

from models.profileModels import SocialNetUpdate, BirthDateUpdate

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos
    allow_headers=["*"],  # Permitir todos los encabezados
)

@app.get("/")
async def hello():
    return {
        "Hello": "World"
        , "version": "0.1.0"
    }


@app.get("/db-check")
async def db_check():
    try:
        # Intentar conectarse a la base de datos
        conn = await get_db_connection()
        # Si la conexión es exitosa, cierra la conexión y devuelve un mensaje de éxito
        conn.close()
        return {"status": "success", "message": "Database connection successful"}
    except Exception as e:
        # Si ocurre un error, devolver un mensaje de error
        raise HTTPException(status_code=500, detail=str(e))
    


id_user = "YexPlay"  # Reemplaza con el ID del usuario de prueba que desees

@app.get("/user")
async def get_user_profile():
    user_data = await get_user_profile_data(id_user)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    return user_data
    
@app.put("/user/{iduser}/social-networks")
async def update_user_social_networks(id_user: str, payload: SocialNetUpdate):
    success = await update_user_social_networks(id_user, payload.social_net)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update social networks")
    return {"status": "success", "message": "Social networks updated successfully"}

@app.put("/user/{idUser}/birth")
async def update_birthdate(idUser: str, birthdate: BirthDateUpdate):
    try:
        result = await update_user_birthdate(idUser, birthdate.fechaNacimiento)
        if result:
            return {"status": "success", "message": "Birthdate updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/profile/{idUser}")
async def get_user_profile(idUser1: str):
    profile_data = await get_profile_data(idUser1)
    if not profile_data:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile_data


@app.get("/artist")
async def search_artist(name: str = Query(..., min_length=1)):
    try:
        artists = await search_artists_by_name(name)
        if not artists:
            raise HTTPException(status_code=404, detail="No artists found")
        return artists
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/profile/{idUser}/follower")
async def follow_user(idUser: str, id_user):
    try:
        success = await follow_artist(id_user, idUser)
        if not success:
            raise HTTPException(status_code=400, detail="No se pudo seguir al artista")
        return {"status": "success", "message": "Artista seguido exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/galerias/{idGaleria}")
async def get_gallery(idGaleria: int):
    try:
        gallery_details = await get_gallery_details(idGaleria)
        if not gallery_details:
            raise HTTPException(status_code=404, detail="Gallery not found")
        return gallery_details
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/galerias/{idGaleria}/artworks/{idArt}")
async def get_artwork(idGaleria: int, idArt: int):
    try:
        artwork_details = await get_artwork_details(idGaleria, idArt)
        if not artwork_details:
            raise HTTPException(status_code=404, detail="Artwork not found")
        return artwork_details
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/galerias/{idGaleria}/artworks/{idArt}/comments")
async def get_artwork_comments_endpoint(idGaleria: int, idArt: int):
    try:
        comments = await get_artwork_comments(idGaleria, idArt)
        if comments is None:
            raise HTTPException(status_code=404, detail="No comments found")
        return comments
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/galerias/{idGaleria}/artworks/{idArt}/description")
async def update_artwork_description_endpoint(idGaleria: int, idArt: int, description: str = Body(...)):
    try:
        success = await update_artwork_description(idGaleria, idArt, description)
        if not success:
            raise HTTPException(status_code=404, detail="Artwork not found or description not updated")
        return {"status": "success", "message": "Description updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/galerias/{idGaleria}/artworks/{idArt}/comment")
async def add_comment_endpoint(idGaleria: int, idArt: int, comment: str = Body(...), user_id: str = "test_user"):
    try:
        success = await add_comment_to_artwork(idGaleria, idArt, user_id, comment)
        if not success:
            raise HTTPException(status_code=404, detail="Artwork not found or comment not added")
        return {"status": "success", "message": "Comment added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/galerias/{idGaleria}/artworks/{idArt}/like")
async def add_like_endpoint(idGaleria: int, idArt: int, like_payload: dict = Body(...)):
    try:
        user_id = like_payload.get("idUser")
        if not user_id:
            raise HTTPException(status_code=400, detail="idUser is required in the payload")
        
        success = await add_like_to_artwork(idGaleria, idArt, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Artwork not found or like not added")
        return {"status": "success", "message": "Like added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))






@app.get("/login/google")
async def logingoogle():
    return await login_google()

@app.get("/auth/google/callback")
async def authcallbackgoogle(request: Request):
    return await auth_callback_google(request)


##@app.get("/login")
##async def login():
    #return await login_o365()

#@app.get("/auth/callback")
#async def authcallback(request: Request):
   #return await auth_callback_o365(request)

