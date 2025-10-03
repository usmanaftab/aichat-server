from app import create_app
from mangum import Mangum

app = create_app()
handler = Mangum(app, lifespan="off")
