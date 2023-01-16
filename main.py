from fastapi import FastAPI, Depends, HTTPException, status
from database import comments_table, database, post_table, user_table
from models import Comment, CommentIn, User, UserIn, UserPost, UserPostIn, UserPostWithComments
from security import authenticate_user, create_access_token, get_current_user, get_password_hash


app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/")
async def root():
    return {"message": "Hello, World"}


@app.post("/post", status_code=201, response_model=UserPost)
async def create_post(
        post: UserPostIn,
        current_user: User = Depends(get_current_user)
):
    data = {**post.dict(), "user_id": current_user.id}
    query = post_table.insert().values(data)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}


@app.get("/posts", response_model=list[UserPost])
async def get_all_posts():
    query = post_table.select()
    return await database.fetch_all(query)


@app.post("/register")
async def register(user: UserIn):
    hashed_password = get_password_hash(user.password)
    query = user_table.insert().values(username=user.username, password=hashed_password)
    await database.execute(query)
    access_token = create_access_token(user.username)
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/token")
async def login(user: UserIn):
    user = await authenticate_user(user.username, user.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(user.username)
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@app.post("/comment", response_model=Comment)
async def create_comment(
    comment: CommentIn, current_user: User = Depends(get_current_user)
):
    data = {**comment.dict(), "user_id": current_user.id}
    query = comments_table.insert().values(data)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}


@app.get("/post/{post_id}/comments", response_model=list[Comment])
async def get_comments_on_post(post_id: int):
    query = comments_table.select().where(comments_table.c.post_id == post_id)
    return await database.fetch_all(query)


@app.get("/posts/{post_id}", response_model=UserPostWithComments)
async def get_post_with_comments(post_id: int):
    query = post_table.select().where(post_table.c.id == post_id)
    post = await database.fetch_one(query)
    query = comments_table.select().where(comments_table.c.post_id == post_id)
    comments = await database.fetch_all(query)
    return {**post, "comments": comments}

