from pydantic import BaseModel

class PhraseIn(BaseModel):
    text: str
    author_id: str

class VoteIn(BaseModel):
    phrase_id: str
    voter_id: str
