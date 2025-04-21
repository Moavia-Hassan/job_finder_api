from app.integrated_api import app
from mangum import Mangum

# Create an ASGI handler for Vercel serverless functions
handler = Mangum(app)