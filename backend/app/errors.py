from uuid import uuid4


class AppError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status: int = 422,
        stage: str = "request",
        retryable: bool = False,
    ):
        super().__init__(code)
        self.code, self.message, self.status = code, message, status
        self.stage, self.retryable = stage, retryable

    def envelope(self, request_id: str | None = None):
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "stage": self.stage,
                "retryable": self.retryable,
                "request_id": request_id or str(uuid4()),
            }
        }
