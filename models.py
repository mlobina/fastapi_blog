from pydantic import BaseModel


class UserPostIn(BaseModel):
    user_id: int
    body: str


class UserPost(UserPostIn):
    id: int


class User(BaseModel):
    id: int | None = None
    username: str


class UserIn(User):
    password: str


class CommentIn(BaseModel):
    body: str
    post_id: int


class Comment(CommentIn):
    id: int
    user_id: int


class UserPostWithComments(UserPost):
    comments: list[Comment]

