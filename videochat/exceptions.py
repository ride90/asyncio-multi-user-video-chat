from fastapi import status
from fastapi.responses import JSONResponse


async def http_exception_handler(request, exc):
    # return html response for 404
    if exc.status_code == status.HTTP_404_NOT_FOUND:
        return request.app.templates.TemplateResponse(
            '404.jinja2', {'request': request}, status_code=status.HTTP_404_NOT_FOUND
        )
    return JSONResponse(status_code=exc.status_code, content={'detail': exc.detail})
