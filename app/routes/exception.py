from fastapi import HTTPException
from starlette.status import HTTP_404_NOT_FOUND,HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED

UserNotFoundException = HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User with this ID does not exist.")
UserExistedException = HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="User with this username or email has already been existed.")

ImageNotFoundException = HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Image with this ID does not exist.")

SpeciesNotFoundException = HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Species with this ID does not existed.")
SpeciesNameExistedException = HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Species with this name has already been existed")

TaskNotFoundException = HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Task with this ID does not exist.")
TaskAcceptAcceptedException = HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Task with this ID has already been accepted.")
TaskFinishUserNotSame = HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="You cannot finish a task that has been accepted by another user.")
TaskFinishNotAcceptedTaskError = HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="You cannot finish a task that has been not accepted.")
TaskFinishFinishedTaskError = HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="You cannot finish a task that has been finished.")
TaskAcceptFinishedException = HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Task with this ID has already been finished.")

BboxNotFoundException = HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Bbox with this ID does not exist.")
PolygonNotFoundException = HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Polygon with this ID does not exist.")

AddAnnotationToFinishedTaskException = HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="You cannot add an annotation to a task that has already been finished.")
AddAnnotationToPendingTaskException = HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="You cannot add an annotation to a task that has not been accepted.")
AddAnnotationFromNotAcceptedUser = HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="You cannot add an annotation to a task that did not accepted.")
AddBboxToPolygonTaskTypeException = HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="You cannot add a bbox to a task that have not bbox annotation type")
AddPolygonToBboxTaskTypeException = HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="You cannot add a polygon to a task that have not polygon annotation type")